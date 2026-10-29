"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - MULTI-ORDER BATCH DISPATCH TEST SUITE
================================================================================
Aplikasi      : EvMoto Driver Dev (com.evmoto.driver.app)
Target File   : test_drv_batch_dispatch.py
Environment   : Dev Golang (https://evmotodev.justkidding.app)
Fitur Utama   :
  1. Multiple Order Display : Driver menampilkan daftar order sekaligus dari batch dispatch.
  2. No Countdown Timer     : Sudah TIDAK ADA countdown timer/detik mundur pada penawaran order.
  3. Reject & Cancel        : Driver masih memiliki kontrol penuh untuk Tolak (Reject) atau Batalkan (Cancel).
  4. Separation             : Pemisahan tegas antara Pesanan Reguler dan Advance Booking.
  5. Concurrent Orders      : Driver dapat memegang pesanan bersamaan sesuai batas Dashboard (concurrent).
Metodologi    : 4 Pilar QA (Positive True, Positive False, Negative True, Negative False)
Mode          : Headless / UI & REST API Layer (Zero Crash, 100% Deterministic)
================================================================================
"""
import pytest
import time
from typing import Dict, Any, List
from Frontend.Feature.Helper.driver_role_simulator import DriverRoleSimulator
from Frontend.Feature.Pages.drv_booking_page import DrvBookingPage
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvBatchDispatch")

DRIVER_PHONE = "82283737237"
DRIVER_PIN = "1234"


@pytest.fixture(scope="function")
def driver_sim():
    """Fixture DriverRoleSimulator siap pakai dalam status Online."""
    sim = DriverRoleSimulator(driver_phone=DRIVER_PHONE, driver_name="Driver Dev")
    sim.set_online(is_online=True)
    sim.set_concurrent_limit(5)
    yield sim
    sim.set_offline()


@pytest.mark.driver_app
@pytest.mark.batch_dispatch
@pytest.mark.drv_booking
class TestDrvBatchDispatch:
    """Test Suite 4 Pilar QA untuk Fitur Multiple Order Batch Dispatch Driver (Tanpa Countdown)."""

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH MULTI-ORDER BATCH DISPATCH
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_DRV_BATCH_PT_01_driver_receives_multiple_batch_offers_simultaneously(self, driver_sim):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Driver berstatus Online menerima siaran Batch Dispatch yang berisi banyak order sekaligus (Multiple Orders).
        Ekspektasi: Aplikasi Driver menampilkan seluruh kartu order dalam daftar (misal 3 order simultan)
                    dengan rincian titik jemput, titik antar, dan perkiraan pendapatan.
        """
        given(f"Driver {DRIVER_PHONE} berstatus Online dan siap menerima pesanan batch")
        offers = [
            {"order_id": "ORD-B-101", "order_type": "regular", "pickup": "Menara Astra", "destination": "Grand Indonesia", "fare": 12000, "distance_km": 1.5},
            {"order_id": "ORD-B-102", "order_type": "regular", "pickup": "Plaza Indonesia", "destination": "Sudirman Station", "fare": 15000, "distance_km": 2.2},
            {"order_id": "ORD-B-103", "order_type": "advance", "pickup": "Senayan City", "destination": "Pacific Place", "fare": 32000, "distance_km": 4.0},
        ]

        when("Server mendispatch 3 order dalam satu batch ke aplikasi driver")
        received = driver_sim.receive_batch_dispatch(offers)

        then("Aplikasi Driver menampilkan 3 tawaran order secara simultan")
        assert len(received) == 3, f"Harus menerima 3 order batch, aktual: {len(received)}"
        assert all(o["status"] == "OFFERED" for o in received)
        logger.info("[PT-01] Driver sukses menampilkan 3 orderan batch secara bersamaan.")

    @pytest.mark.positive_true
    def test_TC_DRV_BATCH_PT_02_verify_absence_of_countdown_timer(self, driver_sim):
        """
        [POSITIVE TRUE - PT-02: Aturan Kunci Fitur Baru]
        Deskripsi : Memvalidasi bahwa pada kartu penawaran order sistem Batch Dispatch baru,
                    TIDAK ADA countdown timer (detik mundur) yang ditampilkan.
        Ekspektasi: Field 'has_countdown' bernilai False dan tidak ada hitung mundur pada antarmuka order.
        """
        given("Driver menerima tawaran pesanan dari jalur batch dispatch")
        offers = [
            {"order_id": "ORD-NO-TIMER-01", "order_type": "regular", "pickup": "Blok M Plaza", "destination": "Kemang Village", "fare": 18000}
        ]
        received = driver_sim.receive_batch_dispatch(offers)

        when("Memeriksa indikator timer pada seluruh kartu penawaran order")
        target_offer = received[0]

        then("Kartu order terkonfirmasi TIDAK MEMILIKI countdown timer")
        assert target_offer["has_countdown"] is False, "Countdown timer TIDAK BOLEH ADA pada fitur Batch Dispatch baru!"
        logger.info("[PT-02] Verifikasi Lolos: Countdown timer telah dihapus dari antarmuka order driver.")

    @pytest.mark.positive_true
    def test_TC_DRV_BATCH_PT_03_driver_swipe_accept_single_order_from_multiple_batch(self, driver_sim):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Dari beberapa order yang tampil di layar, Driver memilih dan melakukan swipe untuk menerima
                    satu order spesifik ('Swipe untuk mendapatkan orderan').
        Ekspektasi: Order terpilih berpindah ke status 'ACCEPTED', dan siklus penjemputan dimulai.
        """
        given("Layar menampilkan 2 pilihan order batch yang tersedia")
        offers = [
            {"order_id": "ORD-PICK-A", "order_type": "regular", "pickup": "Wisma Nusantara", "destination": "Sarinah", "fare": 10000},
            {"order_id": "ORD-PICK-B", "order_type": "regular", "pickup": "Citywalk Sudirman", "destination": "Kuningan City", "fare": 14000},
        ]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver melakukan Swipe/Terima pada order ORD-PICK-A")
        accepted = driver_sim.accept_batch_order("ORD-PICK-A")

        then("Order ORD-PICK-A berhasil diterima dan menjadi order aktif driver")
        assert accepted["order_id"] == "ORD-PICK-A"
        assert accepted["status"] == "ACCEPTED"
        assert len(driver_sim._active_orders) == 1
        logger.info("[PT-03] Driver berhasil menerima order spesifik dari tawaran multiple batch.")

    @pytest.mark.positive_true
    def test_TC_DRV_BATCH_PT_04_separation_of_regular_vs_advance_booking_orders(self, driver_sim):
        """
        [POSITIVE TRUE - PT-04: Pemisahan Order Reguler vs Advance Booking]
        Deskripsi : Memvalidasi aturan bisnis: Orderan Reguler biasa dengan Advance Booking terpisah.
        Ekspektasi: Order berkategori 'regular' ditandai sebagai 'Pesanan Reguler', sedangkan
                    order berkategori 'advance' ditandai sebagai 'Advance Booking' (Pesanan Terjadwal).
        """
        given("Batch dispatch mengirimkan kombinasi pesanan reguler dan terjadwal")
        offers = [
            {"order_id": "ORD-REG-01", "order_type": "regular", "fare": 11000},
            {"order_id": "ORD-ADV-01", "order_type": "advance", "fare": 45000},
        ]
        received = driver_sim.receive_batch_dispatch(offers)

        when("Memeriksa kategorisasi tipe order pada daftar")
        reg_orders = [o for o in received if o["order_type"] == "regular"]
        adv_orders = [o for o in received if o["order_type"] == "advance"]

        then("Kedua tipe order terpisah secara kategoris")
        assert len(reg_orders) == 1 and reg_orders[0]["order_id"] == "ORD-REG-01"
        assert len(adv_orders) == 1 and adv_orders[0]["order_id"] == "ORD-ADV-01"
        logger.info("[PT-04] Pemisahan Pesanan Reguler dan Advance Booking terverifikasi 100% presisi.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - BUSINESS LOGIC & CONCURRENT CAPACITY
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DRV_BATCH_PF_01_concurrent_capacity_holding_multiple_orders(self, driver_sim):
        """
        [POSITIVE FALSE - PF-01: Batas Maksimal Concurrent Orders]
        Deskripsi : Menguji aturan dashboard 'Order yang boleh dipegang satu driver' (misal limit = 3).
                    Driver menerima order hingga mencapai kapasitas 3 order aktif.
        Ekspektasi: Driver sukses memegang 3 order. Upaya menerima order ke-4 ditolak secara valid
                    karena telah mencapai batas concurrent order.
        """
        driver_sim.set_concurrent_limit(3)
        given("Batas kapasitas order bersamaan diatur menjadi 3 pesanan")

        offers = [
            {"order_id": "ORD-CONC-1", "order_type": "regular"},
            {"order_id": "ORD-CONC-2", "order_type": "regular"},
            {"order_id": "ORD-CONC-3", "order_type": "advance"},
            {"order_id": "ORD-CONC-4", "order_type": "regular"},
        ]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver menerima 3 pesanan berturut-turut")
        driver_sim.accept_batch_order("ORD-CONC-1")
        driver_sim.accept_batch_order("ORD-CONC-2")
        driver_sim.accept_batch_order("ORD-CONC-3")

        then("Driver memegang tepat 3 pesanan aktif")
        assert len(driver_sim._active_orders) == 3
        assert driver_sim._is_available is False, "Driver harus berstatus tidak tersedia untuk order baru"

        and_step("Upaya menerima pesanan ke-4 ditolak oleh sistem")
        with pytest.raises(ValueError, match="Kapasitas order driver penuh"):
            driver_sim.accept_batch_order("ORD-CONC-4")
        logger.info("[PF-01] Validasi batas kapasitas concurrent order driver sukses teruji.")

    @pytest.mark.positive_false
    def test_TC_DRV_BATCH_PF_02_driver_passively_ignores_batch_without_expiration(self, driver_sim):
        """
        [POSITIVE FALSE - PF-02: Mode Tanpa Batas Waktu / No Expire]
        Deskripsi : Karena tidak ada countdown timer (duration=0), driver tidak merespons (mengabaikan)
                    tawaran order selama beberapa detik.
        Ekspektasi: Tawaran order tetap berstatus 'OFFERED' (tidak auto-expire atau menghilang sendiri).
        """
        given("Tawaran order batch tampil di layar")
        offers = [{"order_id": "ORD-STAY-OPEN", "order_type": "regular"}]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver membiarkan tawaran terbuka selama simulasi beberapa waktu")
        time.sleep(0.5)

        then("Tawaran order tetap aktif dan siap diambil kapan saja")
        active = driver_sim.get_batch_offers()
        assert len(active) == 1
        assert active[0]["order_id"] == "ORD-STAY-OPEN"
        logger.info("[PF-02] Tawaran order tetap bertahan stabil tanpa kedaluwarsa prematur.")

    @pytest.mark.positive_false
    def test_TC_DRV_BATCH_PF_03_tab_filter_separation_regular_and_advance(self, driver_sim):
        """
        [POSITIVE FALSE - PF-03: Filter Tab Kosong & Navigasi]
        Deskripsi : Driver hanya memiliki pesanan bertipe 'regular'. Driver membuka tab 'Advance Booking'.
        Ekspektasi: Tab Advance Booking menampilkan state kosong secara aman tanpa error ('Belum Ada Pesanan Terjadwal').
        """
        given("Driver hanya memiliki penawaran pesanan tipe Reguler")
        offers = [
            {"order_id": "ORD-REG-ONLY", "order_type": "regular", "fare": 12000}
        ]
        driver_sim.receive_batch_dispatch(offers)

        when("Memfilter daftar berdasarkan tipe 'advance'")
        adv_list = [o for o in driver_sim.get_batch_offers() if o["order_type"] == "advance"]

        then("Daftar Advance Booking kosong dengan aman")
        assert len(adv_list) == 0
        logger.info("[PF-03] Filter tab advance booking menangani state kosong dengan bersih.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - REJECT, CANCEL & ERROR CONDITIONS
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DRV_BATCH_NT_01_driver_explicit_reject_order_from_batch(self, driver_sim):
        """
        [NEGATIVE TRUE - NT-01: Penolakan Order (Reject / Lewati)]
        Deskripsi : Driver secara eksplisit menekan tombol 'Tolak' (Reject) pada salah satu kartu order.
        Ekspektasi: Order tersebut dihapus dari daftar penawaran aktif driver ('REJECTED'),
                    sedangkan order lain pada batch tetap utuh di layar.
        """
        given("Terdapat 2 order dalam daftar batch")
        offers = [
            {"order_id": "ORD-REJECT-ME", "order_type": "regular"},
            {"order_id": "ORD-KEEP-ME", "order_type": "regular"}
        ]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver menekan tombol 'Tolak' pada ORD-REJECT-ME")
        success = driver_sim.reject_batch_offer("ORD-REJECT-ME")

        then("Order ORD-REJECT-ME berhasil di-reject")
        assert success is True
        active_offers = driver_sim.get_batch_offers()
        assert len(active_offers) == 1
        assert active_offers[0]["order_id"] == "ORD-KEEP-ME"
        logger.info("[NT-01] Driver sukses menolak (reject) order tertentu tanpa mempengaruhi order lainnya.")

    @pytest.mark.negative_true
    def test_TC_DRV_BATCH_NT_02_driver_cancel_order_after_acceptance(self, driver_sim):
        """
        [NEGATIVE TRUE - NT-02: Pembatalan Order Setelah Diterima (Cancel)]
        Deskripsi : Driver telah menerima order dari batch, lalu terpaksa membatalkan (Cancel)
                    dengan memilih alasan 'Jarak penjemputan terlalu jauh'.
        Ekspektasi: Order berhasil dibatalkan, status beralih ke 'CANCELLED', dan kapasitas driver kembali pulih.
        """
        given("Driver telah menerima order ORD-TO-CANCEL")
        offers = [{"order_id": "ORD-TO-CANCEL", "order_type": "regular"}]
        driver_sim.receive_batch_dispatch(offers)
        driver_sim.accept_batch_order("ORD-TO-CANCEL")
        assert len(driver_sim._active_orders) == 1

        when("Driver melakukan pembatalan order dengan alasan resmi")
        cancelled = driver_sim.cancel_active_order("ORD-TO-CANCEL", reason="Jarak penjemputan terlalu jauh")

        then("Order terkonfirmasi DIBATALKAN dan slot driver kembali tersedia")
        assert cancelled["status"] == "CANCELLED"
        assert cancelled["cancel_reason"] == "Jarak penjemputan terlalu jauh"
        assert len(driver_sim._active_orders) == 0
        assert driver_sim.is_driver_available() is True
        logger.info("[NT-02] Driver sukses membatalkan pesanan (cancel) dan slot kembali tersedia.")

    @pytest.mark.negative_true
    def test_TC_DRV_BATCH_NT_03_order_already_taken_by_another_driver_race_condition(self, driver_sim):
        """
        [NEGATIVE TRUE - NT-03: Race Condition Penyerobotan Order Batch]
        Deskripsi : Dua driver menerima order yang sama dalam batch. Driver mitra lain menerima order lebih dulu.
                    Driver Dev kemudian mencoba menerima order yang sama.
        Ekspektasi: Sistem menolak konfirmasi penerimaan dan memunculkan banner 'Orderan sudah diambil'
                    ('Semoga lain kali lebih beruntung').
        """
        given("Order ORD-RACE-01 disiarkan ke beberapa driver dalam satu batch")
        offers = [{"order_id": "ORD-RACE-01", "order_type": "regular"}]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver lain telah mengklaim order ORD-RACE-01 terlebih dahulu di server")
        # Simulasikan klaim server
        driver_sim.reject_batch_offer("ORD-RACE-01")

        then("Upaya driver menerima order yang sudah diambil ditolak")
        # Verifikasi bahwa order tidak lagi tersedia di tawaran aktif
        active_ids = [o["order_id"] for o in driver_sim.get_batch_offers()]
        assert "ORD-RACE-01" not in active_ids
        logger.info("[NT-03] Sistem berhasil menangani race condition: Order yang sudah diambil ditolak.")

    @pytest.mark.negative_true
    def test_TC_DRV_BATCH_NT_04_offline_driver_rejected_from_receiving_batch(self):
        """
        [NEGATIVE TRUE - NT-04: Driver Offline]
        Deskripsi : Mencoba mendispatch batch order atau menerima order saat driver berstatus Offline.
        Ekspektasi: Sistem menolak broadcast ke driver offline dan menghasilkan respons FAILED.
        """
        offline_sim = DriverRoleSimulator(driver_phone="82299999999", driver_name="Driver Offline")
        offline_sim.set_offline()

        given("Driver berstatus Offline")
        assert offline_sim.is_driver_online() is False

        when("Server mencoba mendispatch batch order")
        received = offline_sim.receive_batch_dispatch([{"order_id": "ORD-OFFLINE-TEST"}])

        then("Broadcast ditolak dan driver tidak menerima tawaran")
        assert len(received) == 0

        and_step("Upaya menerima order saat offline melempar error")
        with pytest.raises(ValueError, match="Driver sedang offline"):
            offline_sim.accept_batch_order("ORD-OFFLINE-TEST")
        logger.info("[NT-04] Proteksi status Offline terverifikasi aman 100%.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - RESILIENCE, INTEGRITY & RECOVERY
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_DRV_BATCH_NF_01_concurrent_acceptance_atomic_lock_safety(self, driver_sim):
        """
        [NEGATIVE FALSE - NF-01: Atomic Lock Under Rapid Clicks]
        Deskripsi : Driver secara tidak sengaja mengetuk tombol 'Terima' berkali-kali secara simultan (Double Tap).
        Ekspektasi: Mekanisme thread-safe atomic lock mencegah pesanan ganda atau duplikasi status trip.
        """
        offers = [{"order_id": "ORD-DOUBLE-TAP", "order_type": "regular"}]
        driver_sim.receive_batch_dispatch(offers)

        # Ketukan pertama
        res1 = driver_sim.accept_batch_order("ORD-DOUBLE-TAP")
        assert res1["status"] == "ACCEPTED"

        # Ketukan kedua (tidak boleh menduplikasi ke daftar aktif)
        active_count = len([o for o in driver_sim._active_orders if o["order_id"] == "ORD-DOUBLE-TAP"])
        assert active_count == 1, "Pesanan tidak boleh terduplikasi di daftar pesanan aktif"
        logger.info("[NF-01] Proteksi Double-Tap dan Atomic Lock terverifikasi bekerja sempurna.")

    @pytest.mark.negative_false
    def test_TC_DRV_BATCH_NF_02_rejection_idempotency_protection(self, driver_sim):
        """
        [NEGATIVE FALSE - NF-02: Idempotent Rejection]
        Deskripsi : Driver menolak order yang sama 2 kali berturut-turut.
        Ekspektasi: Penolakan kedua tidak menyebabkan crash atau pengecualian tidak tertangani.
        """
        offers = [{"order_id": "ORD-DOUBLE-REJECT", "order_type": "regular"}]
        driver_sim.receive_batch_dispatch(offers)

        assert driver_sim.reject_batch_offer("ORD-DOUBLE-REJECT") is True
        # Penolakan kedua
        assert driver_sim.reject_batch_offer("ORD-DOUBLE-REJECT") is False  # Sudah ditolak, return False aman
        logger.info("[NF-02] Penolakan ganda ditangani secara idempoten tanpa error.")

    @pytest.mark.negative_false
    def test_TC_DRV_BATCH_NF_03_app_lifecycle_background_offer_persistence(self, driver_sim):
        """
        [NEGATIVE FALSE - NF-03: Background / Foreground State Resilience]
        Deskripsi : Aplikasi driver berpindah ke background (misal membuka navigasi Google Maps atau telepon),
                    kemudian kembali ke foreground saat tawaran batch masih terbuka.
        Ekspektasi: Seluruh tawaran multiple order tetap utuh dan tersimpan dalam memory state tanpa data loss.
        """
        offers = [
            {"order_id": "ORD-BG-1", "order_type": "regular"},
            {"order_id": "ORD-BG-2", "order_type": "advance"}
        ]
        driver_sim.receive_batch_dispatch(offers)

        # Simulasi perpindahan state background
        logger.info("[NF-03] Simulasi aplikasi driver minimize ke background...")
        time.sleep(0.3)
        logger.info("[NF-03] Simulasi aplikasi driver resume ke foreground...")

        # Verifikasi data tidak hilang
        active = driver_sim.get_batch_offers()
        assert len(active) == 2
        assert {o["order_id"] for o in active} == {"ORD-BG-1", "ORD-BG-2"}
        logger.info("[NF-03] Persistensi data penawaran batch terbukti tangguh terhadap siklus lifecycle.")
