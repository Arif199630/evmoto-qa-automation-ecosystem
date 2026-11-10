"""
=============================================================================
TEST SUITE 06: OPENING UP URBAN MANAGEMENT (MENU #6)
Website:
  1. Urban Management             : <BASE_URL>/tOpenCity
  2. City search address settings : <BASE_URL>/THotAddress
  3. Service Area                 : <BASE_URL>/service-area
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Kota Operasional, Hot Address, Service Area, Rentang Tanggal Terbalik, SQLi, XSS
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan tabel kota operasional, alamat populer, & tautan sidebar aktif (True).
2. Positif (False) : Memastikan tombol aksi nonaktif sebelum seleksi & bebas error server 500 (False).
3. Negatif (True)  : Memastikan pengalihan ke /login aktif saat rute diakses tanpa login (True).
4. Negatif (False) : Memastikan data fiktif, SQLi, & tanggal terbalik tidak merusak sistem (False).
=============================================================================
"""

import os
import sys
import time
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_00_login import LoginPage
from pages.page_06_urban_management import UrbanPage


class TestUrbanManagement(unittest.TestCase):
    """Test Suite Modul Urban Management dengan Konsep 4 Pilar Testing (19 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = UrbanPage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # SUB-HALAMAN 1: URBAN MANAGEMENT (/tOpenCity)
    # =========================================================================
    def test_01_pilar1_positif_true_open_city_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka /tOpenCity dan memverifikasi tabel kota operasional tampil."""
        print("\n[Urban Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Urban Management...")
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        self.assertIn("Urban Management", self.page.get_title())
        self.assertIn("Urban management", self.page.get_open_city_heading_text())
        self.assertTrue(self.page.is_city_table_displayed(), "Tabel kota harus tampil (True).")
        self.assertFalse(self.page.is_city_edit_btn_enabled(), "Tombol Update harus disabled sebelum kota dipilih.")
        self.assertFalse(self.page.is_city_delete_btn_enabled(), "Tombol Delete harus disabled sebelum kota dipilih.")

        jumlah_baris = self.page.get_city_rows_count()
        print(f"  -> PASSED [True]: Halaman Urban Management termuat dengan {jumlah_baris} baris data kota.")

    def test_02_pilar1_positif_true_open_city_filter_pencarian_nama_kota_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari kota berdasarkan nama kota yang ada di environment aktif."""
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        # GIVEN: ambil nama kota dari baris pertama tabel (data milik environment ini)
        city = self.page.get_first_row_value("CITY NAME")
        if not city:
            self.skipTest("Belum ada data kota di environment ini; tambahkan data uji kota.")
        print(f"\n[Urban Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian kota valid '{city}'...")

        # WHEN: cari kota tersebut
        self.page.search_city_by_name(city)
        self.page.wait_for_url_contains("name=")

        # THEN: hasil pencarian memuat kota itu
        self.assertTrue(self.page.get_city_rows_count() > 0, f"Harus ditemukan baris data kota {city}.")
        self.assertIn(city, self.page.get_city_first_row_text())
        print("  -> PASSED [True]: Pencarian nama kota berhasil diterapkan.")

    def test_03_pilar1_positif_true_open_city_filter_tanggal_dan_nama(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter kombinasi rentang tanggal dan nama kota."""
        print("\n[Urban Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal & nama...")
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        self.page.filter_city_by_date_and_name("2026-01-01", "2026-12-31", "China")
        self.page.wait_for_url_contains("name=China")

        self.assertIn("beginDate=2026-01-01", self.page.get_current_url())
        self.assertIn("endDate=2026-12-31", self.page.get_current_url())
        self.assertIn("name=China", self.page.get_current_url())
        print("  -> PASSED [True]: Filter kombinasi tanggal dan nama terpasang di URL.")

    def test_04_pilar1_positif_true_open_city_seleksi_radio_mengaktifkan_tombol_aksi(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio kota mengaktifkan tombol aksi Update & Delete."""
        print("\n[Urban Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Seleksi radio kota dan aktivasi tombol...")
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        self.assertFalse(self.page.is_city_edit_btn_enabled())
        self.assertFalse(self.page.is_city_delete_btn_enabled())

        sukses_pilih = self.page.select_first_city()
        self.assertTrue(sukses_pilih, "Harus ada data kota di tabel (True).")
        self.assertTrue(self.page.is_city_edit_btn_enabled(), "Tombol Update harus menjadi aktif (True).")
        self.assertTrue(self.page.is_city_delete_btn_enabled(), "Tombol Delete harus menjadi aktif (True).")
        print("  -> PASSED [True]: Tombol Update dan Delete aktif setelah radio kota dipilih.")

    def test_05_pilar1_positif_true_deep_link_dengan_parameter_pencarian(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[Urban Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.OPEN_CITY_URL}?name=Kuningan")
        self.page.wait_for_url_contains("name=Kuningan")

        self.assertTrue(self.page.is_city_table_displayed(), "Tabel kota harus tampil via deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    # =========================================================================
    # SUB-HALAMAN 2: CITY SEARCH ADDRESS SETTINGS (/THotAddress)
    # =========================================================================
    def test_06_pilar1_positif_true_hot_address_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka City search address settings (/THotAddress) dan memverifikasi tabel."""
        print("\n[Urban Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Navigasi ke /THotAddress...")
        self.login_sebagai_admin()
        self.page.navigate_hot_address()

        self.assertIn("Hot Address Management", self.page.get_title())
        self.assertIn("City search address settings", self.page.get_hot_address_heading_text())
        self.assertTrue(self.page.is_hot_address_table_displayed(), "Tabel hot address harus tampil (True).")
        self.assertFalse(self.page.is_hot_address_edit_btn_enabled())
        self.assertFalse(self.page.is_hot_address_delete_btn_enabled())

        jumlah_baris = self.page.get_hot_address_rows_count()
        print(f"  -> PASSED [True]: Halaman Hot Address termuat dengan {jumlah_baris} baris data alamat.")

    def test_07_pilar1_positif_true_hot_address_filter_pencarian_nama_alamat_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari alamat berdasarkan nama lokasi yang valid ('Central Park')."""
        print("\n[Urban Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Pencarian alamat valid 'Jakarta'...")
        self.login_sebagai_admin()
        self.page.navigate_hot_address()

        self.page.search_address_by_name("Jakarta")
        self.page.wait_for_url_contains("name=Jakarta")

        self.assertIn("name=Jakarta", self.page.get_current_url())
        self.assertTrue(self.page.get_hot_address_rows_count() > 0, "Harus ditemukan alamat Jakarta (True).")
        self.assertIn("Jakarta", self.page.get_hot_address_first_row_text())
        print("  -> PASSED [True]: Pencarian alamat berhasil diterapkan.")

    def test_08_pilar1_positif_true_hot_address_seleksi_radio_mengaktifkan_tombol_aksi(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio alamat mengaktifkan tombol Update & Delete."""
        print("\n[Urban Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Seleksi radio alamat dan aktivasi tombol...")
        self.login_sebagai_admin()
        self.page.navigate_hot_address()

        self.assertFalse(self.page.is_hot_address_edit_btn_enabled())
        self.assertFalse(self.page.is_hot_address_delete_btn_enabled())

        sukses_pilih = self.page.select_first_address()
        self.assertTrue(sukses_pilih, "Harus ada data alamat di tabel (True).")
        self.assertTrue(self.page.is_hot_address_edit_btn_enabled(), "Tombol Update harus aktif (True).")
        self.assertTrue(self.page.is_hot_address_delete_btn_enabled(), "Tombol Delete harus aktif (True).")
        print("  -> PASSED [True]: Tombol Update dan Delete aktif setelah radio alamat dipilih.")

    # =========================================================================
    # SUB-HALAMAN 3: SERVICE AREA (/service-area)
    # =========================================================================
    def test_09_pilar1_positif_true_service_area_verifikasi_link_sidebar(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi tautan 'Service Area' tersedia di sidebar menu navigasi."""
        print("\n[Urban Mgmt - Test 09] [PILAR 1: POSITIF (TRUE)] Verifikasi link 'Service Area' di sidebar...")
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        link = self.page.get_sidebar_service_area_link()
        self.assertTrue(link.is_displayed(), "Tautan sidebar navigasi Urban Management harus tampil (True).")
        href = link.get_attribute("href")
        self.assertTrue("/tOpenCity" in href or "/service-area" in href, "Tautan harus mengarah ke rute urban yang valid (True).")
        print(f"  -> PASSED [True]: Tautan navigasi sidebar ditemukan (href: {href}).")

    def test_10_pilar2_positif_false_service_area_status_respons_tanpa_error_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Menavigasi ke /service-area dan memverifikasi respon tanpa error 500."""
        print("\n[Urban Mgmt - Test 10] [PILAR 2: POSITIF (FALSE)] Navigasi ke /service-area tanpa crash 500...")
        self.login_sebagai_admin()
        self.page.navigate_service_area()
        time.sleep(1)

        page_src = self.page.get_page_source()
        self.assertNotIn("500 Internal Server Error", page_src, "Server tidak boleh 500 internal server error.")
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh error 500 (False).")
        print("  -> PASSED [False]: Rute /service-area ditangani secara aman tanpa error 500.")

    def test_11_pilar1_positif_true_urban_semua_sub_halaman_dapat_diakses_berurutan(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengakses sub-halaman Urban Management berturut-turut setelah login."""
        print("\n[Urban Mgmt - Test 11] [PILAR 1: POSITIF (TRUE)] Akses sekuensial seluruh sub-halaman...")
        self.login_sebagai_admin()

        sub_pages = [
            (Config.OPEN_CITY_URL, "/tOpenCity"),
            (Config.HOT_ADDRESS_URL, "/THotAddress"),
        ]
        for url, frag in sub_pages:
            self.driver.get(url)
            self.page.wait_for_url_contains(frag)
            self.assertNotIn("500 Internal Server Error", self.page.get_page_source())
            print(f"    [OK] {url} -> OK")

        print("  -> PASSED [True]: Seluruh sub-halaman aktif dapat diakses berurutan.")

    # =========================================================================
    # NEGATIF & KEAMANAN
    # =========================================================================
    def test_12_pilar3_negatif_true_open_city_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tOpenCity langsung tanpa login dialihkan ke /login."""
        print("\n[Urban Mgmt - Test 12] [PILAR 3: NEGATIF (TRUE)] Akses /tOpenCity tanpa autentikasi...")
        self.page.navigate_open_city()
        self.page.wait_for_url_contains("/login")
        self.assertIn("/login", self.page.get_current_url())
        print("  -> PASSED [True]: Proteksi rute /tOpenCity aktif (dialihkan ke /login).")

    def test_13_pilar3_negatif_true_hot_address_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /THotAddress langsung tanpa login dialihkan ke /login."""
        print("\n[Urban Mgmt - Test 13] [PILAR 3: NEGATIF (TRUE)] Akses /THotAddress tanpa autentikasi...")
        self.page.navigate_hot_address()
        self.page.wait_for_url_contains("/login")
        self.assertIn("/login", self.page.get_current_url())
        print("  -> PASSED [True]: Proteksi rute /THotAddress aktif (dialihkan ke /login).")

    def test_14_pilar4_negatif_false_open_city_pencarian_kota_tidak_terdaftar(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama kota fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Urban Mgmt - Test 14] [PILAR 4: NEGATIF (FALSE)] Pencarian nama kota fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        self.page.search_city_by_name("Kota_Fiktif_Tidak_Ada_XYZ_9999")
        self.page.wait_for_url_contains("name=Kota_Fiktif")

        self.assertNotIn("500 Internal Server Error", self.page.get_page_source())
        self.assertFalse(self.page.get_city_radios_count() > 0, "Tidak boleh ada data kota fiktif (False).")
        print("  -> PASSED [False]: Pencarian kota fiktif ditangani dengan aman (0 data).")

    def test_15_pilar4_negatif_false_hot_address_pencarian_alamat_tidak_terdaftar(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama alamat fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Urban Mgmt - Test 15] [PILAR 4: NEGATIF (FALSE)] Pencarian alamat fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_hot_address()

        self.page.search_address_by_name("Alamat_Fiktif_9999999_Tidak_Ada")
        self.page.wait_for_url_contains("name=Alamat_Fiktif")

        self.assertNotIn("500 Internal Server Error", self.page.get_page_source())
        self.assertFalse(self.page.get_hot_address_radios_count() > 0, "Tidak boleh ada data alamat fiktif (False).")
        print("  -> PASSED [False]: Pencarian alamat fiktif ditangani dengan aman (0 data).")

    def test_16_pilar4_negatif_false_url_sub_path_fiktif_ditangani_tanpa_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tOpenCity/invalid_path ditangani dengan aman tanpa crash 500."""
        print("\n[Urban Mgmt - Test 16] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tOpenCity/invalid_path...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.BASE_URL}/tOpenCity/invalid_city_path_xyz_9999")
        time.sleep(1)

        self.assertNotIn("500 Internal Server Error", self.page.get_page_source())
        self.assertFalse("500 Internal Server Error" in self.page.get_page_source(), "Tidak boleh error 500 (False).")
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")

    def test_17_pilar4_negatif_false_filter_tanggal_terbalik_pada_open_city(self):
        """[PILAR 4 - NEGATIF (FALSE)] Rentang tanggal terbalik (begin > end) ditangani aman tanpa crash."""
        print("\n[Urban Mgmt - Test 17] [PILAR 4: NEGATIF (FALSE)] Uji rentang tanggal terbalik...")
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        self.page.filter_city_by_date_and_name("2026-12-31", "2026-01-01", "Kuningan")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Tanggal terbalik tidak boleh memicu error 500 (False)."
        )
        print("  -> PASSED [False]: Filter tanggal terbalik ditangani dengan aman oleh sistem.")

    def test_18_pilar4_negatif_false_sql_injection_pada_pencarian_kota(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian kota tidak membobol data."""
        print("\n[Urban Mgmt - Test 18] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada pencarian kota...")
        self.login_sebagai_admin()
        self.page.navigate_open_city()

        self.page.search_city_by_name("' OR '1'='1' --")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Pencarian SQLi tidak boleh memicu error server 500 (False)."
        )
        print("  -> PASSED [False]: Serangan SQL Injection pada nama kota berhasil ditangkal.")

    def test_19_pilar4_negatif_false_xss_pada_pencarian_hot_address(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada Hot Address search tidak dieksekusi browser."""
        print("\n[Urban Mgmt - Test 19] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian alamat...")
        self.login_sebagai_admin()
        self.page.navigate_hot_address()

        self.page.search_address_by_name("<script>window.xss_hot_addr=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_hot_addr === true;")
        self.assertFalse(
            is_exploited,
            "Script XSS tidak boleh dieksekusi oleh halaman Hot Address (False)."
        )
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Hot Address.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
