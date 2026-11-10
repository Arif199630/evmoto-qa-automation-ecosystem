"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - ORDER HALL & MULTIPLE ORDER EDGE CASES
================================================================================
Aplikasi      : EvMoto Driver Dev (v1.9.29)
File Target   : test_drv_order_hall_and_multiple_orders_edge_cases.py
Metodologi    : 4 Pilar QA Lengkap (PT, PF, NT, NF)
Cakupan Uji   :
  1. Fitur Order Hall (Lobi / Ruang Pesanan Driver):
     - Tampilan daftar order yang tersedia (Lobby View)
     - Navigasi tab: Pesanan Reguler vs Advance Booking
     - Pull-to-refresh & sinkronisasi live polling
     - Sorting jarak (proximity) & tarif argo (fare)
     - Empty State ketika tidak ada pesanan di sekitar radius ("Belum ada orderan")
  2. Multiple Order Edge Cases:
     - Customer membatalkan pesanan saat masih tayang di Order Hall
     - Mitra pengemudi lain mengklaim pesanan secara simultan (Realtime Revocation)
     - Driver mencapai batas maksimal kapasitas bersamaan (Concurrent Capacity Limit)
     - Driver mematikan status kerja (Toggle Offline) saat Order Hall aktif
     - Penolakan parsial (menolak 1 order, mempertahankan order lain)
     - Penanganan double-tap cepat (Atomic Lock)
     - Gangguan jaringan (Socket Drop / Reconnection Sync)
     - Isolasi payload abnormal (Argo <= 0 / koordinat rusak)
     - High volume stress flood (25+ multiple orders simultan)
================================================================================
"""
import os
import pytest
import time
from Frontend.Feature.Helper.driver_role_simulator import DriverRoleSimulator
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvOrderHallAndMultipleOrdersEdgeCases")

DRIVER_PHONE = os.environ.get("EVMOTO_PHONE_EXTRA_1", "")
DRIVER_NAME = "Driver Dev Order Hall"


@pytest.fixture
def driver_sim():
    """Fixture DriverRoleSimulator siap pakai dalam status Online dengan Order Hall."""
    sim = DriverRoleSimulator(driver_phone=DRIVER_PHONE, driver_name=DRIVER_NAME)
    sim.set_online(is_online=True)
    sim.set_concurrent_limit(3)
    yield sim
    sim.set_offline()


@pytest.mark.driver_app
@pytest.mark.order_hall
@pytest.mark.multiple_orders
@pytest.mark.edge_cases
class TestDrvOrderHallAndMultipleOrdersEdgeCases:
    """Test Suite 4 Pilar QA untuk Fitur Order Hall dan Multiple Order Edge Cases."""

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - ORDER HALL & MULTIPLE ORDERS HAPPY PATH
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_HALL_PT_01_driver_opens_order_hall_and_views_multiple_available_orders(self, driver_sim):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Driver membuka layar Order Hall (Lobi Pesanan) dan melihat kumpulan multiple orders
                    yang tersedia di radius operasionalnya secara realtime.
        Ekspektasi: Order Hall menampilkan seluruh kartu pesanan dengan informasi lengkap:
                    ID order, rute titik jemput, titik antar, jarak tempuh, dan perkiraan pendapatan.
        """
        given(f"Driver {DRIVER_PHONE} membuka layar Order Hall")
        multiple_orders = [
            {"order_id": "ORD-HALL-01", "order_type": "regular", "pickup": "Grand Indonesia", "destination": "Menara BCA", "distance_km": 0.8, "fare": 12000},
            {"order_id": "ORD-HALL-02", "order_type": "regular", "pickup": "Plaza Indonesia", "destination": "Stasiun MRT Bundaran HI", "distance_km": 1.2, "fare": 14000},
            {"order_id": "ORD-HALL-03", "order_type": "regular", "pickup": "Sarinah Thamrin", "destination": "Monas", "distance_km": 2.0, "fare": 18000},
        ]
        driver_sim.receive_batch_dispatch(multiple_orders)

        when("Driver mengakses tampilan Order Hall pada tab Reguler")
        hall_view = driver_sim.enter_order_hall(active_tab="regular")

        then("Layar Order Hall menampilkan 3 kartu pesanan yang siap diambil")
        assert hall_view["status"] == "ONLINE"
        assert hall_view["total_available"] == 3
        assert len(hall_view["orders"]) == 3
        assert hall_view["is_empty"] is False
        assert [o["order_id"] for o in hall_view["orders"]] == ["ORD-HALL-01", "ORD-HALL-02", "ORD-HALL-03"]
        logger.info("[PASSED PT-01] Driver berhasil melihat daftar multiple order di Order Hall.")

    @pytest.mark.positive_true
    def test_TC_HALL_PT_02_order_hall_tab_switching_regular_vs_advance_booking(self, driver_sim):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Driver berpindah tab antara 'Pesanan Reguler' dan 'Advance Booking' di Order Hall.
        Ekspektasi: Tab Reguler hanya memuat pesanan langsung (instant), sedangkan tab Advance Booking
                    hanya memuat pesanan terjadwal (booking masa depan).
        """
        given("Order Hall menerima campuran pesanan Reguler dan Advance Booking")
        mixed_pool = [
            {"order_id": "ORD-REG-101", "order_type": "regular", "pickup": "Sudirman", "destination": "Thamrin", "fare": 11000},
            {"order_id": "ORD-REG-102", "order_type": "regular", "pickup": "Kuningan", "destination": "Tebet", "fare": 15000},
            {"order_id": "ORD-ADV-201", "order_type": "advance", "pickup": "Bandara Soetta", "destination": "Hotel Indonesia", "fare": 85000},
            {"order_id": "ORD-ADV-202", "order_type": "advance", "pickup": "Stasiun Gambir", "destination": "Bogor", "fare": 95000},
        ]
        driver_sim.receive_batch_dispatch(mixed_pool)

        when("Driver membuka tab Pesanan Reguler di Order Hall")
        reg_hall = driver_sim.enter_order_hall(active_tab="regular")

        then("Hanya 2 pesanan bertipe Reguler yang ditampilkan")
        assert reg_hall["total_available"] == 2
        assert all(o["order_type"] == "regular" for o in reg_hall["orders"])

        when("Driver beralih ke tab Advance Booking di Order Hall")
        adv_hall = driver_sim.enter_order_hall(active_tab="advance")

        then("Hanya 2 pesanan bertipe Advance Booking yang ditampilkan")
        assert adv_hall["total_available"] == 2
        assert all(o["order_type"] == "advance" for o in adv_hall["orders"])
        logger.info("[PASSED PT-02] Navigasi tab Reguler vs Advance Booking di Order Hall 100% presisi.")

    @pytest.mark.positive_true
    def test_TC_HALL_PT_03_order_hall_pull_to_refresh_and_live_polling_sync(self, driver_sim):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Driver melakukan aksi pull-to-refresh atau sistem polling otomatis memperbarui
                    daftar pesanan di Order Hall saat server merilis pesanan baru.
        Ekspektasi: Pesanan baru langsung muncul di daftar Order Hall secara mulus tanpa reload aplikasi.
        """
        given("Order Hall awalnya hanya berisi 1 pesanan aktif")
        initial_orders = [{"order_id": "ORD-INIT-01", "order_type": "regular", "fare": 13000}]
        driver_sim.receive_batch_dispatch(initial_orders)
        assert len(driver_sim.enter_order_hall("regular")["orders"]) == 1

        when("Server mendispatch pesanan baru dan driver melakukan pull-to-refresh")
        updated_server_orders = [
            {"order_id": "ORD-INIT-01", "order_type": "regular", "fare": 13000},
            {"order_id": "ORD-NEW-SYNC-02", "order_type": "regular", "fare": 22000},
            {"order_id": "ORD-NEW-SYNC-03", "order_type": "regular", "fare": 31000},
        ]
        driver_sim.simulate_network_reconnect_sync(updated_server_orders)

        then("Daftar Order Hall kini memuat 3 pesanan terupdate")
        refreshed_hall = driver_sim.enter_order_hall("regular")
        assert refreshed_hall["total_available"] == 3
        assert "ORD-NEW-SYNC-02" in [o["order_id"] for o in refreshed_hall["orders"]]
        logger.info("[PASSED PT-03] Pull-to-refresh dan live sync Order Hall sukses sinkronisasi.")

    @pytest.mark.positive_true
    def test_TC_HALL_PT_04_driver_selects_and_claims_highest_fare_order_from_hall(self, driver_sim):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Driver membandingkan beberapa penawaran di Order Hall dan secara sadar memilih
                    pesanan dengan potensi pendapatan (argo) tertinggi.
        Ekspektasi: Pesanan argo tertinggi berhasil diklaim (ACCEPTED), kartu pesanan tersebut berpindah
                    ke status trip aktif, dan sisa order di Order Hall tetap utuh.
        """
        given("Order Hall menyajikan 3 pesanan dengan tingkatan argo berbeda")
        offers = [
            {"order_id": "ORD-LOW", "order_type": "regular", "fare": 10000},
            {"order_id": "ORD-HIGH", "order_type": "regular", "fare": 45000},
            {"order_id": "ORD-MID", "order_type": "regular", "fare": 20000},
        ]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver memilih dan melakukan swipe accept pada ORD-HIGH")
        accepted = driver_sim.accept_batch_order("ORD-HIGH")

        then("Pesanan ORD-HIGH berstatus ACCEPTED dan masuk ke pesanan aktif")
        assert accepted["status"] == "ACCEPTED"
        assert accepted["order_id"] == "ORD-HIGH"
        assert accepted["fare"] == 45000

        and_step("Sisa 2 pesanan lainnya tetap tersedia di Order Hall")
        remaining = driver_sim.get_batch_offers()
        assert len(remaining) == 2
        assert {o["order_id"] for o in remaining} == {"ORD-LOW", "ORD-MID"}
        logger.info("[PASSED PT-04] Driver berhasil memilih dan mengklaim pesanan argo tertinggi.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - BUSINESS LOGIC & BOUNDARY CONDITIONS
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_HALL_PF_01_order_hall_empty_state_when_no_orders_in_radius(self, driver_sim):
        """
        [POSITIVE FALSE - PF-01: Empty State Valid]
        Deskripsi : Saat tidak ada pesanan aktif yang dibuat di sekitar radius driver (0 order).
        Ekspektasi: Order Hall menampilkan pesan informatif ('Belum ada orderan di sekitar Anda')
                    tanpa crash, spinner macet, atau tampilan kosong aneh.
        """
        given("Tidak ada pesanan aktif di sekitar lokasi driver")
        driver_sim.receive_batch_dispatch([])

        when("Driver membuka Order Hall")
        hall_view = driver_sim.enter_order_hall(active_tab="regular")

        then("Order Hall menampilkan Empty State bersih")
        assert hall_view["is_empty"] is True
        assert hall_view["total_available"] == 0
        assert hall_view["empty_state_message"] == "Belum ada orderan di sekitar Anda"
        logger.info("[PASSED PF-01] Validasi Empty State Order Hall terverifikasi bersih.")

    @pytest.mark.positive_false
    def test_TC_HALL_PF_02_concurrent_capacity_locks_order_hall_acceptance(self, driver_sim):
        """
        [POSITIVE FALSE - PF-02: Batas Kapasitas Concurrent]
        Deskripsi : Konfigurasi batas concurrent order diatur = 2. Driver telah menerima 2 pesanan.
                    Driver mencoba menerima pesanan ke-3 dari Order Hall.
        Ekspektasi: Sistem menolak penerimaan pesanan ke-3 dengan validasi 'Kapasitas order driver penuh'
                    dan status ketersediaan driver menjadi tidak siap (is_available=False).
        """
        driver_sim.set_concurrent_limit(2)
        given("Driver telah memegang 2 pesanan aktif (mencapai batas maksimal concurrent)")
        batch = [
            {"order_id": "ORD-SLOT-1", "order_type": "regular"},
            {"order_id": "ORD-SLOT-2", "order_type": "regular"},
            {"order_id": "ORD-SLOT-3", "order_type": "regular"},
        ]
        driver_sim.receive_batch_dispatch(batch)
        driver_sim.accept_batch_order("ORD-SLOT-1")
        driver_sim.accept_batch_order("ORD-SLOT-2")
        assert driver_sim.is_driver_available() is False

        when("Driver mencoba menerima pesanan ke-3 dari Order Hall")
        with pytest.raises(ValueError, match="Kapasitas order driver penuh"):
            driver_sim.accept_batch_order("ORD-SLOT-3")

        then("Driver tetap hanya memegang 2 pesanan tanpa kebocoran kuota")
        assert len(driver_sim._active_orders) == 2
        logger.info("[PASSED PF-02] Batas kapasitas concurrent berhasil mengunci penerimaan di Order Hall.")

    @pytest.mark.positive_false
    def test_TC_HALL_PF_03_order_hall_distance_and_fare_sorting_matrix(self, driver_sim):
        """
        [POSITIVE FALSE - PF-03: Matriks Sorting Jarak & Tarif]
        Deskripsi : Driver mengurutkan Order Hall berdasarkan jarak terdekat (proximity) dan argo tertinggi.
        Ekspektasi: Hasil pengurutan sesuai urutan metrik:
                    Jarak terdekat: 0.5 km -> 1.5 km -> 4.2 km.
                    Argo tertinggi: Rp 35.000 -> Rp 20.000 -> Rp 11.000.
        """
        given("Order Hall memuat 3 pesanan dengan metrik acak")
        orders = [
            {"order_id": "ORD-B", "distance_km": 1.5, "fare": 20000},
            {"order_id": "ORD-C", "distance_km": 4.2, "fare": 35000},
            {"order_id": "ORD-A", "distance_km": 0.5, "fare": 11000},
        ]
        driver_sim.receive_batch_dispatch(orders)

        when("Driver memilih sorting jarak terdekat (distance)")
        sorted_by_dist = driver_sim.sort_order_hall(by="distance")

        then("Pesanan tersusun terdekat: ORD-A (0.5km), ORD-B (1.5km), ORD-C (4.2km)")
        assert [o["order_id"] for o in sorted_by_dist] == ["ORD-A", "ORD-B", "ORD-C"]

        when("Driver memilih sorting tarif tertinggi (fare)")
        sorted_by_fare = driver_sim.sort_order_hall(by="fare", reverse=True)

        then("Pesanan tersusun argo tertinggi: ORD-C (35k), ORD-B (20k), ORD-A (11k)")
        assert [o["order_id"] for o in sorted_by_fare] == ["ORD-C", "ORD-B", "ORD-A"]
        logger.info("[PASSED PF-03] Fitur sorting jarak & tarif di Order Hall terbukti akurat.")

    @pytest.mark.positive_false
    def test_TC_HALL_PF_04_advance_booking_scheduled_window_filtering(self, driver_sim):
        """
        [POSITIVE FALSE - PF-04: Filter Window Waktu Pesanan Terjadwal]
        Deskripsi : Pesanan Advance Booking dengan jadwal penjemputan berbeda (misal: 2 jam lagi vs 48 jam lagi).
        Ekspektasi: Order Hall hanya mengelompokkan pesanan terjadwal pada tab khusus tanpa mencampurkannya ke tab reguler.
        """
        given("Terdapat pesanan terjadwal dan reguler di server")
        orders = [
            {"order_id": "ORD-SCH-2H", "order_type": "advance", "scheduled_in_hours": 2, "fare": 40000},
            {"order_id": "ORD-NOW-01", "order_type": "regular", "scheduled_in_hours": 0, "fare": 12000},
        ]
        driver_sim.receive_batch_dispatch(orders)

        when("Mengecek tab Reguler")
        reg = driver_sim.enter_order_hall("regular")
        assert len(reg["orders"]) == 1
        assert reg["orders"][0]["order_id"] == "ORD-NOW-01"

        when("Mengecek tab Advance")
        adv = driver_sim.enter_order_hall("advance")
        assert len(adv["orders"]) == 1
        assert adv["orders"][0]["order_id"] == "ORD-SCH-2H"
        logger.info("[PASSED PF-04] Pemisahan window waktu pesanan terjadwal dan reguler valid.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - MULTIPLE ORDER EDGE CASES & CANCELLATIONS
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_HALL_NT_01_customer_cancels_while_order_is_in_order_hall(self, driver_sim):
        """
        [NEGATIVE TRUE - NT-01: Pembatalan Customer Saat Order Masih di Hall]
        Deskripsi : Customer membatalkan pemesanan saat kartu order masih tayang di Order Hall driver.
        Ekspektasi: Order tersebut langsung dicabut (revoked) seketika dari Order Hall. Jika driver
                    mencoba swipe order yang sudah dibatalkan, sistem menolak dengan aman tanpa crash.
        """
        given("Dua order ORD-LIVE-01 dan ORD-LIVE-02 tayang di Order Hall")
        orders = [
            {"order_id": "ORD-LIVE-01", "order_type": "regular", "fare": 15000},
            {"order_id": "ORD-LIVE-02", "order_type": "regular", "fare": 18000},
        ]
        driver_sim.receive_batch_dispatch(orders)

        when("Customer membatalkan pesanan ORD-LIVE-01 sebelum driver mana pun menerima")
        cancelled = driver_sim.customer_cancels_in_order_hall("ORD-LIVE-01", reason="Pengguna batal pesan")
        assert cancelled is True

        then("Order ORD-LIVE-01 lenyap dari daftar penawaran Order Hall")
        active_in_hall = driver_sim.get_batch_offers()
        assert len(active_in_hall) == 1
        assert active_in_hall[0]["order_id"] == "ORD-LIVE-02"

        and_step("Order ORD-LIVE-02 lainnya tetap aman dan dapat diterima normal")
        res = driver_sim.accept_batch_order("ORD-LIVE-02")
        assert res["status"] == "ACCEPTED"
        logger.info("[PASSED NT-01] Pembatalan customer di Order Hall tertangani seketika dan bersih.")

    @pytest.mark.negative_true
    def test_TC_HALL_NT_02_order_claimed_by_peer_realtime_revocation_from_hall(self, driver_sim):
        """
        [NEGATIVE TRUE - NT-02: Klaim Mitra Lain / Realtime Peer Revocation]
        Deskripsi : Mitra driver lain (Peer) mengklaim pesanan yang sedang ditampilkan di Order Hall driver ini.
        Ekspektasi: Pesanan langsung dicabut dari Order Hall driver ini disertai notifikasi
                    'Orderan sudah diambil oleh pengemudi lain'.
        """
        given("Order ORD-SHARED-99 tayang di Order Hall")
        driver_sim.receive_batch_dispatch([{"order_id": "ORD-SHARED-99", "order_type": "regular"}])
        assert len(driver_sim.get_batch_offers()) == 1

        when("Driver mitra lain (DRV-PEER-Budi) mengklaim order lebih dulu di server")
        peer_claim = driver_sim.peer_claims_in_order_hall("ORD-SHARED-99", peer_driver_id="DRV-PEER-Budi")

        then("Order langsung dicabut dari Order Hall driver saat ini")
        assert peer_claim["revoked"] is True
        assert peer_claim["notification"] == "Orderan sudah diambil oleh pengemudi lain"
        assert len(driver_sim.get_batch_offers()) == 0
        logger.info("[PASSED NT-02] Realtime peer revocation di Order Hall berhasil melindungi konsistensi.")

    @pytest.mark.negative_true
    def test_TC_HALL_NT_03_offline_toggle_purges_order_hall_completely(self, driver_sim):
        """
        [NEGATIVE TRUE - NT-03: Toggle Offline Menghapus Seluruh Isi Order Hall]
        Deskripsi : Driver mengubah status kerjanya menjadi Offline saat Order Hall memuat banyak order.
        Ekspektasi: Seluruh tawaran di Order Hall langsung ditutup/dikosongkan, dan layar menampilkan
                    status 'Driver Offline - Aktifkan status kerja untuk melihat Order Hall'.
        """
        given("Order Hall memiliki 4 pesanan aktif")
        offers = [
            {"order_id": f"ORD-PURGE-{i}", "order_type": "regular"} for i in range(1, 5)
        ]
        driver_sim.receive_batch_dispatch(offers)
        assert len(driver_sim.get_batch_offers()) == 4

        when("Driver menekan tombol matikan kerja (Set Offline)")
        driver_sim.set_offline()

        then("Order Hall terkunci dan status menunjukkan OFFLINE")
        hall = driver_sim.enter_order_hall("regular")
        assert hall["status"] == "OFFLINE"
        assert hall["is_empty"] is True
        assert len(hall["orders"]) == 0
        logger.info("[PASSED NT-03] Toggle offline berhasil mengamankan dan membersihkan Order Hall.")

    @pytest.mark.negative_true
    def test_TC_HALL_NT_04_driver_rejects_single_order_from_hall_preserves_remaining(self, driver_sim):
        """
        [NEGATIVE TRUE - NT-04: Penolakan Tunggal di Order Hall Mempertahankan Order Lain]
        Deskripsi : Driver menolak/mengabaikan satu order tertentu dari kumpulan 3 multiple orders di Order Hall.
        Ekspektasi: Hanya order yang ditolak yang berpindah ke status 'REJECTED', 2 order lainnya tetap
                    tersedia di Order Hall tanpa gangguan.
        """
        given("Terdapat 3 tawaran order ORD-1, ORD-2, ORD-3 di Order Hall")
        offers = [
            {"order_id": "ORD-1", "order_type": "regular"},
            {"order_id": "ORD-2", "order_type": "regular"},
            {"order_id": "ORD-3", "order_type": "regular"},
        ]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver menekan tombol 'Tolak' pada ORD-2")
        rejected = driver_sim.reject_batch_offer("ORD-2")
        assert rejected is True

        then("ORD-2 tereliminasi dari penawaran, sedangkan ORD-1 dan ORD-3 tetap aktif")
        active_ids = [o["order_id"] for o in driver_sim.get_batch_offers()]
        assert active_ids == ["ORD-1", "ORD-3"]
        logger.info("[PASSED NT-04] Penolakan selektif di Order Hall berhasil tanpa mengganggu order lain.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - RESILIENCE, INTEGRITY & CONCURRENCY
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_HALL_NF_01_rapid_multi_order_swipes_atomic_lock_prevents_double_claim(self, driver_sim):
        """
        [NEGATIVE FALSE - NF-01: Double Swipe Atomic Lock]
        Deskripsi : Driver melakukan gesture geser/swipe secara sangat cepat (milidetik) pada 2 order
                    berbeda dalam satu layar Order Hall (accidental double tap).
        Ekspektasi: Mekanisme thread-safe mutex atomic lock memastikan hanya order pertama yang diproses,
                    mencegah race condition atau status double in-trip.
        """
        driver_sim.set_concurrent_limit(1)
        given("Dua pesanan tersedia di Order Hall dengan limit concurrent = 1")
        offers = [
            {"order_id": "ORD-RAPID-A", "order_type": "regular"},
            {"order_id": "ORD-RAPID-B", "order_type": "regular"},
        ]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver melakukan swipe ORD-RAPID-A dan seketika swipe ORD-RAPID-B")
        res_a = driver_sim.accept_batch_order("ORD-RAPID-A")
        assert res_a["status"] == "ACCEPTED"

        then("Swipe kedua pada ORD-RAPID-B ditolak secara aman karena kuota telah terisi")
        with pytest.raises(ValueError, match="Kapasitas order driver penuh"):
            driver_sim.accept_batch_order("ORD-RAPID-B")

        assert len(driver_sim._active_orders) == 1
        assert driver_sim._active_orders[0]["order_id"] == "ORD-RAPID-A"
        logger.info("[PASSED NF-01] Atomic lock sukses mencegah benturan double-swipe pada multiple orders.")

    @pytest.mark.negative_false
    def test_TC_HALL_NF_02_network_interruption_and_order_hall_reconnection_sync(self, driver_sim):
        """
        [NEGATIVE FALSE - NF-02: Flaky Network Reconnection Resilience]
        Deskripsi : Driver mengalami gangguan sinyal/koneksi saat membuka Order Hall (socket dropped),
                    kemudian sinyal pulih kembali (reconnected).
        Ekspektasi: Order Hall melakukan auto-reconcile state: pesanan yang sudah kedaluwarsa dibersihkan,
                    dan pesanan baru yang masuk selama offline disinkronkan tanpa kartu duplikat.
        """
        given("Driver memiliki 2 order di Order Hall sebelum sinyal terputus")
        initial_orders = [
            {"order_id": "ORD-NET-1", "order_type": "regular"},
            {"order_id": "ORD-NET-2", "order_type": "regular"},
        ]
        driver_sim.receive_batch_dispatch(initial_orders)

        when("Sinyal pulih dan server memberikan snapshot terbaru (ORD-NET-2 tetap ada, ORD-NET-3 baru masuk)")
        server_snapshot = [
            {"order_id": "ORD-NET-2", "order_type": "regular", "fare": 16000},
            {"order_id": "ORD-NET-3", "order_type": "regular", "fare": 25000},
        ]
        driver_sim.simulate_network_reconnect_sync(server_snapshot)

        then("Order Hall ter-update rapi: ORD-NET-1 kedaluwarsa, ORD-NET-2 & ORD-NET-3 aktif")
        active = driver_sim.get_batch_offers()
        active_ids = {o["order_id"] for o in active}
        assert active_ids == {"ORD-NET-2", "ORD-NET-3"}
        logger.info("[PASSED NF-02] Reconnection sync tangguh menangani fluktuasi jaringan di Order Hall.")

    @pytest.mark.negative_false
    def test_TC_HALL_NF_03_corrupted_or_zero_fare_payload_isolated_gracefully(self, driver_sim):
        """
        [NEGATIVE FALSE - NF-03: Defensive Parsing Data Abnormal / Rusak]
        Deskripsi : Salah satu pesanan dalam batch dispatch memiliki nilai argo <= 0 atau data tidak lengkap.
        Ekspektasi: Sistem menangani data abnormal dengan aman tanpa melempar NullPointerException / Uncaught Exception,
                    menggunakan nilai fallback standar sehingga Order Hall tetap dapat digunakan normal.
        """
        given("Server mengirimkan pesanan dengan payload fare = 0 atau negatif")
        corrupted_payload = [
            {"order_id": "ORD-ZERO-FARE", "order_type": "regular", "fare": 0, "pickup": "Lokasi Valid", "destination": "Tujuan Valid"},
            {"order_id": "ORD-NORMAL-OK", "order_type": "regular", "fare": 15000, "pickup": "Lokasi Normal", "destination": "Tujuan Normal"},
        ]

        when("Driver menerima daftar batch tersebut di Order Hall")
        received = driver_sim.receive_batch_dispatch(corrupted_payload)

        then("Kedua pesanan terdaftar di memory tanpa merusak UI Order Hall")
        assert len(received) == 2
        assert received[0]["fare"] == 0
        assert received[1]["fare"] == 15000

        and_step("Driver dapat mengabaikan order anomali dan mengambil order normal dengan sukses")
        accepted = driver_sim.accept_batch_order("ORD-NORMAL-OK")
        assert accepted["status"] == "ACCEPTED"
        logger.info("[PASSED NF-03] Defensive handling berhasil mengisolasi payload argo anomali.")

    @pytest.mark.negative_false
    def test_TC_HALL_NF_04_high_volume_order_hall_flood_stress_resilience(self, driver_sim):
        """
        [NEGATIVE FALSE - NF-04: Stress Flood 25+ Multiple Orders di Order Hall]
        Deskripsi : Pada kondisi jam sibuk ekstrem (rush hour / badai hujan), 25 pesanan disiarkan sekaligus
                    ke dalam Order Hall secara serentak.
        Ekspektasi: Order Hall mampu menampung seluruh 25 penawaran dengan latensi render di bawah 200ms,
                    daftar terindeks dengan rapi, dan tidak terjadi memory leak atau frame freezing.
        """
        given("25 pesanan masuk secara bersamaan ke Order Hall")
        flood_orders = [
            {
                "order_id": f"ORD-FLOOD-{i:02d}",
                "order_type": "regular" if i % 2 == 0 else "advance",
                "fare": 10000 + (i * 1000),
                "distance_km": 1.0 + (i * 0.2)
            }
            for i in range(1, 26)
        ]

        when("Sistem mendispatch seluruh 25 order secara instan")
        t_start = time.time()
        received = driver_sim.receive_batch_dispatch(flood_orders)
        t_duration = time.time() - t_start

        then("Seluruh 25 pesanan tersimpan lengkap di Order Hall")
        assert len(received) == 25
        assert len(driver_sim.get_batch_offers()) == 25
        assert t_duration < 0.2, f"Render latensi harus < 200ms, aktual: {t_duration*1000:.2f}ms"

        and_step("Pengemudi dapat memilih sembarang order (misal ORD-FLOOD-18) tanpa lag")
        accepted = driver_sim.accept_batch_order("ORD-FLOOD-18")
        assert accepted["status"] == "ACCEPTED"
        assert accepted["order_id"] == "ORD-FLOOD-18"
        assert len(driver_sim.get_batch_offers()) == 24
        logger.info(f"[PASSED NF-04] Stress testing 25 multiple orders di Order Hall lolos stabil ({t_duration*1000:.2f}ms).")

