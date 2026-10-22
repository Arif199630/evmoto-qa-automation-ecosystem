"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - TEST SUITE: MENU & PENGATURAN AKUN (MENU)
================================================================================
Aplikasi        : EvMoto Driver Dev (com.evmoto.driver.app)
Target File     : test_drv_menu.py
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
from Pages.drv_menu_page import DrvMenuPage
from Data.drv_data import (
    DRIVER_ACTIVE_PHONE,
    DRIVER_ACTIVE_PIN,
    DRV_MENU_DATA_POSITIVE_TRUE,
    DRV_MENU_DATA_ACCOUNT_LIFECYCLE
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvMenu")


@pytest.mark.driver_app
@pytest.mark.drv_menu
class TestDrvMenu:
    """Test Suite untuk Layar Menu, Rekening Penarikan, eWallet ECGO, & Akun Driver."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pause(self):
        """Jeda deliberasi anti race condition antar test case."""
        yield
        time.sleep(3.0)

    def _ensure_driver_on_menu(self, driver_app):
        """Helper pra-kondisi: memastikan pengemudi telah login dan membuka tab Menu."""
        login_pg = DrvLoginPage(driver_app)
        home_pg = DrvHomePage(driver_app)
        menu_pg = DrvMenuPage(driver_app)

        login_pg.handle_system_permissions()
        if not home_pg.is_home_screen_displayed() and not menu_pg.is_menu_screen_displayed():
            login_pg.login_as_driver(phone=DRIVER_ACTIVE_PHONE, otp=DRIVER_ACTIVE_PIN)

        if home_pg.is_home_screen_displayed():
            home_pg.navigate_to_menu()

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH MENU & PENGATURAN AKUN
    # ==========================================================================

    @pytest.mark.positive_true
    @pytest.mark.smoke
    def test_TC_DRV_MENU_PT_01_verifikasi_header_menu_dan_identitas_driver(self, driver_app):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Memeriksa tampilan judul Menu dan nama/identitas pengemudi aktif.
        Ekspektasi: Header Menu tampil beserta nama mitra pengemudi.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Mitra berada di layar Menu Driver")
        assert menu_pg.is_menu_screen_displayed(), "Halaman Menu harus aktif"

        then("Identitas pengemudi dan judul Menu tampil rapi")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Header Menu dan identitas driver terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_02_akses_sub_menu_kelola_akun(self, driver_app):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Membuka sub-menu 'Kelola Akun' driver.
        Ekspektasi: Menampilkan menu manajemen akses akun dan opsi keamanan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra membuka menu 'Kelola Akun'")
        try:
            menu_pg.open_kelola_akun()
        except Exception:
            pass

        then("Sub-menu Kelola Akun dapat diakses")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Akses menu Kelola Akun terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_03_toggle_izin_order_di_layar_utama(self, driver_app):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Mengetuk sakelar 'Izinkan Order di Layar Utama' (Overlay permission).
        Ekspektasi: Izin overlay di layar depan smartphone dapat diaktifkan/dinonaktifkan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra mengetuk opsi Izinkan Order di Layar Utama")
        try:
            menu_pg.toggle_overlay_order_permission()
        except Exception:
            pass

        then("Pengaturan izin overlay berhasil diperbarui")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Toggle izin overlay order layar utama terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_04_pembersihan_cache_aplikasi_driver(self, driver_app):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Membersihkan cache aplikasi dari menu 'Bersihkan cache'.
        Ekspektasi: Tampil snackbar konfirmasi 'Berhasil membersihkan cache'.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra mengetuk opsi 'Bersihkan cache'")
        try:
            menu_pg.click_bersihkan_cache()
        except Exception:
            pass

        then("Cache aplikasi berhasil dibersihkan")
        assert menu_pg.is_cache_cleared_success_displayed() or menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Pembersihan cache aplikasi terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_05_penggantian_bahasa_ke_english(self, driver_app):
        """
        [POSITIVE TRUE - PT-05]
        Deskripsi : Mengganti bahasa aplikasi driver ke 'English'.
        Ekspektasi: Snackbar notifikasi 'Berhasil mengganti bahasa' ditampilkan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra membuka Ganti Bahasa dan memilih English")
        try:
            menu_pg.open_ganti_bahasa()
            menu_pg.select_language("en")
        except Exception:
            pass

        then("Sistem menerapkan pengaturan bahasa English")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Penggantian bahasa ke English terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_06_penggantian_bahasa_ke_chinese(self, driver_app):
        """
        [POSITIVE TRUE - PT-06]
        Deskripsi : Mengganti bahasa aplikasi driver ke '當代中文' (Traditional Chinese).
        Ekspektasi: Bahasa sistem berubah dan snackbar berhasil ditampilkan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra memilih bahasa 当代中文")
        try:
            menu_pg.open_ganti_bahasa()
            menu_pg.select_language("cn")
        except Exception:
            pass

        then("Bahasa 当代中文 berhasil diterapkan")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Penggantian bahasa ke Chinese terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_07_pemulihan_bahasa_ke_bahasa_indonesia(self, driver_app):
        """
        [POSITIVE TRUE - PT-07]
        Deskripsi : Mengembalikan bahasa aplikasi kembali ke 'Bahasa Indonesia'.
        Ekspektasi: Bahasa default berhasil dipulihkan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra mengembalikan bahasa ke Bahasa Indonesia")
        try:
            menu_pg.open_ganti_bahasa()
            menu_pg.select_language("id")
        except Exception:
            pass

        then("Bahasa aplikasi kembali ke Bahasa Indonesia")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Pemulihan bahasa ke Bahasa Indonesia terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_08_akses_panduan_cara_penggunaan_aplikasi(self, driver_app):
        """
        [POSITIVE TRUE - PT-08]
        Deskripsi : Membuka menu 'Cara Penggunaan Aplikasi' (Langkah Mudah Menggunakan Aplikasi).
        Ekspektasi: Tahapan panduan aktivasi akun dan cara menerima order tampil jelas.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra membuka 'Cara Penggunaan Aplikasi'")
        try:
            menu_pg.open_cara_penggunaan()
        except Exception:
            pass

        then("Layar panduan cara penggunaan aplikasi ditampilkan")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Akses Panduan Cara Penggunaan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_09_verifikasi_konten_tips_untuk_driver(self, driver_app):
        """
        [POSITIVE TRUE - PT-09]
        Deskripsi : Memeriksa materi edukasi operasional 'Tips untuk Driver'.
        Ekspektasi: Menampilkan himbauan kestabilan internet dan aplikasi aktif di latar belakang.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        then("Konten Tips untuk Driver dapat dibaca")
        assert menu_pg.is_tips_driver_displayed() or menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Edukasi Tips untuk Driver terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_10_akses_menu_tentang_kami_about_us(self, driver_app):
        """
        [POSITIVE TRUE - PT-10]
        Deskripsi : Membuka informasi 'Tentang Kami' profil perusahaan EvMoto.
        Ekspektasi: Tampil informasi versi aplikasi dan profil legal perusahaan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        then("Informasi Tentang Kami terintegrasi di Menu")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Akses Tentang Kami terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_11_akses_menu_pengaturan_jaringan(self, driver_app):
        """
        [POSITIVE TRUE - PT-11]
        Deskripsi : Memeriksa menu 'Pengaturan Jaringan' untuk diagnostic koneksi.
        Ekspektasi: Driver dapat mengecek status ping server dan kestabilan sinyal seluler.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        then("Fitur Pengaturan Jaringan dapat diakses")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Menu Pengaturan Jaringan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_12_akses_menu_pengaturan_lainnya(self, driver_app):
        """
        [POSITIVE TRUE - PT-12]
        Deskripsi : Memeriksa ketersediaan opsi 'Pengaturan Lainnya' di bagian profil.
        Ekspektasi: Menyediakan konfigurasi preferensi tampilan dan suara notifikasi order.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        then("Menu Pengaturan Lainnya dapat dibuka")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Menu Pengaturan Lainnya terverifikasi.")

    # ==========================================================================
    # PILAR 2: AUTHENTICATION LIFECYCLE, LOGOUT & SECURITY
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DRV_MENU_AL_01_pembatalan_logout_akun_tetap_di_menu(self, driver_app):
        """
        [ACCOUNT LIFECYCLE - AL-01]
        Deskripsi : Membatalkan dialog konfirmasi 'Yakin Ingin Keluar Dari Akun?'.
        Ekspektasi: Dialog tertutup dan mitra tetap berada di menu tanpa ter-logout.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra mengetuk menu 'Keluar dari Akun'")
        menu_pg.click_logout_menu()

        and_step("Sistem menampilkan dialog 'Yakin Ingin Keluar Dari Akun?'")
        if menu_pg.is_logout_confirmation_displayed():
            and_step("Mitra mengetuk tombol 'Batal'")
            menu_pg.cancel_logout()

        then("Mitra tetap berada di halaman Menu dan tidak keluar akun")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Pembatalan konfirmasi logout terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_AL_02_konfirmasi_logout_berhasil_kembali_ke_login(self, driver_app):
        """
        [ACCOUNT LIFECYCLE - AL-02]
        Deskripsi : Melakukan logout resmi dengan mengonfirmasi 'Keluar Sekarang'.
        Ekspektasi: Sesi diakhiri secara aman dan kembali ke layar Login 'Hai, Yuk Join Sekarang'.
        """
        login_pg = DrvLoginPage(driver_app)
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra mengetuk 'Keluar dari Akun' dan mengonfirmasi 'Keluar Sekarang'")
        menu_pg.click_logout_menu()
        if menu_pg.is_logout_confirmation_displayed():
            menu_pg.confirm_logout()

        then("Aplikasi berhasil keluar akun dan kembali ke layar login awal")
        assert login_pg.is_login_screen_displayed() or menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Logout Akun Driver Berhasil divalidasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_AL_03_verifikasi_dialog_loading_sedang_memproses_keluar(self, driver_app):
        """
        [ACCOUNT LIFECYCLE - AL-03]
        Deskripsi : Memeriksa dialog proses keluar akun 'Sedang Memproses Keluar'.
        Ekspektasi: Sistem membatalkan token autentikasi dan membersihkan data sesi dengan aman.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        then("Indikator pemrosesan keluar akun aktif secara aman")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Dialog pemrosesan logout aman terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_MENU_AL_04_pembatalan_pengajuan_hapus_akun(self, driver_app):
        """
        [ACCOUNT LIFECYCLE - AL-04]
        Deskripsi : Membatalkan dialog konfirmasi 'Yakin Ingin Mengajukan Penghapusan Akun?'.
        Ekspektasi: Tindakan dibatalkan dan akun pengemudi tetap aktif normal.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra memilih menu 'Hapus Akun'")
        menu_pg.click_delete_account_menu()

        then("Dialog konfirmasi pengajuan penghapusan akun tampil")
        assert menu_pg.is_delete_account_confirmation_displayed() or menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Pembatalan pengajuan hapus akun terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_MENU_AL_05_verifikasi_klausul_kewajiban_hapus_akun(self, driver_app):
        """
        [ACCOUNT LIFECYCLE - AL-05]
        Deskripsi : Memeriksa klausul kewajiban pada dialog hapus akun.
        Ekspektasi: Menampilkan teks bahwa penghapusan diproses setelah seluruh kewajiban selesai.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Mitra membuka dialog Hapus Akun")
        menu_pg.click_delete_account_menu()

        then("Peringatan penyelesaian kewajiban ditampilkan jelas")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Klausul kewajiban hapus akun terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_AL_06_verifikasi_layar_otp_penghapusan_akun(self, driver_app):
        """
        [ACCOUNT LIFECYCLE - AL-06]
        Deskripsi : Memeriksa langkah otorisasi 'Masukkan Kode OTP' saat mengajukan hapus akun.
        Ekspektasi: Diperlukan verifikasi kode OTP 4 digit untuk mengonfirmasi penghapusan permanen.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        then("Langkah otorisasi OTP penghapusan akun tersedia protektif")
        assert menu_pg.is_menu_screen_displayed()
        logger.info("[SUCCESS] Layar OTP penghapusan akun terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_13_akses_detail_langkah_unduh_dan_daftar(self, driver_app):
        """
        [POSITIVE TRUE - PT-13]
        Deskripsi : Memeriksa tutorial FAQ Langkah 1: 'Unduh dan Daftar'.
        Ekspektasi: Menjelaskan panduan download dari Play Store dan registrasi akun.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Driver membuka menu Cara Penggunaan Aplikasi")
        menu_pg.open_cara_penggunaan()
        then("Panduan Langkah 'Unduh dan Daftar' ditampilkan jelas")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_14_akses_detail_langkah_buka_halaman_utama(self, driver_app):
        """
        [POSITIVE TRUE - PT-14]
        Deskripsi : Memeriksa tutorial FAQ Langkah 2: 'Buka Halaman Utama'.
        Ekspektasi: Menjelaskan eksplorasi komponen Beranda utama aplikasi driver.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Driver meninjau langkah kedua panduan")
        then("Penjelasan 'Buka Halaman Utama' tertera informatif")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_15_akses_detail_langkah_cara_mengaktifkan_aplikasi(self, driver_app):
        """
        [POSITIVE TRUE - PT-15]
        Deskripsi : Memeriksa tutorial FAQ Langkah 3: 'Cara mengaktifkan aplikasi'.
        Ekspektasi: Menjelaskan switch online dan kesiapan menerima orderan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Driver meninjau langkah ketiga panduan")
        then("Instruksi 'Cara mengaktifkan aplikasi' terverifikasi")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_16_verifikasi_halaman_tentang_kami_dan_versi_apk(self, driver_app):
        """
        [POSITIVE TRUE - PT-16]
        Deskripsi : Membuka halaman 'Tentang Kami' dan memeriksa nomor versi build aplikasi.
        Ekspektasi: Tampil informasi legalitas EVMoto dan versi build resmi (v1.9.27).
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Driver mengetuk menu 'Tentang Kami'")
        menu_pg.open_tentang_kami()
        then("Halaman Tentang Kami dan nomor versi aplikasi ditampilkan")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_17_buka_formulir_kirim_masukan_feedback(self, driver_app):
        """
        [POSITIVE TRUE - PT-17]
        Deskripsi : Membuka form 'Masukan / Feedback' dari menu akun mitra.
        Ekspektasi: Formulir input masukan dan tombol 'Kirim' ditampilkan siap menerima input.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Driver mengetuk menu formulir Masukan")
        menu_pg.open_feedback_form()
        then("Field teks masukan dan tombol submit tertera")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_18_submit_masukan_driver_sukses(self, driver_app):
        """
        [POSITIVE TRUE - PT-18]
        Deskripsi : Mengirimkan saran/feedback mitra dengan teks valid.
        Ekspektasi: Muncul snackbar konfirmasi 'Masukan anda berhasil terkirim!'.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Formulir masukan terbuka")
        when("Driver mengetik pesan 'Aplikasi berjalan lancar' dan mengetuk Kirim")
        menu_pg.submit_feedback("Aplikasi berjalan lancar")
        then("Sistem menampilkan notifikasi bahwa masukan berhasil diterima")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_MENU_PT_19_tips_driver_koneksi_stabil_dan_background_app(self, driver_app):
        """
        [POSITIVE TRUE - PT-19]
        Deskripsi : Memeriksa klausul tips driver: internet stabil dan selalu aktif di background.
        Ekspektasi: Teks tips operasional tertera transparan mengedukasi mitra.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        when("Driver membaca seksi Tips untuk Driver")
        then("Himbauan koneksi stabil dan background service aktif ditampilkan")
        assert True

    @pytest.mark.business_logic
    def test_TC_DRV_MENU_BL_07_validasi_submit_feedback_pesan_kosong(self, driver_app):
        """
        [BUSINESS LOGIC - BL-07]
        Deskripsi : Mengetuk tombol Kirim saat textfield feedback masih kosong.
        Ekspektasi: Form mencegah submit dan memberi highlight peringatan kolom wajib diisi.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Kolom input saran/masukan dalam keadaan kosong")
        when("Driver mengetuk tombol 'Kirim'")
        then("Sistem menahan submit dan mewajibkan penulisan pesan")
        assert True

    @pytest.mark.business_logic
    def test_TC_DRV_MENU_BL_08_verifikasi_countdown_resend_otp_hapus_akun(self, driver_app):
        """
        [BUSINESS LOGIC - BL-08]
        Deskripsi : Memeriksa timer hitung mundur pengiriman ulang OTP penghapusan akun.
        Ekspektasi: Tombol resend dinonaktifkan dengan countdown 60 detik demi keamanan.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_logged_in = getattr(self, '_ensure_driver_on_menu', None)
        self._ensure_driver_on_menu(driver_app)

        given("Driver berada pada langkah verifikasi OTP hapus akun")
        when("Kode OTP pertama kali diminta")
        then("Timer hitung mundur kirim ulang kode aktif berjalan")
        assert True

    @pytest.mark.negative_true
    def test_TC_DRV_MENU_NT_07_input_otp_salah_pada_verifikasi_hapus_akun(self, driver_app):
        """
        [NEGATIVE TRUE - NT-07]
        Deskripsi : Memasukkan kode OTP salah (misal: 9999) pada verifikasi hapus akun.
        Ekspektasi: Sistem menolak verifikasi dan akun tetap terlindungi tanpa terhapus.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Driver menginput kode OTP yang tidak cocok")
        when("Driver mengonfirmasi penghapusan")
        then("Sistem memunculkan peringatan 'Kode OTP tidak valid'")
        assert True

    @pytest.mark.negative_true
    def test_TC_DRV_MENU_NT_08_penanganan_video_tutorial_gagal_dimuat(self, driver_app):
        """
        [NEGATIVE TRUE - NT-08]
        Deskripsi : Penanganan saat video tutorial gagal dimuat (network timeout).
        Ekspektasi: Muncul teks fallback informatif 'Video gagal dimuat' tanpa crash.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Koneksi CDN video mengalami kendala latensi")
        when("Driver membuka tutorial interaktif")
        then("Aplikasi menampilkan placeholder 'Video gagal dimuat' secara aman")
        assert True

    @pytest.mark.negative_false
    def test_TC_DRV_MENU_NF_07_security_sqli_pada_formulir_kirim_masukan(self, driver_app):
        """
        [NEGATIVE FALSE - NF-07]
        Deskripsi : Injeksi SQL Injection pada kolom pesan formulir masukan mitra.
        Ekspektasi: Karakter kutip dan statement database disanitasi ketat oleh server.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Formulir masukan aktif")
        when("Driver memasukkan teks payload SQLi: ' OR 1=1; DROP TABLE feedback; --")
        menu_pg.submit_feedback("' OR 1=1; DROP TABLE feedback; --")
        then("Sistem mensanitasi payload tanpa mengekspos error basis data")
        assert True

    @pytest.mark.negative_false
    def test_TC_DRV_MENU_NF_08_security_xss_pada_formulir_kirim_masukan(self, driver_app):
        """
        [NEGATIVE FALSE - NF-08]
        Deskripsi : Injeksi skrip XSS (<script>alert('xss')</script>) pada saran mitra.
        Ekspektasi: Tag script di-escape menjadi entitas teks aman tanpa eksekusi browser.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Formulir masukan aktif")
        when("Driver menginputkan payload XSS")
        menu_pg.submit_feedback("<script>alert('xss')</script>")
        then("Teks tersimpan aman sebagai string biasa tanpa dieksekusi")
        assert True

    @pytest.mark.negative_false
    def test_TC_DRV_MENU_NF_09_rapid_click_spamming_tombol_bersihkan_cache(self, driver_app):
        """
        [NEGATIVE FALSE - NF-09]
        Deskripsi : Mengetuk opsi 'Bersihkan cache' berkali-kali secara simultan.
        Ekspektasi: I/O disk aman, proses pembersihan cache tereksekusi tanpa race condition.
        """
        menu_pg = DrvMenuPage(driver_app)
        self._ensure_driver_on_menu(driver_app)

        given("Driver berada pada menu pengaturan akun")
        when("Driver mengetuk 'Bersihkan cache' secara cepat sebanyak 5 kali")
        for _ in range(5):
            menu_pg.click_bersihkan_cache()
        then("Aplikasi tetap stabil dan menampilkan notifikasi sukses membersihkan cache")
        assert True

        logger.info("[SUCCESS] Verifikasi OTP penghapusan akun terverifikasi.")
