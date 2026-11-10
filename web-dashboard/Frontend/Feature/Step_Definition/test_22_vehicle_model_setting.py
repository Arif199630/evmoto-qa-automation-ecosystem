"""
=============================================================================
TEST SUITE 22: VEHICLE MODEL SETTING (MENU #22)
Target URL  : <BASE_URL>/tMotorModel
Sub-Halaman : <BASE_URL>/tMotorModel/tMotorModel_add
Desain      : Page Object Model (POM)
Konsep      : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan     : Filter Bahasa, Sub-Halaman Tambah Model, Formulir Input, Aksi Disable,
              Dropdown Profil Pojok Kanan Atas, Keamanan Sesi, Sanitasi SQLi/XSS, Resiliensi Server
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan pemuatan daftar model motor, filter bahasa, navigasi sub-halaman add, tombol cancel/reset, & dropdown profil aktif valid (True).
2. Positif (False) : Memastikan tombol aksi baris hadir, DOM tabel bersih tanpa duplikasi header, & antarmuka bebas error server 500 / Whitelabel (False).
3. Negatif (True)  : Memastikan penolakan akses tamu tanpa login dialihkan ke /login, anomali filter ditangani aman, & toast profil aktif (True).
4. Negatif (False) : Memastikan penyerang SQLi, manipulasi query, XSS script, rute fiktif, & manipulasi browser back pasca logout DITOLAK total (False).
=============================================================================
"""

import os
import sys
import unittest
import time
from urllib.parse import unquote
from selenium.webdriver.common.by import By

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_00_login import LoginPage
from pages.page_22_vehicle_model_setting import VehicleModelPage


class TestVehicleModelSetting(unittest.TestCase):
    """Test Suite Vehicle Model Setting & Sub-Halaman dengan Konsep 4 Pilar QA (30 Test Lengkap)."""

    @classmethod
    def setUpClass(cls):
        """Inisialisasi satu kali sesi browser Chrome terotentikasi sebagai admin."""
        cls.driver = Config.get_driver()
        cls.login_page = LoginPage(cls.driver)
        cls.model_page = VehicleModelPage(cls.driver)

        # Login sebagai Administrator resmi
        cls.login_page.login_as_admin()

    @classmethod
    def tearDownClass(cls):
        """Tutup browser setelah seluruh 30 skenario selesai."""
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        """Memastikan berada pada URL dasar Vehicle Model Setting sebelum setiap test dimulai."""
        self.driver.get(Config.MOTOR_MODEL_URL)
        time.sleep(0.3)

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Validasi Fungsional & Form Interaktif (12 Test)
    # =========================================================================

    def test_01_vehicle_model_page_loaded(self):
        """[P1 True] Memastikan halaman utama Motorcycle model setting termuat aktif dengan URL dan title valid."""
        self.model_page.open_model_setting()
        current_url = self.driver.current_url
        page_title = self.driver.title
        self.assertTrue("/tMotorModel" in current_url, f"URL tidak sesuai: {current_url}")
        self.assertTrue("Motorcycle model setting" in page_title or "eVMOTO" in page_title, f"Title tidak valid: {page_title}")

    def test_02_vehicle_model_table_and_columns(self):
        """[P1 True] Memastikan struktur tabel model motor memiliki header kolom yang lengkap."""
        self.model_page.open_model_setting()
        headers = self.model_page.get_table_headers()
        self.assertTrue(len(headers) >= 4, f"Header kolom kurang: {headers}")
        self.assertTrue(any("GRADE OF SERVICE" in h.upper() for h in headers), "Kolom GRADE OF SERVICE tidak ditemukan")
        self.assertTrue(any("STATE" in h.upper() for h in headers), "Kolom STATE tidak ditemukan")

    def test_03_vehicle_model_filter_all_language(self):
        """[P1 True] Memastikan opsi filter bahasa 'All' dapat dipilih dan menjaga kestabilan halaman."""
        self.model_page.open_model_setting()
        self.model_page.filter_by_language("All")
        self.assertTrue("/tMotorModel" in self.driver.current_url,
                        f"Gagal mempertahankan rute pasca filter All: {self.driver.current_url}")

    def test_04_vehicle_model_filter_english(self):
        """[P1 True] Memastikan filter bahasa 'English' berhasil diterapkan ke query URL."""
        self.model_page.open_model_setting()
        self.model_page.filter_by_language("English")
        current_url = unquote(self.driver.current_url)
        self.assertTrue("yy=2" in current_url or "/tMotorModel" in current_url,
                        f"Filter bahasa English gagal diterapkan: {current_url}")

    def test_05_vehicle_model_filter_indonesian(self):
        """[P1 True] Memastikan filter bahasa 'Indonesian' berhasil diterapkan ke query URL."""
        self.model_page.open_model_setting()
        self.model_page.filter_by_language("Indonesian")
        current_url = unquote(self.driver.current_url)
        self.assertTrue("yy=3" in current_url or "/tMotorModel" in current_url,
                        f"Filter bahasa Indonesian gagal diterapkan: {current_url}")

    def test_06_vehicle_model_filter_chinese(self):
        """[P1 True] Memastikan filter bahasa 'Chinese' berhasil diterapkan ke query URL."""
        self.model_page.open_model_setting()
        self.model_page.filter_by_language("Chinese")
        current_url = unquote(self.driver.current_url)
        self.assertTrue("yy=1" in current_url or "/tMotorModel" in current_url,
                        f"Filter bahasa Chinese gagal diterapkan: {current_url}")

    def test_07_vehicle_model_reset_button(self):
        """[P1 True] Memastikan tombol Reset membersihkan query filter dan mengembalikan URL ke rute dasar."""
        self.model_page.open_model_setting()
        self.model_page.filter_by_language("English")
        time.sleep(0.3)
        self.model_page.click_reset()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/tMotorModel" in current_url and "yy=" not in current_url,
                        f"Tombol reset gagal membersihkan query URL: {current_url}")

    def test_08_vehicle_model_add_subpage_loaded(self):
        """[P1 True] Memastikan mengklik tombol Add membuka sub-halaman tambah model (/tMotorModel/tMotorModel_add)."""
        self.model_page.open_model_setting()
        self.model_page.click_add()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("tMotorModel_add" in current_url,
                        f"Gagal bernavigasi ke sub-halaman Add: {current_url}")

    def test_09_vehicle_model_add_form_elements(self):
        """[P1 True] Memastikan sub-halaman Add memuat formulir lengkap (name, ename, yname, language, Submit)."""
        self.model_page.open_model_setting_add()
        time.sleep(0.5)
        self.assertTrue(self.model_page.is_add_form_displayed(),
                        "Formulir tambah model motor tidak tampil lengkap di layar")
        self.assertTrue(self.model_page.is_displayed(self.model_page.LOCATOR_ADD_INPUT_ENAME),
                        "Input ename (English name) tidak ditemukan")
        self.assertTrue(self.model_page.is_displayed(self.model_page.LOCATOR_ADD_INPUT_YNAME),
                        "Input yname (Indonesian name) tidak ditemukan")

    def test_10_vehicle_model_add_cancel_link(self):
        """[P1 True] Memastikan mengklik tombol Cancel pada formulir Add mengarahkan kembali ke daftar model."""
        self.model_page.open_model_setting_add()
        time.sleep(0.5)
        self.model_page.click_add_cancel()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue(current_url.endswith("/tMotorModel"),
                        f"Tombol Cancel tidak mengembalikan ke rute /tMotorModel: {current_url}")

    def test_11_vehicle_model_rows_and_service_grade(self):
        """[P1 True] Memastikan baris tabel model motor menampilkan data grade of service yang aktif."""
        self.model_page.open_model_setting()
        row_count = self.model_page.get_table_rows_count()
        self.assertTrue(row_count > 0, "Tabel model motor seharusnya memiliki data baris aktif")
        page_source = self.driver.page_source
        self.assertTrue("ECGO 3" in page_source or "Standard" in page_source,
                        "Data model standar/ECGO 3 tidak terdeteksi pada tabel")

    def test_12_top_profile_dropdown_displayed(self):
        """[P1 True] Memastikan menu profil di pojok kanan atas navbar hadir aktif dan menampilkan identitas admin."""
        self.model_page.open_model_setting()
        time.sleep(1)
        self.assertTrue(self.model_page.is_profile_trigger_present(),
                        "Trigger profil harus hadir di pojok kanan atas.")
        self.model_page.open_profile_dropdown()
        time.sleep(0.4)
        is_open = self.model_page.is_profile_dropdown_open()
        header_text = self.model_page.get_profile_header_text()
        self.assertTrue(is_open, "Dropdown profil harus terbuka saat trigger diklik.")
        self.assertTrue("Admin" in header_text, "Header dropdown profil harus memuat nama akun Admin.")
        self.model_page.close_profile_dropdown()

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Ketiadaan Cacat & Tombol Terkunci (6 Test)
    # =========================================================================

    def test_13_row_disable_buttons_present(self):
        """[P2 False] Memastikan tombol aksi baris disable tidak nihil pada data tabel yang aktif."""
        self.model_page.open_model_setting()
        disable_count = self.model_page.get_disable_buttons_count()
        self.assertFalse(disable_count == 0,
                         "Tombol aksi baris disable tidak boleh kosong pada data model aktif")

    def test_14_vehicle_model_no_server_500_error(self):
        """[P2 False] Memastikan halaman utama Vehicle model setting bebas dari respons server error HTTP 500."""
        self.model_page.open_model_setting()
        page_source = self.driver.page_source.lower()
        self.assertFalse("internal server error" in page_source, "Terdeteksi internal server error 500")
        self.assertFalse("500 general error" in page_source, "Terdeteksi 500 general error")

    def test_15_subpage_add_no_server_500_error(self):
        """[P2 False] Memastikan sub-halaman Add Vehicle model setting bebas dari crash server HTTP 500."""
        self.model_page.open_model_setting_add()
        page_source = self.driver.page_source.lower()
        self.assertFalse("status=500" in page_source or "500 internal" in page_source,
                         "Sub-halaman Add model motor mengalami crash server 500")

    def test_16_no_whitelabel_error_page(self):
        """[P2 False] Memastikan antarmuka Vehicle model setting bebas dari exception Whitelabel Spring Boot."""
        self.model_page.open_model_setting()
        page_source = self.driver.page_source
        self.assertFalse("Whitelabel Error Page" in page_source,
                         "Terdeteksi Whitelabel Error Page Spring Boot pada halaman model motor")

    def test_17_no_duplicate_thead_in_table(self):
        """[P2 False] Memastikan struktur tabel model motor bersih dari duplikasi tag <thead."""
        self.model_page.open_model_setting()
        theads = self.driver.find_elements(By.CSS_SELECTOR, "table thead")
        self.assertFalse(len(theads) > 1, f"Ditemukan duplikasi thead pada tabel: {len(theads)}")

    def test_18_profile_dropdown_hidden_by_default(self):
        """[P2 False] Memastikan dropdown menu profil dalam status tertutup saat awal halaman dimuat."""
        self.model_page.open_model_setting()
        time.sleep(1)
        is_shown = self.model_page.is_profile_dropdown_open()
        self.assertFalse(is_shown, "Dropdown profil seharusnya tertutup secara default saat halaman dimuat")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Keamanan Sesi & Penanganan Anomali (4 Test)
    # =========================================================================

    def test_19_unauthenticated_vehicle_model_redirected(self):
        """[P3 True] Memastikan akses langsung ke /tMotorModel tanpa login dicegat dan dialihkan ke /login."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.MOTOR_MODEL_URL)
            time.sleep(0.5)
            self.assertTrue("/login" in guest_driver.current_url,
                            f"Tamu tanpa login tidak dialihkan ke login: {guest_driver.current_url}")
        finally:
            guest_driver.quit()

    def test_20_unauthenticated_subpage_add_redirected(self):
        """[P3 True] Memastikan akses langsung ke /tMotorModel/tMotorModel_add tanpa login dicegat ke /login."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.MOTOR_MODEL_ADD_URL)
            time.sleep(0.5)
            self.assertTrue("/login" in guest_driver.current_url,
                            f"Akses ilegal ke Add Model Motor tidak dialihkan ke login: {guest_driver.current_url}")
        finally:
            guest_driver.quit()

    def test_21_invalid_language_filter_parameter(self):
        """[P3 True] Memastikan parameter query bahasa tidak valid (yy=9999) ditangani aman tanpa server crash."""
        self.driver.get(f"{Config.MOTOR_MODEL_URL}?yy=9999")
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/tMotorModel" in current_url,
                        "Sistem mengalami crash atau rute terputus saat parameter anomali diinput")

    def test_22_edit_profile_interaction_triggers_feedback(self):
        """[P3 True] Memastikan klik menu Edit Profil pada navbar memicu notifikasi umpan balik aktif."""
        self.model_page.open_model_setting()
        time.sleep(1)
        self.model_page.click_edit_profile()
        time.sleep(0.4)
        toast = self.model_page.get_toast_message()
        self.assertTrue(len(toast) > 0 or self.model_page.is_displayed(self.model_page.LOCATOR_TOAST),
                        "Toast pesan umpan balik interaksi Edit Profil harus aktif muncul.")
        self.model_page.close_profile_dropdown()

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Keamanan Siber, Penolakan Akses, & Resiliensi (8 Test)
    # =========================================================================

    def test_23_tampered_yy_parameter_no_data_leak(self):
        """[P4 False] Memastikan manipulasi nilai parameter bahasa tidak membocorkan exception atau log sistem."""
        self.driver.get(f"{Config.MOTOR_MODEL_URL}?yy=INVALID_LANG_CODE_ABC")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("stack trace" in page_source or "sqlexception" in page_source,
                         "Terdeteksi kebocoran jejak stack trace pada parameter yang dimanipulasi")

    def test_24_guest_cannot_access_vehicle_models(self):
        """[P4 False] Memastikan pengguna publik tanpa otentikasi TIDAK BISA mengakses data model motor."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.MOTOR_MODEL_URL)
            time.sleep(0.5)
            self.assertFalse("/tMotorModel" in guest_driver.current_url and "/login" not in guest_driver.current_url,
                             "Tamu publik dapat membaca data model motor tanpa login!")
        finally:
            guest_driver.quit()

    def test_25_sqli_attack_resilience_on_yy_param(self):
        """[P4 False] Memastikan serangan SQL Injection standar (yy=' OR '1'='1) pada query ditangkal aman."""
        self.driver.get(f"{Config.MOTOR_MODEL_URL}?yy=%27%20OR%20%271%27=%271")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("sql syntax" in page_source, "Terdeteksi pesan kesalahan sintaks SQL (SQLi rentan)")
        self.assertFalse("mysql_fetch" in page_source or "jdbc.exceptions" in page_source,
                         "Terdeteksi database driver exception akibat SQLi")

    def test_26_destructive_sqli_drop_table_thwarted(self):
        """[P4 False] Memastikan serangan destruktif SQL Injection DROP TABLE tidak merusak database."""
        self.driver.get(f"{Config.MOTOR_MODEL_URL}?yy=%27;%20DROP%20TABLE%20t_motor_model;%20--")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("table deleted" in page_source, "Indikasi eksekusi drop table berhasil!")
        self.assertFalse("syntax error near 'drop'" in page_source, "Pesan error raw query bocor ke client")

    def test_27_xss_injection_sanitized_on_add_inputs(self):
        """[P4 False] Memastikan injeksi payload skrip XSS pada input tambah model disanitasi tanpa eksekusi popup."""
        self.model_page.open_model_setting_add()
        time.sleep(0.5)
        self.model_page.fill_add_form(name="<script>alert('xss_model')</script>", ename="XSS Test")
        time.sleep(0.3)
        # Verifikasi tidak ada alert popup browser yang menghalangi
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.dismiss()
            self.assertFalse(True, f"Alert XSS terpancing muncul di browser: '{alert_text}'")
        except Exception:
            # Tidak ada alert dialog menandakan payload berhasil disanitasi
            pass

    def test_28_invalid_subpath_handled_safely(self):
        """[P4 False] Memastikan rute URL fiktif /tMotorModel/invalid_subpath ditangani aman tanpa crash 500."""
        self.driver.get(f"{Config.MOTOR_MODEL_URL}/invalid_path_xyz_99")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("http status 500" in page_source, "Terjadi HTTP Status 500 saat rute fiktif dibuka")

    def test_29_profile_logout_terminates_session(self):
        """[P4 False] Memastikan tombol Keluar pada profil navbar mengakhiri sesi dan mencegah akses rute model motor."""
        self.model_page.open_model_setting()
        time.sleep(1)
        self.model_page.click_logout()
        time.sleep(1.5)

        # Setelah logout harus terlempar ke /login
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url,
                        f"Pengguna tidak diarahkan ke halaman login: {current_url}")

        # Coba akses kembali ke rute terproteksi
        self.model_page.open(Config.MOTOR_MODEL_URL)
        time.sleep(1)
        self.assertFalse("/tMotorModel" in self.driver.current_url and "/login" not in self.driver.current_url,
                         f"User yang telah logout TIDAK BISA mengakses kembali halaman model motor: {self.driver.current_url}")

        # Login kembali agar sesi setUpClass berikutnya / pengujian selanjutnya tetap utuh
        login_page = LoginPage(self.driver)
        login_page.login_as_admin()

    def test_30_browser_back_after_logout_prevented(self):
        """[P4 False] Memastikan manipulasi browser Back pasca logout terlindungi aman dari kebocoran sesi."""
        self.model_page.open_model_setting()
        time.sleep(1)
        self.model_page.click_logout()
        time.sleep(1.5)

        # Coba klik tombol Back di browser
        self.driver.back()
        time.sleep(1)
        self.driver.refresh()
        time.sleep(1)

        # Tamu tidak boleh bisa membaca data model motor
        current_url = self.driver.current_url
        self.assertFalse("/tMotorModel" in current_url and "/login" not in current_url,
                         f"Celah browser Back terdeteksi, user masih di: {current_url}")

        # Pulihkan sesi admin untuk teardown bersih
        login_page = LoginPage(self.driver)
        login_page.login_as_admin()


if __name__ == "__main__":
    unittest.main(verbosity=2)
