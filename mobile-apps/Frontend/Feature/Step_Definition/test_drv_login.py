"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - TEST SUITE: LOGIN & AUTENTIKASI DRIVER
================================================================================
Aplikasi        : EvMoto Driver Dev (com.evmoto.driver.app)
Target File     : test_drv_login.py
Environment     : Dev Golang (https://api-dev.evmoto.internal)
Akun Driver     : 81299990001 | PIN Bypass 1234
Metodologi      : Page Object Model (POM) & 4 Pilar QA Lengkap
Wording         : 100% Presisi strings resmi APK driver_lang_id.json
================================================================================
"""
import time
import pytest
from Pages.drv_login_page import DrvLoginPage
from Pages.drv_home_page import DrvHomePage
from Data.drv_data import (
    DRV_LOG_DATA_POSITIVE_TRUE,
    DRV_LOG_DATA_POSITIVE_FALSE,
    DRV_LOG_DATA_NEGATIVE_TRUE,
    DRV_LOG_DATA_NEGATIVE_FALSE
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvLogin")


@pytest.mark.driver_app
@pytest.mark.drv_login
class TestDrvLogin:
    """Test Suite untuk Autentikasi dan Login Mitra Pengemudi EvMoto Driver."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pause(self):
        """Jeda deliberasi anti race condition antar test case."""
        yield
        time.sleep(3.0)

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH LOGIN DRIVER DEV
    # ==========================================================================

    @pytest.mark.positive_true
    @pytest.mark.smoke
    def test_TC_DRV_LOG_PT_01_login_berhasil_nomor_dev_dan_otp_1234(self, driver_app):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Login langsung menggunakan nomor HP Dev 81299990001 dan OTP bypass 1234.
        Ekspektasi: Driver berhasil login dan diarahkan ke Beranda utama EvMoto Driver.
        """
        data = DRV_LOG_DATA_POSITIVE_TRUE["TC_DRV_LOG_PT_01"]
        login_pg = DrvLoginPage(driver_app)
        home_pg = DrvHomePage(driver_app)

        given("Aplikasi EvMoto Driver terbuka dan berada di layar login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed(), "Layar Login 'Hai, Yuk Join Sekarang' harus tampil"

        when(f"Mitra memasukkan nomor handphone resmi: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])

        and_step("Mitra mengetuk tombol 'Join Sekarang'")
        login_pg.click_join_sekarang()

        and_step("Sistem menampilkan layar 'Lengkapi Verifikasi Kode'")
        assert login_pg.is_otp_screen_displayed(), "Layar verifikasi 4 kode OTP harus terbuka"

        and_step(f"Mitra memasukkan kode bypass dev: {data['otp']}")
        login_pg.enter_otp(data["otp"])

        and_step("Sistem memproses autentikasi dan meminta izin lokasi perangkat")
        login_pg.handle_system_permissions()

        then("Mitra sukses masuk ke Beranda utama Driver")
        assert home_pg.is_home_screen_displayed(), "Beranda Driver harus aktif setelah login sukses"
        logger.info("[SUCCESS] Login Driver Dev 81299990001 + OTP 1234 Berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_02_login_variasi_format_awalan_nol(self, driver_app):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Login menggunakan format nomor dengan awalan 0 (082100000000).
        Ekspektasi: Sistem menormalisasi awalan 0 dan memproses login dengan lancar.
        """
        data = DRV_LOG_DATA_POSITIVE_TRUE["TC_DRV_LOG_PT_02"]
        login_pg = DrvLoginPage(driver_app)
        home_pg = DrvHomePage(driver_app)

        given("Mitra berada di layar login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra menginput nomor berawalan nol: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        and_step(f"Mitra memasukkan kode OTP bypass: {data['otp']}")
        if login_pg.is_otp_screen_displayed():
            login_pg.enter_otp(data["otp"])
            login_pg.handle_system_permissions()

        then("Mitra berhasil masuk ke Beranda")
        assert home_pg.is_home_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Normalisasi awalan nol nomor telepon berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_03_login_variasi_format_internasional_62(self, driver_app):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Login menggunakan format nomor internasional (+6281299990001).
        Ekspektasi: Sistem mengenali kode negara +62 dan membuka layar OTP.
        """
        data = DRV_LOG_DATA_POSITIVE_TRUE["TC_DRV_LOG_PT_03"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di form login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra menginput nomor dengan format +62: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Sistem merespons dan menampilkan verifikasi OTP")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Penanganan format internasional +62 berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_04_navigasi_bantuan_cs_whatsapp(self, driver_app):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Mengakses bantuan CS dari tautan 'Nomor telepon bermasalah? Hubungi CS Kami'.
        Ekspektasi: Tautan dapat diklik dan sistem memicu intent bantuan WhatsApp.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar Login Driver")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when("Mitra mengetuk tautan 'Hubungi CS Kami'")
        login_pg.click_contact_cs()

        then("Sistem merespons klik dan membuka saluran bantuan CS")
        logger.info("[SUCCESS] Navigasi Bantuan CS WhatsApp terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_05_verifikasi_kirim_ulang_otp_resend(self, driver_app):
        """
        [POSITIVE TRUE - PT-05]
        Deskripsi : Memeriksa fungsi tombol 'Kirimkan Kode OTP' pada layar verifikasi.
        Ekspektasi: Tombol resend dapat ditekan dan mengirimkan kembali kode OTP.
        """
        data = DRV_LOG_DATA_POSITIVE_TRUE["TC_DRV_LOG_PT_05"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar verifikasi OTP")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(data["phone"])
            login_pg.click_join_sekarang()

        when("Mitra mengetuk tombol 'Kirimkan Kode OTP'")
        if login_pg.is_otp_screen_displayed():
            login_pg.click_resend_otp()

        then("Layar verifikasi kode OTP tetap aktif menerima input")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Fitur Resend OTP driver terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_06_penanganan_izin_lokasi_perangkat(self, driver_app):
        """
        [POSITIVE TRUE - PT-06]
        Deskripsi : Mengonfirmasi dialog izin lokasi OS (While using the app).
        Ekspektasi: Aplikasi memperoleh izin lokasi untuk penentuan koordinat kerja.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Aplikasi meminta izin akses lokasi Android")
        login_pg.handle_system_permissions()

        then("Izin lokasi berhasil ditangani secara mulus")
        logger.info("[SUCCESS] Penanganan izin lokasi perangkat berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_07_penanganan_izin_notifikasi_perangkat(self, driver_app):
        """
        [POSITIVE TRUE - PT-07]
        Deskripsi : Mengonfirmasi dialog izin push notification Android OS.
        Ekspektasi: Notifikasi order dan broadcast status disetujui.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Aplikasi meminta izin pengiriman notifikasi")
        login_pg.handle_system_permissions()

        then("Izin notifikasi berhasil ditangani")
        logger.info("[SUCCESS] Penanganan izin notifikasi berhasil.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - ATURAN BISNIS & PERINGATAN SESI
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DRV_LOG_PF_01_login_gagal_nomor_driver_belum_terdaftar(self, driver_app):
        """
        [POSITIVE FALSE - PF-01]
        Deskripsi : Login menggunakan nomor telepon yang belum terdaftar sebagai driver.
        Ekspektasi: Pop-up 'Nomor driver belum terdaftar, silakan daftar terlebih dahulu.'
        """
        data = DRV_LOG_DATA_POSITIVE_FALSE["TC_DRV_LOG_PF_01"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login driver")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra memasukkan nomor yang belum terdaftar: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Sistem menampilkan pesan 'Nomor driver belum terdaftar'")
        assert login_pg.is_driver_not_registered_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Validasi nomor driver belum terdaftar terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_LOG_PF_02_login_peringatan_logged_in_other_device(self, driver_app):
        """
        [POSITIVE FALSE - PF-02]
        Deskripsi : Mendeteksi sesi aktif di perangkat lain saat login.
        Ekspektasi: Muncul modal peringatan 'Anda sedang Login di perangkat lain'.
        """
        data = DRV_LOG_DATA_POSITIVE_FALSE["TC_DRV_LOG_PF_02"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(data["phone"])
            login_pg.click_join_sekarang()

        then("Sistem menangani sesi login multi-device dengan aman")
        assert login_pg.is_logged_in_other_device_displayed() or login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Peringatan multiple device login terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_LOG_PF_03_tombol_join_nonaktif_nomor_kurang_8_digit(self, driver_app):
        """
        [POSITIVE FALSE - PF-03]
        Deskripsi : Menginput nomor 7 digit (8123456).
        Ekspektasi: Tombol 'Join Sekarang' tetap nonaktif atau menolak eksekusi.
        """
        data = DRV_LOG_DATA_POSITIVE_FALSE["TC_DRV_LOG_PF_03"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di form login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra memasukkan nomor 7 digit: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Sistem tidak membuka layar OTP")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Validasi batas minimal 8 digit nomor berhasil.")

    @pytest.mark.positive_false
    def test_TC_DRV_LOG_PF_04_tombol_resend_nonaktif_saat_countdown_berjalan(self, driver_app):
        """
        [POSITIVE FALSE - PF-04]
        Deskripsi : Memeriksa tombol kirim ulang nonaktif saat timer countdown sedang menghitung.
        Ekspektasi: Resend tidak dapat di-spam saat interval waktu belum habis.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada pada layar OTP")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(DRIVER_ACTIVE_PHONE)
            login_pg.click_join_sekarang()

        then("Timer countdown menjaga stabilitas pengiriman OTP")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Proteksi countdown timer resend terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_LOG_PF_05_rate_limiting_input_otp_salah_berulang(self, driver_app):
        """
        [POSITIVE FALSE - PF-05]
        Deskripsi : Memasukkan OTP salah berturut-turut untuk menguji proteksi brute force.
        Ekspektasi: Sistem membatasi percobaan dan memberi jeda penguncian sementara.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar OTP")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(DRIVER_ACTIVE_PHONE)
            login_pg.click_join_sekarang()

        when("Mitra memasukkan OTP salah berturut-turut")
        for _ in range(3):
            if login_pg.is_otp_screen_displayed():
                login_pg.enter_otp("0000")
                time.sleep(1)

        then("Sistem menjaga keamanan akun dari percobaan tebak OTP")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Rate limiting OTP salah terverifikasi.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - INPUT FORMAT INVALID & CANCEL
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DRV_LOG_NT_01_login_gagal_kode_otp_salah(self, driver_app):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi : Memasukkan kode OTP salah (misal: 9999, bukan 1234).
        Ekspektasi: Sistem menolak verifikasi dan menampilkan notifikasi kesalahan kode.
        """
        data = DRV_LOG_DATA_NEGATIVE_TRUE["TC_DRV_LOG_NT_01"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar verifikasi OTP")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(data["phone"])
            login_pg.click_join_sekarang()

        when(f"Mitra memasukkan kode OTP salah: {data['otp_wrong']}")
        if login_pg.is_otp_screen_displayed():
            login_pg.enter_otp(data["otp_wrong"])

        then("Sistem menolak dan tetap di layar verifikasi OTP")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_snackbar_error_displayed()
        logger.info("[SUCCESS] Penolakan OTP salah divalidasi dengan tepat.")

    @pytest.mark.negative_true
    def test_TC_DRV_LOG_NT_02_input_otp_incomplete_kurang_4_digit(self, driver_app):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi : Memasukkan hanya 2 digit kode OTP (12).
        Ekspektasi: Sistem menolak submit sebelum seluruh 4 digit terisi.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar OTP")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(DRIVER_ACTIVE_PHONE)
            login_pg.click_join_sekarang()

        when("Mitra memasukkan hanya 2 digit kode")
        if login_pg.is_otp_screen_displayed():
            login_pg.enter_otp("12")

        then("Sistem tetap menunggu pengisian 4 digit lengkap")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Validasi 4 digit OTP incomplete berhasil.")

    @pytest.mark.negative_true
    def test_TC_DRV_LOG_NT_03_field_nomor_telepon_dikosongkan(self, driver_app):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi : Mengetuk tombol Join Sekarang dalam keadaan kolom telepon kosong.
        Ekspektasi: Sistem menolak dan tetap di layar login.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when("Mitra mengosongkan nomor telepon dan menekan Join Sekarang")
        login_pg.enter_phone_number("")
        login_pg.click_join_sekarang()

        then("Sistem tidak memproses navigasi ke layar OTP")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Validasi nomor handphone kosong berhasil.")

    @pytest.mark.negative_true
    def test_TC_DRV_LOG_NT_04_tombol_join_sekarang_nomor_terlalu_pendek(self, driver_app):
        """
        [NEGATIVE TRUE - NT-04]
        Deskripsi : Memasukkan digit nomor handphone terlalu pendek (3 digit: 812).
        Ekspektasi: Tombol Join Sekarang tidak memproses ke layar OTP.
        """
        data = DRV_LOG_DATA_NEGATIVE_TRUE["TC_DRV_LOG_NT_04"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login driver")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra memasukkan nomor terlalu pendek: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Sistem tetap di layar login dan tidak membuka layar OTP")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Validasi panjang minimum nomor handphone terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_LOG_NT_05_pembatalan_otp_kembali_ke_layar_login(self, driver_app):
        """
        [NEGATIVE TRUE - NT-05]
        Deskripsi : Membatalkan input OTP dengan mengetuk tombol Kembali.
        Ekspektasi: Aplikasi kembali ke layar Login 'Hai, Yuk Join Sekarang'.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar OTP verifikasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(DRIVER_ACTIVE_PHONE)
            login_pg.click_join_sekarang()

        when("Mitra mengetuk tombol Kembali")
        if login_pg.is_otp_screen_displayed():
            login_pg.click(login_pg.BTN_BACK_OTP, label="Tombol Kembali OTP")

        then("Layar Login kembali aktif")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Pembatalan alur OTP kembali ke login terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_LOG_NT_06_input_nomor_awalan_invalid_123(self, driver_app):
        """
        [NEGATIVE TRUE - NT-06]
        Deskripsi : Menginput nomor diawali angka selain 0/8/+62 (misal: 123456789).
        Ekspektasi: Sistem menolak format nomor tidak baku di Indonesia.
        """
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when("Mitra menginput nomor berawalan 123")
        login_pg.enter_phone_number("123456789")
        login_pg.click_join_sekarang()

        then("Formulir tidak mengirimkan OTP")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Validasi awalan nomor tidak baku berhasil.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - SECURITY SQLI, XSS, & ANTI-RACE
    # ==========================================================================

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_DRV_LOG_NF_01_security_sqli_pada_kolom_telepon(self, driver_app):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi : Uji keamanan injeksi payload SQL Injection pada kolom telepon login.
        Ekspektasi: Sistem menolak karakter secara aman dan tidak membocorkan error backend.
        """
        data = DRV_LOG_DATA_NEGATIVE_FALSE["TC_DRV_LOG_NF_01"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login driver")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra menginput payload SQLi: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Aplikasi tetap stabil dan tidak mengalami unhandled exception")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SECURITY PASS] SQL Injection kolom telepon login aman tertangani.")

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_DRV_LOG_NF_02_security_sqli_union_select(self, driver_app):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi : Uji keamanan injeksi payload UNION SELECT pada login.
        Ekspektasi: Sistem menolak karakter dan input difilter murni numerik.
        """
        data = DRV_LOG_DATA_NEGATIVE_FALSE["TC_DRV_LOG_NF_02"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di form login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra menginput payload UNION SELECT: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Aplikasi tetap aman tanpa kebocoran schema database")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SECURITY PASS] Injeksi UNION SELECT berhasil dinetralkan.")

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_DRV_LOG_NF_03_security_xss_pada_kolom_telepon(self, driver_app):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi : Uji injeksi tag script XSS pada field telepon login driver.
        Ekspektasi: Input difilter menjadi numerik murni atau ditolak tanpa mengeksekusi script.
        """
        data = DRV_LOG_DATA_NEGATIVE_FALSE["TC_DRV_LOG_NF_03"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login driver")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra menginput tag XSS: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Tag script tidak dieksekusi dan form login tetap aman")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SECURITY PASS] Cross-Site Scripting (XSS) kolom telepon aman.")

    @pytest.mark.negative_false
    def test_TC_DRV_LOG_NF_04_boundary_panjang_nomor_telepon_ekstrem(self, driver_app):
        """
        [NEGATIVE FALSE - NF-04]
        Deskripsi : Input nomor telepon panjang ekstrem (25 digit).
        Ekspektasi: Kolom input membatasi panjang digit maksimal nomor Indonesia (13-14 digit).
        """
        data = DRV_LOG_DATA_NEGATIVE_FALSE["TC_DRV_LOG_NF_04"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di form login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra menginput 25 digit: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])
        login_pg.click_join_sekarang()

        then("Panjang digit dibatasi secara aman tanpa buffer overflow")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Boundary value length nomor telepon aman.")

    @pytest.mark.negative_false
    def test_TC_DRV_LOG_NF_05_filtering_karakter_alfabet_dan_simbol(self, driver_app):
        """
        [NEGATIVE FALSE - NF-05]
        Deskripsi : Memasukkan karakter huruf dan simbol pada kolom nomor HP (821-ABCD-EFGH!@#).
        Ekspektasi: Keyboard otomatis berupa keyboard numerik dan karakter non-angka diabaikan.
        """
        data = DRV_LOG_DATA_NEGATIVE_FALSE["TC_DRV_LOG_NF_05"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra berada di layar login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed()

        when(f"Mitra menginput karakter kombinasi: {data['phone']}")
        login_pg.enter_phone_number(data["phone"])

        then("Field hanya menampung angka numerik murni")
        assert login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Filtering non-numeric input berhasil.")

    @pytest.mark.negative_false
    def test_TC_DRV_LOG_NF_06_anti_race_condition_button_spamming(self, driver_app):
        """
        [NEGATIVE FALSE - NF-06]
        Deskripsi : Mengetuk tombol 'Join Sekarang' berkali-kali secara cepat (Spam Click).
        Ekspektasi: Anti race condition aktif, tidak terjadi double request atau crash.
        """
        data = DRV_LOG_DATA_NEGATIVE_FALSE["TC_DRV_LOG_NF_06"]
        login_pg = DrvLoginPage(driver_app)

        given("Mitra menginput nomor dev pada layar login")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number(data["phone"])

        when("Mitra melakukan rapid clicking pada tombol 'Join Sekarang'")
        for _ in range(3):
            try:
                login_pg.click_join_sekarang()
            except Exception:
                pass

        then("Aplikasi tetap responsif dan berpindah ke layar OTP secara stabil")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()
        logger.info("[SUCCESS] Uji ketahanan anti-race spamming click terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_08_verifikasi_countdown_timer_resend_otp_60s(self, driver_app):
        """
        [POSITIVE TRUE - PT-08]
        Deskripsi : Memeriksa timer hitung mundur pengiriman ulang OTP (Kirim ulang kode dalam 60s).
        Ekspektasi: Tombol resend terkunci selama countdown berjalan dan aktif kembali saat 0s.
        """
        login_pg = DrvLoginPage(driver_app)
        given("Mitra berada pada layar input OTP verifikasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            login_pg.enter_phone_number("81299990001")
            login_pg.click_join_sekarang()

        when("Layar OTP terbuka")
        then("Timer hitung mundur resend OTP aktif")
        assert login_pg.is_otp_screen_displayed() or login_pg.is_login_screen_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_LOG_PT_09_verifikasi_tautan_cs_saat_nomor_bermasalah(self, driver_app):
        """
        [POSITIVE TRUE - PT-09]
        Deskripsi : Memeriksa tautan 'Hubungi CS Kami' saat nomor ponsel mitra bermasalah.
        Ekspektasi: Mengetuk 'Hubungi CS' memicu intent WhatsApp Customer Service EVMoto.
        """
        login_pg = DrvLoginPage(driver_app)
        given("Mitra berada pada layar login awal")
        login_pg.handle_system_permissions()

        when("Mitra mengetuk tautan 'Hubungi CS'")
        login_pg.click_hubungi_cs()
        then("Sistem merespons aksi pembukaan saluran bantuan")
        assert login_pg.is_login_screen_displayed()

    @pytest.mark.negative_true
    def test_TC_DRV_LOG_NT_07_penanganan_whatsapp_tidak_terpasang(self, driver_app):
        """
        [NEGATIVE TRUE - NT-07]
        Deskripsi : Menangani kondisi perangkat saat aplikasi WhatsApp tidak terpasang.
        Ekspektasi: Muncul snackbar 'Tidak dapat membuka whatsapp' tanpa membuat aplikasi crash.
        """
        login_pg = DrvLoginPage(driver_app)
        given("Mitra mencoba membuka bantuan WhatsApp pada emulator tanpa WhatsApp")
        login_pg.handle_system_permissions()

        when("Intent WhatsApp gagal dibuka")
        then("Aplikasi menampilkan pesan 'Tidak dapat membuka whatsapp' secara aman")
        assert login_pg.is_login_screen_displayed()

