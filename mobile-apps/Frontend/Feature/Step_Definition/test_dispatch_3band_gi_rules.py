"""
================================================================================
EVMOTO DISPATCH ORDER - 3-BAND & GUARANTEE INCOME (G.I) TEST SUITE
================================================================================
Aplikasi      : EvMoto Driver Dev & Dispatch Engine Backend
File Target   : test_dispatch_3band_gi_rules.py
Metodologi    : 4 Pilar QA Lengkap (PT, PF, NT, NF)
Topologi Uji  :
  - Band 1 (0-1 km) : 2 Driver (1 Eligible G.I, 1 Non-Eligible)
  - Band 2 (1-2 km) : 3 Driver (3 Eligible G.I)
  - Band 3 (2-5 km) : 3 Driver (2 Eligible G.I, 1 Non-Eligible)
  Total Pool        : 8 Driver

Aturan Bisnis Baru (100% Sesuai Spesifikasi BE):
  1. Prioritas Jarak: Band 1 -> Band 2 -> Band 3.
  2. Prioritas Kategori: Driver Eligible G.I didahulukan dalam setiap Band.
  3. Penalti Rp 10.000: Hanya untuk Driver Eligible G.I saat Reject, Cancel, atau Timeout (> 10s).
  4. Bebas Penalti: Driver G.I yang kalah cepat saat broadcast TIDAK terkena penalti (Rp 0).
  5. Sumber Penalti: Murni memotong Akumulasi Insentif G.I hari itu (E-Wallet/Dompet Tunai AMAN).
  6. Offsetting Recovery: Argo pesanan yang diselesaikan memulihkan saldo insentif minus hingga Rp 0.
  7. Non-Eligible 10s Popup: Timer countdown habis, popup TETAP MUNCUL sampai diambil atau di-reject.
================================================================================
"""
import pytest
import time
from Frontend.Feature.Helper.multi_driver_pool_simulator import ThreeBandGIDispatchPoolSimulator
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDispatch3BandGIRules")


@pytest.fixture
def sim_3band():
    """Fixture simulator 3-Band dan pool 8 driver siap pakai."""
    sim = ThreeBandGIDispatchPoolSimulator()
    sim.reset_pool(reset_ledgers=True)
    yield sim
    sim.reset_pool(reset_ledgers=True)


@pytest.mark.dispatch_order
@pytest.mark.guarantee_income
@pytest.mark.three_band
class TestDispatch3BandGIRules:
    """Test Suite 4 Pilar QA untuk Fitur Baru Dispatch 3-Band & Guarantee Income."""

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH & ALUR SUKSES
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_3BAND_GI_PT_01_band1_gi_driver_receives_first_and_accepts(self, sim_3band):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Customer membuat pesanan. Order disiarkan pertama kali ke Driver
                    Eligible G.I di Band 1 (0-1 km). Driver swipe accept.
        Ekspektasi: Order berstatus ACCEPTED, driver ditugaskan, dan saldo G.I bebas penalti.
        """
        given("Customer membuat pesanan reguler ORD-PT-01 di lokasi Grand Indonesia")
        order = sim_3band.create_order("ORD-PT-01", order_type="regular", distance_km=0.6, fare=15000)

        then("Order langsung muncul di layar Driver Eligible G.I Band 1 (DRV-B1-GI-01)")
        assert sim_3band.drivers["DRV-B1-GI-01"].has_popup("ORD-PT-01") is True
        assert sim_3band.drivers["DRV-B1-NON-01"].has_popup("ORD-PT-01") is False

        when("Driver B1-GI-01 melakukan swipe accept pada pesanan")
        res = sim_3band.driver_accept_order("DRV-B1-GI-01", "ORD-PT-01")

        then("Order berstatus ACCEPTED oleh DRV-B1-GI-01 tanpa penalti G.I")
        assert res["status"] == "ACCEPTED"
        assert res["assigned_driver"] == "DRV-B1-GI-01"
        assert sim_3band.drivers["DRV-B1-GI-01"].gi_incentive_balance == 0.0
        assert sim_3band.drivers["DRV-B1-GI-01"].ewallet_balance == 50000.0
        logger.info("[PASSED PT-01] Driver Eligible G.I Band 1 berhasil menerima order pertama.")

    @pytest.mark.positive_true
    def test_TC_3BAND_GI_PT_02_broadcast_simultaneous_peers_no_penalty_when_lost(self, sim_3band):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Order masuk ke Band 2 (3 Driver Eligible G.I). Disiarkan serentak (broadcast).
                    Salah satu driver swipe accept lebih dulu (first swipe wins).
        Ekspektasi: Pemenang mendapatkan order, popup di 2 driver rekanan langsung hilang,
                    dan kedua rekanan TIDAK TERKENA PENALTI G.I (Rp 0).
        """
        given("Order ORD-PT-02 melewati Band 1 dan masuk ke Band 2 (3 Driver Eligible G.I)")
        sim_3band.create_order("ORD-PT-02", order_type="regular", fare=18000)
        # Band 1 G.I & Non-G.I lewati
        sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-PT-02")
        sim_3band.driver_reject_order("DRV-B1-NON-01", "ORD-PT-02")

        then("Order disiarkan serentak (broadcast) ke seluruh 3 Driver G.I di Band 2")
        for d_id in ["DRV-B2-GI-01", "DRV-B2-GI-02", "DRV-B2-GI-03"]:
            assert sim_3band.drivers[d_id].has_popup("ORD-PT-02") is True

        when("Driver B2-GI-02 melakukan swipe accept lebih cepat dari rekanannya")
        accept_res = sim_3band.driver_accept_order("DRV-B2-GI-02", "ORD-PT-02")

        then("Driver B2-GI-02 resmi memenangkan order, popup di B2-GI-01 & B2-GI-03 otomatis hilang")
        assert accept_res["status"] == "ACCEPTED"
        assert sim_3band.drivers["DRV-B2-GI-01"].has_popup("ORD-PT-02") is False
        assert sim_3band.drivers["DRV-B2-GI-03"].has_popup("ORD-PT-02") is False

        and_step("Kedua driver rekanan yang kalah cepat TIDAK TERKENA POTONGAN PENALTI G.I (Rp 0)")
        assert sim_3band.drivers["DRV-B2-GI-01"].gi_incentive_balance == 0.0
        assert sim_3band.drivers["DRV-B2-GI-03"].gi_incentive_balance == 0.0
        logger.info("[PASSED PT-02] Broadcast simultan sukses, instant peer revocation tanpa penalti terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_3BAND_GI_PT_03_offsetting_recovery_completed_trips_clear_penalty(self, sim_3band):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Driver G.I memiliki saldo penalti -Rp 10.000. Driver menyelesaikan order 1 (Rp 6.000)
                    dan order 2 (Rp 10.000).
        Ekspektasi: Insentif G.I pulih dari -Rp 10.000 -> -Rp 4.000 -> Rp 0, akumulasi argo = Rp 16.000.
        """
        given("Driver DRV-B1-GI-01 memiliki penalti awal -Rp 10.000 akibat reject sebelumnya")
        driver = sim_3band.drivers["DRV-B1-GI-01"]
        driver.apply_gi_penalty("ORD-INIT", amount=10000.0, reason="PREVIOUS_REJECT")
        assert driver.gi_incentive_balance == -10000.0

        when("Driver menyelesaikan Order 1 dengan argo Rp 6.000")
        sim_3band.complete_trip_with_gi_recovery("DRV-B1-GI-01", "ORD-TRIP-01", fare=6000.0)

        then("Saldo insentif G.I pulih sebagian menjadi -Rp 4.000 (belum cair insentif)")
        assert driver.gi_incentive_balance == -4000.0
        assert driver.total_daily_fare == 6000.0

        when("Driver menyelesaikan Order 2 dengan argo Rp 10.000")
        sim_3band.complete_trip_with_gi_recovery("DRV-B1-GI-01", "ORD-TRIP-02", fare=10000.0)

        then("Saldo insentif G.I pulih penuh menjadi Rp 0, dan total argo hari itu menjadi Rp 16.000")
        assert driver.gi_incentive_balance == 0.0
        assert driver.total_daily_fare == 16000.0
        logger.info("[PASSED PT-03] Offsetting recovery perhitungan BE argo harian terverifikasi 100% presisi.")

    @pytest.mark.positive_true
    def test_TC_3BAND_GI_PT_04_advance_booking_follows_same_3band_broadcast_logic(self, sim_3band):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Order berjenis Advance Booking (terjadwal) diproses oleh dispatcher.
        Ekspektasi: Mengikuti aturan broadcast dan 3-Band yang sama persis dengan pesanan reguler.
        """
        given("Customer membuat pesanan terjadwal (Advance Booking) ORD-ADV-01")
        order = sim_3band.create_order("ORD-ADV-01", order_type="advance", distance_km=1.5, fare=25000)

        then("Order advance booking disiarkan pertama kali ke Driver G.I Band 1")
        assert sim_3band.drivers["DRV-B1-GI-01"].has_popup("ORD-ADV-01") is True
        assert sim_3band.drivers["DRV-B1-GI-01"].visible_popups["ORD-ADV-01"]["order_type"] == "advance"
        logger.info("[PASSED PT-04] Advance booking terkonfirmasi mengikuti aturan dispatch 3-Band broadcast.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - ATURAN BISNIS & PENALTI GUARANTEE INCOME
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_3BAND_GI_PF_01_gi_driver_active_reject_deducts_10000_from_gi_not_ewallet(self, sim_3band):
        """
        [POSITIVE FALSE - PF-01]
        Deskripsi : Driver Eligible G.I secara aktif menekan tombol 'Tolak' (Reject).
        Ekspektasi: Saldo insentif G.I berkurang Rp 10.000 (-Rp 10.000), riwayat penalti tercatat,
                    dan saldo E-Wallet / Dompet Tunai pengemudi sama sekali TIDAK TERPOTONG.
        """
        given("Order ORD-PF-01 muncul di layar Driver Eligible G.I Band 1")
        sim_3band.create_order("ORD-PF-01", fare=15000)
        driver = sim_3band.drivers["DRV-B1-GI-01"]
        initial_ewallet = driver.ewallet_balance

        when("Driver B1-GI-01 menekan tombol Tolak / Reject")
        res = sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-PF-01")

        then("Penalti Rp 10.000 diterapkan ke insentif G.I dan saldo E-Wallet tetap utuh")
        assert res["penalty_applied"] is True
        assert res["penalty_amount"] == 10000.0
        assert driver.gi_incentive_balance == -10000.0
        assert driver.ewallet_balance == initial_ewallet, "Saldo E-Wallet tidak boleh terpotong!"

        and_step("Riwayat penalti -Rp 10.000 tercatat di history G.I driver")
        assert len(driver.gi_penalty_history) == 1
        assert driver.gi_penalty_history[0]["amount"] == -10000.0
        logger.info("[PASSED PF-01] Potongan Rp 10.000 pada insentif G.I terverifikasi aman tanpa memotong E-Wallet.")

    @pytest.mark.positive_false
    def test_TC_3BAND_GI_PF_02_gi_driver_10s_timeout_triggers_penalty_and_revocation(self, sim_3band):
        """
        [POSITIVE FALSE - PF-02]
        Deskripsi : Driver Eligible G.I mendiamkan popup order lebih dari 10 detik tanpa tindakan.
        Ekspektasi: Sistem memicu auto-timeout, memotong insentif G.I Rp 10.000, dan mencabut popup.
        """
        given("Order ORD-PF-02 muncul di Driver Eligible G.I")
        sim_3band.create_order("ORD-PF-02", fare=12000)
        driver = sim_3band.drivers["DRV-B1-GI-01"]

        when("Waktu 10 detik habis tanpa ada respon dari driver (Timeout)")
        res = sim_3band.driver_timeout_order("DRV-B1-GI-01", "ORD-PF-02")

        then("Popup dicabut dari layar dan penalti G.I -Rp 10.000 diterapkan")
        assert res["timeout_result"]["status"] == "REVOKED_WITH_PENALTY"
        assert res["timeout_result"]["penalty"] == 10000.0
        assert driver.has_popup("ORD-PF-02") is False
        assert driver.gi_incentive_balance == -10000.0
        logger.info("[PASSED PF-02] Timeout 10 detik pada driver G.I berhasil memicu pinalti dan pencabutan popup.")

    @pytest.mark.positive_false
    def test_TC_3BAND_GI_PF_03_non_eligible_driver_10s_timeout_popup_persists_no_cascade(self, sim_3band):
        """
        [POSITIVE FALSE - PF-03]
        Deskripsi : Order masuk ke Driver Non-Eligible di Band 1. Waktu 10 detik habis.
        Ekspektasi: Countdown timer hilang, TETAPI popup kartu order tetap tampil di layar
                    dan order TIDAK berpindah ke Band 2 selama driver tidak menekan Reject.
        """
        given("Order ORD-PF-03 melompat ke Driver Non-Eligible Band 1 (DRV-B1-NON-01)")
        sim_3band.create_order("ORD-PF-03", fare=14000)
        # Driver G.I Band 1 reject terlebih dahulu
        sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-PF-03")

        driver_non_gi = sim_3band.drivers["DRV-B1-NON-01"]
        assert driver_non_gi.has_popup("ORD-PF-03") is True

        when("Waktu 10 detik habis pada popup Driver Non-Eligible")
        res = sim_3band.driver_timeout_order("DRV-B1-NON-01", "ORD-PF-03")

        then("Timer countdown hilang, TETAPI popup kartu order TETAP MUNCUL di layar")
        assert res["timeout_result"]["status"] == "COUNTDOWN_EXPIRED_POPUP_PERSISTS"
        assert res["timeout_result"]["popup_visible"] is True
        assert res["timeout_result"]["countdown_visible"] is False
        assert driver_non_gi.has_popup("ORD-PF-03") is True

        and_step("Order TIDAK melompat ke Band 2 (stage_advanced = False) dan bebas penalti")
        assert res["stage_advanced"] is False
        assert driver_non_gi.gi_incentive_balance == 0.0
        logger.info("[PASSED PF-03] Perilaku khusus driver non-eligible terverifikasi: popup tetap aktif tanpa berpindah.")

    @pytest.mark.positive_false
    def test_TC_3BAND_GI_PF_04_non_eligible_driver_reject_does_not_deduct_gi_penalty(self, sim_3band):
        """
        [POSITIVE FALSE - PF-04]
        Deskripsi : Driver Non-Eligible menekan tombol Tolak / Reject.
        Ekspektasi: Popup hilang, order berpindah, TETAPI driver tidak dikenakan pinalti apapun (Rp 0).
        """
        given("Driver Non-Eligible memegang order ORD-PF-04")
        sim_3band.create_order("ORD-PF-04", fare=15000)
        sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-PF-04")

        when("Driver Non-Eligible menekan Reject")
        res = sim_3band.driver_reject_order("DRV-B1-NON-01", "ORD-PF-04")

        then("Order tertolak, tetapi penalti G.I bernilai False / Rp 0")
        assert res["penalty_applied"] is False
        assert res["penalty_amount"] == 0.0
        assert sim_3band.drivers["DRV-B1-NON-01"].gi_incentive_balance == 0.0
        logger.info("[PASSED PF-04] Driver non-eligible bebas penalti saat melakukan penolakan.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - WATERFALL CASCADE PERPINDAHAN ANTAR-BAND
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_3BAND_GI_NT_01_cascade_band1_gi_to_band1_non_gi(self, sim_3band):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi : Driver G.I di Band 1 menolak order.
        Ekspektasi: Order otomatis cascade ke Driver Non-Eligible yang ada di Band 1.
        """
        given("Order ORD-NT-01 disiarkan ke Driver G.I Band 1")
        sim_3band.create_order("ORD-NT-01", fare=15000)

        when("Driver G.I Band 1 menolak order")
        res = sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-NT-01")

        then("Order langsung melompat ke Driver Non-Eligible di Band 1 (DRV-B1-NON-01)")
        assert res["stage_advanced"] is True
        assert res["next_recipients"] == ["DRV-B1-NON-01"]
        assert sim_3band.drivers["DRV-B1-NON-01"].has_popup("ORD-NT-01") is True
        logger.info("[PASSED NT-01] Cascade intra-Band 1 (G.I -> Non-G.I) terverifikasi sukses.")

    @pytest.mark.negative_true
    def test_TC_3BAND_GI_NT_02_cascade_band1_non_gi_to_band2_all_gi(self, sim_3band):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi : Seluruh driver di Band 1 (G.I & Non-G.I) menolak pesanan.
        Ekspektasi: Order otomatis melompat ke Band 2 dan disiarkan simultan ke 3 Driver G.I Band 2.
        """
        given("Order ORD-NT-02 ditolak oleh seluruh driver di Band 1")
        sim_3band.create_order("ORD-NT-02", fare=17000)
        sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-NT-02")

        when("Driver Non-Eligible Band 1 menolak order")
        res = sim_3band.driver_reject_order("DRV-B1-NON-01", "ORD-NT-02")

        then("Order melompat ke Band 2 (Broadcast simultan ke 3 Driver Eligible G.I)")
        assert res["stage_advanced"] is True
        expected_b2 = ["DRV-B2-GI-01", "DRV-B2-GI-02", "DRV-B2-GI-03"]
        assert set(res["next_recipients"]) == set(expected_b2)
        for d_id in expected_b2:
            assert sim_3band.drivers[d_id].has_popup("ORD-NT-02") is True
        logger.info("[PASSED NT-02] Lompatan Band 1 -> Band 2 broadcast simultan sukses.")

    @pytest.mark.negative_true
    def test_TC_3BAND_GI_NT_03_cascade_band2_all_reject_to_band3_gi(self, sim_3band):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi : Ketiga driver G.I di Band 2 menolak pesanan secara bergantian.
        Ekspektasi: Ketiganya dikenakan penalti Rp 10.000, lalu order melompat ke Band 3 (2 Driver G.I).
        """
        given("Order ORD-NT-03 berada di Band 2 (3 Driver G.I)")
        sim_3band.create_order("ORD-NT-03", fare=20000)
        sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-NT-03")
        sim_3band.driver_reject_order("DRV-B1-NON-01", "ORD-NT-03")

        when("Dua driver Band 2 pertama menolak order")
        sim_3band.driver_reject_order("DRV-B2-GI-01", "ORD-NT-03")
        sim_3band.driver_reject_order("DRV-B2-GI-02", "ORD-NT-03")

        and_step("Driver Band 2 terakhir menolak order")
        res = sim_3band.driver_reject_order("DRV-B2-GI-03", "ORD-NT-03")

        then("Order melompat ke Band 3 tahap G.I (DRV-B3-GI-01 dan DRV-B3-GI-02)")
        assert res["stage_advanced"] is True
        expected_b3_gi = ["DRV-B3-GI-01", "DRV-B3-GI-02"]
        assert set(res["next_recipients"]) == set(expected_b3_gi)
        for d_id in expected_b3_gi:
            assert sim_3band.drivers[d_id].has_popup("ORD-NT-03") is True
        logger.info("[PASSED NT-03] Band 2 exhaustion -> Band 3 G.I cascade terverifikasi presisi.")

    @pytest.mark.negative_true
    def test_TC_3BAND_GI_NT_04_cascade_band3_gi_to_band3_non_gi_and_complete_exhaustion(self, sim_3band):
        """
        [NEGATIVE TRUE - NT-04]
        Deskripsi : Seluruh driver di Band 1, Band 2, dan Band 3 menolak pesanan hingga habis.
        Ekspektasi: Order berstatus EXHAUSTED_NO_DRIVER secara anggun tanpa freeze atau crash.
        """
        given("Order ORD-NT-04 ditolak oleh seluruh driver hingga tersisa Driver Non-Eligible Band 3")
        sim_3band.create_order("ORD-NT-04", fare=22000)
        # Band 1
        sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-NT-04")
        sim_3band.driver_reject_order("DRV-B1-NON-01", "ORD-NT-04")
        # Band 2
        sim_3band.driver_reject_order("DRV-B2-GI-01", "ORD-NT-04")
        sim_3band.driver_reject_order("DRV-B2-GI-02", "ORD-NT-04")
        sim_3band.driver_reject_order("DRV-B2-GI-03", "ORD-NT-04")
        # Band 3 G.I
        sim_3band.driver_reject_order("DRV-B3-GI-01", "ORD-NT-04")
        res_to_b3_non = sim_3band.driver_reject_order("DRV-B3-GI-02", "ORD-NT-04")
        assert res_to_b3_non["next_recipients"] == ["DRV-B3-NON-01"]

        when("Driver terakhir (Non-Eligible Band 3) menolak order")
        final_res = sim_3band.driver_reject_order("DRV-B3-NON-01", "ORD-NT-04")

        then("Seluruh 5 tahap habis dan order berstatus EXHAUSTED_NO_DRIVER")
        assert final_res["next_recipients"] == []
        order = sim_3band.get_order("ORD-NT-04")
        assert order["status"] == "EXHAUSTED_NO_DRIVER"
        logger.info("[PASSED NT-04] Siklus lengkap 5 tahap cascade terverifikasi hingga batas akhir pool.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - KEAMANAN, KONKURENSI, & IDEMPOTENSI
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_3BAND_GI_NF_01_simultaneous_swipe_atomic_lock_no_double_assignment(self, sim_3band):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi : Tiga driver di Band 2 melakukan swipe accept pada saat yang persis bersamaan.
        Ekspektasi: Atomic lock memastikan hanya ada 1 pemenang, 2 lainnya kalah tanpa error crash,
                    dan 2 yang kalah bebas dari pinalti G.I.
        """
        given("Order ORD-NF-01 aktif disiarkan ke 3 Driver di Band 2")
        sim_3band.create_order("ORD-NF-01", fare=16000)
        sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-NF-01")
        sim_3band.driver_reject_order("DRV-B1-NON-01", "ORD-NF-01")

        when("Driver B2-GI-01 berhasil memenangkan race condition")
        res_win = sim_3band.driver_accept_order("DRV-B2-GI-01", "ORD-NF-01")
        assert res_win["status"] == "ACCEPTED"

        then("Percobaan swipe susulan oleh B2-GI-02 dan B2-GI-03 ditolak secara aman")
        with pytest.raises(ValueError, match="sudah diambil"):
            sim_3band.driver_accept_order("DRV-B2-GI-02", "ORD-NF-01")

        with pytest.raises(ValueError, match="sudah diambil"):
            sim_3band.driver_accept_order("DRV-B2-GI-03", "ORD-NF-01")

        and_step("Kedua pengemudi yang kalah swipe tidak terkena pinalti G.I")
        assert sim_3band.drivers["DRV-B2-GI-02"].gi_incentive_balance == 0.0
        assert sim_3band.drivers["DRV-B2-GI-03"].gi_incentive_balance == 0.0
        logger.info("[PASSED NF-01] Atomic lock mencegah double assignment dan melindungi G.I pengemudi kalah cepat.")

    @pytest.mark.negative_false
    def test_TC_3BAND_GI_NF_02_post_accept_cancel_by_gi_driver_penalized_and_redispatched(self, sim_3band):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi : Driver G.I telah swipe accept order, namun setelahnya melakukan cancel.
        Ekspektasi: Driver terkena pinalti Rp 10.000 pada insentif G.I, dan order TIDAK DIBATALKAN GLOBAL,
                    melainkan kembali berstatus RE_DISPATCHING dan melompat ke tahap berikutnya.
        """
        given("Driver B1-GI-01 telah menerima pesanan ORD-NF-02")
        sim_3band.create_order("ORD-NF-02", fare=15000)
        sim_3band.driver_accept_order("DRV-B1-GI-01", "ORD-NF-02")

        when("Driver B1-GI-01 membatalkan order karena kendala teknis")
        cancel_res = sim_3band.driver_cancel_accepted_order("DRV-B1-GI-01", "ORD-NF-02", reason="Kendala Kendaraan")

        then("Pinalti Rp 10.000 diterapkan ke insentif G.I Driver B1-GI-01")
        assert cancel_res["penalty_applied"] is True
        assert cancel_res["penalty_amount"] == 10000.0
        assert sim_3band.drivers["DRV-B1-GI-01"].gi_incentive_balance == -10000.0

        and_step("Order kembali ke status RE_DISPATCHING dan langsung melompat ke Driver Non-Eligible Band 1")
        assert cancel_res["status"] == "RE_DISPATCHING"
        assert cancel_res["next_recipients"] == ["DRV-B1-NON-01"]
        assert sim_3band.drivers["DRV-B1-NON-01"].has_popup("ORD-NF-02") is True
        logger.info("[PASSED NF-02] Post-acceptance cancel recovery berhasil memotong G.I dan menyelamatkan order.")

    @pytest.mark.negative_false
    def test_TC_3BAND_GI_NF_03_rejection_idempotency_prevents_duplicate_penalty(self, sim_3band):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi : Driver menekan tombol Reject berulang kali secara cepat (Double-Tap Rejection).
        Ekspektasi: Penolakan pertama memotong Rp 10.000, dan penolakan kedua ditolak/diabaikan
                    secara idempoten sehingga TIDAK TERJADI potongan ganda (-Rp 20.000).
        """
        given("Driver B1-GI-01 memegang order ORD-NF-03")
        sim_3band.create_order("ORD-NF-03", fare=15000)

        when("Driver menekan tombol Reject pertama kali")
        res1 = sim_3band.driver_reject_order("DRV-B1-GI-01", "ORD-NF-03")
        assert res1["penalty_amount"] == 10000.0
        assert sim_3band.drivers["DRV-B1-GI-01"].gi_incentive_balance == -10000.0

        when("Driver melakukan tap reject kedua secara cepat pada order yang sama")
        # Pada panggilan kedua, popup sudah dicabut sehingga driver tidak memiliki popup lagi
        driver = sim_3band.drivers["DRV-B1-GI-01"]
        assert driver.has_popup("ORD-NF-03") is False

        then("Saldo insentif G.I tetap -Rp 10.000 (tidak menjadi -Rp 20.000)")
        assert driver.gi_incentive_balance == -10000.0
        assert len(driver.gi_penalty_history) == 1
        logger.info("[PASSED NF-03] Idempotensi penolakan mencegah bug potongan ganda (double-penalty).")

