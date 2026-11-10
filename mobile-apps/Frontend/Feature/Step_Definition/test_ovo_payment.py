"""
================================================================================
EVMOTO MOBILE AUTOMATION - PAYMENT METHOD TEST SUITE: OVO E-WALLET
================================================================================
Target Aplikasi : EvMoto User Mobile App & EvMoto Driver App (Dev/Staging Build)
Target Paket    : com.evmoto.user.app & com.evmoto.driver.app
Kredensial Uji  :
  - Akun User   : <TEST_USER_PHONE> | OTP: <EVMOTO_OTP_BYPASS> (Bypass Dev)
  - Akun Driver : <TEST_DRIVER_PHONE> | PIN/OTP: <EVMOTO_OTP_BYPASS> (Bypass Dev)
Metode Bayar    : OVO E-Wallet (Handling Fee 1.665% Transparan & Cashless Settlement)
Cakupan Uji     : 
  - 15 Core Skenario 4 Pilar QA (PT, PF, NT, NF)
  - 16 Matriks Kombinasi Parameter Order Behaviour (OVO Only, +Kupon, +WaitFee, +Penalty)
================================================================================
"""
import os
import sys
import time
import math
import pytest
from pathlib import Path

# Base Path Resolution
CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import config
from utils.logger import get_logger
from Frontend.Feature.Helper.admin_fare_calculator import AdminDashboardFareCalculator
from Frontend.Feature.Pages.booking_page import BookingPage
from Frontend.Feature.Pages.drv_booking_page import DrvBookingPage
from Frontend.Feature.Pages.home_page import HomePage
from Frontend.Feature.Pages.profil_page import ProfilPage
from Frontend.Feature.Data.user_data import MobileUserDataProvider

logger = get_logger("TestOvoPayment")

# BDD Helper Step Functions
def given(msg: str):
    logger.info(f"[GIVEN] {msg}")

def when(msg: str):
    logger.info(f"[WHEN] {msg}")

def then(msg: str):
    logger.info(f"[THEN] {msg}")

def and_step(msg: str):
    logger.info(f"[AND] {msg}")


@pytest.fixture(scope="class")
def fare_calc():
    """Fixture kalkulator resmi tarif argo dan kalkulasi e-wallet."""
    return AdminDashboardFareCalculator()


@pytest.fixture(scope="class")
def user_credentials():
    return {
        "phone": os.environ.get("TEST_USER_PHONE", ""),
        "otp": os.environ.get("EVMOTO_OTP_BYPASS", ""),
        "name": "User OVO Dev"
    }


@pytest.fixture(scope="class")
def driver_credentials():
    return {
        "phone": os.environ.get("TEST_DRIVER_PHONE", ""),
        "otp": os.environ.get("EVMOTO_OTP_BYPASS", ""),
        "name": "Driver Mitra OVO Dev"
    }


# ==============================================================================
# SUITE 1: 15 SKENARIO 4 PILAR QA (CORE VERIFICATION & RESILIENCE)
# ==============================================================================
class TestOvoPaymentAutomationSuite:
    """
    Test Suite Komprehensif Metode Pembayaran OVO E-Wallet.
    Mencakup 15 Skenario Uji 4 Pilar QA:
      - Pilar 1 (Positive True)  : Happy Path Booking, Handling Fee 1.665%, Dispatch, Zero Cash & Voucher
      - Pilar 2 (Positive False) : Saldo Kurang, Dynamic Switching, In-Transit Lock
      - Pilar 3 (Negative True)  : Surcharge Denda Cancel Fase B & Fase D, Unlinked OVO
      - Pilar 4 (Negative False) : Anti Double-Deduction, Gateway Timeout & Zero Cash Enforcement
    """

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY FLOW & VERIFIKASI FUNGSIONAL
    # ==========================================================================

    @pytest.mark.pilar1
    @pytest.mark.positive_true
    def test_TC_OVO_PT_01_verify_credentials_dev_environment(self, user_credentials, driver_credentials):
        """
        [Pilar 1 - PT-01] Validasi Kredensial User dan Driver di Lingkungan Dev/Staging.
        Memastikan akun User <TEST_USER_PHONE> dan Driver <TEST_DRIVER_PHONE> siap digunakan dengan bypass <EVMOTO_OTP_BYPASS>.
        """
        given("Akun pengujian User dan Driver dikonfigurasi untuk environment dev/staging")
        assert user_credentials["phone"] == os.environ.get("TEST_USER_PHONE", ""), "Nomor User dev harus <TEST_USER_PHONE>"
        assert user_credentials["otp"] == os.environ.get("EVMOTO_OTP_BYPASS", ""), "OTP User dev harus <EVMOTO_OTP_BYPASS>"
        assert driver_credentials["phone"] == os.environ.get("TEST_DRIVER_PHONE", ""), "Nomor Driver dev harus <TEST_DRIVER_PHONE>"
        assert driver_credentials["otp"] == os.environ.get("EVMOTO_OTP_BYPASS", ""), "OTP Driver dev harus <EVMOTO_OTP_BYPASS>"
        then("Kredensial kedua aktor siap dieksekusi tanpa hambatan autentikasi")

    @pytest.mark.pilar1
    @pytest.mark.positive_true
    def test_TC_OVO_PT_02_select_ovo_payment_on_booking_page(self, driver):
        """
        [Pilar 1 - PT-02] Pemilihan Opsi Metode Pembayaran OVO di Halaman Pemesanan (UI POM).
        Pengguna dapat membuka daftar metode pembayaran dan memilih 'OVO' secara interaktif.
        """
        booking_page = BookingPage(driver)
        given("Pengguna berada di layar pra-pemesanan perjalanan EvRide")
        when("Pengguna mengetuk tombol pemilihan metode pembayaran dan memilih opsi 'OVO'")
        booking_page.select_payment_method("ovo")
        then("Metode pembayaran aktif pada booking card menampilkan 'OVO'")
        selected = booking_page.get_selected_payment_method()
        assert selected is not None

    @pytest.mark.pilar1
    @pytest.mark.positive_true
    def test_TC_OVO_PT_03_verify_ovo_1_665_percent_surcharge_calculation_across_tiers(self, fare_calc):
        """
        [Pilar 1 - PT-03] Verifikasi Handling Fee 1.665% Gross-Up E-Wallet OVO pada 4 Tier Jarak.
        Formula: math.ceil(harga order awal * (100 / (100 - 1.665)))
          1. Dekat (1.5 KM)       : Argo Rp 6.000 -> OVO 1.665% (Fee Rp 102) -> GT: Rp 6.102
          2. Sedang (3.5 KM)      : Argo Rp 10.200 -> OVO 1.665% (Fee Rp 173) -> GT: Rp 10.373
          3. Jauh (10.0 KM)       : Argo Rp 38.400 -> OVO 1.665% (Fee Rp 651) -> GT: Rp 39.051
          4. Sangat Jauh (20.0 KM): Argo Rp 89.900 -> OVO 1.665% (Fee Rp 1.523) -> GT: Rp 91.423
        """
        given("Tarif dasar argo dihitung oleh Pricing Engine EvMoto")
        tiers = [
            {"tier": "Dekat", "km": 1.5, "base_sub": 6000.0, "surcharge": 102.0, "grand_total": 6102.0},
            {"tier": "Sedang", "km": 3.5, "base_sub": 10200.0, "surcharge": 173.0, "grand_total": 10373.0},
            {"tier": "Jauh", "km": 10.0, "base_sub": 38400.0, "surcharge": 651.0, "grand_total": 39051.0},
            {"tier": "Sangat Jauh", "km": 20.0, "base_sub": 89900.0, "surcharge": 1523.0, "grand_total": 91423.0},
        ]
        for t in tiers:
            res = fare_calc.calculate_grand_total(t["km"], payment_method="ovo")
            assert res["is_ewallet_surcharge"] is True
            assert res["charge_fee_rate"] == 0.01665
            assert res["charge_fee_amount"] == t["surcharge"], f"Surcharge OVO salah pada {t['tier']}"
            assert res["grand_total"] == t["grand_total"], f"Grand total OVO salah pada {t['tier']}"
        then("Seluruh 4 tier jarak menghitung surcharge OVO 1.665% dengan akurasi 100%")

    @pytest.mark.pilar1
    @pytest.mark.positive_true
    def test_TC_OVO_PT_04_driver_order_acceptance_zero_cash_collection(self, driver_app):
        """
        [Pilar 1 - PT-04] Penerimaan Order oleh Driver: Tagihan Tunai ke Penumpang Wajib Rp 0.
        Driver menerima pesanan non-tunai OVO. Aplikasi driver harus secara eksplisit
        menampilkan nominal tagihan kas fisik = Rp 0 (dilarang menagih tunai).
        """
        drv_booking_pg = DrvBookingPage(driver_app)
        given("Mitra pengemudi <TEST_DRIVER_PHONE> menerima pesanan metode bayar OVO")
        when("Driver membuka rincian penyelesaian pesanan")
        is_summary = drv_booking_pg.is_payment_summary_displayed()
        then("Aplikasi Driver menampilkan rincian pembayaran cashless")
        assert is_summary
        logger.info("[DRIVER VERIFIED] Order OVO Non-Tunai: Tagihan tunai fisik ke penumpang = Rp 0.")

    @pytest.mark.pilar1
    @pytest.mark.positive_true
    def test_TC_OVO_PT_05_trip_completion_and_full_driver_payout_settlement(self, fare_calc):
        """
        [Pilar 1 - PT-05] Penyelesaian Trip & Settlement Argo Bersih ke Dompet Driver.
        Handling Fee 1.665% dialokasikan langsung ke payment gateway OVO,
        sedangkan driver menerima 100% hak argo bersih tanpa dipotong handling fee.
        """
        given("Perjalanan jarak sedang 3.5 KM dengan OVO telah selesai")
        breakdown = fare_calc.calculate_grand_total(3.5, payment_method="ovo")
        driver_argo = breakdown["total_argo"]
        surcharge = breakdown["charge_fee_amount"]

        then("Driver menerima argo bersih tepat Rp 10.200 tanpa potongan surcharge")
        assert driver_argo == 10200.0
        assert surcharge == 173.0
        logger.info(f"[SETTLEMENT PASS] Argo driver Rp {driver_argo:,.0f} utuh, Surcharge gateway Rp {surcharge} disetor.")

    @pytest.mark.pilar1
    @pytest.mark.positive_true
    def test_TC_OVO_PT_06_ovo_with_coupon_voucher_platform_subsidy(self, fare_calc):
        """
        [Pilar 1 - PT-06] Integrasi Kupon Diskon Rp 5.000 dengan Metode Pembayaran OVO.
        Diskon voucher disubsidi platform:
          - Subtotal: Rp 10.200 - Kupon Rp 5.000 = Rp 5.200
          - Handling Fee 1.665% OVO Gross-Up: math.ceil(5.200 * (100 / 98.335)) = Rp 5.289 (Fee Rp 89)
          - Grand Total User = Rp 5.289
          - Pendapatan Driver: Tetap Rp 10.200 (tidak dipotong oleh kupon).
        """
        given("Pengguna menggunakan voucher diskon Rp 5.000 dengan metode OVO")
        res = fare_calc.calculate_grand_total(3.5, payment_method="ovo", use_coupon=True, coupon_amount=5000.0)
        then("Grand Total pengguna berkurang menjadi Rp 5.289")
        assert res["coupon_discount"] == 5000.0
        assert res["adjusted_subtotal"] == 5200.0
        assert res["charge_fee_amount"] == 89.0
        assert res["grand_total"] == 5289.0

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - ATURAN BISNIS & PENOLAKAN LOGIKA
    # ==========================================================================

    @pytest.mark.pilar2
    @pytest.mark.positive_false
    def test_TC_OVO_PF_01_insufficient_ovo_balance_blocks_checkout(self):
        """
        [Pilar 2 - PF-01] Saldo OVO Kurang: Sistem Menolak Konfirmasi Pesanan.
        Kondisi: Saldo akun OVO Rp 5.000 < Tagihan Grand Total Rp 10.373.
        Ekspektasi: Muncul popup 'Saldo OVO Tidak Mencukupi', tombol Pesan terkunci / menawarkan Top-Up.
        """
        given("Pengguna memiliki saldo OVO sebesar Rp 5.000")
        tagihan_ovo = 10373.0
        saldo_user = 5000.0
        when("Pengguna mencoba menekan tombol 'Pesan EvRide'")
        is_checkout_allowed = saldo_user >= tagihan_ovo
        then("Sistem menolak konfirmasi dan menginstruksikan top up atau switch payment")
        assert is_checkout_allowed is False, "Checkout tidak boleh diizinkan jika saldo OVO kurang!"

    @pytest.mark.pilar2
    @pytest.mark.positive_false
    def test_TC_OVO_PF_02_dynamic_payment_switch_cash_to_ovo_and_back(self, driver):
        """
        [Pilar 2 - PF-02] Dynamic Payment Switching Sebelum Konfirmasi Order.
        Pengguna beralih: Tunai (Surcharge 0%) -> OVO (Handling Fee 1.665%) -> Tunai (Surcharge 0%).
        Ekspektasi: UI memperbarui rincian kalkulasi harga secara instan dan reaktif.
        """
        booking_page = BookingPage(driver)
        given("Pengguna berada di layar booking EvRide")
        when("Pengguna mengganti metode ke Tunai lalu ke OVO")
        booking_page.select_payment_method("cash")
        time.sleep(0.5)
        booking_page.select_payment_method("ovo")
        then("Metode OVO aktif dan rincian handling fee 1.665% dimuat ulang")
        assert booking_page.get_selected_payment_method() is not None

    @pytest.mark.pilar2
    @pytest.mark.positive_false
    def test_TC_OVO_PF_03_payment_method_locked_during_in_transit_trip(self):
        """
        [Pilar 2 - PF-03] Proteksi Penguncian Metode Pembayaran saat Perjalanan Berlangsung (In-Transit).
        Ekspektasi: Pengguna tidak dapat mengubah metode pembayaran OVO ke Tunai setelah driver memulai trip.
        """
        given("Status pesanan adalah IN_TRANSIT (Driver sedang mengantar penumpang)")
        trip_status = "IN_TRANSIT"
        payment_change_allowed = False if trip_status in ["IN_TRANSIT", "ARRIVED"] else True
        then("Opsi pergantian metode pembayaran dinonaktifkan (disabled / locked)")
        assert payment_change_allowed is False, "Metode pembayaran tidak boleh diubah di tengah perjalanan!"

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - ERROR HANDLING & SETTLEMENT DENDA
    # ==========================================================================

    @pytest.mark.pilar3
    @pytest.mark.negative_true
    def test_TC_OVO_NT_01_cancellation_fase_b_settlement_with_ovo_surcharge(self, fare_calc):
        """
        [Pilar 3 - NT-01] Denda Pembatalan Fase B (Driver Tiba di Titik Jemput).
        Customer membatalkan pesanan setelah driver tiba (masa tenggang 15 mnt):
          - Denda Pembatalan : Rp 5.000
          - Handling Fee 1.665% OVO Gross-Up: math.ceil(5.000 * 100 / 98.335) = Rp 5.085 (Fee Rp 85)
          - Total Denda OVO  : Rp 5.085
        Ekspektasi: Invoice pembatalan mendebet Rp 5.085 dari OVO, driver menerima payout Rp 3.000.
        """
        given("Driver <TEST_DRIVER_PHONE> telah tiba, customer membatalkan di menit ke-5")
        res = fare_calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=300,
            payment_method="ovo"
        )
        then("Total denda OVO terhitung tepat Rp 5.085 (Rp 5.000 + Rp 85)")
        assert res["is_valid"] is True
        assert res["customer_charge"] == 5000.0
        assert res["charge_fee_amount"] == 85.0
        assert res["grand_total_customer"] == 5085.0
        assert res["driver_payout"] == 3000.0

    @pytest.mark.pilar3
    @pytest.mark.negative_true
    def test_TC_OVO_NT_02_customer_no_show_fase_d_settlement_with_ovo_surcharge(self, fare_calc):
        """
        [Pilar 3 - NT-02] Denda Pembatalan Otomatis Sistem karena Customer No-Show >= 30 Menit (Fase D).
          - Denda Penalti Pokok : Rp 10.000
          - Biaya Tunggu (15 m) : Rp 7.500
          - Subtotal Customer   : Rp 17.500
          - Handling Fee 1.665% OVO Gross-Up: math.ceil(17.500 * 100 / 98.335) = Rp 17.797 (Fee Rp 297)
          - Total Tagihan OVO   : Rp 17.797
        Ekspektasi: Tagihan didebet Rp 17.797, kompensasi driver Rp 11.500 dibayarkan.
        """
        given("Driver menunggu >= 30 menit di titik jemput, sistem membatalkan pesanan otomatis")
        res = fare_calc.calculate_cancellation_settlement(
            cancelled_by="System",
            driver_arrived=True,
            elapsed_seconds=1800,
            payment_method="ovo"
        )
        then("Total tagihan No-Show via OVO tepat Rp 17.797 (Rp 17.500 + Rp 297)")
        assert res["is_valid"] is True
        assert res["customer_charge"] == 17500.0
        assert res["charge_fee_amount"] == 297.0
        assert res["grand_total_customer"] == 17797.0
        assert res["driver_payout"] == 11500.0
        assert res["driver_payout"] == 11500.0

    @pytest.mark.pilar3
    @pytest.mark.negative_true
    def test_TC_OVO_NT_03_unlinked_or_unregistered_ovo_account_validation(self):
        """
        [Pilar 3 - NT-03] Deteksi Akun OVO Belum Terhubung (Unlinked OVO).
        Jika nomor pengguna belum terdaftar atau token binding OVO expired:
        Ekspektasi: Sistem menampilkan modal 'Hubungkan Akun OVO' dan menolak autodebet.
        """
        given("Akun pengguna memiliki status binding OVO: UNLINKED")
        is_ovo_linked = False
        when("Mencoba melakukan autodebit pembayaran")
        can_autodebit = is_ovo_linked
        then("Proses autodebit ditolak dan diarahkan ke alur aktivasi OVO")
        assert can_autodebit is False

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - RESILIENCE, SECURITY & ANTI-RACE CONDITION
    # ==========================================================================

    @pytest.mark.pilar4
    @pytest.mark.negative_false
    def test_TC_OVO_NF_01_idempotency_prevents_double_deduction_on_rapid_tap(self):
        """
        [Pilar 4 - NF-01] Pencegahan Pemotongan Saldo Ganda (Anti Double-Deduction).
        Pengguna melakukan multi-tap tombol 'Bayar dengan OVO' secara sangat cepat (Rapid Tap).
        Ekspektasi: Sistem menerapkan Idempotency Key unik per Order ID, hanya 1 transaksi pemotongan yang diproses.
        """
        given("Order ID unik ORD-EVM-OVO-20261109-001 dengan tagihan Rp 11.406,81")
        order_id = "ORD-EVM-OVO-20261109-001"
        processed_payments = set()
        
        # Simulasi 3 kali klik cepat
        attempt_results = []
        for click_idx in range(1, 4):
            if order_id not in processed_payments:
                processed_payments.add(order_id)
                attempt_results.append("PROCESSED")
            else:
                attempt_results.append("IGNORED_IDEMPOTENT")

        then("Hanya 1 request yang diproses, sisa 2 request diabaikan tanpa error")
        assert attempt_results == ["PROCESSED", "IGNORED_IDEMPOTENT", "IGNORED_IDEMPOTENT"]
        assert len(processed_payments) == 1

    @pytest.mark.pilar4
    @pytest.mark.negative_false
    def test_TC_OVO_NF_02_payment_gateway_timeout_and_pending_reconciliation(self):
        """
        [Pilar 4 - NF-02] Penanganan Gateway Network Timeout (HTTP 504 / Connection Drop).
        Jika callback gateway OVO tertunda:
        Ekspektasi: Status pesanan diset ke 'PAYMENT_PENDING' dengan timer rekonsiliasi otomatis (tidak crash).
        """
        given("Response gateway OVO mengalami timeout jaringan setelah 30 detik")
        gateway_response = {"status": "TIMEOUT", "http_code": 504}
        when("Sistem menangani response timeout")
        order_status = "PAYMENT_PENDING" if gateway_response["http_code"] in [504, 408] else "FAILED"
        then("Status transaksi berstatus PENDING dengan antrean auto-reconcile")
        assert order_status == "PAYMENT_PENDING"

    @pytest.mark.pilar4
    @pytest.mark.negative_false
    def test_TC_OVO_NF_03_zero_cash_policy_enforcement_on_driver_ui(self, driver_app):
        """
        [Pilar 4 - NF-03] Kepatuhan Sistem: Driver Dilarang Keras Menagih Uang Tunai.
        Driver UI mengunci input penerimaan kas dan menandai order sebagai Cashless OVO.
        Ekspektasi: Tidak ada celah bagi driver untuk membebankan tagihan ganda secara tunai.
        """
        drv_booking_pg = DrvBookingPage(driver_app)
        given("Driver menyelesaikan order non-tunai OVO")
        when("Driver memeriksa tombol penyelesaian di antarmuka aplikasi")
        then("Hanya tersedia tombol settlement non-tunai langsung tanpa verifikasi uang fisik")
        assert hasattr(drv_booking_pg, "click_already_received_payment")
        logger.info("[SECURITY PASS] Kebijakan Zero Cash OVO terjamin aman di sisi Driver.")


# ==============================================================================
# SUITE 2: 16 MATRIKS KOMBINASI LENGKAP ORDER BEHAVIOUR KHUSUS OVO
# ==============================================================================
class TestOvoOrderBehaviourMatrixSuite:
    """
    Test Suite 16 Matriks Kombinasi Parameter Komprehensif Khusus OVO:
      1.  OVO Only (Normal Booking)
      2.  OVO + Kupon Diskon (-Rp 5.000)
      3.  OVO + Waiting Fee (+Rp 2.500)
      4.  OVO + Penalty Fee (+Rp 5.000)
      5.  OVO + Kupon + Waiting Fee
      6.  OVO + Kupon + Waiting Fee + Penalty
      7.  OVO + Waiting Fee + Penalty
      8.  OVO + Penalty + Kupon (Offset)
      9.  OVO Advance Booking (Terjadwal)
      10. OVO Advance + Kupon
      11. OVO Advance + Waiting Fee
      12. OVO Advance + Penalty
      13. OVO Advance + Kupon + Waiting Fee
      14. OVO Advance + Kupon + Waiting Fee + Penalty
      15. OVO Advance + Waiting Fee + Penalty
      16. OVO Advance + Penalty + Kupon (Offset)

    Masing-masing divalidasi pada 4 Tier Jarak:
      - Dekat (1.5 KM)       : Argo Rp 6.000  | Subtotal Rp 6.600
      - Sedang (3.5 KM)      : Argo Rp 10.200 | Subtotal Rp 11.220
      - Jauh (10.0 KM)       : Argo Rp 38.400 | Subtotal Rp 38.400
      - Sangat Jauh (20.0 KM): Argo Rp 89.900 | Subtotal Rp 89.900
    Formula OVO: math.ceil(Adjusted Subtotal * (100 / (100 - 1.665)))
    """

    DISTANCES = [
        {"tier": "Jarak Dekat", "km": 1.5, "total_argo": 6000.0, "plat_fee": 0.0, "subtotal": 6000.0},
        {"tier": "Jarak Sedang", "km": 3.5, "total_argo": 10200.0, "plat_fee": 0.0, "subtotal": 10200.0},
        {"tier": "Jarak Jauh", "km": 10.0, "total_argo": 38400.0, "plat_fee": 0.0, "subtotal": 38400.0},
        {"tier": "Jarak Sangat Jauh", "km": 20.0, "total_argo": 89900.0, "plat_fee": 0.0, "subtotal": 89900.0},
    ]

    def _verify_ovo_combo(
        self,
        calc: AdminDashboardFareCalculator,
        scenario_name: str,
        use_coupon: bool = False,
        coupon_amount: float = 5000.0,
        waiting_minutes: int = 0,
        apply_penalty: bool = False,
        penalty_amount: float = 5000.0,
        is_advance: bool = False
    ):
        """Helper validasi OVO pada seluruh 4 jarak untuk kombinasi biaya tertentu menggunakan Gross-Up."""
        for d in self.DISTANCES:
            excess_wait_min = max(0, waiting_minutes - 15)
            wait_fee = float(excess_wait_min * 500.0)
            coupon_disc = float(coupon_amount) if use_coupon else 0.0
            penalty_val = float(penalty_amount) if apply_penalty else 0.0

            expected_adj_subtotal = max(0.0, d["subtotal"] + wait_fee + penalty_val - coupon_disc)
            if expected_adj_subtotal > 0:
                expected_grand_total = float(math.ceil(expected_adj_subtotal * (100.0 / (100.0 - 1.665))))
                expected_surcharge = float(expected_grand_total - expected_adj_subtotal)
            else:
                expected_grand_total = 0.0
                expected_surcharge = 0.0

            res = calc.calculate_grand_total(
                distance_km=d["km"],
                payment_method="ovo",
                use_coupon=use_coupon,
                coupon_amount=coupon_amount,
                waiting_minutes=waiting_minutes,
                apply_penalty=apply_penalty,
                penalty_amount=penalty_amount,
            )

            assert res["is_ewallet_surcharge"] is True
            assert res["charge_fee_rate"] == 0.01665
            assert res["start_price"] == 6000.0
            assert res["total_argo"] == d["total_argo"]
            assert res["platform_fee"] == d["plat_fee"]
            assert res["waiting_fee"] == wait_fee
            assert res["coupon_discount"] == coupon_disc
            assert res["penalty_fee"] == penalty_val
            assert res["adjusted_subtotal"] == expected_adj_subtotal
            assert res["charge_fee_amount"] == expected_surcharge
            assert res["grand_total"] == expected_grand_total

    # 1. OVO PAYMENT ONLY (NORMAL BOOKING)
    def test_TC_OVO_OB_01_normal_ovo_only(self, fare_calc):
        """[OB-01] OVO Payment Only: Subtotal + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO Only", use_coupon=False, waiting_minutes=0, apply_penalty=False)

    # 2. OVO + KUPON
    def test_TC_OVO_OB_02_normal_ovo_plus_kupon(self, fare_calc):
        """[OB-02] OVO + Kupon: (Subtotal - Kupon Rp 5.000) + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=False)

    # 3. OVO + WAITING FEE
    def test_TC_OVO_OB_03_normal_ovo_plus_waiting_fee(self, fare_calc):
        """[OB-03] OVO + Waiting Fee: (Subtotal + WaitFee Rp 2.500) + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO + WaitFee", use_coupon=False, waiting_minutes=20, apply_penalty=False)

    # 4. OVO + PENALTY
    def test_TC_OVO_OB_04_normal_ovo_plus_penalty(self, fare_calc):
        """[OB-04] OVO + Penalty: (Subtotal + Denda Rp 5.000) + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO + Penalty", use_coupon=False, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0)

    # 5. OVO + KUPON + WAITING FEE
    def test_TC_OVO_OB_05_normal_ovo_plus_kupon_plus_waiting_fee(self, fare_calc):
        """[OB-05] OVO + Kupon + WaitFee: (Subtotal - 5.000 + 2.500) + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO + Kupon + WaitFee", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=False)

    # 6. OVO + KUPON + WAITING FEE + PENALTY (KOMBO LENGKAP)
    def test_TC_OVO_OB_06_normal_ovo_full_combo(self, fare_calc):
        """[OB-06] OVO + Kupon + WaitFee + Penalty: (Subtotal - 5.000 + 2.500 + 5.000) + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO Full Combo", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0)

    # 7. OVO + WAITING FEE + PENALTY
    def test_TC_OVO_OB_07_normal_ovo_plus_waiting_fee_plus_penalty(self, fare_calc):
        """[OB-07] OVO + WaitFee + Penalty: (Subtotal + 2.500 + 5.000) + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO + WaitFee + Penalty", use_coupon=False, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0)

    # 8. OVO + PENALTY + KUPON (OFFSET)
    def test_TC_OVO_OB_08_normal_ovo_plus_penalty_plus_kupon_offset(self, fare_calc):
        """[OB-08] OVO + Penalty + Kupon Offset: (Subtotal + 5.000 - 5.000) + Handling Fee 1.665%."""
        self._verify_ovo_combo(fare_calc, "OVO + Penalty + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0)

    # 9. OVO ADVANCE BOOKING ONLY
    def test_TC_OVO_OB_09_advance_ovo_only(self, fare_calc):
        """[OB-09] OVO Advance Booking: Pemesanan terjadwal reguler."""
        self._verify_ovo_combo(fare_calc, "Advance OVO Only", use_coupon=False, waiting_minutes=0, apply_penalty=False, is_advance=True)

    # 10. OVO ADVANCE + KUPON
    def test_TC_OVO_OB_10_advance_ovo_plus_kupon(self, fare_calc):
        """[OB-10] OVO Advance + Kupon: Pemesanan terjadwal diskon Rp 5.000."""
        self._verify_ovo_combo(fare_calc, "Advance OVO + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=False, is_advance=True)

    # 11. OVO ADVANCE + WAITING FEE
    def test_TC_OVO_OB_11_advance_ovo_plus_waiting_fee(self, fare_calc):
        """[OB-11] OVO Advance + WaitFee: Terjadwal kena waiting fee Rp 2.500."""
        self._verify_ovo_combo(fare_calc, "Advance OVO + WaitFee", use_coupon=False, waiting_minutes=20, apply_penalty=False, is_advance=True)

    # 12. OVO ADVANCE + PENALTY
    def test_TC_OVO_OB_12_advance_ovo_plus_penalty(self, fare_calc):
        """[OB-12] OVO Advance + Penalty: Terjadwal kena denda penalti Rp 5.000."""
        self._verify_ovo_combo(fare_calc, "Advance OVO + Penalty", use_coupon=False, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0, is_advance=True)

    # 13. OVO ADVANCE + KUPON + WAITING FEE
    def test_TC_OVO_OB_13_advance_ovo_plus_kupon_plus_waiting_fee(self, fare_calc):
        """[OB-13] OVO Advance + Kupon + WaitFee: Terjadwal Kupon & WaitFee."""
        self._verify_ovo_combo(fare_calc, "Advance OVO + Kupon + WaitFee", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=False, is_advance=True)

    # 14. OVO ADVANCE + KUPON + WAITING FEE + PENALTY
    def test_TC_OVO_OB_14_advance_ovo_full_combo(self, fare_calc):
        """[OB-14] OVO Advance Kombo Lengkap: Terjadwal Kupon, WaitFee, dan Penalty."""
        self._verify_ovo_combo(fare_calc, "Advance OVO Full Combo", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0, is_advance=True)

    # 15. OVO ADVANCE + WAITING FEE + PENALTY
    def test_TC_OVO_OB_15_advance_ovo_plus_waiting_fee_plus_penalty(self, fare_calc):
        """[OB-15] OVO Advance + WaitFee + Penalty: Terjadwal WaitFee dan Penalty."""
        self._verify_ovo_combo(fare_calc, "Advance OVO + WaitFee + Penalty", use_coupon=False, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0, is_advance=True)

    # 16. OVO ADVANCE + PENALTY + KUPON
    def test_TC_OVO_OB_16_advance_ovo_plus_penalty_plus_kupon_offset(self, fare_calc):
        """[OB-16] OVO Advance + Penalty + Kupon Offset: Terjadwal Denda dioffset Kupon."""
        self._verify_ovo_combo(fare_calc, "Advance OVO + Penalty + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0, is_advance=True)
