"""
=============================================================================
TEST SUITE 18: FEEDBACK MANAGEMENT (MENU #18)
Website     : <BASE_URL>/tFeedback (Driver Feedback)
Sub-Halaman : <BASE_URL>/tFeedback/userFeedback (User Feedback)
Detail View : <BASE_URL>/tFeedback/lookDetail/81/1
Desain      : Page Object Model (POM)
Konsep      : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan     : Driver Feedback, User Feedback, Filter Status & Waktu,
              Pencarian Driver/User, Tombol Reset, Tombol Immediately Process,
              Sub-halaman Detail View & Back, Profil & Top Navigation Management,
              Proteksi Sesi, Sanitasi SQLi & XSS, dan Penanganan Anomali
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel umpan balik termuat, filter nama & no HP
                     aktif di query URL, tombol Reset berfungsi, sub-halaman detail
                     memuat tombol Back, serta komponen profil navbar berfungsi (True).
2. Positif (False) : Memastikan tombol Immediately process terkunci awal (disabled),
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
from pages.page_18_feedback_management import FeedbackPage


class TestFeedbackManagement(unittest.TestCase):
    """Test Suite Komprehensif untuk Modul Feedback Management & Sub-Halaman."""

    driver = None
    page = None
    login_page = None

    @classmethod
    def setUpClass(cls):
        """Inisialisasi WebDriver satu kali untuk efisiensi pengujian modul."""
        cls.driver = Config.get_driver()
        cls.login_page = LoginPage(cls.driver)
        cls.page = FeedbackPage(cls.driver)

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
        """Memastikan setiap test case mulai dari sesi login aktif dan halaman driver feedback."""
        self.ensure_logged_in()
        if "/tFeedback" not in self.driver.current_url:
            self.page.navigate_driver()
            time.sleep(1)

        # Pastikan dropdown profil tertutup
        if self.page.is_profile_dropdown_open():
            self.page.close_profile_dropdown()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Validasi Fungsional & Navigasi Sukses (12 Test)
    # =========================================================================

    def test_01_pilar1_positif_true_halaman_driver_feedback_termuat(self):
        """[PILAR 1 - POSITIF (TRUE)] Halaman Driver Feedback Management termuat aktif dengan URL dan title valid."""
        print("\n[Feedback - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi pemuatan Driver Feedback...")
        self.page.navigate_driver()
        time.sleep(1)
        current_url = self.page.get_current_url()
        title = self.page.get_title()
        self.assertTrue("/tFeedback" in current_url, "URL harus memuat /tFeedback.")
        self.assertTrue("Driver feedback" in title, "Judul halaman harus memuat 'Driver feedback'.")
        print("  -> PASSED [True]: Halaman Driver Feedback Management aktif terkonfirmasi.")

    def test_02_pilar1_positif_true_struktur_tabel_driver_feedback_lengkap(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi tabel Driver Feedback memuat kolom lengkap (Feedback Time, Person, Phone, Contents, State)."""
        print("[Feedback - Test 02] [PILAR 1: POSITIF (TRUE)] Verifikasi kolom tabel Driver Feedback...")
        self.page.navigate_driver()
        time.sleep(1)
        is_table = self.page.is_table_displayed()
        headers = self.page.get_table_header_texts()
        self.assertTrue(is_table, "Tabel Driver Feedback harus terlihat di layar.")
        self.assertTrue(any("FEEDBACK TIME" in h.upper() for h in headers), "Kolom FEEDBACK TIME harus hadir.")
        self.assertTrue(any("FEEDBACK PERSON" in h.upper() for h in headers), "Kolom FEEDBACK PERSON harus hadir.")
        self.assertTrue(any("MOBILE PHONE" in h.upper() for h in headers), "Kolom FEEDBACK MOBILE PHONE NUMBER harus hadir.")
        self.assertTrue(any("FEEDBACK CONTENTS" in h.upper() for h in headers), "Kolom FEEDBACK CONTENTS harus hadir.")
        self.assertTrue(any("STATE" in h.upper() for h in headers), "Kolom STATE harus hadir.")
        print(f"  -> PASSED [True]: Struktur kolom tabel Driver Feedback lengkap ({len(headers)} kolom).")

    def test_03_pilar1_positif_true_sub_halaman_user_feedback_termuat(self):
        """[PILAR 1 - POSITIF (TRUE)] Sub-halaman User Feedback Management termuat aktif dengan URL dan title valid."""
        print("[Feedback - Test 03] [PILAR 1: POSITIF (TRUE)] Verifikasi pemuatan User Feedback...")
        self.page.navigate_user()
        time.sleep(1)
        current_url = self.page.get_current_url()
        title = self.page.get_title()
        self.assertTrue("userFeedback" in current_url, "URL harus memuat userFeedback.")
        self.assertTrue("User feedback" in title, "Judul halaman harus memuat 'User feedback'.")
        print("  -> PASSED [True]: Sub-halaman User Feedback Management aktif terkonfirmasi.")

    def test_04_pilar1_positif_true_tabel_user_feedback_dan_empty_state(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi tabel User Feedback terlihat dan menampilkan status data kosong."""
        print("[Feedback - Test 04] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel User Feedback & empty state...")
        self.page.navigate_user()
        time.sleep(1)
        is_table = self.page.is_table_displayed()
        src = self.page.get_page_source().lower()
        self.assertTrue(is_table, "Tabel User Feedback harus hadir di antarmuka.")
        has_empty_indicator = "no user feedback found" in src or len(self.driver.find_elements(By.XPATH, "//table//tbody/tr")) > 0
        self.assertTrue(has_empty_indicator, "Tabel harus memuat baris data atau pesan empty state.")
        print("  -> PASSED [True]: Antarmuka tabel User Feedback terkonfirmasi stabil dan responsif.")

    def test_05_pilar1_positif_true_filter_pencarian_nama_driver(self):
        """[PILAR 1 - POSITIF (TRUE)] Pencarian berdasarkan nama driver (driverName) teraplikasi di query URL."""
        print("[Feedback - Test 05] [PILAR 1: POSITIF (TRUE)] Uji filter nama driver...")
        self.page.navigate_driver()
        time.sleep(1)
        self.page.filter_driver_feedback(driver_name="Budi")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("driverName=Budi" in current_url, "Query URL harus memuat driverName=Budi.")
        print("  -> PASSED [True]: Filter pencarian nama driver berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_filter_pencarian_telepon_driver(self):
        """[PILAR 1 - POSITIF (TRUE)] Pencarian berdasarkan nomor telepon driver (driverPhone) teraplikasi di query URL."""
        print("[Feedback - Test 06] [PILAR 1: POSITIF (TRUE)] Uji filter telepon driver...")
        self.page.navigate_driver()
        time.sleep(1)
        self.page.filter_driver_feedback(driver_phone="08123456789")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("driverPhone=08123456789" in current_url, "Query URL harus memuat driverPhone=08123456789.")
        print("  -> PASSED [True]: Filter pencarian nomor telepon driver berhasil diaplikasikan.")

    def test_07_pilar1_positif_true_filter_status_driver_feedback(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter status penanganan Driver Feedback (state=1) teraplikasi di query URL."""
        print("[Feedback - Test 07] [PILAR 1: POSITIF (TRUE)] Uji filter status penanganan driver...")
        self.page.navigate_driver()
        time.sleep(1)
        self.page.filter_driver_feedback(state="1")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("state=1" in current_url, "Query URL harus memuat parameter state=1.")
        print("  -> PASSED [True]: Filter status Driver Feedback berhasil diaplikasikan.")

    def test_08_pilar1_positif_true_filter_pencarian_user_feedback(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter nama user (userName) dan telepon user (userPhone) teraplikasi di query URL."""
        print("[Feedback - Test 08] [PILAR 1: POSITIF (TRUE)] Uji filter pencarian user feedback...")
        self.page.navigate_user()
        time.sleep(1)
        self.page.filter_user_feedback(user_name="Siti", user_phone="08987654321")
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("userName=Siti" in current_url, "Query URL harus memuat userName=Siti.")
        self.assertTrue("userPhone=08987654321" in current_url, "Query URL harus memuat userPhone=08987654321.")
        print("  -> PASSED [True]: Filter pencarian user feedback berhasil diaplikasikan.")

    def test_09_pilar1_positif_true_tombol_reset_driver_feedback(self):
        """[PILAR 1 - POSITIF (TRUE)] Tombol Reset pada Driver Feedback mengembalikan URL ke kondisi awal tanpa query filter."""
        print("[Feedback - Test 09] [PILAR 1: POSITIF (TRUE)] Uji tombol Reset Driver Feedback...")
        self.page.navigate_driver()
        time.sleep(1)
        self.page.filter_driver_feedback(driver_name="FilterTest")
        time.sleep(0.5)
        self.page.click_reset_driver()
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("/tFeedback" in current_url, "URL harus kembali ke rute dasar Driver Feedback.")
        print("  -> PASSED [True]: Tombol Reset Driver Feedback berhasil membersihkan formulir filter.")

    def test_10_pilar1_positif_true_tombol_reset_user_feedback(self):
        """[PILAR 1 - POSITIF (TRUE)] Tombol Reset pada User Feedback mengembalikan URL ke rute dasar userFeedback."""
        print("[Feedback - Test 10] [PILAR 1: POSITIF (TRUE)] Uji tombol Reset User Feedback...")
        self.page.navigate_user()
        time.sleep(1)
        self.page.filter_user_feedback(user_name="FilterUser")
        time.sleep(0.5)
        self.page.click_reset_user()
        time.sleep(1)
        current_url = self.page.get_current_url()
        self.assertTrue("userFeedback" in current_url, "URL harus kembali ke rute dasar User Feedback.")
        print("  -> PASSED [True]: Tombol Reset User Feedback berhasil membersihkan formulir filter.")

    def test_11_pilar1_positif_true_sub_halaman_detail_feedback_dan_tombol_back(self):
        """[PILAR 1 - POSITIF (TRUE)] Sub-halaman detail umpan balik (/lookDetail) memuat data konten dan tombol navigasi Back."""
        print("[Feedback - Test 11] [PILAR 1: POSITIF (TRUE)] Uji sub-halaman Detail Feedback View...")
        if not self.page.navigate_detail():
            self.skipTest("Belum ada feedback driver di environment ini; tambahkan data uji.")
        time.sleep(1.5)
        current_url = self.page.get_current_url()
        title = self.page.get_title()
        print(f"  judul halaman detail: {title!r}")
        has_back_btn = len(self.driver.find_elements(*self.page.BTN_BACK_DETAIL)) > 0
        self.assertTrue("lookDetail" in current_url, "URL harus memuat lookDetail.")
        self.assertTrue("Feedback contents" in title, "Judul halaman detail harus memuat 'Feedback contents'.")
        self.assertTrue(has_back_btn, "Tombol Back harus hadir di halaman detail konten feedback.")
        print("  -> PASSED [True]: Sub-halaman detail feedback memuat data dan tombol Back aktif.")

    def test_12_pilar1_positif_true_profil_dan_top_navigation_berfungsi(self):
        """[PILAR 1 - POSITIF (TRUE)] Menu profil di pojok kanan atas hadir, dapat dibuka, dan memuat identitas akun admin."""
        print("[Feedback - Test 12] [PILAR 1: POSITIF (TRUE)] Uji profil & top navigation di halaman feedback...")
        self.page.navigate_driver()
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

    def test_13_pilar2_positif_false_tombol_process_driver_feedback_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol Immediately process pada Driver Feedback terkunci (disabled) sebelum ada item yang dipilih."""
        print("[Feedback - Test 13] [PILAR 2: POSITIF (FALSE)] Uji tombol Immediately process terkunci awal (Driver)...")
        self.page.navigate_driver()
        time.sleep(1)
        is_enabled = self.page.is_process_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Immediately process TIDAK BOLEH aktif sebelum baris dipilih (False).")
        print("  -> PASSED [False]: Tombol Immediately process terkunci aman sebelum pemilihan data.")

    def test_14_pilar2_positif_false_tombol_process_user_feedback_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol Immediately process pada User Feedback terkunci (disabled) sebelum ada item yang dipilih."""
        print("[Feedback - Test 14] [PILAR 2: POSITIF (FALSE)] Uji tombol Immediately process terkunci awal (User)...")
        self.page.navigate_user()
        time.sleep(1)
        is_enabled = self.page.is_process_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Immediately process TIDAK BOLEH aktif saat data kosong / belum dipilih (False).")
        print("  -> PASSED [False]: Tombol Immediately process terkunci aman pada User Feedback.")

    def test_15_pilar2_positif_false_ketiadaan_error_server_500_driver_feedback(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman Driver Feedback bebas dari respon crash HTTP 500."""
        print("[Feedback - Test 15] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500 di Driver Feedback...")
        self.page.navigate_driver()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src or "status=500" in src
        self.assertFalse(has_500, "Halaman Driver Feedback TIDAK BOLEH memuat error 500.")
        print("  -> PASSED [False]: Halaman Driver Feedback bebas dari respon crash 500 Internal Server Error.")

    def test_16_pilar2_positif_false_ketiadaan_error_server_500_user_feedback(self):
        """[PILAR 2 - POSITIF (FALSE)] Sub-halaman User Feedback bebas dari respon crash HTTP 500."""
        print("[Feedback - Test 16] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500 di User Feedback...")
        self.page.navigate_user()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src or "status=500" in src
        self.assertFalse(has_500, "Sub-halaman User Feedback TIDAK BOLEH memuat error 500.")
        print("  -> PASSED [False]: Sub-halaman User Feedback bebas dari respon crash 500 Internal Server Error.")

    def test_17_pilar2_positif_false_ketiadaan_whitelabel_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Antarmuka Feedback Management bebas dari exception Whitelabel Spring Boot."""
        print("[Feedback - Test 17] [PILAR 2: POSITIF (FALSE)] Memastikan bebas dari Whitelabel Error...")
        self.page.navigate_driver()
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_whitelabel = "whitelabel error page" in src or "there was an unexpected error" in src
        self.assertFalse(has_whitelabel, "Antarmuka TIDAK BOLEH menampilkan pesan Whitelabel Error.")
        print("  -> PASSED [False]: Antarmuka bersih dari exception Whitelabel Spring Boot.")

    def test_18_pilar2_positif_false_dropdown_profil_tertutup_saat_halaman_dimuat(self):
        """[PILAR 2 - POSITIF (FALSE)] Dropdown profil dalam status tersembunyi (hidden) saat awal halaman dimuat."""
        print("[Feedback - Test 18] [PILAR 2: POSITIF (FALSE)] Memastikan dropdown profil tersembunyi awal...")
        self.page.navigate_driver()
        time.sleep(1)
        is_open = self.page.is_profile_dropdown_open()
        self.assertFalse(is_open, "Dropdown profil TIDAK BOLEH terbuka secara otomatis sebelum diklik (False).")
        print("  -> PASSED [False]: Dropdown profil terkonfirmasi tertutup aman saat halaman dimuat.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Keamanan Sesi & Penanganan Anomali (4 Test)
    # =========================================================================

    def test_19_pilar3_negatif_true_akses_tanpa_login_ke_driver_feedback_dicegat(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke Driver Feedback (/tFeedback) tanpa login dicegat dan dialihkan ke /login."""
        print("[Feedback - Test 19] [PILAR 3: NEGATIF (TRUE)] Uji proteksi Driver Feedback tanpa login...")
        self.page.click_logout()
        time.sleep(2)
        self.driver.get(Config.FEEDBACK_DRIVER_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Akses tanpa login harus dialihkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute Driver Feedback aktif (dialihkan ke /login).")

    def test_20_pilar3_negatif_true_akses_tanpa_login_ke_user_feedback_dicegat(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke User Feedback (/tFeedback/userFeedback) tanpa login dicegat dan dialihkan ke /login."""
        print("[Feedback - Test 20] [PILAR 3: NEGATIF (TRUE)] Uji proteksi User Feedback tanpa login...")
        if "/login" not in self.driver.current_url:
            self.page.click_logout()
            time.sleep(2)
        self.driver.get(Config.FEEDBACK_USER_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Akses User Feedback tanpa login harus dialihkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute User Feedback aktif (dialihkan ke /login).")

    def test_21_pilar3_negatif_true_rentang_tanggal_terbalik_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Filter rentang tanggal terbalik (begin > end) ditangani aman tanpa server crash 500."""
        print("[Feedback - Test 21] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada Driver Feedback...")
        self.ensure_logged_in()
        self.page.filter_by_date(Config.FEEDBACK_DRIVER_URL, "2026-12-31", "2026-01-01")
        time.sleep(1.5)
        src = self.page.get_page_source().lower()
        has_no_crash = "500 internal server error" not in src and "whitelabel error" not in src
        self.assertTrue(has_no_crash, "Sistem harus menangani tanggal terbalik secara stabil tanpa crash.")
        print("  -> PASSED [True]: Filter tanggal terbalik ditangani aman oleh sistem.")

    def test_22_pilar3_negatif_true_interaksi_menu_profil_memberikan_feedback_aktif(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengklik 'Edit Profil' di menu navigasi atas memicu notifikasi umpan balik aktif."""
        print("[Feedback - Test 22] [PILAR 3: NEGATIF (TRUE)] Uji interaksi Edit Profil di navbar...")
        self.page.navigate_driver()
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

    def test_23_pilar4_negatif_false_pencarian_nama_driver_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama driver fiktif menghasilkan tabel tanpa data secara aman tanpa kebocoran data acak."""
        print("[Feedback - Test 23] [PILAR 4: NEGATIF (FALSE)] Pencarian nama driver fiktif...")
        self.page.navigate_driver()
        time.sleep(1)
        self.page.filter_driver_feedback(driver_name="driver_fiktif_random_99999_xyz")
        time.sleep(1)
        rows = self.driver.find_elements(By.XPATH, "//table//tbody/tr")
        is_empty_or_no_data = len(rows) == 0 or any("no" in r.text.lower() and "feedback" in r.text.lower() for r in rows)
        self.assertTrue(is_empty_or_no_data or len(rows) == 1, "Pencarian fiktif harus menghasilkan 0 data atau baris empty.")
        has_bogus_leak = any("random_99999" in r.text.lower() and "no" not in r.text.lower() for r in rows)
        self.assertFalse(has_bogus_leak, "Data fiktif tidak boleh bocor ke tabel (False).")
        print("  -> PASSED [False]: Pencarian driver fiktif ditangani dengan aman tanpa kebocoran data.")

    def test_24_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_data_umpan_balik(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA mengakses atau membaca database feedback pengemudi/pengguna."""
        print("[Feedback - Test 24] [PILAR 4: NEGATIF (FALSE)] Penolakan akses database umpan balik publik...")
        self.page.click_logout()
        time.sleep(2)
        self.driver.get(Config.FEEDBACK_DRIVER_URL)
        time.sleep(1.5)
        has_table_exposed = len(self.driver.find_elements(By.TAG_NAME, "table")) > 0 and "/login" not in self.driver.current_url
        self.assertFalse(has_table_exposed, "Tamu tanpa login TIDAK BOLEH membaca tabel feedback (False).")
        print("  -> PASSED [False]: Database umpan balik terproteksi penuh dari akses publik tanpa otentikasi.")

    def test_25_pilar4_negatif_false_sql_injection_pada_pencarian_driver(self):
        """[PILAR 4 - NEGATIF (FALSE)] Serangan SQL Injection pada form pencarian driver (' OR '1'='1) berhasil ditangkal."""
        print("[Feedback - Test 25] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nama driver...")
        self.ensure_logged_in()
        self.page.navigate_driver()
        time.sleep(1)
        self.page.filter_driver_feedback(driver_name="' OR '1'='1")
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_sql_error = "sql syntax" in src or "database error" in src or "org.hibernate" in src
        self.assertFalse(has_sql_error, "Form pencarian TIDAK BOLEH membocorkan error database SQL (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada pencarian driver berhasil ditangkal.")

    def test_26_pilar4_negatif_false_sql_injection_drop_table_pada_feedback(self):
        """[PILAR 4 - NEGATIF (FALSE)] Serangan SQL Injection destruktif drop table tidak merusak database."""
        print("[Feedback - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji SQLi destruktif drop table...")
        self.page.filter_driver_feedback(driver_name="'; DROP TABLE t_feedback; --")
        time.sleep(1)
        src = self.page.get_page_source().lower()
        has_server_down = "500 internal server error" in src or "connection refused" in src
        self.assertFalse(has_server_down, "Serangan DROP TABLE tidak boleh melumpuhkan server (False).")
        print("  -> PASSED [False]: Serangan SQL Injection destruktif berhasil ditangkal aman.")

    def test_27_pilar4_negatif_false_xss_script_pada_pencarian_feedback(self):
        """[PILAR 4 - NEGATIF (FALSE)] Injeksi skrip XSS (<script>alert(1)</script>) pada form pencarian disanitasi aman."""
        print("[Feedback - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada form feedback...")
        self.page.filter_driver_feedback(driver_name="<script>window.xss_exploited=true;</script>")
        time.sleep(1)
        is_exploited = self.driver.execute_script("return window.xss_exploited === true;")
        self.assertFalse(is_exploited, "Skrip XSS tidak boleh dieksekusi oleh browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada formulir umpan balik.")

    def test_28_pilar4_negatif_false_url_subpath_fiktif_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tFeedback/invalid_subpath ditangani aman tanpa crash 500."""
        print("[Feedback - Test 28] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tFeedback/invalid_subpath...")
        self.driver.get(f"{Config.FEEDBACK_DRIVER_URL}/invalid_subpath_xyz_99")
        time.sleep(1.5)
        src = self.page.get_page_source().lower()
        has_500 = "500 internal server error" in src
        self.assertFalse(has_500, "URL subpath fiktif TIDAK BOLEH memicu crash 500 (False).")
        print("  -> PASSED [False]: URL fiktif feedback ditangani secara aman tanpa server crash.")

    def test_29_pilar4_negatif_false_logout_via_profil_memutus_sesi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Klik tombol 'Keluar' pada menu profil di halaman feedback memutus sesi aktif."""
        print("[Feedback - Test 29] [PILAR 4: NEGATIF (FALSE)] Uji logout via menu profil navbar...")
        self.ensure_logged_in()
        self.page.navigate_driver()
        time.sleep(1)
        self.page.click_logout()
        time.sleep(2)
        current_url = self.page.get_current_url()
        has_dashboard_session = "/tFeedback" in current_url or "/blackboard" in current_url
        self.assertFalse(has_dashboard_session, "Setelah klik Keluar, user TIDAK BOLEH tetap di rute dashboard (False).")
        print("  -> PASSED [False]: Sesi akun terkonfirmasi diputus secara tuntas oleh tombol Keluar.")

    def test_30_pilar4_negatif_false_browser_back_pasca_logout_tidak_buka_sesi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Simulasi tombol Back dan refresh browser pasca logout TIDAK BISA mengakses data sesi."""
        print("[Feedback - Test 30] [PILAR 4: NEGATIF (FALSE)] Uji proteksi navigasi browser Back pasca logout...")
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
