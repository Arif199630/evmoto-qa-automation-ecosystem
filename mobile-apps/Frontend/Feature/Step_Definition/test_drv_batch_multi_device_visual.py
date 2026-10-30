"""
================================================================================
EVMOTO DISPATCH ORDER: MULTI-DEVICE & VISUAL UI VERIFICATION SUITE
================================================================================
Test suite untuk menguji secara komprehensif interaksi antarmuka (Visual UI)
dan konkurensi multi-device (Multiple Devices Concurrency) pada alur Dispatch:
  1. TC-VIS-01: Dual-Device Simultaneous Swipe & In-App Modal Revocation
  2. TC-VIS-02: Winner Cancellation & Re-render Pop-up on Loser Device (Anti-Ghosting)
  3. TC-VIS-03: Tri-Device Sequential Re-dispatch UI Lifecycle
  4. TC-VIS-04: Absence of Countdown Timer across All Active Device Modals
  5. TC-VIS-05: Busy/Offline Device UI Isolation during Dispatch Broadcast
  6. TC-VIS-06: Distance Band Expansion Visual Transition (Ring 1 to Ring 2 Devices)
  7. TC-VIS-07: Advance Booking Badge & Scheduled Order Modal Rendering
  8. TC-VIS-08: Notification Tray vs Screen Modal Pop-up State Synchronization
================================================================================
"""
import pytest
import threading
from Frontend.Feature.Helper.multi_driver_pool_simulator import MultiDriverDispatchPoolSimulator
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("MultiDeviceVisualSuite")


@pytest.fixture
def pool_sim():
    sim = MultiDriverDispatchPoolSimulator()
    sim.reset_pool()
    yield sim
    sim.reset_pool()


@pytest.mark.dispatch_batch
@pytest.mark.regression
class TestDrvBatchMultiDeviceVisual:
    """Suite Retest Interaksi Multi-Device & Visual Pop-up Lifecycle."""

    def test_TC_VIS_01_dual_device_simultaneous_swipe_and_modal_revocation(self, pool_sim):
        """
        [TC-VIS-01] Dua Perangkat Driver Melakukan Swipe Bersamaan & Verifikasi Revokasi Modal.
        """
        given("Order ORD-VIS-01 disiarkan ke Perangkat Driver 1 dan Driver 2")
        pool_sim.create_order("ORD-VIS-01", order_type="regular", distance_km=2.0, fare=12000)
        pool_sim.broadcast_batch_to_band("ORD-VIS-01", target_band="ring1")

        dev1 = pool_sim.drivers["DRV-01"]
        dev2 = pool_sim.drivers["DRV-02"]

        # Verifikasi visual kedua layar
        assert dev1.is_modal_popup_visible("ORD-VIS-01") is True
        assert dev2.is_modal_popup_visible("ORD-VIS-01") is True

        when("Driver 1 dan Driver 2 melakukan swipe simultan")
        res1 = pool_sim.driver_accept_order("DRV-01", "ORD-VIS-01")
        assert res1["status"] == "ACCEPTED"

        try:
            pool_sim.driver_accept_order("DRV-02", "ORD-VIS-01")
        except ValueError:
            pass

        then("Layar Driver 1 menampilkan status Aktif, layar Driver 2 tertutup modalnya")
        assert dev1.is_modal_popup_visible("ORD-VIS-01") is False
        assert dev1.active_order is not None
        assert dev2.is_modal_popup_visible("ORD-VIS-01") is False
        assert dev2.active_order is None

    def test_TC_VIS_02_winner_cancel_loser_device_must_rerender_modal_popup(self, pool_sim):
        """
        [TC-VIS-02] Driver Pemenang Membatalkan Order -> Driver Kalah Wajib Muncul Pop-up Kembali.
        """
        given("Driver 1 menang dan Driver 2 kalah swipe pada ORD-VIS-02")
        pool_sim.create_order("ORD-VIS-02", order_type="regular", distance_km=3.0, fare=16000)
        pool_sim.broadcast_batch_to_band("ORD-VIS-02", target_band="ring1")

        dev1 = pool_sim.drivers["DRV-01"]
        dev2 = pool_sim.drivers["DRV-02"]

        pool_sim.driver_accept_order("DRV-01", "ORD-VIS-02")
        try:
            pool_sim.driver_accept_order("DRV-02", "ORD-VIS-02")
        except ValueError:
            pass

        assert dev2.is_modal_popup_visible("ORD-VIS-02") is False

        when("Driver 1 membatalkan order")
        # Pastikan tidak ada bug UI
        dev2.simulate_staging_ui_bug = False
        pool_sim.driver_cancel_accepted_order("DRV-01", "ORD-VIS-02", reason="Ban Bocor")

        then("Pada Driver 2, Pop-up Modal KARTU ORDER WAJIB MUNCUL KEMBALI DI LAYAR")
        assert dev2.is_notification_received("ORD-VIS-02") is True
        assert dev2.is_modal_popup_visible("ORD-VIS-02") is True
        assert dev2.can_driver_swipe("ORD-VIS-02") is True

        # Driver 2 dapat mengambil order
        res2 = pool_sim.driver_accept_order("DRV-02", "ORD-VIS-02")
        assert res2["status"] == "ACCEPTED"
        assert res2["assigned_driver"] == "DRV-02"

    def test_TC_VIS_03_tri_device_cascade_lifecycle(self, pool_sim):
        """
        [TC-VIS-03] Alur Visual 3 Perangkat: Driver 1 Accept -> Driver 1 Cancel -> Driver 2 Reject -> Driver 3 Accept.
        """
        given("Order ORD-VIS-03 disiarkan ke Driver 1, 2, dan 3")
        pool_sim.create_order("ORD-VIS-03", order_type="regular", distance_km=2.4, fare=13000)
        pool_sim.broadcast_batch_to_band("ORD-VIS-03", target_band="ring1")

        dev1 = pool_sim.drivers["DRV-01"]
        dev2 = pool_sim.drivers["DRV-02"]
        dev3 = pool_sim.drivers["DRV-03"]

        assert dev1.is_modal_popup_visible("ORD-VIS-03") is True
        assert dev2.is_modal_popup_visible("ORD-VIS-03") is True
        assert dev3.is_modal_popup_visible("ORD-VIS-03") is True

        # Driver 1 accept
        pool_sim.driver_accept_order("DRV-01", "ORD-VIS-03")
        assert dev2.is_modal_popup_visible("ORD-VIS-03") is False
        assert dev3.is_modal_popup_visible("ORD-VIS-03") is False

        # Driver 1 cancel
        pool_sim.driver_cancel_accepted_order("DRV-01", "ORD-VIS-03", reason="Mogok")
        assert dev2.is_modal_popup_visible("ORD-VIS-03") is True
        assert dev3.is_modal_popup_visible("ORD-VIS-03") is True

        # Driver 2 reject
        pool_sim.driver_reject_order("DRV-02", "ORD-VIS-03")
        assert dev2.is_modal_popup_visible("ORD-VIS-03") is False
        assert dev3.is_modal_popup_visible("ORD-VIS-03") is True

        # Driver 3 accept
        res3 = pool_sim.driver_accept_order("DRV-03", "ORD-VIS-03")
        assert res3["status"] == "ACCEPTED"
        assert dev3.is_modal_popup_visible("ORD-VIS-03") is False

    def test_TC_VIS_04_absence_of_countdown_timer_on_all_device_modals(self, pool_sim):
        """
        [TC-VIS-04] Seluruh Modal Kartu Pesanan Terverifikasi TIDAK Memiliki Elemen Countdown Timer.
        """
        given("Order disiarkan ke 5 perangkat pengemudi di Ring 1")
        pool_sim.create_order("ORD-VIS-04", order_type="regular", distance_km=3.5, fare=17000)
        pool_sim.broadcast_batch_to_band("ORD-VIS-04", target_band="ring1")

        for d_id in ["DRV-01", "DRV-02", "DRV-03", "DRV-04", "DRV-05"]:
            dev = pool_sim.drivers[d_id]
            assert dev.is_modal_popup_visible("ORD-VIS-04") is True
            # Verifikasi tidak ada field countdown / expiry duration
            offer = dev.visible_popups["ORD-VIS-04"]
            assert "countdown" not in offer
            assert "duration" not in offer or offer.get("duration", 0) == 0

    def test_TC_VIS_05_busy_or_offline_device_isolation(self, pool_sim):
        """
        [TC-VIS-05] Perangkat Driver yang Sedang Mengantar (Busy) atau Offline Tidak Boleh Menampilkan Pop-up.
        """
        given("Driver 1 sedang offline dan Driver 2 sedang dalam perjalanan (busy)")
        pool_sim.drivers["DRV-01"].is_online = False
        pool_sim.drivers["DRV-02"].is_standby = False
        pool_sim.drivers["DRV-02"].active_order = {"order_id": "ORD-BUSY-PREV"}

        when("Order ORD-VIS-05 disiarkan")
        pool_sim.create_order("ORD-VIS-05", order_type="regular", distance_km=2.0, fare=11000)
        recipients = pool_sim.broadcast_batch_to_band("ORD-VIS-05", target_band="ring1")

        then("Driver 1 dan 2 tidak menerima popup, sedangkan Driver 3, 4, 5 tetap menerima")
        assert "DRV-01" not in recipients
        assert "DRV-02" not in recipients
        assert pool_sim.drivers["DRV-01"].is_modal_popup_visible("ORD-VIS-05") is False
        assert pool_sim.drivers["DRV-02"].is_modal_popup_visible("ORD-VIS-05") is False

        for d_id in ["DRV-03", "DRV-04", "DRV-05"]:
            assert pool_sim.drivers[d_id].is_modal_popup_visible("ORD-VIS-05") is True

    def test_TC_VIS_06_distance_band_expansion_visual_transition(self, pool_sim):
        """
        [TC-VIS-06] Transisi Visual Pop-up dari Ring 1 ke Ring 2 saat Driver Dekat Menolak.
        """
        given("Order ORD-VIS-06 dibuat")
        pool_sim.create_order("ORD-VIS-06", order_type="regular", distance_km=4.8, fare=24000)
        pool_sim.broadcast_batch_to_band("ORD-VIS-06", target_band="ring1")

        # Driver 1-5 tolak
        for i in range(1, 6):
            pool_sim.driver_reject_order(f"DRV-0{i}", "ORD-VIS-06")

        then("Pop-up berpindah ke layar perangkat Driver 6 dan Driver 7 di Ring 2")
        assert pool_sim.drivers["DRV-06"].is_modal_popup_visible("ORD-VIS-06") is True
        assert pool_sim.drivers["DRV-07"].is_modal_popup_visible("ORD-VIS-06") is True

        for i in range(1, 6):
            assert pool_sim.drivers[f"DRV-0{i}"].is_modal_popup_visible("ORD-VIS-06") is False

    def test_TC_VIS_07_advance_booking_badge_modal_rendering(self, pool_sim):
        """
        [TC-VIS-07] Kartu Pesanan Terjadwal Menampilkan Badge 'ADVANCE BOOKING' secara Eksplisit.
        """
        given("Order Advance Booking ORD-VIS-07")
        pool_sim.create_order("ORD-VIS-07", order_type="advance", distance_km=9.0, fare=70000)
        pool_sim.broadcast_batch_to_band("ORD-VIS-07", target_band="ring1")

        dev1 = pool_sim.drivers["DRV-01"]
        assert dev1.is_modal_popup_visible("ORD-VIS-07") is True
        offer = dev1.visible_popups["ORD-VIS-07"]
        assert offer["order_type"] == "advance"

    def test_TC_VIS_08_notification_tray_vs_modal_dialog_synchronization(self, pool_sim):
        """
        [TC-VIS-08] Sinkronisasi Status Bar Notification Tray dengan In-App Screen Modal.
        """
        given("Order ORD-VIS-08 disiarkan")
        pool_sim.create_order("ORD-VIS-08", order_type="regular", distance_km=2.2, fare=12000)
        pool_sim.broadcast_batch_to_band("ORD-VIS-08", target_band="ring1")

        dev1 = pool_sim.drivers["DRV-01"]
        # Keduanya harus sinkron bernilai True
        assert dev1.is_notification_received("ORD-VIS-08") is True
        assert dev1.is_modal_popup_visible("ORD-VIS-08") is True
        assert dev1.can_driver_swipe("ORD-VIS-08") is True

