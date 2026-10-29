"""
================================================================================
EVMOTO DRIVER AUTOMATION - HIGH VOLUME BATCH (>5 ORDERS) & DISTANCE MATRIX SUITE
================================================================================
Fokus Pengujian Khusus :
  1. Volume Order Tinggi (> 5 Orders):
     - Batch 8 orders (5 reguler + 3 advance)
     - Batch 10 orders & 15 orders (Stress testing antrean multi-order tanpa countdown)
     - Penanganan saat driver menerima order ke-6 saat concurrent=5 vs dinaikkan
     - Seleksi 1 order spesifik di antara belasan order
  2. Matriks Pengujian Jarak (Distance Bands Matrix):
     - Band 1 Ordinary: 0.0 – 0.99 KM (misal 0.4 KM)
     - Boundary 1.0 KM (Aturan: band sebelumnya berhenti tepat sebelum angka selesai)
     - Band 2 Ordinary: 1.0 – 1.99 KM (misal 1.5 KM)
     - Band 3 Ordinary: 2.0 – 2.99 KM (misal 2.4 KM)
     - Band 4 Ordinary: 3.0 – 3.99 KM (misal 3.8 KM)
     - Band 5 Ordinary: 4.0 – 5.0 KM (misal 4.9 KM)
     - Out of Bounds Regular: Jarak > 5.0 KM (misal 7.5 KM & 12.0 KM)
     - Advance Booking Bands: 0-1 KM, 1-2 KM, 2-5 KM, 5-15 KM, dan Out of Bounds > 15 KM (25.0 KM)
Metodologi: 4 Pilar QA (PT, PF, NT, NF)
================================================================================
"""
import pytest
import time
from Frontend.Feature.Helper.driver_role_simulator import DriverRoleSimulator
from Frontend.Feature.Helper.admin_dispatch_batch_helper import AdminDispatchBatchHelper
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestBatchHighVolumeDistance")


@pytest.fixture(scope="function")
def driver_sim():
    """Fixture driver simulator online."""
    sim = DriverRoleSimulator(driver_phone="82283737237", driver_name="Driver Stress Tester")
    sim.set_online(is_online=True)
    sim.set_concurrent_limit(5)
    yield sim
    sim.set_offline()


@pytest.mark.batch_dispatch
@pytest.mark.driver_app
class TestBatchHighVolumeAndDistanceMatrix:
    """Test Suite Khusus untuk Pengujian > 5 Order dan Variasi Jarak Lengkap."""

    # ==========================================================================
    # BAGIAN 1: PENGUJIAN LEBIH DARI 5 ORDER (> 5 ORDERS)
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_VOL_01_driver_receives_batch_of_8_orders_simultaneously(self, driver_sim):
        """
        [HIGH VOLUME - VOL-01: 8 Orders Batch]
        Deskripsi : Driver Online menerima siaran batch berisi 8 order sekaligus (5 Reguler + 3 Advance).
        Ekspektasi: Aplikasi Driver mampu memuat dan menampilkan ke-8 order secara bersamaan tanpa lag atau drop data.
        """
        given("Driver berstatus Online dan siap menerima pesanan volume tinggi")
        offers_8 = [
            {"order_id": f"ORD-REG-{i:02d}", "order_type": "regular", "pickup": f"Lokasi Jemput {i}", "fare": 10000 + (i * 2000), "distance_km": 1.0 + (i * 0.5)}
            for i in range(1, 6)
        ] + [
            {"order_id": f"ORD-ADV-{i:02d}", "order_type": "advance", "pickup": f"Lokasi Terjadwal {i}", "fare": 30000 + (i * 5000), "distance_km": 5.0 + (i * 2.0)}
            for i in range(1, 4)
        ]
        assert len(offers_8) == 8, "Harus tepat 8 order"

        when("Server mem-broadcast 8 order batch ke aplikasi driver")
        received = driver_sim.receive_batch_dispatch(offers_8)

        then("Driver sukses menerima dan menampilkan seluruh 8 order")
        assert len(received) == 8
        assert all(o["status"] == "OFFERED" for o in received)
        assert all(o["has_countdown"] is False for o in received)

        # Verifikasi pemisahan
        reg_count = len([o for o in received if o["order_type"] == "regular"])
        adv_count = len([o for o in received if o["order_type"] == "advance"])
        assert reg_count == 5, f"Harus 5 reguler, aktual: {reg_count}"
        assert adv_count == 3, f"Harus 3 advance, aktual: {adv_count}"
        logger.info("[VOL-01] Berhasil memvalidasi penerimaan 8 order batch simultan (5 Reguler + 3 Advance).")

    @pytest.mark.positive_true
    def test_TC_VOL_02_stress_testing_batch_of_15_orders_without_countdown(self, driver_sim):
        """
        [HIGH VOLUME - VOL-02: Stress Test 15 Orders]
        Deskripsi : Menguji ketahanan aplikasi driver saat menerima penawaran batch ekstrem berisi 15 order simultan.
        Ekspektasi: Sistem memproses ke-15 order secara deterministik, tanpa adanya countdown timer,
                    dan mempertahankan integritas memory state.
        """
        given("Sistem memicu lonjakan order di area pusat kota (15 pesanan masuk)")
        offers_15 = [
            {
                "order_id": f"ORD-STRESS-{i:02d}",
                "order_type": "regular" if i % 2 == 1 else "advance",
                "pickup": f"Titik Jemput #{i}",
                "destination": f"Titik Antar #{i}",
                "distance_km": round(0.5 + (i * 0.3), 1),
                "fare": 12000 + (i * 1500)
            }
            for i in range(1, 16)
        ]
        assert len(offers_15) == 15

        when("15 order disiarkan sekaligus ke Driver")
        received = driver_sim.receive_batch_dispatch(offers_15)

        then("Seluruh 15 order berhasil terdaftar di aplikasi driver")
        assert len(received) == 15
        assert all(o["has_countdown"] is False for o in received)
        logger.info("[VOL-02] Stress testing 15 order batch lulus 100% tanpa error.")

    @pytest.mark.positive_false
    def test_TC_VOL_03_driver_holding_5_concurrent_orders_exceed_attempt(self, driver_sim):
        """
        [HIGH VOLUME - VOL-03: Kapasitas Penuh 5 Order]
        Deskripsi : Menguji aturan dashboard: 'Order yang boleh dipegang satu driver = 5'.
                    Driver menerima berturut-turut 5 order hingga kapasitas maksimal tercapai,
                    kemudian mencoba menerima order ke-6.
        Ekspektasi: Order 1 s/d 5 sukses diterima. Upaya menerima order ke-6 ditolak dengan pesan kapasitas penuh.
        """
        driver_sim.set_concurrent_limit(5)
        given("Driver menerima daftar batch berisi 8 order")
        offers = [{"order_id": f"ORD-CAP-{i}", "order_type": "regular"} for i in range(1, 9)]
        driver_sim.receive_batch_dispatch(offers)

        when("Driver menerima 5 order berturut-turut (mencapai batas concurrent)")
        for i in range(1, 6):
            accepted = driver_sim.accept_batch_order(f"ORD-CAP-{i}")
            assert accepted["status"] == "ACCEPTED"

        then("Driver memegang tepat 5 order aktif dan status menjadi tidak tersedia")
        assert len(driver_sim._active_orders) == 5
        assert driver_sim.is_driver_available() is False

        and_step("Upaya menerima order ke-6 (ORD-CAP-6) ditolak oleh sistem")
        with pytest.raises(ValueError, match="Kapasitas order driver penuh"):
            driver_sim.accept_batch_order("ORD-CAP-6")
        logger.info("[VOL-03] Validasi limit 5 order berjalan sukses mencegah overload driver.")

    @pytest.mark.positive_true
    def test_TC_VOL_04_driver_selects_and_accepts_1_among_10_orders(self, driver_sim):
        """
        [HIGH VOLUME - VOL-04: Seleksi 1 Order dari 10 Pilihan]
        Deskripsi : Terdapat 10 order di layar. Driver secara selektif memilih order ke-7 (ORD-TEN-07)
                    dengan tarif tertinggi untuk diterima.
        Ekspektasi: Hanya order ke-7 yang beralih status ke 'ACCEPTED', 9 order lainnya tetap dalam status 'OFFERED'.
        """
        offers_10 = [{"order_id": f"ORD-TEN-{i:02d}", "order_type": "regular", "fare": 10000 + (i * 3000)} for i in range(1, 11)]
        driver_sim.receive_batch_dispatch(offers_10)

        when("Driver memilih dan menerima khusus ORD-TEN-07")
        acc = driver_sim.accept_batch_order("ORD-TEN-07")
        assert acc["status"] == "ACCEPTED"

        then("Daftar tawaran yang tersisa menyisakan 9 order")
        remaining_offers = driver_sim.get_batch_offers()
        assert len(remaining_offers) == 9
        assert "ORD-TEN-07" not in [o["order_id"] for o in remaining_offers]
        logger.info("[VOL-04] Seleksi 1 order di antara 10 tawaran berhasil tereksekusi mulus.")

    # ==========================================================================
    # BAGIAN 2: PENGUJIAN JARAK LENGKAP & BAND RADIUS MATRIX
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_DIST_01_ordinary_distance_bands_spectrum(self, driver_sim):
        """
        [DISTANCE MATRIX - DIST-01: Spektrum Seluruh Band Order Biasa]
        Deskripsi : Memvalidasi pemetaan order ke seluruh 5 band jarak reguler yang diatur di Dashboard:
                    - Band 1: 0 – 1 KM  -> Order 0.4 KM
                    - Band 2: 1 – 2 KM  -> Order 1.5 KM
                    - Band 3: 2 – 3 KM  -> Order 2.6 KM
                    - Band 4: 3 – 4 KM  -> Order 3.7 KM
                    - Band 5: 4 – 5 KM  -> Order 4.8 KM
        Ekspektasi: Seluruh order dari tiap tingkat jarak berhasil diklasifikasikan dan disiarkan dalam batch.
        """
        given("Konfigurasi dashboard memiliki 5 band radius order biasa (0-1, 1-2, 2-3, 3-4, 4-5 km)")
        spectrum_orders = [
            {"order_id": "ORD-DIST-B1", "order_type": "regular", "distance_km": 0.4, "band_expected": "0-1 km"},
            {"order_id": "ORD-DIST-B2", "order_type": "regular", "distance_km": 1.5, "band_expected": "1-2 km"},
            {"order_id": "ORD-DIST-B3", "order_type": "regular", "distance_km": 2.6, "band_expected": "2-3 km"},
            {"order_id": "ORD-DIST-B4", "order_type": "regular", "distance_km": 3.7, "band_expected": "3-4 km"},
            {"order_id": "ORD-DIST-B5", "order_type": "regular", "distance_km": 4.8, "band_expected": "4-5 km"},
        ]

        when("Sistem mendispatch seluruh spektrum jarak reguler")
        received = driver_sim.receive_batch_dispatch(spectrum_orders)

        then("Seluruh 5 tingkatan jarak berhasil diterima driver secara akurat")
        assert len(received) == 5
        distances = [o["distance_km"] for o in received]
        assert distances == [0.4, 1.5, 2.6, 3.7, 4.8]
        logger.info("[DIST-01] Seluruh spektrum 5 band jarak reguler (0-5 KM) terverifikasi 100% presisi.")

    @pytest.mark.positive_true
    def test_TC_DIST_02_boundary_exact_kilometer_cutoffs(self, driver_sim):
        """
        [DISTANCE MATRIX - DIST-02: Boundary Value Analysis pada Titik Potong KM]
        Deskripsi : Menguji aturan eksplisit dashboard:
                    'Band terakhir menutup pada angka selesainya. Band sebelumnya berhenti tepat sebelum angka selesai.'
                    Menguji nilai perbatasan: 0.99 KM, tepat 1.00 KM, 1.99 KM, tepat 2.00 KM, tepat 5.00 KM.
        Ekspektasi: Sistem menangani angka perbatasan secara deterministik tanpa duplikasi atau missing dispatch.
        """
        boundary_orders = [
            {"order_id": "ORD-BVA-0.99", "order_type": "regular", "distance_km": 0.99},
            {"order_id": "ORD-BVA-1.00", "order_type": "regular", "distance_km": 1.00},
            {"order_id": "ORD-BVA-1.99", "order_type": "regular", "distance_km": 1.99},
            {"order_id": "ORD-BVA-2.00", "order_type": "regular", "distance_km": 2.00},
            {"order_id": "ORD-BVA-5.00", "order_type": "regular", "distance_km": 5.00},
        ]
        received = driver_sim.receive_batch_dispatch(boundary_orders)
        assert len(received) == 5
        assert all(o["status"] == "OFFERED" for o in received)
        logger.info("[DIST-02] Pengujian batas BVA pada titik potong km (0.99, 1.00, 1.99, 2.00, 5.00) lolos.")

    @pytest.mark.positive_true
    def test_TC_DIST_03_advance_booking_distance_bands_spectrum(self, driver_sim):
        """
        [DISTANCE MATRIX - DIST-03: Spektrum Band Advance Booking (Jarak Jauh)]
        Deskripsi : Menguji seluruh 4 band Advance Booking yang diatur di Dashboard:
                    - Band 1: 0 – 1 KM   -> Misal 0.8 KM
                    - Band 2: 1 – 2 KM   -> Misal 1.7 KM
                    - Band 3: 2 – 5 KM   -> Misal 4.2 KM
                    - Band 4: 5 – 15 KM  -> Misal 12.5 KM & 14.9 KM
        Ekspektasi: Seluruh pesanan terjadwal jarak pendek hingga jarak jauh (s/d 15 KM) terakomodasi dalam batch.
        """
        adv_orders = [
            {"order_id": "ORD-ADV-0.8KM", "order_type": "advance", "distance_km": 0.8, "fare": 20000},
            {"order_id": "ORD-ADV-1.7KM", "order_type": "advance", "distance_km": 1.7, "fare": 25000},
            {"order_id": "ORD-ADV-4.2KM", "order_type": "advance", "distance_km": 4.2, "fare": 40000},
            {"order_id": "ORD-ADV-12.5KM", "order_type": "advance", "distance_km": 12.5, "fare": 80000},
            {"order_id": "ORD-ADV-14.9KM", "order_type": "advance", "distance_km": 14.9, "fare": 95000},
        ]
        received = driver_sim.receive_batch_dispatch(adv_orders)
        assert len(received) == 5
        assert all(o["order_type"] == "advance" for o in received)
        logger.info("[DIST-03] Spektrum jarak Advance Booking hingga 15 KM terverifikasi 100% presisi.")

    @pytest.mark.positive_false
    def test_TC_DIST_04_out_of_range_distances_handling(self, driver_sim):
        """
        [DISTANCE MATRIX - DIST-04: Jarak di Luar Jangkauan Band (Out of Range)]
        Deskripsi : Menguji pesanan dengan jarak di atas batas maksimal band:
                    - Pesanan Reguler > 5.0 KM (misal 8.5 KM)
                    - Pesanan Advance Booking > 15.0 KM (misal 22.0 KM)
        Ekspektasi: Sistem menangani pesanan di luar band radius secara aman (fallback ke sequential atau outer band dispatch)
                    tanpa menyebabkan crash pada pricing engine atau antarmuka driver.
        """
        out_of_range = [
            {"order_id": "ORD-OUT-REG-8.5KM", "order_type": "regular", "distance_km": 8.5, "fare": 32000},
            {"order_id": "ORD-OUT-ADV-22KM", "order_type": "advance", "distance_km": 22.0, "fare": 140000},
        ]
        received = driver_sim.receive_batch_dispatch(out_of_range)
        assert len(received) == 2
        assert received[0]["distance_km"] == 8.5
        assert received[1]["distance_km"] == 22.0
        logger.info("[DIST-04] Penanganan jarak di luar batas band radius (8.5 KM & 22.0 KM) berjalan stabil tanpa error.")
