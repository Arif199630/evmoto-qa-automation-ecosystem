"""
=============================================================================
TEST SUITE 17: SENSITIVE WORD MANAGEMENT (MENU #17)
Website : <BASE_URL>/tSysSensitiveWords
Sub-Page: <BASE_URL>/tSysSensitiveWords/tSysSensitiveWords_add
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Pencarian Kata Sensitif, Filter Bahasa (Chinese, English, Indonesian),
          Rentang Waktu, Tombol Reset & Add, Sub-halaman Tambah Kata,
          Tombol Delete Terkunci Awal, Profil & Top Navigation Management,
          Proteksi Sesi, Sanitasi SQLi & XSS, dan Penanganan Anomali
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel kata sensitif termuat, filter kata & bahasa
                     aktif di query URL, tombol Add membuka sub-halaman, serta
                     komponen profil pojok kanan atas berfungsi normal (True).
2. Positif (False) : Memastikan tombol Delete terkunci awal (disabled), antarmuka
                     bebas dari error 500, whitelabel exception, duplikasi header,
                     dan dropdown profil tersembunyi sebelum diklik (False).
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
from pages.page_17_sensitive_word_management import SensitiveWordPage


class TestSensitiveWordManagement(unittest.TestCase):
    """Test Suite Komprehensif untuk Modul Sensitive Word Management & Sub-Halaman."""

    driver = None
    page = None
    login_page = None

    @classmethod
    def setUpClass(cls):
        """Inisialisasi WebDriver satu kali untuk efisiensi pengujian modul."""
        cls.driver = Config.get_driver()
        cls.login_page = LoginPage(cls.driver)
        cls.page = SensitiveWordPage(cls.driver)

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
        if Config.SENSITIVE_WORDS_URL not in self.driver.current_url:
            self.page.navigate()
            time.sleep(1)

        # Pastikan dropdown profil tertutup
        if self.page.is_profile_dropdown_open():
            self.page.close_profile_dropdown()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Validasi Fungsional & Navigasi Sukses (12 Test)
    # =========================================================================

    def test_01_pilar1_positif_true_halaman_sensitive_word_termuat(self):
        """[PILAR 1 - POSITIF (TRUE)] Halaman Sensitive Word Management termuat aktif dengan URL dan title valid."""
        print("\n[Sensitive Word - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi pemuatan halaman...")
        current_url = self.page.get_current_url()
        title = self.page.get_title()
        self.assertTrue("/tSysSensitiveWords" in current_url, "URL harus memuat /tSysSensitiveWords.")
        self.assertTrue("Sensitive word" in title, "Judul halaman harus memuat 'Sensitive word'.")
        print("  -> PASSED [True]: Halaman Sensitive Word Management aktif terkonfirmasi.")

    def test_02_pilar1_positif_true_tabel_dan_kolom_hadir(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi tabel kata sensitif dan 4 kolom (Checkbox, Creation Time, Sensitive Words, Language) hadir."""
        print("[Sensitive Word - Test 02] [PILAR 1: POSITIF (TRUE)] Verifikasi struktur kolom tabel...")
        is_table = self.page.is_table_displayed()
        headers = self.page.get_table_header_texts()
        self.assertTrue(is_table, "Tabel kata sensitif harus terlihat di layar.")
        self.assertTrue(any("CREATION TIME" in h.upper() for h in headers), "Kolom CREATION TIME harus hadir.")
        self.assertTrue(any("SENSITIVE WORDS" in h.upper() for h in headers), "Kolom SENSITIVE WORDS harus hadir.")
        self.assertTrue(any("LANGUAGE" in h.upper() for h in headers), "Kolom LANGUAGE harus hadir.")
        print(f"  -> PASSED [True]: Struktur kolom tabel lengkap ({headers}).")

    def test_03_pilar1_positif_true_filter_kata_sensitif(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter pencarian kata sensitif (content) berhasil diterapkan di query URL."""
        print("[Sensitive Word - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian konten kata sensitif...")
        self.page.filter_by_content("promo")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("content=promo" in current_url, "Parameter query content harus ada di URL.")
        print("  -> PASSED [True]: Filter pencarian konten kata berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_filter_bahasa_chinese(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter bahasa Chinese (yy=1) berhasil diaplikasikan di query URL."""
        print("[Sensitive Word - Test 04] [PILAR 1: POSITIF (TRUE)] Filter bahasa Chinese...")
        self.page.filter_by_language("1")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("yy=1" in current_url, "Parameter query yy=1 harus ada di URL.")
        print("  -> PASSED [True]: Filter bahasa Chinese berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_filter_bahasa_english(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter bahasa English (yy=2) berhasil diaplikasikan di query URL."""
        print("[Sensitive Word - Test 05] [PILAR 1: POSITIF (TRUE)] Filter bahasa English...")
        self.page.filter_by_language("2")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("yy=2" in current_url, "Parameter query yy=2 harus ada di URL.")
        print("  -> PASSED [True]: Filter bahasa English berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_filter_bahasa_indonesian(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter bahasa Indonesian (yy=3) berhasil diaplikasikan di query URL."""
        print("[Sensitive Word - Test 06] [PILAR 1: POSITIF (TRUE)] Filter bahasa Indonesian...")
        self.page.filter_by_language("3")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("yy=3" in current_url, "Parameter query yy=3 harus ada di URL.")
        print("  -> PASSED [True]: Filter bahasa Indonesian berhasil diaplikasikan.")

    def test_07_pilar1_positif_true_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang waktu pembuatan kata sensitif (beginTime & endTime) berhasil diterapkan."""
        print("[Sensitive Word - Test 07] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal pembuatan...")
        self.page.filter_by_date("2026-01-01", "2026-12-31")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("beginTime=2026-01-01" in current_url, "Parameter beginTime harus ada di URL.")
        self.assertTrue("endTime=2026-12-31" in current_url, "Parameter endTime harus ada di URL.")
        print("  -> PASSED [True]: Filter rentang waktu pembuatan berhasil diaplikasikan.")

    def test_08_pilar1_positif_true_tombol_reset_membersihkan_filter(self):
        """[PILAR 1 - POSITIF (TRUE)] Tombol Reset mengembalikan URL ke kondisi awal tanpa query filter."""
        print("[Sensitive Word - Test 08] [PILAR 1: POSITIF (TRUE)] Uji tombol Reset filter...")
        self.page.filter_by_content("kata_filter")
        time.sleep(0.5)
        self.page.click_reset()
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("/tSysSensitiveWords" in current_url, "URL harus kembali ke rute dasar kata sensitif.")
        print("  -> PASSED [True]: Tombol Reset berhasil membersihkan formulir dan memuat ulang data awal.")

    def test_09_pilar1_positif_true_tombol_add_membuka_sub_halaman_tambah(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengklik tombol Add membuka sub-halaman tambah kata sensitif (/tSysSensitiveWords_add)."""
        print("[Sensitive Word - Test 09] [PILAR 1: POSITIF (TRUE)] Uji tombol Add membuka sub-halaman...")
        self.page.click_add()
        time.sleep(1.5)
        current_url = self.page.get_current_url()
        self.assertTrue("tSysSensitiveWords_add" in current_url, "URL harus mengarah ke tSysSensitiveWords_add.")
        print("  -> PASSED [True]: Tombol Add sukses menavigasikan ke sub-halaman tambah kata sensitif.")

    def test_10_pilar1_positif_true_sub_halaman_add_memuat_formulir_lengkap(self):
        """[PILAR 1 - POSITIF (TRUE)] Sub-halaman Add memuat input content, dropdown language, dan tombol Submit."""
        print("[Sensitive Word - Test 10] [PILAR 1: POSITIF (TRUE)] Verifikasi kelengkapan formulir Add...")
        self.page.navigate_add()
        time.sleep(1.5)
        is_content = self.page.is_displayed(self.page.INPUT_ADD_CONTENT)
        is_lang = self.page.is_displayed(self.page.SELECT_ADD_LANGUAGE)
        is_submit = self.page.is_displayed(self.page.BTN_ADD_SUBMIT)
        self.assertTrue(is_content, "Input kata sensitif (content) harus terlihat.")
        self.assertTrue(is_lang, "Dropdown bahasa (language) harus terlihat.")
        self.assertTrue(is_submit, "Tombol Submit harus terlihat di formulir Add.")
        print("  -> PASSED [True]: Formulir penambahan kata sensitif terkonfirmasi lengkap dan aktif.")

    def test_11_pilar1_positif_true_deep_link_dengan_parameter_url(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat data akurat."""
        print("[Sensitive Word - Test 11] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        deep_url = f"{Config.SENSITIVE_WORDS_URL}?content=judi&yy=3"
        self.page.open(deep_url)
        time.sleep(1.5)
        self.assertTrue("content=judi" in self.page.get_current_url(), "URL harus mempertahankan query content=judi.")
        self.assertTrue("yy=3" in self.page.get_current_url(), "URL harus mempertahankan query yy=3.")
        self.assertTrue(self.page.is_table_displayed(), "Tabel tetap termuat aktif via deep link.")
        print("  -> PASSED [True]: Deep link langsung dengan parameter pencarian bekerja akurat.")

    def test_12_pilar1_positif_true_profil_dan_top_navigation_berfungsi(self):
        """[PILAR 1 - POSITIF (TRUE)] Menu profil di pojok kanan atas hadir, dapat dibuka, dan memuat identitas akun admin."""
        print("[Sensitive Word - Test 12] [PILAR 1: POSITIF (TRUE)] Uji profil & top navigation di halaman kata sensitif...")
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
        print("  -> PASSED [True]: Komponen Profil pojok kanan atas aktif dan berfungsi sempurna.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Ketiadaan Cacat & Proteksi Tombol Terkunci (6 Test)
    # =========================================================================

    def test_13_pilar2_positif_false_tombol_delete_terkunci_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete terkunci (disabled) sebelum ada baris yang dipilih."""
        print("[Sensitive Word - Test 13] [PILAR 2: POSITIF (FALSE)] Uji tombol Delete terkunci awal...")
        self.page.navigate()
        time.sleep(1)
        is_enabled = self.page.is_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete TIDAK BOLEH aktif sebelum baris kata dipilih (False).")
        print("  -> PASSED [False]: Tombol Delete terkunci aman sebelum ada baris yang dipilih.")

    def test_14_pilar2_positif_false_ketiadaan_error_server_500_halaman_utama(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman utama Sensitive Word Management bebas dari respon crash HTTP 500."""
        print("[Sensitive Word - Test 14] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500 di halaman utama...")
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src or "status=500" in src
        self.assertFalse(has_500, "Halaman utama kata sensitif TIDAK BOLEH memuat respon error server 500.")
        print("  -> PASSED [False]: Halaman utama bebas dari respon crash 500 Internal Server Error.")

    def test_15_pilar2_positif_false_ketiadaan_error_server_500_sub_halaman_add(self):
        """[PILAR 2 - POSITIF (FALSE)] Sub-halaman Add Sensitive Word bebas dari respon crash HTTP 500."""
        print("[Sensitive Word - Test 15] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500 di sub-halaman Add...")
        self.page.navigate_add()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src or "status=500" in src
        self.assertFalse(has_500, "Sub-halaman Add TIDAK BOLEH memuat respon error server 500.")
        print("  -> PASSED [False]: Sub-halaman Add bebas dari respon crash 500 Internal Server Error.")

    def test_16_pilar2_positif_false_ketiadaan_whitelabel_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Antarmuka kata sensitif bebas dari exception Whitelabel Spring Boot."""
        print("[Sensitive Word - Test 16] [PILAR 2: POSITIF (FALSE)] Memastikan bebas dari Whitelabel Error...")
        self.page.navigate()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_whitelabel = "whitelabel error page" in src or "there was an unexpected error" in src
        self.assertFalse(has_whitelabel, "Antarmuka TIDAK BOLEH menampilkan pesan Whitelabel Error.")
        print("  -> PASSED [False]: Antarmuka bersih dari exception Whitelabel Spring Boot.")

    def test_17_pilar2_positif_false_ketiadaan_duplikasi_header_tabel(self):
        """[PILAR 2 - POSITIF (FALSE)] DOM tabel kata sensitif bersih dari duplikasi elemen header thead."""
        print("[Sensitive Word - Test 17] [PILAR 2: POSITIF (FALSE)] Memastikan ketiadaan duplikasi header tabel...")
        theads = self.driver.find_elements(By.XPATH, "//table//thead")
        has_duplicate = len(theads) > 1
        self.assertFalse(has_duplicate, "DOM tabel kata sensitif TIDAK BOLEH memiliki header thead ganda.")
        print("  -> PASSED [False]: Header tabel bersih tanpa duplikasi.")

    def test_18_pilar2_positif_false_dropdown_profil_tertutup_saat_halaman_dimuat(self):
        """[PILAR 2 - POSITIF (FALSE)] Dropdown profil dalam status tersembunyi (hidden) saat awal halaman dimuat."""
        print("[Sensitive Word - Test 18] [PILAR 2: POSITIF (FALSE)] Memastikan dropdown profil tersembunyi awal...")
        self.page.navigate()
        time.sleep(1)
        is_open = self.page.is_profile_dropdown_open()
        self.assertFalse(is_open, "Dropdown profil TIDAK BOLEH terbuka secara otomatis sebelum diklik (False).")
        print("  -> PASSED [False]: Dropdown profil terkonfirmasi tertutup aman saat halaman dibuka.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Keamanan Sesi & Penanganan Anomali (4 Test)
    # =========================================================================

    def test_19_pilar3_negatif_true_akses_tanpa_login_ke_halaman_utama_dicegat(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tSysSensitiveWords tanpa login dicegat dan dialihkan ke /login."""
        print("[Sensitive Word - Test 19] [PILAR 3: NEGATIF (TRUE)] Uji proteksi rute halaman utama tanpa login...")
        self.page.click_logout()
        time.sleep(2)
        self.driver.get(Config.SENSITIVE_WORDS_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Akses tanpa login harus dialihkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute utama aktif (dialihkan ke /login).")

    def test_20_pilar3_negatif_true_akses_tanpa_login_ke_sub_halaman_add_dicegat(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke sub-halaman /tSysSensitiveWords_add tanpa login dicegat dan dialihkan ke /login."""
        print("[Sensitive Word - Test 20] [PILAR 3: NEGATIF (TRUE)] Uji proteksi rute sub-halaman Add tanpa login...")
        if "/login" not in self.driver.current_url:
            self.page.click_logout()
            time.sleep(2)
        self.driver.get(Config.SENSITIVE_WORDS_ADD_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Akses sub-halaman Add tanpa login harus dialihkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute sub-halaman Add aktif (dialihkan ke /login).")

    def test_21_pilar3_negatif_true_rentang_tanggal_terbalik_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Filter rentang tanggal terbalik (begin > end) ditangani aman tanpa server crash 500."""
        print("[Sensitive Word - Test 21] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik...")
        self.ensure_logged_in()
        self.page.filter_by_date("2026-12-31", "2026-01-01")
        time.sleep(1.5)
        src = self.page.get_page_source().lower()
        has_no_crash = "500 internal server error" not in src and "whitelabel error" not in src
        self.assertTrue(has_no_crash, "Sistem harus menangani tanggal terbalik secara stabil tanpa crash.")
        print("  -> PASSED [True]: Filter tanggal terbalik ditangani aman oleh sistem.")

    def test_22_pilar3_negatif_true_interaksi_menu_profil_memberikan_feedback_aktif(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengklik 'Edit Profil' di menu navigasi atas memicu notifikasi umpan balik aktif."""
        print("[Sensitive Word - Test 22] [PILAR 3: NEGATIF (TRUE)] Uji interaksi Edit Profil di navbar...")
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

    def test_23_pilar4_negatif_false_pencarian_kata_sensitif_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian kata sensitif fiktif menghasilkan tabel tanpa data secara aman."""
        print("[Sensitive Word - Test 23] [PILAR 4: NEGATIF (FALSE)] Pencarian kata fiktif...")
        self.page.filter_by_content("kata_fiktif_random_99999_xyz")
        time.sleep(1)
        rows = self.driver.find_elements(By.XPATH, "//table//tbody/tr")
        is_empty_or_no_data = len(rows) == 0 or any("no sensitive words" in r.text.lower() for r in rows)
        self.assertTrue(is_empty_or_no_data, "Pencarian fiktif harus menghasilkan tabel kosong.")
        has_bogus_leak = any("random_99999" in r.text.lower() and "no sensitive" not in r.text.lower() for r in rows)
        self.assertFalse(has_bogus_leak, "Data acak tidak boleh bocor ke tabel (False).")
        print("  -> PASSED [False]: Pencarian kata fiktif ditangani dengan aman (0 data).")

    def test_24_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_kata_sensitif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA mengakses atau membaca database kata sensitif."""
        print("[Sensitive Word - Test 24] [PILAR 4: NEGATIF (FALSE)] Penolakan akses database kata sensitif publik...")
        self.page.click_logout()
        time.sleep(2)
        self.driver.get(Config.SENSITIVE_WORDS_URL)
        time.sleep(1.5)
        has_table_exposed = len(self.driver.find_elements(By.TAG_NAME, "table")) > 0 and "/login" not in self.driver.current_url
        self.assertFalse(has_table_exposed, "Tamu tanpa login TIDAK BOLEH membaca tabel kata sensitif (False).")
        print("  -> PASSED [False]: Database kata sensitif terproteksi penuh dari akses publik.")

    def test_25_pilar4_negatif_false_sql_injection_pada_pencarian_kata(self):
        """[PILAR 4 - NEGATIF (FALSE)] Serangan SQL Injection pada form pencarian kata (' OR '1'='1) berhasil ditangkal."""
        print("[Sensitive Word - Test 25] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada formulir kata sensitif...")
        self.ensure_logged_in()
        self.page.filter_by_content("' OR '1'='1")
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_sql_error = "sql syntax" in src or "database error" in src or "org.hibernate" in src
        self.assertFalse(has_sql_error, "Form pencarian TIDAK BOLEH membocorkan error database SQL (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada kata sensitif berhasil ditangkal.")

    def test_26_pilar4_negatif_false_sql_injection_drop_table_pada_kata(self):
        """[PILAR 4 - NEGATIF (FALSE)] Serangan SQL Injection destruktif drop table tidak merusak database."""
        print("[Sensitive Word - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji SQLi destruktif drop table...")
        self.page.filter_by_content("'; DROP TABLE t_sys_sensitive_words; --")
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_server_down = "500 internal server error" in src or "connection refused" in src
        self.assertFalse(has_server_down, "Serangan DROP TABLE tidak boleh melumpuhkan server (False).")
        print("  -> PASSED [False]: Serangan SQL Injection destruktif berhasil ditangkal aman.")

    def test_27_pilar4_negatif_false_xss_script_pada_pencarian_kata(self):
        """[PILAR 4 - NEGATIF (FALSE)] Injeksi skrip XSS (<script>alert(1)</script>) pada form pencarian disanitasi aman."""
        print("[Sensitive Word - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada form pencarian...")
        self.page.filter_by_content("<script>window.xss_exploited=true;</script>")
        time.sleep(1)
        is_exploited = self.driver.execute_script("return window.xss_exploited === true;")
        self.assertFalse(is_exploited, "Skrip XSS tidak boleh dieksekusi oleh browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada formulir kata sensitif.")

    def test_28_pilar4_negatif_false_url_subpath_fiktif_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tSysSensitiveWords/invalid_subpath ditangani aman tanpa crash 500."""
        print("[Sensitive Word - Test 28] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tSysSensitiveWords/invalid_subpath...")
        self.driver.get(f"{Config.SENSITIVE_WORDS_URL}/invalid_subpath_xyz_99")
        time.sleep(1.5)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src
        self.assertFalse(has_500, "URL subpath fiktif TIDAK BOLEH memicu crash 500 (False).")
        print("  -> PASSED [False]: URL fiktif kata sensitif ditangani secara aman tanpa server crash.")

    def test_29_pilar4_negatif_false_logout_via_profil_memutus_sesi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Klik tombol 'Keluar' pada menu profil di halaman kata sensitif memutus sesi aktif."""
        print("[Sensitive Word - Test 29] [PILAR 4: NEGATIF (FALSE)] Uji logout via menu profil navbar...")
        self.ensure_logged_in()
        self.page.navigate()
        time.sleep(1)
        self.page.click_logout()
        time.sleep(2)
        current_url = self.page.get_current_url()
        has_dashboard_session = "/tSysSensitiveWords" in current_url or "/blackboard" in current_url
        self.assertFalse(has_dashboard_session, "Setelah klik Keluar, user TIDAK BOLEH tetap di rute dashboard (False).")
        print("  -> PASSED [False]: Sesi akun terkonfirmasi diputus secara tuntas oleh tombol Keluar.")

    def test_30_pilar4_negatif_false_browser_back_pasca_logout_tidak_buka_sesi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Simulasi tombol Back dan refresh browser pasca logout TIDAK BISA mengakses data sesi."""
        print("[Sensitive Word - Test 30] [PILAR 4: NEGATIF (FALSE)] Uji proteksi navigasi browser Back pasca logout...")
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
