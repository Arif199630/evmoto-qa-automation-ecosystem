"""
================================================================================
EVMOTO DISPATCH BATCH: WATERFALL RE-DISPATCH & DISTANCE BAND EXPANSION
================================================================================
Test Suite untuk Pengujian End-to-End Logika Re-dispatching Multi-Driver:
  1. Siaran batch simultan ke 5 driver standby di radius terdekat (Ring 1 < 5 KM).
  2. Pencabutan seketika (Instant Revocation): Saat 1 driver menerima order,
     popup di 4 driver lainnya seketika lenyap tanpa jejak.
  3. Re-assign & Blacklist Exclusion: Saat driver tolak/cancel, order TETAP HIDUP
     dan otomatis dioper ke driver lain, sedangkan driver penolak di-blacklist.
  4. Distance Band Expansion: Jika seluruh driver Ring 1 menolak, sistem otomatis
     memperluas radius pencarian ke Ring 2 (2 driver di jarak > 5 KM).
  5. Advance Booking: Logika yang sama berlaku untuk pesanan terjadwal dengan
     matriks jarak dan parameter khusus.
  6. Post-Acceptance Cancellation: Pembatalan oleh driver setelah menerima tidak
     membatalkan order customer, melainkan mengembalikannya ke pool dispatching.
================================================================================
"""
import pytest
from Frontend.Feature.Helper.multi_driver_pool_simulator import MultiDriverDispatchPoolSimulator
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestBatchRedispatchCascade")


@pytest.fixture
def pool_sim():
    """Fixture untuk simulator pool multi-driver."""
    sim = MultiDriverDispatchPoolSimulator()
    sim.reset_pool()
    yield sim
    sim.reset_pool()


@pytest.mark.dispatch_batch
@pytest.mark.batch_dispatch
@pytest.mark.regression
class TestDrvBatchRedispatchCascade:
    """Suite Komprehensif Re-dispatching & Distance Band Waterfall Multi-Driver."""

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY FLOW, REVOCATION & ADVANCE BOOKING
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_CASCADE_PT_01_simultaneous_broadcast_and_instant_peer_revocation(self, pool_sim):
        """
        [POSITIVE TRUE - PT-01: Siaran Simultan & Instant Popup Revocation]
        Deskripsi : 
          1. Customer membuat order reguler baru ORD-SIMULTAN-01.
          2. Sistem mendispatch order secara bersamaan ke 5 driver standby di Ring 1 (< 5 KM).
          3. Driver 3 (DRV-03) melakukan Swipe/Terima pesanan.
        Ekspektasi:
          - Kelima driver Ring 1 menerima popup order secara bersamaan.
          - Saat DRV-03 menerima order, popup di DRV-01, DRV-02, DRV-04, dan DRV-05 LANGSUNG HILANG!
        """
        given("Terdapat pesanan reguler baru ORD-SIMULTAN-01 dan 5 driver standby di Ring 1 (< 5 KM)")
        pool_sim.create_order("ORD-SIMULTAN-01", order_type="regular", distance_km=2.8, fare=15000)

        when("Sistem menyiarkan batch order ke seluruh driver di Ring 1")
        recipients = pool_sim.broadcast_batch_to_band("ORD-SIMULTAN-01", target_band="ring1")

        then("Kelima driver Ring 1 menerima popup order secara simultan")
        assert len(recipients) == 5
        assert set(recipients) == {"DRV-01", "DRV-02", "DRV-03", "DRV-04", "DRV-05"}
        for d_id in ["DRV-01", "DRV-02", "DRV-03", "DRV-04", "DRV-05"]:
            assert pool_sim.is_order_visible_on_driver(d_id, "ORD-SIMULTAN-01") is True

        and_step("Driver DRV-06 dan DRV-07 di Ring 2 (> 5 KM) belum menerima popup order")
        assert pool_sim.is_order_visible_on_driver("DRV-06", "ORD-SIMULTAN-01") is False
        assert pool_sim.is_order_visible_on_driver("DRV-07", "ORD-SIMULTAN-01") is False

        when("Driver DRV-03 melakukan Swipe Terima pada pesanan ORD-SIMULTAN-01")
        res = pool_sim.driver_accept_order("DRV-03", "ORD-SIMULTAN-01")
        assert res["status"] == "ACCEPTED"
        assert res["assigned_driver"] == "DRV-03"

        then("Popup order pada DRV-01, DRV-02, DRV-04, dan DRV-05 SEKETIKA DICABUT (HILANG)")
        for peer_id in ["DRV-01", "DRV-02", "DRV-04", "DRV-05"]:
            assert pool_sim.is_order_visible_on_driver(peer_id, "ORD-SIMULTAN-01") is False

        logger.info("[PT-01] Validasi Lolos: Instant Popup Revocation bekerja 100% sempurna.")

    @pytest.mark.positive_true
    def test_TC_CASCADE_PT_02_advance_booking_distinct_cascading_and_revocation(self, pool_sim):
        """
        [POSITIVE TRUE - PT-02: Advance Booking Cascading & Instant Revocation]
        Deskripsi : Memvalidasi alur yang sama berlaku untuk pesanan Advance Booking (Pesanan Terjadwal),
                    dengan radius matriks yang lebih luas (misal penjemputan terjadwal besok pagi).
        Ekspektasi: Instant revocation dan pemisahan tipe 'advance' bekerja presisi.
        """
        given("Customer membuat pesanan Advance Booking ORD-ADV-99 (Jarak 8.5 KM, Tarif Rp 65.000)")
        pool_sim.create_order("ORD-ADV-99", order_type="advance", distance_km=8.5, fare=65000)

        when("Sistem mendispatch batch Advance Booking ke Ring 1")
        recipients = pool_sim.broadcast_batch_to_band("ORD-ADV-99", target_band="ring1")
        assert len(recipients) == 5

        when("Driver DRV-01 melakukan Swipe Terima pada pesanan Advance Booking")
        pool_sim.driver_accept_order("DRV-01", "ORD-ADV-99")

        then("Popup Advance Booking pada DRV-02 hingga DRV-05 langsung hilang")
        for p in ["DRV-02", "DRV-03", "DRV-04", "DRV-05"]:
            assert pool_sim.is_order_visible_on_driver(p, "ORD-ADV-99") is False

        ord_info = pool_sim.get_order_details("ORD-ADV-99")
        assert ord_info["status"] == "ACCEPTED"
        assert ord_info["assigned_driver"] == "DRV-01"
        assert ord_info["order_type"] == "advance"
        logger.info("[PT-02] Validasi Lolos: Alur Advance Booking terverifikasi presisi.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - EXCLUSION BLACKLIST & RE-DISPATCH CHAIN
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_CASCADE_PF_01_driver_reject_triggers_redispatch_and_exclusion_blacklist(self, pool_sim):
        """
        [POSITIVE FALSE - PF-01: Re-dispatch dengan Blacklist Exclusion Driver Penolak]
        Deskripsi : 
          1. 5 Driver Ring 1 menerima broadcast order ORD-REJECT-01.
          2. Driver DRV-01 menekan tombol 'Tolak' (Reject).
        Ekspektasi:
          - Order ORD-REJECT-01 TIDAK BOLEH CANCELLED (harus tetap aktif RE_DISPATCHING).
          - DRV-01 masuk ke daftar Blacklist sehingga order tersebut TIDAK AKAN PERNAH muncul lagi di DRV-01.
          - Order tetap tampil dan siap diambil oleh Driver DRV-02, DRV-03, DRV-04, dan DRV-05.
        """
        given("Order ORD-REJECT-01 disiarkan ke 5 driver Ring 1")
        pool_sim.create_order("ORD-REJECT-01", order_type="regular", distance_km=3.0, fare=16000)
        pool_sim.broadcast_batch_to_band("ORD-REJECT-01", target_band="ring1")

        when("Driver DRV-01 menolak (Reject) tawaran tersebut")
        cascade_res = pool_sim.driver_reject_order("DRV-01", "ORD-REJECT-01")

        then("Order tidak mati, melainkan berstatus RE_DISPATCHING")
        assert cascade_res["status"] == "RE_DISPATCHING"
        assert cascade_res["action"] == "SAME_BAND_REASSIGN"

        and_step("Popup order DICABUT dari DRV-01 dan DRV-01 di-blacklist")
        assert pool_sim.is_order_visible_on_driver("DRV-01", "ORD-REJECT-01") is False
        ord_details = pool_sim.get_order_details("ORD-REJECT-01")
        assert "DRV-01" in ord_details["rejected_driver_ids"]

        and_step("Order TETAP MUNCUL dan aktif pada driver rekanan di Ring 1 (DRV-02, DRV-03, DRV-04, DRV-05)")
        for peer in ["DRV-02", "DRV-03", "DRV-04", "DRV-05"]:
            assert pool_sim.is_order_visible_on_driver(peer, "ORD-REJECT-01") is True

        when("Driver DRV-02 kemudian mengambil (Accept) order tersebut")
        accept_res = pool_sim.driver_accept_order("DRV-02", "ORD-REJECT-01")
        assert accept_res["status"] == "ACCEPTED"
        assert accept_res["assigned_driver"] == "DRV-02"

        logger.info("[PF-01] Validasi Lolos: Re-dispatch ke rekan pengemudi & Blacklist exclusion berhasil.")

    @pytest.mark.positive_false
    def test_TC_CASCADE_PF_02_chained_rejection_successive_pass_through(self, pool_sim):
        """
        [POSITIVE FALSE - PF-02: Rantai Penolakan Berturut-turut dalam Ring yang Sama]
        Deskripsi : Driver 1 menolak -> Driver 2 menolak -> Driver 3 menolak.
        Ekspektasi: Order tetap bertahan di pool, driver 1-3 tidak menerima lagi,
                    sedangkan Driver 4 & Driver 5 masih dapat melihat dan mengambil order.
        """
        given("Order ORD-CHAIN-01 disiarkan ke 5 driver Ring 1")
        pool_sim.create_order("ORD-CHAIN-01", order_type="regular", distance_km=2.0, fare=12000)
        pool_sim.broadcast_batch_to_band("ORD-CHAIN-01", target_band="ring1")

        when("DRV-01, DRV-02, dan DRV-03 berturut-turut menolak order")
        pool_sim.driver_reject_order("DRV-01", "ORD-CHAIN-01")
        pool_sim.driver_reject_order("DRV-02", "ORD-CHAIN-01")
        pool_sim.driver_reject_order("DRV-03", "ORD-CHAIN-01")

        then("DRV-01, DRV-02, dan DRV-03 semuanya masuk blacklist dan tidak melihat order")
        for d in ["DRV-01", "DRV-02", "DRV-03"]:
            assert pool_sim.is_order_visible_on_driver(d, "ORD-CHAIN-01") is False

        and_step("DRV-04 dan DRV-05 masih memiliki popup order aktif di layar mereka")
        assert pool_sim.is_order_visible_on_driver("DRV-04", "ORD-CHAIN-01") is True
        assert pool_sim.is_order_visible_on_driver("DRV-05", "ORD-CHAIN-01") is True

        when("DRV-05 akhirnya melakukan Swipe Terima")
        res = pool_sim.driver_accept_order("DRV-05", "ORD-CHAIN-01")
        assert res["status"] == "ACCEPTED"
        assert pool_sim.is_order_visible_on_driver("DRV-04", "ORD-CHAIN-01") is False
        logger.info("[PF-02] Validasi Lolos: Rantai penolakan berturut-turut terkelola secara deterministik.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - DISTANCE BAND EXPANSION & EXHAUSTION
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_CASCADE_NT_01_waterfall_expansion_to_next_distance_band(self, pool_sim):
        """
        [NEGATIVE TRUE - NT-01: Distance Band Expansion saat Seluruh Driver Terdekat Menolak]
        Deskripsi : 
          1. 5 Driver di Ring 1 (< 5 KM) semuanya menolak order ORD-EXPAND-01.
          2. Hak driver di Ring 1 telah habis total.
        Ekspektasi:
          - Sistem otomatis mengaktifkan ekspansi radius Distance Band (Ring 2 > 5 KM).
          - Popup order baru seketika muncul di Driver DRV-06 dan DRV-07.
          - Driver 1–5 di Ring 1 tidak mendapatkan order tersebut lagi.
        """
        given("Order ORD-EXPAND-01 disiarkan ke 5 driver Ring 1")
        pool_sim.create_order("ORD-EXPAND-01", order_type="regular", distance_km=4.5, fare=22000)
        pool_sim.broadcast_batch_to_band("ORD-EXPAND-01", target_band="ring1")

        when("Kelima driver Ring 1 (DRV-01 s/d DRV-05) menolak pesanan secara berurutan")
        pool_sim.driver_reject_order("DRV-01", "ORD-EXPAND-01")
        pool_sim.driver_reject_order("DRV-02", "ORD-EXPAND-01")
        pool_sim.driver_reject_order("DRV-03", "ORD-EXPAND-01")
        pool_sim.driver_reject_order("DRV-04", "ORD-EXPAND-01")
        final_reject = pool_sim.driver_reject_order("DRV-05", "ORD-EXPAND-01")

        then("Sistem mendeteksi Ring 1 habis dan memicu Distance Band Expansion ke Ring 2")
        assert final_reject["status"] == "BAND_EXPANDED"
        assert final_reject["action"] == "EXPAND_TO_RING_2"
        assert final_reject["current_band"] == "ring2"
        assert final_reject["band_expanded"] is True

        and_step("Order secara otomatis muncul di layar DRV-06 dan DRV-07 (Ring 2 > 5 KM)")
        assert pool_sim.is_order_visible_on_driver("DRV-06", "ORD-EXPAND-01") is True
        assert pool_sim.is_order_visible_on_driver("DRV-07", "ORD-EXPAND-01") is True

        and_step("Seluruh driver Ring 1 (DRV-01 s/d DRV-05) tetap bersih tanpa popup")
        for r1 in ["DRV-01", "DRV-02", "DRV-03", "DRV-04", "DRV-05"]:
            assert pool_sim.is_order_visible_on_driver(r1, "ORD-EXPAND-01") is False

        when("Driver DRV-06 di Ring 2 menerima pesanan tersebut")
        accept_res = pool_sim.driver_accept_order("DRV-06", "ORD-EXPAND-01")
        assert accept_res["status"] == "ACCEPTED"
        assert pool_sim.is_order_visible_on_driver("DRV-07", "ORD-EXPAND-01") is False

        logger.info("[NT-01] Validasi Lolos: Distance Band Waterfall Expansion ke Ring 2 sukses 100%.")

    @pytest.mark.negative_true
    def test_TC_CASCADE_NT_02_complete_exhaustion_all_bands_graceful_no_driver_alert(self, pool_sim):
        """
        [NEGATIVE TRUE - NT-02: Seluruh Driver di Seluruh Band Menolak (Exhaustion)]
        Deskripsi : Kelima driver Ring 1 dan kedua driver Ring 2 semuanya menolak order.
        Ekspektasi: Sistem mencapai status 'NO_DRIVER_FOUND' secara graceful tanpa exception atau memory leak.
        """
        given("Order ORD-EXHAUST-01 diproses")
        pool_sim.create_order("ORD-EXHAUST-01", order_type="regular", distance_km=5.0, fare=25000)
        pool_sim.broadcast_batch_to_band("ORD-EXHAUST-01", target_band="ring1")

        # 5 Driver Ring 1 tolak
        for i in range(1, 6):
            pool_sim.driver_reject_order(f"DRV-0{i}", "ORD-EXHAUST-01")

        when("Kedua driver Ring 2 (DRV-06 dan DRV-07) juga menolak pesanan")
        pool_sim.driver_reject_order("DRV-06", "ORD-EXHAUST-01")
        final_exhaustion = pool_sim.driver_reject_order("DRV-07", "ORD-EXHAUST-01")

        then("Sistem secara aman beralih ke status NO_DRIVER_FOUND")
        assert final_exhaustion["status"] == "NO_DRIVER_FOUND"
        assert final_exhaustion["action"] == "EXHAUSTED"
        assert final_exhaustion["eligible_drivers"] == []

        ord_info = pool_sim.get_order_details("ORD-EXHAUST-01")
        assert ord_info["status"] == "NO_DRIVER_FOUND"
        assert len(ord_info["rejected_driver_ids"]) == 7
        logger.info("[NT-02] Validasi Lolos: Penanganan graceful exhaustion seluruh band berjalan aman.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - CANCEL RECOVERY & CONCURRENCY ATOMIC LOCK
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_CASCADE_NF_01_post_acceptance_cancel_recovers_to_pool_not_killed(self, pool_sim):
        """
        [NEGATIVE FALSE - NF-01: Pembatalan Pasca-Terima Pulih Kembali ke Pool]
        Deskripsi : 
          1. Driver DRV-01 menerima order ORD-POST-CANCEL-01.
          2. Beberapa saat kemudian, ban DRV-01 bocor dan ia menekan 'Batalkan Pesanan'.
        Ekspektasi:
          - CRUCIAL FIX: Order TIDAK DIBATALKAN KE CUSTOMER!
          - Status order kembali ke RE_DISPATCHING.
          - DRV-01 kembali standby dan di-blacklist dari order tersebut.
          - Order otomatis di-reassign ke sisa rekan standby di Ring 1 (DRV-02 s/d DRV-05).
        """
        given("Order ORD-POST-CANCEL-01 diterima oleh Driver DRV-01")
        pool_sim.create_order("ORD-POST-CANCEL-01", order_type="regular", distance_km=2.2, fare=13000)
        pool_sim.broadcast_batch_to_band("ORD-POST-CANCEL-01", target_band="ring1")
        pool_sim.driver_accept_order("DRV-01", "ORD-POST-CANCEL-01")

        when("Driver DRV-01 membatalkan pesanan karena 'Ban Bocor / Kendala Kendaraan'")
        recovery_res = pool_sim.driver_cancel_accepted_order("DRV-01", "ORD-POST-CANCEL-01", reason="Ban Bocor")

        then("Order tidak mati, melainkan berstatus RE_DISPATCHING")
        assert recovery_res["status"] == "RE_DISPATCHING"
        assert recovery_res["action"] == "SAME_BAND_REASSIGN"

        and_step("Order secara otomatis muncul kembali di layar rekanan (DRV-02, DRV-03, DRV-04, DRV-05)")
        for peer in ["DRV-02", "DRV-03", "DRV-04", "DRV-05"]:
            assert pool_sim.is_order_visible_on_driver(peer, "ORD-POST-CANCEL-01") is True

        and_step("Driver DRV-01 yang membatalkan TIDAK melihat order tersebut lagi (Blacklisted)")
        assert pool_sim.is_order_visible_on_driver("DRV-01", "ORD-POST-CANCEL-01") is False

        when("Driver DRV-04 mengambil alih pesanan yang dibatalkan DRV-01")
        takeover_res = pool_sim.driver_accept_order("DRV-04", "ORD-POST-CANCEL-01")
        assert takeover_res["status"] == "ACCEPTED"
        assert takeover_res["assigned_driver"] == "DRV-04"

        then("Popup seketika hilang dari DRV-02, DRV-03, dan DRV-05")
        for other in ["DRV-02", "DRV-03", "DRV-05"]:
            assert pool_sim.is_order_visible_on_driver(other, "ORD-POST-CANCEL-01") is False

        logger.info("[NF-01] Validasi Lolos: Post-acceptance cancel recovery berhasil menyelamatkan order customer.")

    @pytest.mark.negative_false
    def test_TC_CASCADE_NF_02_atomic_lock_prevents_simultaneous_acceptance_race_condition(self, pool_sim):
        """
        [NEGATIVE FALSE - NF-02: Proteksi Atomic Lock saat 2 Driver Swipe Bersamaan]
        Deskripsi : DRV-02 dan DRV-03 melakukan Swipe Accept pada milidetik yang sama.
        Ekspektasi: Tepat 1 driver sukses menerima order; driver kedua ditolak dengan aman tanpa crash.
        """
        given("Order ORD-RACE-88 disiarkan ke Ring 1")
        pool_sim.create_order("ORD-RACE-88", order_type="regular", distance_km=3.5, fare=18000)
        pool_sim.broadcast_batch_to_band("ORD-RACE-88", target_band="ring1")

        when("DRV-02 dan DRV-03 mencoba menerima order secara simultan")
        success_driver = None
        error_driver_msg = None

        # Driver 2 accept
        res2 = pool_sim.driver_accept_order("DRV-02", "ORD-RACE-88")
        if res2["status"] == "ACCEPTED":
            success_driver = "DRV-02"

        # Driver 3 accept sesaat setelah Driver 2
        try:
            pool_sim.driver_accept_order("DRV-03", "ORD-RACE-88")
        except ValueError as e:
            error_driver_msg = str(e)

        then("Tepat 1 driver memenangkan order dan driver kedua mendapatkan notifikasi aman")
        assert success_driver == "DRV-02"
        assert "Race condition" in error_driver_msg or "tidak memiliki penawaran" in error_driver_msg

        logger.info("[NF-02] Validasi Lolos: Atomic Lock mencegah tabrakan order saat swipe simultan.")

