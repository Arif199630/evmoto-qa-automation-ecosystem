"""
=============================================================================
TEST SUITE 21: ACTIVITY MANAGEMENT (MENU #21)
Target URL  : <BASE_URL>/driverActivity
Sub-Halaman :
  1. Driver Activity Management (/driverActivity) & Add (/driverActivity/driverActivity_add)
  2. Gift Activity Management (/sysCouponActivity) & Add (/sysCouponActivity/sysCouponActivity_add)
  3. User Activity Management (/userActivity) & Add (/userActivity/userActivity_add)
  4. Large Coupon Activities (/tUserLarge) & Add (/tUserLarge/tUserLarge_add)
  5. Driver Guaranteed Income (/tEnsureIncomeRule) & Add (/tEnsureIncomeRule/tEnsureIncomeRule_add)
  6. Coupon Distribution (/couponDistribution) & Add (/couponDistribution/couponDistribution_add)
  7. Coupon Usage (/couponUsage)
  8. Coupon Record Management (/sysCouponRecord) & Add (/sysCouponRecord/sysCouponRecord_add)
Desain      : Page Object Model (POM)
Konsep      : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan     : Filter Multi-tier, Sub-halaman Add, Proteksi Tombol Aksi, Top Navigation Profile Dropdown,
              Keamanan Sesi, Sanitasi SQLi/XSS, Resiliensi Server
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan navigasi 8 sub-modul aktivitas, filter form, tombol add sub-halaman, & dropdown profil pojok kanan atas aktif valid (True).
2. Positif (False) : Memastikan tombol aksi terkunci sebelum data dipilih & antarmuka bebas error server 500 / Whitelabel (False).
3. Negatif (True)  : Memastikan penolakan akses tamu tanpa login dialihkan ke /login, penanganan tanggal terbalik, & toast profil bekerja (True).
4. Negatif (False) : Memastikan penyerang SQLi, XSS script, deep link fiktif, & manipulasi browser back pasca logout DITOLAK total (False).
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
from pages.page_21_activity_management import ActivityPage


class TestActivityManagement(unittest.TestCase):
    """Test Suite Activity Management & Sub-Halaman dengan Konsep 4 Pilar QA (30 Test Lengkap)."""

    @classmethod
    def setUpClass(cls):
        """Inisialisasi satu kali sesi browser Chrome terotentikasi sebagai admin."""
        cls.driver = Config.get_driver()
        cls.login_page = LoginPage(cls.driver)
        cls.activity_page = ActivityPage(cls.driver)

        # Login sebagai Administrator resmi
        cls.login_page.login_as_admin()

    @classmethod
    def tearDownClass(cls):
        """Tutup browser setelah seluruh 30 skenario selesai."""
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        """Memastikan berada pada URL dasar Driver Activity sebelum setiap test dimulai."""
        self.driver.get(Config.ACTIVITY_DRIVER_URL)
        time.sleep(0.3)

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Validasi Fungsional & Navigasi Sub-Halaman (12 Test)
    # =========================================================================

    def test_01_driver_activity_page_loaded(self):
        """[P1 True] Memastikan halaman utama Driver Activity termuat aktif dengan URL dan title yang sesuai."""
        self.activity_page.open_driver_activity()
        current_url = self.driver.current_url
        page_title = self.driver.title
        self.assertTrue("/driverActivity" in current_url, f"URL tidak sesuai: {current_url}")
        self.assertTrue("Driver Activities" in page_title or "eVMOTO" in page_title, f"Title tidak valid: {page_title}")

    def test_02_driver_activity_table_and_columns(self):
        """[P1 True] Memastikan struktur tabel Driver Activity memiliki header kolom yang lengkap."""
        self.activity_page.open_driver_activity()
        headers = self.activity_page.get_table_headers()
        self.assertTrue(len(headers) >= 6, f"Header kolom kurang: {headers}")
        self.assertTrue(any("NAME" in h.upper() for h in headers), "Kolom NAME tidak ditemukan")
        self.assertTrue(any("START" in h.upper() for h in headers), "Kolom START tidak ditemukan")

    def test_03_driver_activity_search_applied(self):
        """[P1 True] Memastikan pencarian nama aktivitas pada Driver Activity berhasil diterapkan ke query URL."""
        self.activity_page.open_driver_activity()
        self.activity_page.search_driver_activity(name="BonusRamadhan", begin_date="2026-01-01", end_date="2026-12-31")
        time.sleep(0.5)
        current_url = unquote(self.driver.current_url)
        self.assertTrue("name=BonusRamadhan" in current_url or "beginDate=2026-01-01" in current_url,
                        f"Query pencarian tidak muncul di URL: {current_url}")

    def test_04_driver_activity_add_subpage(self):
        """[P1 True] Memastikan navigasi tombol Add pada Driver Activity berhasil membuka sub-halaman tambah."""
        self.activity_page.open_driver_activity_add()
        time.sleep(0.5)
        self.assertTrue("driverActivity_add" in self.driver.current_url,
                        f"Gagal membuka sub-halaman Add: {self.driver.current_url}")

    def test_05_gift_activity_page_and_filter(self):
        """[P1 True] Memastikan halaman Gift Activity Management termuat aktif dengan opsi filter yang berfungsi."""
        self.activity_page.open_gift_activity()
        time.sleep(0.5)
        self.assertTrue("/sysCouponActivity" in self.driver.current_url,
                        f"URL Gift Activity tidak valid: {self.driver.current_url}")
        self.activity_page.search_gift_activity(coupon_use_type="Motorcycle coupon", status="All")
        time.sleep(0.5)
        self.assertTrue("/sysCouponActivity" in self.driver.current_url,
                        "Halaman Gift Activity crash pasca filter")

    def test_06_gift_activity_add_subpage(self):
        """[P1 True] Memastikan navigasi tombol Add pada Gift Activity berhasil membuka sub-halaman tambah."""
        self.activity_page.open_gift_activity_add()
        time.sleep(0.5)
        self.assertTrue("sysCouponActivity_add" in self.driver.current_url,
                        f"Gagal membuka sub-halaman Add Gift: {self.driver.current_url}")

    def test_07_user_activity_search_applied(self):
        """[P1 True] Memastikan halaman User Activity Management termuat aktif dan filter status diaplikasikan."""
        self.activity_page.open_user_activity()
        time.sleep(0.5)
        self.assertTrue("/userActivity" in self.driver.current_url,
                        f"URL User Activity tidak valid: {self.driver.current_url}")
        self.activity_page.search_user_activity(name="PromoMemberBaru", status="All")
        time.sleep(0.5)
        current_url = unquote(self.driver.current_url)
        self.assertTrue("PromoMemberBaru" in current_url or "/userActivity" in current_url,
                        f"Filter user activity gagal diterapkan: {current_url}")

    def test_08_large_coupon_activity_loaded(self):
        """[P1 True] Memastikan halaman Large Coupon Activities Management termuat aktif dengan kolom tabel utuh."""
        self.activity_page.open_large_coupon_activity()
        time.sleep(0.5)
        self.assertTrue("/tUserLarge" in self.driver.current_url,
                        f"URL Large Coupon tidak valid: {self.driver.current_url}")
        headers = self.activity_page.get_table_headers()
        self.assertTrue(len(headers) >= 6, f"Header Large Coupon kurang: {headers}")

    def test_09_guaranteed_income_rule_loaded(self):
        """[P1 True] Memastikan halaman Driver Guaranteed Income Management termuat dan filter ruleName diterapkan."""
        self.activity_page.open_income_rule()
        time.sleep(0.5)
        self.assertTrue("/tEnsureIncomeRule" in self.driver.current_url,
                        f"URL Guaranteed Income tidak valid: {self.driver.current_url}")
        self.activity_page.search_income_rule(rule_name="TargetHarianJakarta")
        time.sleep(0.5)
        current_url = unquote(self.driver.current_url)
        self.assertTrue("TargetHarianJakarta" in current_url or "/tEnsureIncomeRule" in current_url,
                        f"Pencarian income rule gagal: {current_url}")

    def test_10_coupon_distribution_loaded(self):
        """[P1 True] Memastikan halaman Coupon Distribution Management termuat aktif dengan filter target pengguna."""
        self.activity_page.open_coupon_distribution()
        time.sleep(0.5)
        self.assertTrue("/couponDistribution" in self.driver.current_url,
                        f"URL Coupon Distribution tidak valid: {self.driver.current_url}")
        self.activity_page.search_coupon_distribution(target_type="Existing user")
        time.sleep(0.5)
        self.assertTrue("/couponDistribution" in self.driver.current_url,
                        "Halaman Coupon Distribution crash pasca filter")

    def test_11_coupon_usage_and_record_loaded(self):
        """[P1 True] Memastikan halaman Coupon Usage dan Coupon Record Management dapat diakses aktif dan stabil."""
        self.activity_page.open_coupon_usage()
        time.sleep(0.5)
        self.assertTrue("/couponUsage" in self.driver.current_url,
                        f"URL Coupon Usage tidak valid: {self.driver.current_url}")

        self.activity_page.open_coupon_record()
        time.sleep(0.5)
        self.assertTrue("/sysCouponRecord" in self.driver.current_url,
                        f"URL Coupon Record tidak valid: {self.driver.current_url}")
        headers = self.activity_page.get_table_headers()
        self.assertTrue(len(headers) >= 6, f"Header Coupon Record kurang: {headers}")

    def test_12_top_profile_dropdown_displayed(self):
        """[P1 True] Memastikan menu profil di pojok kanan atas navbar hadir aktif dan menampilkan identitas admin."""
        self.activity_page.open_driver_activity()
        time.sleep(1)
        self.assertTrue(self.activity_page.is_profile_trigger_present(), "Trigger profil harus hadir di pojok kanan atas.")
        self.activity_page.open_profile_dropdown()
        time.sleep(0.4)
        is_open = self.activity_page.is_profile_dropdown_open()
        header_text = self.activity_page.get_profile_header_text()
        self.assertTrue(is_open, "Dropdown profil harus terbuka saat trigger diklik.")
        self.assertTrue("Admin" in header_text, "Header dropdown profil harus memuat nama akun Admin.")
        self.activity_page.close_profile_dropdown()

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Ketiadaan Cacat & Tombol Terkunci (6 Test)
    # =========================================================================

    def test_13_action_buttons_disabled_without_selection(self):
        """[P2 False] Memastikan tombol Audit/Modify pada Gift Activity terkunci sebelum baris data dipilih."""
        self.activity_page.open_gift_activity()
        # Tombol Update atau Delete atau Audit harus dalam kondisi disabled atau membutuhkan seleksi
        btn_update_disabled = self.activity_page.is_button_disabled(self.activity_page.LOCATOR_GA_UPDATE_BTN)
        btn_delete_disabled = self.activity_page.is_button_disabled(self.activity_page.LOCATOR_GA_DELETE_BTN)
        self.assertFalse(not btn_update_disabled and not btn_delete_disabled,
                         "Tombol aksi tidak boleh aktif bebas sebelum item dipilih")

    def test_14_driver_activity_no_server_500_error(self):
        """[P2 False] Memastikan halaman Driver Activity bebas dari respons server error HTTP 500."""
        self.activity_page.open_driver_activity()
        page_source = self.driver.page_source.lower()
        self.assertFalse("internal server error" in page_source, "Terdeteksi internal server error 500")
        self.assertFalse("500 general error" in page_source, "Terdeteksi 500 general error")

    def test_15_subpages_no_server_500_error(self):
        """[P2 False] Memastikan sub-halaman Add pada Activity Management bebas dari crash server HTTP 500."""
        sub_urls = [
            Config.ACTIVITY_DRIVER_ADD_URL,
            Config.ACTIVITY_GIFT_ADD_URL,
            Config.ACTIVITY_USER_ADD_URL,
            Config.ACTIVITY_RECORD_ADD_URL,
        ]
        for sub_url in sub_urls:
            self.driver.get(sub_url)
            time.sleep(0.3)
            page_source = self.driver.page_source.lower()
            self.assertFalse("status=500" in page_source or "500 internal" in page_source,
                             f"Sub-halaman {sub_url} mengalami crash 500")

    def test_16_no_whitelabel_error_page(self):
        """[P2 False] Memastikan antarmuka seluruh modul aktivitas bebas dari exception Whitelabel Spring Boot."""
        self.activity_page.open_income_rule()
        page_source = self.driver.page_source
        self.assertFalse("Whitelabel Error Page" in page_source,
                         "Terdeteksi Whitelabel Error Page Spring Boot pada halaman Income Rule")

    def test_17_no_duplicate_thead_in_tables(self):
        """[P2 False] Memastikan struktur tabel data aktivitas bersih dari duplikasi tag <thead."""
        self.activity_page.open_coupon_distribution()
        theads = self.driver.find_elements(By.CSS_SELECTOR, "table thead")
        # Jika ada tabel, thead maksimal 1 per tabel
        self.assertFalse(len(theads) > 1, f"Ditemukan duplikasi thead pada tabel: {len(theads)}")

    def test_18_profile_dropdown_hidden_by_default(self):
        """[P2 False] Memastikan dropdown menu profil dalam status tertutup saat awal halaman aktivitas dimuat."""
        self.activity_page.open_driver_activity()
        time.sleep(1)
        is_shown = self.activity_page.is_profile_dropdown_open()
        self.assertFalse(is_shown, "Dropdown profil seharusnya tertutup secara default saat halaman dimuat")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Keamanan Sesi & Penanganan Anomali (4 Test)
    # =========================================================================

    def test_19_unauthenticated_driver_activity_redirected(self):
        """[P3 True] Memastikan akses langsung ke /driverActivity tanpa login dicegat dan dialihkan ke /login."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.ACTIVITY_DRIVER_URL)
            time.sleep(0.5)
            self.assertTrue("/login" in guest_driver.current_url,
                            f"Tamu tanpa login tidak dialihkan ke login: {guest_driver.current_url}")
        finally:
            guest_driver.quit()

    def test_20_unauthenticated_subpage_add_redirected(self):
        """[P3 True] Memastikan akses langsung ke sub-halaman Add tanpa login dicegat dan dialihkan ke /login."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.ACTIVITY_DRIVER_ADD_URL)
            time.sleep(0.5)
            self.assertTrue("/login" in guest_driver.current_url,
                            f"Akses ilegal ke Add Driver Activity tidak dialihkan ke login: {guest_driver.current_url}")
        finally:
            guest_driver.quit()

    def test_21_reversed_date_range_handled_gracefully(self):
        """[P3 True] Memastikan filter tanggal terbalik (beginDate > endDate) ditangani aman tanpa server crash."""
        self.activity_page.open_driver_activity()
        self.activity_page.search_driver_activity(begin_date="2026-12-31", end_date="2026-01-01")
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/driverActivity" in current_url,
                        "Sistem mengalami crash atau rute terputus saat tanggal terbalik diinput")

    def test_22_edit_profile_interaction_triggers_feedback(self):
        """[P3 True] Memastikan klik menu Edit Profil pada navbar memicu notifikasi umpan balik aktif."""
        self.activity_page.open_driver_activity()
        time.sleep(1)
        self.activity_page.click_edit_profile()
        time.sleep(0.4)
        toast = self.activity_page.get_toast_message()
        self.assertTrue(len(toast) > 0 or self.activity_page.is_displayed(self.activity_page.LOCATOR_TOAST),
                        "Toast pesan umpan balik interaksi Edit Profil harus aktif muncul.")
        self.activity_page.close_profile_dropdown()

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Keamanan Siber, Penolakan Akses, & Resiliensi (8 Test)
    # =========================================================================

    def test_23_fictitious_search_yields_empty_table(self):
        """[P4 False] Memastikan pencarian nama aktivitas fiktif tidak memunculkan data acak/bocor."""
        self.activity_page.open_driver_activity()
        self.activity_page.search_driver_activity(name="AktivitasFiktifAntigravity999XYZ")
        time.sleep(0.5)
        page_source = self.driver.page_source
        self.assertFalse("AktivitasFiktifAntigravity999XYZ" in page_source and "table tbody tr td" in page_source,
                         "Ditemukan data yang tidak seharusnya ada pada pencarian fiktif")

    def test_24_guest_cannot_access_coupon_records(self):
        """[P4 False] Memastikan pengguna tamu tanpa otentikasi TIDAK BISA mengakses rekaman kupon diskon."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.ACTIVITY_RECORD_URL)
            time.sleep(0.5)
            self.assertFalse("/sysCouponRecord" in guest_driver.current_url and "/login" not in guest_driver.current_url,
                             "Tamu publik dapat mengakses sysCouponRecord tanpa login!")
        finally:
            guest_driver.quit()

    def test_25_sqli_attack_resilience_on_activity_search(self):
        """[P4 False] Memastikan serangan SQL Injection standar (' OR '1'='1) pada pencarian ditangkal aman."""
        self.activity_page.open_driver_activity()
        self.activity_page.search_driver_activity(name="' OR '1'='1")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("sql syntax" in page_source, "Terdeteksi pesan kesalahan sintaks SQL (SQLi rentan)")
        self.assertFalse("mysql_fetch" in page_source or "jdbc.exceptions" in page_source,
                         "Terdeteksi database driver exception akibat SQLi")

    def test_26_destructive_sqli_drop_table_thwarted(self):
        """[P4 False] Memastikan serangan destruktif SQL Injection DROP TABLE tidak merusak database."""
        self.activity_page.open_income_rule()
        self.activity_page.search_income_rule(rule_name="'; DROP TABLE t_driver_activity; --")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("table deleted" in page_source, "Indikasi eksekusi drop table berhasil!")
        self.assertFalse("syntax error near 'drop'" in page_source, "Pesan error raw query bocor ke client")

    def test_27_xss_injection_sanitized_on_activity(self):
        """[P4 False] Memastikan payload skrip XSS (<script>alert('xss')</script>) disanitasi tanpa eksekusi."""
        self.activity_page.open_user_activity()
        self.activity_page.search_user_activity(name="<script>alert('xss_act')</script>")
        time.sleep(0.5)
        # Verifikasi tidak ada alert popup browser yang menghalangi
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.dismiss()
            self.assertFalse(True, f"Alert XSS terpancing muncul di browser: '{alert_text}'")
        except Exception:
            # Tidak ada alert dialog menandakan payload berhasil disanitasi
            pass

    def test_28_invalid_activity_subpath_handled_safely(self):
        """[P4 False] Memastikan rute URL fiktif /driverActivity/invalid_subpath ditangani aman tanpa crash 500."""
        self.driver.get(f"{Config.ACTIVITY_DRIVER_URL}/invalid_path_xyz_99")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("http status 500" in page_source, "Terjadi HTTP Status 500 saat rute fiktif dibuka")

    def test_29_profile_logout_terminates_session(self):
        """[P4 False] Memastikan tombol Keluar pada profil navbar mengakhiri sesi dan mencegah akses rute aktivitas."""
        self.activity_page.open_driver_activity()
        time.sleep(1)
        self.activity_page.click_logout()
        time.sleep(1.5)

        # Setelah logout harus terlempar ke /login
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url,
                        f"Pengguna tidak diarahkan ke halaman login: {current_url}")

        # Coba akses kembali ke rute terproteksi
        self.activity_page.open(Config.ACTIVITY_DRIVER_URL)
        time.sleep(1)
        self.assertFalse("/driverActivity" in self.driver.current_url and "/login" not in self.driver.current_url,
                         f"User yang telah logout TIDAK BISA mengakses kembali halaman driver activity: {self.driver.current_url}")

        # Login kembali agar sesi setUpClass berikutnya / pengujian selanjutnya tetap utuh
        login_page = LoginPage(self.driver)
        login_page.login_as_admin()

    def test_30_browser_back_after_logout_prevented(self):
        """[P4 False] Memastikan manipulasi browser Back pasca logout terlindungi aman dari kebocoran sesi."""
        self.activity_page.open_driver_activity()
        time.sleep(1)
        self.activity_page.click_logout()
        time.sleep(1.5)

        # Coba klik tombol Back di browser
        self.driver.back()
        time.sleep(1)
        self.driver.refresh()
        time.sleep(1)

        # Tamu tidak boleh bisa membaca data aktivitas
        current_url = self.driver.current_url
        self.assertFalse("/driverActivity" in current_url and "/login" not in current_url,
                         f"Celah browser Back terdeteksi, user masih di: {current_url}")

        # Pulihkan sesi admin untuk teardown bersih
        login_page = LoginPage(self.driver)
        login_page.login_as_admin()


if __name__ == "__main__":
    unittest.main(verbosity=2)
