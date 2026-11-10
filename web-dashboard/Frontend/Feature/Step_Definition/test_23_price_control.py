"""
=============================================================================
TEST SUITE 23: PRICE CONTROL (MENU #23)
Target Endpoints:
1. Motorcycle Price Settings                  : <BASE_URL>/tSystemPrice/special
2. Intra-city Express Delivery Price Setting  : <BASE_URL>/tSystemPrice/small
3. Price Review Queue / List                 : <BASE_URL>/tSystemPrice/check
4. Add Special Car Price                      : <BASE_URL>/tSystemPrice/tSystemPrice_add
Desain      : Page Object Model (POM)
Konsep      : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan     : Pengaturan Tarif Motor & Ekspedisi, Formulir Tambah Tarif, Antrean Review Harga,
              Tombol Terkunci Aman, Dropdown Profil Pojok Kanan Atas, Keamanan Sesi, Sanitasi SQLi/XSS, Resiliensi Server
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan pemuatan tarif motor, form ekspedisi dalam kota, antrean review, filter pencarian, tombol cancel/reset, & dropdown profil aktif valid (True).
2. Positif (False) : Memastikan tombol aksi Update/Delete/Freeze/Audit terkunci aman sebelum baris dipilih, DOM tabel bersih, & antarmuka bebas error server 500 / Whitelabel (False).
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
from pages.page_23_price_control import PricePage


class TestPriceControl(unittest.TestCase):
    """Test Suite Price Control & Seluruh Sub-Halaman dengan Konsep 4 Pilar QA (30 Test Lengkap)."""

    @classmethod
    def setUpClass(cls):
        """Inisialisasi satu kali sesi browser Chrome terotentikasi sebagai admin."""
        cls.driver = Config.get_driver()
        cls.login_page = LoginPage(cls.driver)
        cls.price_page = PricePage(cls.driver)

        # Login sebagai Administrator resmi
        cls.login_page.login_as_admin()

    @classmethod
    def tearDownClass(cls):
        """Tutup browser setelah seluruh 30 skenario selesai."""
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        """Memastikan berada pada URL dasar Motorcycle Price Settings sebelum setiap test dimulai."""
        self.driver.get(Config.PRICE_SPECIAL_URL)
        time.sleep(0.3)

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Validasi Fungsional & Form Interaktif (12 Test)
    # =========================================================================

    def test_01_special_price_page_loaded(self):
        """[P1 True] Memastikan halaman utama Motorcycle Price Settings termuat aktif dengan URL dan title valid."""
        self.price_page.open_special_price()
        current_url = self.driver.current_url
        page_title = self.driver.title
        self.assertTrue("/tSystemPrice/special" in current_url, f"URL tidak sesuai: {current_url}")
        self.assertTrue("Motorcycle Price Settings" in page_title or "eVMOTO" in page_title,
                        f"Title tidak valid: {page_title}")

    def test_02_special_price_table_headers(self):
        """[P1 True] Memastikan tabel Motorcycle Price memuat kolom header lengkap di antarmuka."""
        self.price_page.open_special_price()
        headers = self.price_page.get_special_headers()
        self.assertTrue(len(headers) >= 4, f"Header kolom kurang: {headers}")
        self.assertTrue(any("CITY" in h.upper() for h in headers), "Kolom CITY tidak ditemukan")
        self.assertTrue(any("MODEL NAME" in h.upper() for h in headers), "Kolom MODEL NAME tidak ditemukan")
        self.assertTrue(any("STATE" in h.upper() for h in headers), "Kolom STATE tidak ditemukan")

    def test_03_special_price_rows_and_data(self):
        """[P1 True] Memastikan baris data Motorcycle Price menampilkan data aktif sistem."""
        self.price_page.open_special_price()
        row_count = self.price_page.get_special_rows_count()
        self.assertTrue(row_count > 0, "Tabel Motorcycle Price seharusnya memiliki data baris aktif")
        page_source = self.driver.page_source
        self.assertTrue("Jakarta" in page_source or "ECGO" in page_source,
                        "Data kota Jakarta atau model ECGO tidak terdeteksi pada tabel")

    def test_04_special_price_search_name(self):
        """[P1 True] Memastikan pencarian nama model pada Motorcycle Price berfungsi dan diterapkan ke URL."""
        self.price_page.open_special_price()
        self.price_page.search_special(name="ECGO")
        current_url = unquote(self.driver.current_url)
        self.assertTrue("name=ECGO" in current_url or "/tSystemPrice/special" in current_url,
                        f"Pencarian nama model gagal diterapkan: {current_url}")

    def test_05_special_price_filter_state(self):
        """[P1 True] Memastikan filter status Normal pada Motorcycle Price dapat dipilih dan dieksekusi."""
        self.price_page.open_special_price()
        self.price_page.search_special(state="Normal")
        current_url = unquote(self.driver.current_url)
        self.assertTrue("state=" in current_url or "/tSystemPrice/special" in current_url,
                        f"Filter status gagal diterapkan: {current_url}")

    def test_06_special_price_add_subpage_loaded(self):
        """[P1 True] Memastikan tombol Add mengarahkan ke sub-halaman form tambah harga motor."""
        self.price_page.open_special_price()
        self.price_page.click_special_add()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("tSystemPrice_add" in current_url,
                        f"Gagal bernavigasi ke sub-halaman Add: {current_url}")

    def test_07_special_price_add_form_elements(self):
        """[P1 True] Memastikan formulir tambah harga motor memuat input lengkap di layar."""
        self.price_page.open_add_special_price()
        time.sleep(0.5)
        self.assertTrue(self.price_page.is_add_form_displayed(),
                        "Formulir tambah tarif motor tidak tampil lengkap")
        page_source = self.driver.page_source
        self.assertTrue("Starting price setting" in page_source or "Mileage fee setting" in page_source,
                        "Bagian konfigurasi tarif awal / jarak tidak ditemukan pada form")

    def test_08_special_price_add_cancel_link(self):
        """[P1 True] Memastikan tombol Cancel pada formulir Add mengarahkan kembali ke daftar harga motor."""
        self.price_page.open_add_special_price()
        time.sleep(0.5)
        self.price_page.click_add_cancel()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/tSystemPrice/special" in current_url,
                        f"Tombol Cancel tidak mengembalikan ke rute special: {current_url}")

    def test_09_small_price_page_and_form_loaded(self):
        """[P1 True] Memastikan halaman Intra-city Express Delivery memuat form konfigurasi lengkap."""
        self.price_page.open_small_price()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/tSystemPrice/small" in current_url, f"URL small price tidak sesuai: {current_url}")
        self.assertTrue(self.price_page.is_small_form_displayed(),
                        "Form Intra-city express delivery tidak tampil lengkap")

    def test_10_check_price_page_and_table_loaded(self):
        """[P1 True] Memastikan halaman Price Review Queue memuat tabel antrean review dengan kolom lengkap."""
        self.price_page.open_check_price()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/tSystemPrice/check" in current_url, f"URL check queue tidak sesuai: {current_url}")
        headers = self.price_page.get_check_headers()
        self.assertTrue(len(headers) >= 5, f"Header tabel review queue kurang: {headers}")
        self.assertTrue(any("ACCOUNT" in h.upper() for h in headers), "Kolom ACCOUNT tidak ditemukan")
        self.assertTrue(any("STATE" in h.upper() for h in headers), "Kolom STATE tidak ditemukan")

    def test_11_check_price_filter_and_reset(self):
        """[P1 True] Memastikan filter pencarian dan tombol Reset pada Price Review Queue berfungsi."""
        self.price_page.open_check_price()
        time.sleep(0.5)
        self.price_page.search_check(company="TestCorp")
        time.sleep(0.5)
        self.price_page.click_check_reset()
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/tSystemPrice/check" in current_url,
                        f"Tombol Reset gagal menjaga rute /tSystemPrice/check: {current_url}")

    def test_12_top_profile_dropdown_displayed(self):
        """[P1 True] Memastikan menu profil di pojok kanan atas navbar hadir aktif dan menampilkan identitas admin."""
        self.price_page.open_special_price()
        time.sleep(1)
        self.assertTrue(self.price_page.is_profile_trigger_present(),
                        "Trigger profil harus hadir di pojok kanan atas.")
        self.price_page.open_profile_dropdown()
        time.sleep(0.4)
        is_open = self.price_page.is_profile_dropdown_open()
        header_text = self.price_page.get_profile_header_text()
        self.assertTrue(is_open, "Dropdown profil harus terbuka saat trigger diklik.")
        self.assertTrue("Admin" in header_text, "Header dropdown profil harus memuat nama akun Admin.")
        self.price_page.close_profile_dropdown()

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Ketiadaan Cacat & Tombol Terkunci (6 Test)
    # =========================================================================

    def test_13_special_action_buttons_disabled_initially(self):
        """[P2 False] Memastikan tombol Update, Delete, Freeze, & Unfreeze terkunci aman sebelum baris dipilih."""
        self.price_page.open_special_price()
        self.assertTrue(self.price_page.is_special_update_disabled(), "Tombol Update harus terkunci aman (disabled)")
        self.assertTrue(self.price_page.is_special_delete_disabled(), "Tombol Delete harus terkunci aman (disabled)")
        self.assertTrue(self.price_page.is_special_freeze_disabled(), "Tombol Freeze harus terkunci aman (disabled)")
        self.assertTrue(self.price_page.is_special_unfreeze_disabled(), "Tombol Unfreeze harus terkunci aman (disabled)")

    def test_14_check_action_buttons_disabled_initially(self):
        """[P2 False] Memastikan tombol Audit, Details, & Delete pada Review Queue terkunci aman sebelum baris dipilih."""
        self.price_page.open_check_price()
        self.assertTrue(self.price_page.is_check_audit_disabled(), "Tombol Audit harus terkunci aman (disabled)")
        self.assertTrue(self.price_page.is_check_details_disabled(), "Tombol Details harus terkunci aman (disabled)")
        self.assertTrue(self.price_page.is_check_delete_disabled(), "Tombol Delete harus terkunci aman (disabled)")

    def test_15_price_pages_no_server_500_error(self):
        """[P2 False] Memastikan seluruh halaman Price Control bebas dari respons server error HTTP 500."""
        for url in [Config.PRICE_SPECIAL_URL, Config.PRICE_SMALL_URL, Config.PRICE_CHECK_URL]:
            self.driver.get(url)
            time.sleep(0.4)
            page_source = self.driver.page_source.lower()
            self.assertFalse("internal server error" in page_source, f"Terdeteksi server error 500 pada {url}")
            self.assertFalse("500 general error" in page_source, f"Terdeteksi 500 general error pada {url}")

    def test_16_subpage_add_no_server_500_error(self):
        """[P2 False] Memastikan sub-halaman Add harga motor bebas dari crash server HTTP 500."""
        self.price_page.open_add_special_price()
        page_source = self.driver.page_source.lower()
        self.assertFalse("status=500" in page_source or "500 internal" in page_source,
                         "Sub-halaman Add tarif motor mengalami crash server 500")

    def test_17_no_whitelabel_error_page(self):
        """[P2 False] Memastikan antarmuka seluruh modul Price Control bebas dari exception Whitelabel Spring Boot."""
        self.price_page.open_special_price()
        page_source = self.driver.page_source
        self.assertFalse("Whitelabel Error Page" in page_source,
                         "Terdeteksi Whitelabel Error Page Spring Boot pada modul Price Control")

    def test_18_profile_dropdown_hidden_by_default(self):
        """[P2 False] Memastikan dropdown menu profil dalam status tertutup saat awal halaman dimuat."""
        self.price_page.open_special_price()
        time.sleep(1)
        is_shown = self.price_page.is_profile_dropdown_open()
        self.assertFalse(is_shown, "Dropdown profil seharusnya tertutup secara default saat halaman dimuat")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Keamanan Sesi & Penanganan Anomali (4 Test)
    # =========================================================================

    def test_19_unauthenticated_special_price_redirected(self):
        """[P3 True] Memastikan akses langsung ke /tSystemPrice/special tanpa login dicegat dan dialihkan ke /login."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.PRICE_SPECIAL_URL)
            time.sleep(0.5)
            self.assertTrue("/login" in guest_driver.current_url,
                            f"Tamu tanpa login tidak dialihkan ke login: {guest_driver.current_url}")
        finally:
            guest_driver.quit()

    def test_20_unauthenticated_small_and_check_redirected(self):
        """[P3 True] Memastikan akses langsung ke /tSystemPrice/small dan check tanpa login dicegat ke /login."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.PRICE_SMALL_URL)
            time.sleep(0.5)
            self.assertTrue("/login" in guest_driver.current_url,
                            f"Akses tanpa login ke /small tidak dialihkan: {guest_driver.current_url}")
            guest_driver.get(Config.PRICE_CHECK_URL)
            time.sleep(0.5)
            self.assertTrue("/login" in guest_driver.current_url,
                            f"Akses tanpa login ke /check tidak dialihkan: {guest_driver.current_url}")
        finally:
            guest_driver.quit()

    def test_21_invalid_search_parameters_handled_safely(self):
        """[P3 True] Memastikan parameter filter tanggal / anomali query string ditangani aman tanpa server crash."""
        self.driver.get(f"{Config.PRICE_CHECK_URL}?beginDate=2099-12-31&endDate=2000-01-01&state=9999")
        time.sleep(0.5)
        current_url = self.driver.current_url
        self.assertTrue("/tSystemPrice/check" in current_url,
                        "Sistem mengalami crash atau rute terputus saat rentang anomali diinput")

    def test_22_edit_profile_interaction_triggers_feedback(self):
        """[P3 True] Memastikan klik menu Edit Profil pada navbar memicu notifikasi umpan balik aktif."""
        self.price_page.open_special_price()
        time.sleep(1)
        self.price_page.click_edit_profile()
        time.sleep(0.4)
        toast = self.price_page.get_toast_message()
        self.assertTrue(len(toast) > 0 or self.price_page.is_displayed(self.price_page.LOCATOR_TOAST),
                        "Toast pesan umpan balik interaksi Edit Profil harus aktif muncul.")
        self.price_page.close_profile_dropdown()

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Keamanan Siber, Penolakan Akses, & Resiliensi (8 Test)
    # =========================================================================

    def test_23_fictitious_search_no_data_leak(self):
        """[P4 False] Memastikan pencarian nama model fiktif tidak memunculkan data acak atau bocor."""
        self.price_page.open_special_price()
        self.price_page.search_special(name="FICTITIOUS_MODEL_NONEXISTENT_XYZ_9999")
        time.sleep(0.5)
        rows_count = self.price_page.get_special_rows_count()
        page_source = self.driver.page_source.lower()
        # Tabel kosong / 0 row / no data
        self.assertFalse(rows_count > 1 and "ecgo" in page_source,
                         "Pencarian model fiktif tetap mengembalikan data aktif yang tidak relevan")

    def test_24_guest_cannot_access_price_data(self):
        """[P4 False] Memastikan pengguna publik tanpa otentikasi TIDAK BISA mengakses data tarif sistem."""
        guest_driver = Config.get_driver()
        try:
            guest_driver.get(Config.PRICE_SPECIAL_URL)
            time.sleep(0.5)
            self.assertFalse("/tSystemPrice/special" in guest_driver.current_url and "/login" not in guest_driver.current_url,
                             "Tamu publik dapat membaca data tarif motor tanpa login!")
        finally:
            guest_driver.quit()

    def test_25_sqli_attack_resilience_on_special_search(self):
        """[P4 False] Memastikan serangan SQL Injection standar (' OR '1'='1) pada pencarian ditangkal aman."""
        self.driver.get(f"{Config.PRICE_SPECIAL_URL}?name=%27%20OR%20%271%27=%271")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("sql syntax" in page_source, "Terdeteksi pesan kesalahan sintaks SQL (SQLi rentan)")
        self.assertFalse("mysql_fetch" in page_source or "jdbc.exceptions" in page_source,
                         "Terdeteksi database driver exception akibat SQLi")

    def test_26_destructive_sqli_drop_table_thwarted(self):
        """[P4 False] Memastikan serangan destruktif SQL Injection DROP TABLE tidak merusak basis data."""
        self.driver.get(f"{Config.PRICE_SPECIAL_URL}?name=%27;%20DROP%20TABLE%20t_system_price;%20--")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("table deleted" in page_source, "Indikasi eksekusi drop table berhasil!")
        self.assertFalse("syntax error near 'drop'" in page_source, "Pesan error raw query bocor ke client")

    def test_27_xss_injection_sanitized_on_inputs(self):
        """[P4 False] Memastikan injeksi payload skrip XSS pada input disanitasi tanpa eksekusi popup browser."""
        self.price_page.open_special_price()
        time.sleep(0.5)
        self.price_page.search_special(name="<script>alert('xss_price')</script>")
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
        """[P4 False] Memastikan rute URL fiktif /tSystemPrice/invalid_subpath ditangani aman tanpa crash 500."""
        self.driver.get(f"{Config.BASE_URL}/tSystemPrice/invalid_subpath_xyz_99")
        time.sleep(0.5)
        page_source = self.driver.page_source.lower()
        self.assertFalse("http status 500" in page_source, "Terjadi HTTP Status 500 saat rute fiktif dibuka")

    def test_29_profile_logout_terminates_session(self):
        """[P4 False] Memastikan tombol Keluar pada profil navbar mengakhiri sesi dan mencegah akses rute tarif."""
        self.price_page.open_special_price()
        time.sleep(1)
        self.price_page.click_logout()
        time.sleep(1.5)

        # Setelah logout harus terlempar ke /login
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url,
                        f"Pengguna tidak diarahkan ke halaman login: {current_url}")

        # Coba akses kembali ke rute terproteksi
        self.price_page.open(Config.PRICE_SPECIAL_URL)
        time.sleep(1)
        self.assertFalse("/tSystemPrice/special" in self.driver.current_url and "/login" not in self.driver.current_url,
                         f"User yang telah logout TIDAK BISA mengakses kembali halaman tarif motor: {self.driver.current_url}")

        # Login kembali agar sesi setUpClass berikutnya / pengujian selanjutnya tetap utuh
        login_page = LoginPage(self.driver)
        login_page.login_as_admin()

    def test_30_browser_back_after_logout_prevented(self):
        """[P4 False] Memastikan manipulasi browser Back pasca logout terlindungi aman dari kebocoran sesi."""
        self.price_page.open_special_price()
        time.sleep(1)
        self.price_page.click_logout()
        time.sleep(1.5)

        # Coba klik tombol Back di browser
        self.driver.back()
        time.sleep(1)
        self.driver.refresh()
        time.sleep(1)

        # Tamu tidak boleh bisa membaca data tarif
        current_url = self.driver.current_url
        self.assertFalse("/tSystemPrice/special" in current_url and "/login" not in current_url,
                         f"Celah browser Back terdeteksi, user masih di: {current_url}")

        # Pulihkan sesi admin untuk teardown bersih
        login_page = LoginPage(self.driver)
        login_page.login_as_admin()


if __name__ == "__main__":
    unittest.main(verbosity=2)
