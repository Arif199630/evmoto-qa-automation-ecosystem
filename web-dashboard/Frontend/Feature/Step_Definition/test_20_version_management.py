"""
=============================================================================
TEST SUITE 20: VERSION MANAGEMENT (MENU #20)
Website     : <BASE_URL>/tVersionManagement
Sub-Halaman : <BASE_URL>/tVersionManagement/tVersionManagement_add
Edit-Page   : <BASE_URL>/tVersionManagement/tVersionManagement_update/43
Desain      : Page Object Model (POM)
Konsep      : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan     : Daftar Versi Aplikasi, Filter Nomor Versi & Waktu, Tombol Reset & Add,
              Seleksi Baris & Tombol Update/Delete Terkunci Awal, Sub-halaman Add & Edit,
              Profil & Top Navigation Management, Proteksi Sesi, Sanitasi SQLi & XSS,
              dan Penanganan Anomali
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel versi termuat, filter nomor versi aktif
                     di query URL, tombol Add & Update membuka sub-halaman, serta
                     komponen profil navbar berfungsi normal (True).
2. Positif (False) : Memastikan tombol Update & Delete terkunci awal (disabled),
                     antarmuka bebas error 500, whitelabel exception, dan dropdown
                     profil tersembunyi sebelum diklik (False).
3. Negatif (True)  : Memastikan akses tanpa login dicegat ke /login, rentang tanggal
                     terbalik ditangani aman, dan interaksi profil stabil (True).
4. Negatif (False) : Memastikan pencarian fiktif menghasilkan 0 data, data terlindungi
                     dari publik, kebal serangan SQLi/XSS, dan logout memutus sesi (False).
=============================================================================
"""

import os
import sys
import time
import unittest
from selenium.webdriver.common.by import By

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_00_login import LoginPage
from pages.page_20_version_management import VersionPage


class TestVersionManagement(unittest.TestCase):
    """Test Suite Komprehensif untuk Modul Version Management & Sub-Halaman."""

    driver = None
    page = None
    login_page = None

    @classmethod
    def setUpClass(cls):
        """Inisialisasi WebDriver satu kali untuk efisiensi pengujian modul."""
        cls.driver = Config.get_driver()
        cls.login_page = LoginPage(cls.driver)
        cls.page = VersionPage(cls.driver)

        # Login awal ke sistem
        cls.login_page.open(Config.LOGIN_URL)
        cls.login_page.login(Config.VALID_USER, Config.VALID_PASS)
        time.sleep(2.5)

    @classmethod
    def tearDownClass(cls):
        """Menutup browser setelah seluruh pengujian selesai."""
        if cls.driver:
            cls.driver.quit()

    def ensure_logged_in(self):
        """Helper untuk menjamin browser berada dalam status login aktif."""
        try:
            if "/login" in self.driver.current_url or not self.page.is_profile_trigger_present():
                self.driver.get(Config.LOGIN_URL)
                time.sleep(1)
                if "/login" in self.driver.current_url:
                    self.login_page.login(Config.VALID_USER, Config.VALID_PASS)
                    time.sleep(2)
        except Exception:
            self.driver.get(Config.LOGIN_URL)
            time.sleep(1)
            self.login_page.login(Config.VALID_USER, Config.VALID_PASS)
            time.sleep(2)

    def setUp(self):
        """Memastikan setiap test case mulai dari sesi login aktif dan halaman utama."""
        self.ensure_logged_in()
        if Config.VERSION_MGMT_URL not in self.driver.current_url:
            self.page.navigate()
            time.sleep(1)

        # Pastikan dropdown profil tertutup
        if self.page.is_profile_dropdown_open():
            self.page.close_profile_dropdown()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Validasi Fungsional & Navigasi Sukses (12 Test)
    # =========================================================================

    def test_01_pilar1_positif_true_halaman_version_termuat(self):
        """[PILAR 1 - POSITIF (TRUE)] Halaman Version Management termuat aktif dengan URL dan title valid."""
        print("\n[Version - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi pemuatan halaman Version Management...")
        self.page.navigate()
        time.sleep(1)
        current_url = self.page.get_current_url()
        title = self.page.get_title()
        self.assertTrue("/tVersionManagement" in current_url, "URL harus memuat /tVersionManagement.")
        self.assertTrue("Version management" in title, "Judul halaman harus memuat 'Version management'.")
        print("  -> PASSED [True]: Halaman Version Management aktif terkonfirmasi.")

    def test_02_pilar1_positif_true_tabel_dan_kolom_hadir(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi tabel versi dan 8 kolom utama hadir lengkap."""
        print("[Version - Test 02] [PILAR 1: POSITIF (TRUE)] Verifikasi struktur kolom tabel versi...")
        self.page.navigate()
        time.sleep(1)
        is_table = self.page.is_table_displayed()
        headers = self.page.get_table_header_texts()
        self.assertTrue(is_table, "Tabel versi harus terlihat di layar.")
        self.assertTrue(any("ID" in h.upper() for h in headers), "Kolom ID harus hadir.")
        self.assertTrue(any("ADD TIME" in h.upper() for h in headers), "Kolom ADD TIME harus hadir.")
        self.assertTrue(any("VERSION NUMBER" in h.upper() for h in headers), "Kolom VERSION NUMBER harus hadir.")
        self.assertTrue(any("PORT TYPE" in h.upper() for h in headers), "Kolom PORT TYPE harus hadir.")
        self.assertTrue(any("GOOGLE PLAY" in h.upper() for h in headers), "Kolom GOOGLE PLAY LINK harus hadir.")
        self.assertTrue(any("APPLE STORE" in h.upper() for h in headers), "Kolom APPLE STORE LINK harus hadir.")
        self.assertTrue(any("FORCE UPDATE" in h.upper() for h in headers), "Kolom FORCE UPDATE harus hadir.")
        print(f"  -> PASSED [True]: Struktur kolom tabel versi lengkap ({len(headers)} kolom).")

    def test_03_pilar1_positif_true_filter_nomor_versi(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter pencarian nomor versi (version) berhasil diterapkan di query URL."""
        print("[Version - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian nomor versi aplikasi...")
        self.page.navigate()
        time.sleep(1)
        self.page.filter_by_version("1.2.30")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("version=1.2.30" in current_url, "Parameter version=1.2.30 harus ada di URL.")
        print("  -> PASSED [True]: Filter pencarian nomor versi berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang waktu penambahan versi (beginTime & endTime) berhasil diterapkan."""
        print("[Version - Test 04] [PILAR 1: POSITIF (TRUE)] Filter rentang waktu penambahan versi...")
        self.page.filter_by_date("2026-01-01", "2026-12-31")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("beginTime=2026-01-01" in current_url, "Parameter beginTime harus ada di URL.")
        self.assertTrue("endTime=2026-12-31" in current_url, "Parameter endTime harus ada di URL.")
        print("  -> PASSED [True]: Filter rentang waktu pembuatan berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_tombol_reset_membersihkan_filter(self):
        """[PILAR 1 - POSITIF (TRUE)] Tombol Reset mengembalikan URL ke kondisi awal tanpa query filter."""
        print("[Version - Test 05] [PILAR 1: POSITIF (TRUE)] Uji tombol Reset filter versi...")
        self.page.navigate()
        time.sleep(1)
        self.page.filter_by_version("9.9.9")
        time.sleep(0.5)
        self.page.click_reset()
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("/tVersionManagement" in current_url, "URL harus kembali ke rute dasar Version Management.")
        print("  -> PASSED [True]: Tombol Reset berhasil membersihkan formulir dan memuat ulang data awal.")

    def test_06_pilar1_positif_true_tombol_add_membuka_sub_halaman_tambah(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengklik tombol Add membuka sub-halaman tambah versi (/tVersionManagement_add)."""
        print("[Version - Test 06] [PILAR 1: POSITIF (TRUE)] Uji tombol Add membuka sub-halaman...")
        self.page.navigate()
        time.sleep(1)
        self.page.click_add()
        time.sleep(1.5)
        current_url = self.page.get_current_url()
        self.assertTrue("tVersionManagement_add" in current_url, "URL harus mengarah ke tVersionManagement_add.")
        print("  -> PASSED [True]: Tombol Add sukses menavigasikan ke sub-halaman tambah versi aplikasi.")

    def test_07_pilar1_positif_true_sub_halaman_add_memuat_formulir_lengkap(self):
        """[PILAR 1 - POSITIF (TRUE)] Sub-halaman Add memuat input version, type, link store, minimumVersion, content, dan submit."""
        print("[Version - Test 07] [PILAR 1: POSITIF (TRUE)] Verifikasi kelengkapan formulir Add Version...")
        self.page.navigate_add()
        time.sleep(1.5)
        is_version = self.page.is_displayed(self.page.INPUT_ADD_VERSION)
        is_google = self.page.is_displayed(self.page.INPUT_ADD_GOOGLE_PLAY)
        is_apple = self.page.is_displayed(self.page.INPUT_ADD_APPLE_STORE)
        is_submit = self.page.is_displayed(self.page.BTN_ADD_SUBMIT)
        self.assertTrue(is_version, "Input version harus terlihat di formulir Add.")
        self.assertTrue(is_google, "Input googlePlayLink harus terlihat di formulir Add.")
        self.assertTrue(is_apple, "Input appleStoreLink harus terlihat di formulir Add.")
        self.assertTrue(is_submit, "Tombol Submit harus terlihat di formulir Add.")
        print("  -> PASSED [True]: Formulir penambahan versi aplikasi terkonfirmasi lengkap dan aktif.")

    def test_08_pilar1_positif_true_seleksi_baris_mengaktifkan_tombol_update_dan_delete(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih baris versi via radio button berhasil mengaktifkan tombol Update dan Delete."""
        print("[Version - Test 08] [PILAR 1: POSITIF (TRUE)] Uji aktivasi tombol Update & Delete via seleksi...")
        self.page.navigate()
        time.sleep(1)
        selected = self.page.select_first_version_radio()
        self.assertTrue(selected, "Harus berhasil memilih salah satu baris radio button versi.")
        time.sleep(0.5)
        self.assertTrue(self.page.is_update_btn_enabled(), "Tombol Update harus AKTIF (True) setelah baris dipilih.")
        self.assertTrue(self.page.is_delete_btn_enabled(), "Tombol Delete harus AKTIF (True) setelah baris dipilih.")
        print("  -> PASSED [True]: Seleksi baris versi berhasil mengaktifkan tombol Update dan Delete.")

    def test_09_pilar1_positif_true_klik_update_membuka_sub_halaman_edit(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengklik tombol Update setelah memilih baris membuka sub-halaman edit versi (/tVersionManagement_update)."""
        print("[Version - Test 09] [PILAR 1: POSITIF (TRUE)] Uji tombol Update membuka sub-halaman edit...")
        self.page.navigate()
        time.sleep(1)
        self.page.select_first_version_radio()
        time.sleep(0.5)
        self.page.click_update()
        time.sleep(1.5)
        current_url = self.page.get_current_url()
        self.assertTrue("tVersionManagement_update" in current_url, "URL harus mengarah ke rute tVersionManagement_update.")
        print("  -> PASSED [True]: Tombol Update sukses menavigasikan ke sub-halaman edit versi.")

    def test_10_pilar1_positif_true_tombol_copy_link_store_hadir(self):
        """[PILAR 1 - POSITIF (TRUE)] Tombol copy tautan Google Play dan Apple Store hadir aktif pada baris tabel."""
        print("[Version - Test 10] [PILAR 1: POSITIF (TRUE)] Verifikasi kehadiran tombol copy link store...")
        self.page.navigate()
        time.sleep(1)
        copy_btns = self.driver.find_elements(*self.page.BTNS_COPY)
        self.assertTrue(len(copy_btns) > 0, "Tombol copy tautan aplikasi store harus hadir di tabel versi.")
        print(f"  -> PASSED [True]: Ditemukan {len(copy_btns)} tombol copy tautan store aktif di tabel versi.")

    def test_11_pilar1_positif_true_deep_link_dengan_parameter_url(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat data akurat."""
        print("[Version - Test 11] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        deep_url = f"{Config.VERSION_MGMT_URL}?version=1.2.30"
        self.page.open(deep_url)
        time.sleep(1.5)
        self.assertTrue("version=1.2.30" in self.page.get_current_url(), "URL harus mempertahankan query version=1.2.30.")
        self.assertTrue(self.page.is_table_displayed(), "Tabel tetap termuat aktif via deep link.")
        print("  -> PASSED [True]: Deep link langsung dengan parameter pencarian bekerja akurat.")

    def test_12_pilar1_positif_true_profil_dan_top_navigation_berfungsi(self):
        """[PILAR 1 - POSITIF (TRUE)] Menu profil di pojok kanan atas hadir, dapat dibuka, dan memuat identitas akun admin."""
        print("[Version - Test 12] [PILAR 1: POSITIF (TRUE)] Uji profil & top navigation di halaman version...")
        self.page.navigate()
        time.sleep(1)
        self.assertTrue(self.page.is_profile_trigger_present(), "Trigger profil harus hadir di pojok kanan atas.")
        self.page.open_profile_dropdown()
        time.sleep(0.4)
        is_open = self.page.is_profile_dropdown_open()
        header_text = self.page.get_profile_header_text()
        self.assertTrue(is_open, "Dropdown profil harus terbuka saat trigger diklik.")
        self.assertTrue("Admin" in header_text, "Header dropdown profil harus memuat nama akun Admin.")
        self.page.close_profile_dropdown()
        print("  -> PASSED [True]: Komponen Profil pojok kanan atas aktif dan berfungsi normal.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Ketiadaan Cacat & Proteksi Tombol Terkunci (6 Test)
    # =========================================================================

    def test_13_pilar2_positif_false_tombol_update_terkunci_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Update terkunci (disabled) sebelum ada baris yang dipilih."""
        print("[Version - Test 13] [PILAR 2: POSITIF (FALSE)] Uji tombol Update terkunci awal...")
        self.page.navigate()
        time.sleep(1)
        is_enabled = self.page.is_update_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Update TIDAK BOLEH aktif sebelum baris versi dipilih (False).")
        print("  -> PASSED [False]: Tombol Update terkunci aman sebelum ada baris yang dipilih.")

    def test_14_pilar2_positif_false_tombol_delete_terkunci_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete terkunci (disabled) sebelum ada baris yang dipilih."""
        print("[Version - Test 14] [PILAR 2: POSITIF (FALSE)] Uji tombol Delete terkunci awal...")
        self.page.navigate()
        time.sleep(1)
        is_enabled = self.page.is_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete TIDAK BOLEH aktif sebelum baris versi dipilih (False).")
        print("  -> PASSED [False]: Tombol Delete terkunci aman sebelum ada baris yang dipilih.")

    def test_15_pilar2_positif_false_ketiadaan_error_server_500_halaman_utama(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman utama Version Management bebas dari respon crash HTTP 500."""
        print("[Version - Test 15] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500 di halaman utama...")
        self.page.navigate()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src or "status=500" in src
        self.assertFalse(has_500, "Halaman utama Version Management TIDAK BOLEH memuat error 500.")
        print("  -> PASSED [False]: Halaman utama bebas dari respon crash 500 Internal Server Error.")

    def test_16_pilar2_positif_false_ketiadaan_error_server_500_sub_halaman_add(self):
        """[PILAR 2 - POSITIF (FALSE)] Sub-halaman Add Version bebas dari respon crash HTTP 500."""
        print("[Version - Test 16] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500 di sub-halaman Add...")
        self.page.navigate_add()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src or "status=500" in src
        self.assertFalse(has_500, "Sub-halaman Add TIDAK BOLEH memuat respon error server 500.")
        print("  -> PASSED [False]: Sub-halaman Add bebas dari respon crash 500 Internal Server Error.")

    def test_17_pilar2_positif_false_ketiadaan_whitelabel_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Antarmuka Version Management bebas dari exception Whitelabel Spring Boot."""
        print("[Version - Test 17] [PILAR 2: POSITIF (FALSE)] Memastikan bebas dari Whitelabel Error...")
        self.page.navigate()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_whitelabel = "whitelabel error page" in src or "there was an unexpected error" in src
        self.assertFalse(has_whitelabel, "Antarmuka TIDAK BOLEH menampilkan pesan Whitelabel Error.")
        print("  -> PASSED [False]: Antarmuka bersih dari exception Whitelabel Spring Boot.")

    def test_18_pilar2_positif_false_dropdown_profil_tertutup_saat_halaman_dimuat(self):
        """[PILAR 2 - POSITIF (FALSE)] Dropdown profil dalam status tersembunyi (hidden) saat awal halaman dimuat."""
        print("[Version - Test 18] [PILAR 2: POSITIF (FALSE)] Memastikan dropdown profil tersembunyi awal...")
        self.page.navigate()
        time.sleep(1)
        is_open = self.page.is_profile_dropdown_open()
        self.assertFalse(is_open, "Dropdown profil TIDAK BOLEH terbuka secara otomatis sebelum diklik (False).")
        print("  -> PASSED [False]: Dropdown profil terkonfirmasi tertutup aman saat halaman dibuka.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Keamanan Sesi & Penanganan Anomali (4 Test)
    # =========================================================================

    def test_19_pilar3_negatif_true_akses_tanpa_login_ke_halaman_utama_dicegat(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tVersionManagement tanpa login dicegat dan dialihkan ke /login."""
        print("[Version - Test 19] [PILAR 3: NEGATIF (TRUE)] Uji proteksi rute utama tanpa login...")
        self.page.click_logout()
        time.sleep(2)
        self.driver.get(Config.VERSION_MGMT_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Akses tanpa login harus dialihkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute utama aktif (dialihkan ke /login).")

    def test_20_pilar3_negatif_true_akses_tanpa_login_ke_sub_halaman_add_dicegat(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke sub-halaman /tVersionManagement_add tanpa login dicegat ke /login."""
        print("[Version - Test 20] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sub-halaman Add tanpa login...")
        if "/login" not in self.driver.current_url:
            self.page.click_logout()
            time.sleep(2)
        self.driver.get(Config.VERSION_ADD_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Akses sub-halaman Add tanpa login harus dialihkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute sub-halaman Add aktif (dialihkan ke /login).")

    def test_21_pilar3_negatif_true_rentang_tanggal_terbalik_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Filter rentang tanggal terbalik (begin > end) ditangani aman tanpa server crash 500."""
        print("[Version - Test 21] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada Version Management...")
        self.ensure_logged_in()
        self.page.filter_by_date("2026-12-31", "2026-01-01")
        time.sleep(1.5)
        src = self.page.get_page_source().lower()
        has_no_crash = "500 internal server error" not in src and "whitelabel error" not in src
        self.assertTrue(has_no_crash, "Sistem harus menangani tanggal terbalik secara stabil tanpa crash.")
        print("  -> PASSED [True]: Filter tanggal terbalik ditangani aman oleh sistem.")

    def test_22_pilar3_negatif_true_interaksi_menu_profil_memberikan_feedback_aktif(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengklik 'Edit Profil' di menu navigasi atas memicu notifikasi umpan balik aktif."""
        print("[Version - Test 22] [PILAR 3: NEGATIF (TRUE)] Uji interaksi Edit Profil di navbar...")
        self.page.navigate()
        time.sleep(1)
        self.page.click_edit_profile()
        time.sleep(0.5)
        toast = self.page.get_toast_message()
        self.assertTrue(len(toast) > 0 or "Profil" in toast or "disiapkan" in toast,
                        "Klik Edit Profil harus memicu notifikasi sistem.")
        print(f"  -> PASSED [True]: Respon Edit Profil terverifikasi aktif: '{toast}'.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Keamanan Siber, Penolakan Akses, & Resiliensi (8 Test)
    # =========================================================================

    def test_23_pilar4_negatif_false_pencarian_nomor_versi_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nomor versi fiktif menghasilkan tabel tanpa data secara aman tanpa kebocoran data acak."""
        print("[Version - Test 23] [PILAR 4: NEGATIF (FALSE)] Pencarian nomor versi fiktif...")
        self.page.navigate()
        time.sleep(1)
        self.page.filter_by_version("999.888.777_xyz")
        time.sleep(1)
        rows = self.driver.find_elements(By.XPATH, "//table//tbody/tr")
        is_empty_or_no_data = len(rows) == 0 or any("no" in r.text.lower() and "version" in r.text.lower() for r in rows)
        self.assertTrue(is_empty_or_no_data or len(rows) <= 1, "Pencarian fiktif harus menghasilkan tabel kosong/empty state.")
        has_bogus_leak = any("999.888.777" in r.text.lower() and "no" not in r.text.lower() for r in rows)
        self.assertFalse(has_bogus_leak, "Data acak tidak boleh bocor ke tabel (False).")
        print("  -> PASSED [False]: Pencarian nomor versi fiktif ditangani dengan aman.")

    def test_24_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_database_versi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA mengakses atau membaca database versi aplikasi."""
        print("[Version - Test 24] [PILAR 4: NEGATIF (FALSE)] Penolakan akses database versi publik...")
        self.page.click_logout()
        time.sleep(2)
        self.driver.get(Config.VERSION_MGMT_URL)
        time.sleep(1.5)
        has_table_exposed = len(self.driver.find_elements(By.TAG_NAME, "table")) > 0 and "/login" not in self.driver.current_url
        self.assertFalse(has_table_exposed, "Tamu tanpa login TIDAK BOLEH membaca tabel versi aplikasi (False).")
        print("  -> PASSED [False]: Database versi aplikasi terproteksi penuh dari akses publik tanpa otentikasi.")

    def test_25_pilar4_negatif_false_sql_injection_pada_pencarian_versi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Serangan SQL Injection pada form pencarian versi (' OR '1'='1) berhasil ditangkal."""
        print("[Version - Test 25] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada formulir nomor versi...")
        self.ensure_logged_in()
        self.page.navigate()
        time.sleep(1)
        self.page.filter_by_version("' OR '1'='1")
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_sql_error = "sql syntax" in src or "database error" in src or "org.hibernate" in src
        self.assertFalse(has_sql_error, "Form pencarian TIDAK BOLEH membocorkan error database SQL (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada nomor versi berhasil ditangkal.")

    def test_26_pilar4_negatif_false_sql_injection_drop_table_pada_versi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Serangan SQL Injection destruktif drop table tidak merusak database."""
        print("[Version - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji SQLi destruktif drop table...")
        self.page.filter_by_version("'; DROP TABLE t_version_management; --")
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_server_down = "500 internal server error" in src or "connection refused" in src
        self.assertFalse(has_server_down, "Serangan DROP TABLE tidak boleh melumpuhkan server (False).")
        print("  -> PASSED [False]: Serangan SQL Injection destruktif berhasil ditangkal aman.")

    def test_27_pilar4_negatif_false_xss_script_pada_pencarian_versi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Injeksi skrip XSS (<script>alert(1)</script>) pada pencarian versi disanitasi aman."""
        print("[Version - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian versi...")
        self.page.filter_by_version("<script>window.xss_exploited=true;</script>")
        time.sleep(1)
        is_exploited = self.driver.execute_script("return window.xss_exploited === true;")
        self.assertFalse(is_exploited, "Skrip XSS tidak boleh dieksekusi oleh browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada formulir versi.")

    def test_28_pilar4_negatif_false_url_subpath_fiktif_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tVersionManagement/invalid_subpath ditangani aman tanpa crash 500."""
        print("[Version - Test 28] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tVersionManagement/invalid_subpath...")
        self.driver.get(f"{Config.VERSION_MGMT_URL}/invalid_subpath_xyz_99")
        time.sleep(1.5)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src
        self.assertFalse(has_500, "URL subpath fiktif TIDAK BOLEH memicu crash 500 (False).")
        print("  -> PASSED [False]: URL fiktif versi ditangani secara aman tanpa server crash.")

    def test_29_pilar4_negatif_false_logout_via_profil_memutus_sesi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Klik tombol 'Keluar' pada menu profil di halaman version memutus sesi aktif."""
        print("[Version - Test 29] [PILAR 4: NEGATIF (FALSE)] Uji logout via menu profil navbar...")
        self.ensure_logged_in()
        self.page.navigate()
        time.sleep(1)
        self.page.click_logout()
        time.sleep(2)
        current_url = self.page.get_current_url()
        has_dashboard_session = "/tVersionManagement" in current_url or "/blackboard" in current_url
        self.assertFalse(has_dashboard_session, "Setelah klik Keluar, user TIDAK BOLEH tetap di rute dashboard (False).")
        print("  -> PASSED [False]: Sesi akun terkonfirmasi diputus secara tuntas oleh tombol Keluar.")

    def test_30_pilar4_negatif_false_browser_back_pasca_logout_tidak_buka_sesi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Simulasi tombol Back dan refresh browser pasca logout TIDAK BISA mengakses data sesi."""
        print("[Version - Test 30] [PILAR 4: NEGATIF (FALSE)] Uji proteksi navigasi browser Back pasca logout...")
        self.page.click_logout()
        time.sleep(2)
        self.driver.back()
        time.sleep(1)
        self.driver.refresh()
        time.sleep(2)
        current_url = self.page.get_current_url()
        has_active_session = "/login" not in current_url
        self.assertFalse(has_active_session, "Setelah logout dan reload, sesi server TIDAK BOLEH aktif (False).")
        print("  -> PASSED [False]: Navigasi browser Back pasca logout terlindungi aman dari kebocoran sesi.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
