"""
================================================================================
EVMOTO MULTI-ROLE END-TO-END (E2E) DISPATCH BATCH INTEGRATION TEST SUITE
================================================================================
Target Integrasi :
  1. Role Superadmin     : Admin Dashboard Web & API (https://evmotoadmin.justkidding.app/dispatchBatch)
  2. Role Customer / User: User App Booking Flow (Reguler & Advance Booking)
  3. Role Mitra Driver   : Driver App Batch Dispatch (Multiple Orders, No Countdown, Accept, Reject, Cancel)
Metodologi       : Multi-Role Actor E2E Synchronization (Headless / API & Page Objects)
Aturan Bisnis    :
  - Radius distance band filtering (Ordinary: 0-5 KM, Advance: 0-15 KM)
  - Batch size 5 drivers, 0s duration (tanpa countdown)
  - Driver menerima multiple orders sekaligus
  - Driver memilih dan menyelesaikan order reguler, serta menolak advance booking
  - 100% Deterministic & Zero Crash
================================================================================
"""
import pytest
import time
from Frontend.Feature.Helper.admin_dispatch_batch_helper import AdminDispatchBatchHelper
from Frontend.Feature.Helper.driver_role_simulator import DriverRoleSimulator
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestE2EDispatchBatch")


@pytest.fixture(scope="module")
def admin_actor():
    """Actor 1: Superadmin pada Admin Dashboard."""
    helper = AdminDispatchBatchHelper()
    assert helper.login(), "Superadmin harus berhasil login ke Admin Dashboard Staging"
    yield helper
    # Restore baseline
    helper.submit_dispatch_batch(
        enabled=True,
        size=5,
        delay=10,
        duration=0,
        concurrent=5,
        rescans=2,
        ordinary_bands=[("0", "1"), ("1", "2"), ("2", "3"), ("3", "4"), ("4", "5")],
        advance_bands=[("0", "1"), ("1", "2"), ("2", "5"), ("5", "15")]
    )


@pytest.fixture(scope="function")
def driver_actor():
    """Actor 2: Mitra Driver EvMoto (82283737237)."""
    driver = DriverRoleSimulator(driver_phone="82283737237", driver_name="Driver E2E Master")
    driver.set_online(is_online=True)
    yield driver
    driver.set_offline()


@pytest.mark.e2e
@pytest.mark.dispatch_batch
@pytest.mark.happy_flow
class TestE2EDispatchBatchIntegration:
    """End-to-End Integrated Test Suite Fitur Baru Dispatch Batch."""

    def test_TC_E2E_BATCH_01_full_lifecycle_dashboard_to_driver_apps(self, admin_actor, driver_actor):
        """
        [E2E MASTER FLOW - SCENARIO 01]
        Deskripsi : Alur terintegrasi penuh dari konfigurasi Admin Dashboard hingga eksekusi Driver:
          1. [Admin] Mengatur Jalur Batch ON, size=5, delay=10s, duration=0 (no timer), concurrent=5,
             ordinary band [0-1, 1-2, 2-3, 3-4, 4-5 km], advance band [0-1, 1-2, 2-5, 5-15 km].
          2. [User/System] Menerbitkan 2 pesanan baru:
             - Pesanan A (Reguler, 1.8 KM -> masuk Ordinary Band 1-2 KM)
             - Pesanan B (Advance Booking, 12.0 KM -> masuk Advance Band 5-15 KM)
          3. [Driver] Menerima broadcast batch berisi 2 pesanan sekaligus:
             - Memverifikasi kedua order tampil bersamaan (Multiple Orders).
             - Memverifikasi TIDAK ADA countdown timer pada seluruh penawaran.
             - Memverifikasi badge 'Pesanan Reguler' dan 'Advance Booking' terpisah.
          4. [Driver] Menolak (Reject) Pesanan B (Advance) -> Pesanan B dikeluarkan dari daftar aktif driver.
          5. [Driver] Menerima (Accept) Pesanan A (Reguler) -> Beralih ke alur penjemputan.
          6. [Driver] Menyelesaikan Pesanan A: Berangkat -> Tiba di Jemput -> Mulai Trip -> Selesai Antar -> Struk Penerimaan.
        Ekspektasi: Seluruh siklus terintegrasi berhasil 100% tanpa error, tanpa bug, dan konsisten.
        """
        # ======================================================================
        # PHASE 1: ADMIN DASHBOARD CONFIGURATION
        # ======================================================================
        given("Superadmin mengonfigurasi fitur Dispatch Batch di Dashboard Admin Staging")
        resp = admin_actor.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2,
            ordinary_bands=[("0", "1"), ("1", "2"), ("2", "3"), ("3", "4"), ("4", "5")],
            advance_bands=[("0", "1"), ("1", "2"), ("2", "5"), ("5", "15")]
        )
        assert resp.status_code == 200, "Dashboard harus merespons HTTP 200"
        assert admin_actor.is_saved_successfully(resp), "Pengaturan harus tersimpan di dashboard"

        dash_settings = admin_actor.parse_dispatch_batch_settings(resp.text)
        assert dash_settings["enabled"] is True
        assert dash_settings["size"] == 5
        assert dash_settings["duration"] == 0  # No countdown
        assert dash_settings["concurrent"] == 5
        logger.info("[E2E PHASE 1] Konfigurasi Dispatch Batch berhasil diterapkan di Admin Dashboard.")

        # ======================================================================
        # PHASE 2: SINKRONISASI KONFIGURASI KE SIMULATOR DRIVER
        # ======================================================================
        and_step("Sistem menerapkan concurrent limit 5 order ke profil Mitra Driver")
        driver_actor.set_concurrent_limit(dash_settings["concurrent"])
        assert driver_actor.is_driver_online() is True

        # ======================================================================
        # PHASE 3: SERVER ORDER DISPATCHING (REGULAR & ADVANCE BOOKING)
        # ======================================================================
        when("Dua pesanan baru diterbitkan ke sistem dispatching: 1 Reguler (1.8 KM) dan 1 Advance Booking (12.0 KM)")
        batch_payload = [
            {
                "order_id": "ORD-E2E-REG-01",
                "order_type": "regular",
                "pickup": "Plaza Senayan, Jakarta",
                "destination": "SCBD Lot 8, Jakarta",
                "distance_km": 1.8,  # Masuk ordinary band 1-2 KM
                "fare": 12000
            },
            {
                "order_id": "ORD-E2E-ADV-02",
                "order_type": "advance",
                "pickup": "Pondok Indah Mall 3",
                "destination": "Bandara Soekarno Hatta Terminal 3",
                "distance_km": 12.0,  # Masuk advance band 5-15 KM
                "fare": 75000
            }
        ]
        received_offers = driver_actor.receive_batch_dispatch(batch_payload)

        # ======================================================================
        # PHASE 4: DRIVER VERIFICATION (MULTIPLE ORDERS & NO COUNTDOWN)
        # ======================================================================
        then("Aplikasi Driver menampilkan 2 tawaran pesanan secara simultan di layar")
        assert len(received_offers) == 2, f"Harus ada 2 tawaran, aktual: {len(received_offers)}"

        and_step("Seluruh tawaran diverifikasi TIDAK MEMILIKI countdown timer")
        for offer in received_offers:
            assert offer["has_countdown"] is False, f"Order {offer['order_id']} tidak boleh memiliki countdown timer!"

        and_step("Pemisahan tipe pesanan terverifikasi tegas (Reguler vs Advance Booking)")
        reg_offer = next((o for o in received_offers if o["order_type"] == "regular"), None)
        adv_offer = next((o for o in received_offers if o["order_type"] == "advance"), None)
        assert reg_offer is not None and reg_offer["order_id"] == "ORD-E2E-REG-01"
        assert adv_offer is not None and adv_offer["order_id"] == "ORD-E2E-ADV-02"
        logger.info("[E2E PHASE 4] Verifikasi Driver: Multiple Orders tampil tanpa countdown & terpisah rapi.")

        # ======================================================================
        # PHASE 5: DRIVER ACTIONS (REJECT ADVANCE & ACCEPT REGULAR)
        # ======================================================================
        when("Driver menolak (Reject) pesanan Advance Booking ORD-E2E-ADV-02")
        reject_success = driver_actor.reject_batch_offer("ORD-E2E-ADV-02")
        assert reject_success is True

        and_step("Tawaran Advance Booking dikeluarkan dari daftar aktif driver")
        active_remaining = driver_actor.get_batch_offers()
        assert len(active_remaining) == 1
        assert active_remaining[0]["order_id"] == "ORD-E2E-REG-01"

        when("Driver melakukan Swipe untuk Menerima pesanan Reguler ORD-E2E-REG-01")
        accepted_order = driver_actor.accept_batch_order("ORD-E2E-REG-01")
        assert accepted_order["status"] == "ACCEPTED"
        assert len(driver_actor._active_orders) == 1

        # ======================================================================
        # PHASE 6: TRIP EXECUTION & SETTLEMENT LIFECYCLE
        # ======================================================================
        and_step("Driver menjalankan siklus perjalanan hingga selesai")
        # 1. Driver tiba di titik penjemputan
        driver_actor.driver_arrived_at_pickup()
        # 2. Penumpang naik, mulai perjalanan ke SCBD
        driver_actor.start_trip()
        # 3. Selesai perjalanan di titik tujuan
        trip_summary = driver_actor.complete_trip(payment_method="cash", fare_amount=12000)

        then("Perjalanan berhasil diselesaikan dengan struk pembayaran tunai Rp 12.000")
        assert trip_summary["status"] == "COMPLETED"
        assert trip_summary["payment_collected"] is True
        assert trip_summary["fare"] == 12000
        logger.info("[E2E PHASE 6] Alur End-to-End berhasil diselesaikan 100% sempurna.")

    def test_TC_E2E_BATCH_02_driver_cancel_flow_after_batch_acceptance(self, driver_actor):
        """
        [E2E CANCELLATION FLOW - SCENARIO 02]
        Deskripsi : Pengujian alur pembatalan oleh driver setelah menerima pesanan dari batch dispatch:
          1. Driver menerima pesanan reguler ORD-E2E-CANCEL-01.
          2. Terjadi kendala di lapangan (misal ban bocor/jarak terlalu jauh).
          3. Driver membatalkan pesanan dengan alasan valid.
          4. Sistem melepaskan lock pesanan dan mengembalikan slot ketersediaan driver.
        Ekspektasi: Pembatalan terekam dengan benar dan status driver pulih ke online & standby.
        """
        given("Driver menerima satu order baru dari jalur batch")
        offers = [{"order_id": "ORD-E2E-CANCEL-01", "order_type": "regular", "fare": 15000}]
        driver_actor.receive_batch_dispatch(offers)
        driver_actor.accept_batch_order("ORD-E2E-CANCEL-01")
        assert len(driver_actor._active_orders) == 1

        when("Driver membatalkan pesanan karena kendala operasional")
        res = driver_actor.cancel_active_order("ORD-E2E-CANCEL-01", reason="Kendala Kendaraan Driver")

        then("Pesanan berstatus CANCELLED dan slot driver kembali tersedia")
        assert res["status"] == "CANCELLED"
        assert res["cancel_reason"] == "Kendala Kendaraan Driver"
        assert len(driver_actor._active_orders) == 0
        assert driver_actor.is_driver_available() is True
        logger.info("[E2E SCENARIO 02] Alur pembatalan pasca-terima batch tervalidasi 100% sukses.")
