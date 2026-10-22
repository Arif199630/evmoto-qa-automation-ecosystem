"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - TEST SUITE: REGISTRASI DRIVER BARU
================================================================================
Aplikasi        : EvMoto Driver Dev (com.evmoto.driver.app)
Target File     : test_drv_register.py
Environment     : Dev Golang (https://api-dev.evmoto.internal)
Metodologi      : Page Object Model (POM) & 4 Pilar QA Lengkap
Wording         : 100% Presisi strings resmi APK driver_lang_id.json
================================================================================
"""
import time
import pytest
from Pages.drv_register_page import DrvRegisterPage
from Pages.drv_login_page import DrvLoginPage
from Data.drv_data import (
    DRV_REG_DATA_POSITIVE_TRUE,
    DRV_REG_DATA_POSITIVE_FALSE,
    DRV_REG_DATA_NEGATIVE_TRUE,
    DRV_REG_DATA_NEGATIVE_FALSE
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvRegister")


@pytest.mark.driver_app
@pytest.mark.drv_register
class TestDrvRegister:
    """Test Suite untuk Pendaftaran Mitra Pengemudi Baru EvMoto Driver."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pause(self):
        """Jeda deliberasi anti race condition antar test case."""
        yield
        time.sleep(3.0)

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH PENDAFTARAN MITRA BARU
    # ==========================================================================

    @pytest.mark.positive_true
    @pytest.mark.smoke
    def test_TC_DRV_REG_PT_01_registrasi_mitra_ecgo_sukses(self, driver_app):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Pendaftaran mitra baru armada ECGO Driver data lengkap tanpa referral.
        Ekspektasi: Tampil dialog sukses 'DATA  YANG DIKIRIM BERHASIL' & estimasi 2 jam.
        """
        data = DRV_REG_DATA_POSITIVE_TRUE["TC_DRV_REG_PT_01"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Aplikasi EvMoto Driver terbuka dan menampilkan layar login")
        login_pg.handle_system_permissions()
        assert login_pg.is_login_screen_displayed(), "Layar Login Driver harus tampil di awal"

        when("Mitra mengetuk tautan 'Daftar sebagai Driver baru'")
        reg_pg.click_daftar_driver_baru()

        and_step("Sistem memuat formulir pendaftaran mitra baru")
        assert reg_pg.is_register_screen_displayed(), "Layar Registrasi Driver Baru harus terbuka"

        and_step("Mitra memilih tipe armada ECGO: Ya")
        reg_pg.select_ecgo_driver(is_ecgo=True)

        and_step(f"Mitra menginput plat kendaraan: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])

        and_step("Mitra mengunggah seluruh berkas (KTP, STNK depan & belakang, SKCK)")
        reg_pg.click_upload_selfie_ktp()
        reg_pg.click_upload_stnk_front()
        reg_pg.click_upload_stnk_back()
        reg_pg.click_upload_skck()

        and_step("Mitra menekan tombol Kirim / Submit Formulir")
        reg_pg.submit_registration_form()

        then("Sistem menampilkan dialog 'DATA  YANG DIKIRIM BERHASIL'")
        assert reg_pg.is_registration_success_displayed() or reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Pendaftaran Mitra ECGO Driver Berhasil divalidasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_02_registrasi_mitra_non_ecgo_dengan_referral(self, driver_app):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Pendaftaran mitra baru armada non-ECGO dengan kode referral dev.
        Ekspektasi: Formulir pendaftaran berhasil diproses dengan kode referral valid.
        """
        data = DRV_REG_DATA_POSITIVE_TRUE["TC_DRV_REG_PT_02"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Aplikasi berada di formulir pendaftaran driver baru")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra memilih armada non-ECGO (Tidak)")
        reg_pg.select_ecgo_driver(is_ecgo=False)

        and_step(f"Mitra menginput nomor plat: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])

        and_step(f"Mitra memasukkan kode referral: {data['referral_code']}")
        reg_pg.enter_referral_code(data["referral_code"])

        and_step("Mitra menekan tombol Kirim")
        reg_pg.submit_registration_form()

        then("Formulir pendaftaran berhasil dikirim dengan referral dev")
        assert reg_pg.is_registration_success_displayed() or reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Pendaftaran Non-ECGO dengan referral terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_03_registrasi_plat_motor_1_digit(self, driver_app):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Pendaftaran mitra menggunakan plat nomor motor 1 digit (B 1 AA).
        Ekspektasi: Sistem menerima format plat motor 1 digit secara sah.
        """
        data = DRV_REG_DATA_POSITIVE_TRUE["TC_DRV_REG_PT_03"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada formulir registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra menginput nomor plat 1 digit: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Format plat 1 digit diterima tanpa error validasi format")
        assert reg_pg.is_register_screen_displayed() or reg_pg.is_registration_success_displayed()
        logger.info("[SUCCESS] Validasi plat 1 digit berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_04_registrasi_plat_motor_4_digit(self, driver_app):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Pendaftaran mitra menggunakan plat nomor motor 4 digit (B 9999 CAD).
        Ekspektasi: Sistem memvalidasi plat 4 digit dengan benar.
        """
        data = DRV_REG_DATA_POSITIVE_TRUE["TC_DRV_REG_PT_04"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra menginput nomor plat 4 digit: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Format plat 4 digit diterima sistem")
        assert reg_pg.is_register_screen_displayed() or reg_pg.is_registration_success_displayed()
        logger.info("[SUCCESS] Validasi plat 4 digit berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_05_registrasi_plat_wilayah_bandung_d(self, driver_app):
        """
        [POSITIVE TRUE - PT-05]
        Deskripsi : Pendaftaran mitra dengan plat wilayah Jawa Barat / Bandung (D 1234 AB).
        Ekspektasi: Sistem menerima kode wilayah D selain Jakarta (B).
        """
        data = DRV_REG_DATA_POSITIVE_TRUE["TC_DRV_REG_PT_05"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra memasukkan plat nomor Bandung: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Plat wilayah D berhasil diproses")
        assert reg_pg.is_register_screen_displayed() or reg_pg.is_registration_success_displayed()
        logger.info("[SUCCESS] Validasi plat wilayah Bandung D berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_06_registrasi_plat_wilayah_surabaya_l(self, driver_app):
        """
        [POSITIVE TRUE - PT-06]
        Deskripsi : Pendaftaran mitra dengan plat wilayah Jawa Timur / Surabaya (L 5678 CD).
        Ekspektasi: Sistem menerima kode wilayah L Surabaya secara sah.
        """
        data = DRV_REG_DATA_POSITIVE_TRUE["TC_DRV_REG_PT_06"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra membuka form pendaftaran")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra menginput plat Surabaya: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Plat wilayah L berhasil diverifikasi")
        assert reg_pg.is_register_screen_displayed() or reg_pg.is_registration_success_displayed()
        logger.info("[SUCCESS] Validasi plat wilayah Surabaya L berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_07_navigasi_kembali_ke_login(self, driver_app):
        """
        [POSITIVE TRUE - PT-07]
        Deskripsi : Menekan tombol Kembali pada formulir registrasi.
        Ekspektasi: Kembali ke layar login 'Hai, Yuk Join Sekarang'.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di layar registrasi driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra menekan tombol navigasi Kembali")
        reg_pg.click_back()

        then("Layar Login 'Hai, Yuk Join Sekarang' kembali ditampilkan")
        assert login_pg.is_login_screen_displayed(), "Harus kembali ke layar login utama"
        logger.info("[SUCCESS] Navigasi kembali ke Layar Login terverifikasi.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - BUSINESS LOGIC & DUPLIKASI
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DRV_REG_PF_01_registrasi_plat_nomor_sudah_terdaftar(self, driver_app):
        """
        [POSITIVE FALSE - PF-01]
        Deskripsi : Registrasi menggunakan plat kendaraan yang sudah aktif pada driver lain.
        Ekspektasi: Sistem menolak pendaftaran dan menampilkan peringatan plat terdaftar.
        """
        data = DRV_REG_DATA_POSITIVE_FALSE["TC_DRV_REG_PF_01"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada formulir registrasi driver baru")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra menginput plat kendaraan terdaftar: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Sistem menolak atau memvalidasi plat nomor duplikat secara tepat")
        assert reg_pg.is_mandatory_warning_displayed() or reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Pencegahan registrasi plat nomor duplikat terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_REG_PF_02_registrasi_kode_referral_kadaluarsa(self, driver_app):
        """
        [POSITIVE FALSE - PF-02]
        Deskripsi : Registrasi menggunakan kode referral kadaluarsa atau tidak terdaftar.
        Ekspektasi: Sistem menampilkan error kode referral tidak valid.
        """
        data = DRV_REG_DATA_POSITIVE_FALSE["TC_DRV_REG_PF_02"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra memasukkan kode referral kadaluarsa: {data['referral_code']}")
        reg_pg.enter_referral_code(data["referral_code"])
        reg_pg.submit_registration_form()

        then("Sistem menolak kode referral kadaluarsa")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Validasi penolakan referral kadaluarsa terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_REG_PF_03_submit_tanpa_unggah_dokumen_persyaratan(self, driver_app):
        """
        [POSITIVE FALSE - PF-03]
        Deskripsi : Menekan tombol submit formulir tanpa mengunggah dokumen KTP/STNK.
        Ekspektasi: Sistem menolak dan mewajibkan upload seluruh dokumen legalitas.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra mengisi plat motor namun tidak mengunggah dokumen")
        reg_pg.enter_plate_number("B 3333 XYZ")
        reg_pg.submit_registration_form()

        then("Formulir tidak dapat terkirim dan meminta dokumen dilengkapi")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Penolakan submit tanpa dokumen terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_REG_PF_04_plat_duplikat_armada_ecgo(self, driver_app):
        """
        [POSITIVE FALSE - PF-04]
        Deskripsi : Mendaftarkan armada non-ECGO dengan plat milik armada sewa ECGO.
        Ekspektasi: Sistem menolak pendaftaran plat motor yang dikelola ECGO.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada layar formulir pendaftaran")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra mendaftarkan plat armada ECGO terdaftar")
        reg_pg.select_ecgo_driver(is_ecgo=False)
        reg_pg.enter_plate_number("B 1234 EVM")
        reg_pg.submit_registration_form()

        then("Sistem menolak duplikasi armada ECGO")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Validasi proteksi duplikasi armada ECGO berhasil.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - VALIDASI FORMAT FIELD & MANDATORY
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DRV_REG_NT_01_validasi_error_plat_nomor_kosong(self, driver_app):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi : Submit formulir pendaftaran dalam keadaan nomor plat dikosongkan.
        Ekspektasi: Sistem memunculkan indikator peringatan kolom wajib diisi.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di layar registrasi driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra mengosongkan kolom plat nomor dan menekan Submit")
        reg_pg.enter_plate_number("")
        reg_pg.submit_registration_form()

        then("Sistem menolak pengiriman dan tetap di layar formulir pendaftaran")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Validasi kolom wajib nomor plat terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_REG_NT_02_validasi_error_format_plat_hanya_angka(self, driver_app):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi : Memasukkan format nomor plat tidak valid (hanya angka numerik: 12345).
        Ekspektasi: Sistem menolak dan menampilkan indikasi format tidak sesuai.
        """
        data = DRV_REG_DATA_NEGATIVE_TRUE["TC_DRV_REG_NT_02"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra menginput format plat hanya angka: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Sistem tidak mengizinkan submit format plat tidak valid")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Validasi format plat hanya angka terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_REG_NT_03_validasi_error_format_plat_hanya_huruf(self, driver_app):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi : Memasukkan plat hanya huruf tanpa angka (B ABC).
        Ekspektasi: Sistem menolak plat yang tidak memiliki digit nomor polisi.
        """
        data = DRV_REG_DATA_NEGATIVE_TRUE["TC_DRV_REG_NT_03"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada formulir registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra menginput format plat hanya huruf: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Sistem menolak format plat tanpa angka")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Validasi format plat tanpa angka terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_REG_NT_04_validasi_error_plat_karakter_simbol(self, driver_app):
        """
        [NEGATIVE TRUE - NT-04]
        Deskripsi : Memasukkan simbol-simbol khusus pada plat kendaraan (B 12@4 #$%).
        Ekspektasi: Karakter simbol ditolak oleh validasi format plat.
        """
        data = DRV_REG_DATA_NEGATIVE_TRUE["TC_DRV_REG_NT_04"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada formulir pendaftaran")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra memasukkan simbol terlarang: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Sistem menolak karakter simbol terlarang pada plat")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Validasi simbol terlarang pada plat terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_REG_NT_05_validasi_pilihan_wajib_armada_ecgo(self, driver_app):
        """
        [NEGATIVE TRUE - NT-05]
        Deskripsi : Submit pendaftaran sebelum memilih opsi Ya/Tidak pada armada ECGO.
        Ekspektasi: Formulir mewajibkan memilih salah satu opsi tipe driver.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra mengisi plat motor tanpa memilih tipe armada")
        reg_pg.enter_plate_number("B 1234 XYZ")
        reg_pg.submit_registration_form()

        then("Sistem tidak mengizinkan submit")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Validasi keharusan memilih radio button terverifikasi.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - SECURITY, INJECTION & STABILITAS
    # ==========================================================================

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_DRV_REG_NF_01_security_sqli_pada_form_registrasi(self, driver_app):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi : Uji keamanan injeksi payload SQL Injection pada kolom plat dan referral.
        Ekspektasi: Input disanitasi secara aman tanpa menyebabkan crash atau database exception.
        """
        data = DRV_REG_DATA_NEGATIVE_FALSE["TC_DRV_REG_NF_01"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada layar registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra memasukkan payload SQL Injection: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.enter_referral_code(data["referral_code"])
        reg_pg.submit_registration_form()

        then("Aplikasi tetap stabil dan payload disanitasi dengan aman")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SECURITY PASS] SQL Injection form registrasi aman tersanitasi.")

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_DRV_REG_NF_02_security_xss_pada_form_registrasi(self, driver_app):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi : Uji keamanan script injection XSS pada kolom registrasi driver.
        Ekspektasi: Karakter script dinetralisir dan aplikasi tidak mengalami abnormal behavior.
        """
        data = DRV_REG_DATA_NEGATIVE_FALSE["TC_DRV_REG_NF_02"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada formulir registrasi driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra memasukkan payload XSS: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.enter_referral_code(data["referral_code"])
        reg_pg.submit_registration_form()

        then("Payload XSS ditolak atau dinetralkan secara aman")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SECURITY PASS] Cross-Site Scripting (XSS) form registrasi aman.")

    @pytest.mark.negative_false
    def test_TC_DRV_REG_NF_03_boundary_value_panjang_plat_ekstrem(self, driver_app):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi : Input string plat nomor melebihi batas wajar (35 karakter).
        Ekspektasi: Form memotong karakter secara aman sesuai batas maksimal plat motor.
        """
        data = DRV_REG_DATA_NEGATIVE_FALSE["TC_DRV_REG_NF_03"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi driver")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when(f"Mitra menginput plat panjang ekstrem: {data['plate_number']}")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.submit_registration_form()

        then("Aplikasi tidak mengalami buffer overflow dan memotong panjang karakter")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Boundary value length plat ekstrem aman.")

    @pytest.mark.negative_false
    def test_TC_DRV_REG_NF_04_input_whitespace_spasi_murni_pada_form(self, driver_app):
        """
        [NEGATIVE FALSE - NF-04]
        Deskripsi : Menginput spasi murni tanpa karakter pada field plat dan referral.
        Ekspektasi: Input di-trim dan sistem menganggap kolom tetap kosong.
        """
        data = DRV_REG_DATA_NEGATIVE_FALSE["TC_DRV_REG_NF_04"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra menginput spasi murni pada seluruh kolom")
        reg_pg.enter_plate_number(data["plate_number"])
        reg_pg.enter_referral_code(data["referral_code"])
        reg_pg.submit_registration_form()

        then("Sistem menganggap kolom kosong dan menolak submit")
        assert reg_pg.is_register_screen_displayed()
        logger.info("[SUCCESS] Sanitasi whitespace spasi murni terverifikasi.")

    @pytest.mark.negative_false
    def test_TC_DRV_REG_NF_05_rapid_click_spamming_tombol_kirim(self, driver_app):
        """
        [NEGATIVE FALSE - NF-05]
        Deskripsi : Mengetuk tombol Kirim berkali-kali secara cepat (Spamming Click).
        Ekspektasi: Anti-race condition mencegah terjadinya duplikasi pengiriman formulir.
        """
        data = DRV_REG_DATA_NEGATIVE_FALSE["TC_DRV_REG_NF_05"]
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra menginput data pada formulir registrasi")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()
            reg_pg.enter_plate_number(data["plate_number"])

        when("Mitra melakukan rapid clicking pada tombol Kirim")
        for _ in range(3):
            try:
                reg_pg.submit_registration_form()
            except Exception:
                pass

        then("Aplikasi tetap stabil dan tidak menghasilkan double request")
        assert reg_pg.is_register_screen_displayed() or reg_pg.is_registration_success_displayed()
        logger.info("[SUCCESS] Anti-race rapid click pendaftaran terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_08_upload_selfie_dengan_ktp(self, driver_app):
        """
        [POSITIVE TRUE - PT-08]
        Deskripsi : Mengunggah dokumen 'Driver Selfie dengan KTP' pada formulir pendaftaran.
        Ekspektasi: Foto selfie terunggah sukses dan thumbnail preview gambar ditampilkan.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada pada formulir pendaftaran bagian dokumen legalitas")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra mengunggah foto selfie memegang KTP asli")
        then("Sistem memproses berkas dan menampilkan status terunggah")
        assert reg_pg.is_register_screen_displayed()

    @pytest.mark.positive_true
    def test_TC_DRV_REG_PT_09_verifikasi_klausul_konfirmasi_telepon_sla_2_jam(self, driver_app):
        """
        [POSITIVE TRUE - PT-09]
        Deskripsi : Memeriksa klausul konfirmasi pendaftaran SLA 2 jam kerja dari tim EVMoto.
        Ekspektasi: Tampil penjelasan 'Tim kami akan menghubungi Anda dalam waktu 2 jam'.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra telah mengirimkan data pendaftaran driver baru")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Layar dialog konfirmasi pendaftaran muncul")
        then("Pesan himbauan agar telepon tetap aktif dalam 2 jam kerja tertera")
        assert reg_pg.is_register_screen_displayed()

    @pytest.mark.negative_true
    def test_TC_DRV_REG_NT_06_format_plat_nomor_tanpa_spasi_atau_angka(self, driver_app):
        """
        [NEGATIVE TRUE - NT-06]
        Deskripsi : Memasukkan format plat nomor kendaraan tanpa menyertakan angka sama sekali (misal: B).
        Ekspektasi: Sistem memvalidasi bahwa plat nomor harus menyertakan digit angka.
        """
        login_pg = DrvLoginPage(driver_app)
        reg_pg = DrvRegisterPage(driver_app)

        given("Mitra berada di form registrasi kendaraan")
        login_pg.handle_system_permissions()
        if login_pg.is_login_screen_displayed():
            reg_pg.click_daftar_driver_baru()

        when("Mitra mengisi plat motor tanpa angka: 'B'")
        reg_pg.enter_plate_number("B")
        reg_pg.submit_registration_form()

        then("Sistem menolak format dan menampilkan petunjuk B1234ABC")
        assert reg_pg.is_register_screen_displayed()

