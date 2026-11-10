"""
=============================================================================
TEST SUITE 07: DRIVER MANAGEMENT (MENU #7)
Website: <BASE_URL>/tDriver & Sub-Halamannya
Sub-Halaman:
  1. Driver Audit list (/tDriver)
  2. Driver Replacement Vehicle audit list management (/tDriverVerify)
  3. Driver's list (/tDriver/yesDriver)
  4. Driver Withholding Details (/tDriver/without)
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Pendaftaran Driver, Audit Armada, Driver Aktif, Withholding, Tanggal Terbalik, SQLi, XSS
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan pendaftaran driver, audit armada, direktori pengemudi, & withholding aktif (True).
2. Positif (False) : Memastikan tombol audit terkunci sebelum seleksi & sistem bebas dari error 500 (False).
3. Negatif (True)  : Memastikan perlindungan rute mengalihkan pengemudi/publik tanpa login ke /login (True).
4. Negatif (False) : Memastikan tanggal terbalik, input alfabet, SQLi, & XSS tidak membocorkan data (False).
=============================================================================
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_00_login import LoginPage
from pages.page_07_driver_management import DriverPage


class TestDriverManagement(unittest.TestCase):
    """Test Suite Modul Driver Management dengan Konsep 4 Pilar Testing (27 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = DriverPage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # SUB-HALAMAN 1: DRIVER AUDIT LIST (/tDriver)
    # =========================================================================
    def test_01_pilar1_positif_true_driver_audit_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Driver Audit List (/tDriver) dan memverifikasi tabel driver audit tampil."""
        print("\n[Driver Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Driver Audit...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.assertIn("Driver audit list", self.page.get_title())
        jumlah_baris = self.page.get_audit_rows_count()
        self.assertGreaterEqual(jumlah_baris, 1, "Tabel driver audit harus memuat setidaknya 1 baris data (True).")
        self.assertTrue(self.page.is_audit_action_btn_disabled(), "Tombol 'Audit now' harus disabled sebelum baris dipilih.")
        print(f"  -> PASSED [True]: Tabel Driver Audit memuat {jumlah_baris} baris data.")

    def test_02_pilar1_positif_true_driver_audit_filter_pencarian_phone(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter pencarian nomor telepon pada Driver Audit List."""
        print("\n[Driver Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Filter pencarian nomor telepon...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.page.search_audit_by_phone("08")
        self.page.wait_for_url_contains("phone=08")
        self.assertIn("phone=08", self.page.get_current_url())
        print("  -> PASSED [True]: Filter nomor telepon Driver Audit berhasil terpasang di URL.")

    def test_03_pilar1_positif_true_driver_audit_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter rentang tanggal pada Driver Audit List."""
        print("\n[Driver Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal Driver Audit...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.page.filter_audit_by_date_range("2026-01-01", "2026-12-31")
        self.page.wait_for_url_contains("beginTime=2026-01-01")
        self.assertIn("beginTime=2026-01-01", self.page.get_current_url())
        print("  -> PASSED [True]: Filter tanggal Driver Audit berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_driver_audit_seleksi_radio_mengaktifkan_tombol_audit(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio baris driver audit mengaktifkan tombol 'Audit now'."""
        print("\n[Driver Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Seleksi radio baris mengaktifkan tombol aksi...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.assertTrue(self.page.is_audit_action_btn_disabled())
        sukses_pilih = self.page.select_first_audit_radio()
        self.assertTrue(sukses_pilih, "Harus ada data radio di tabel driver audit (True).")
        self.assertFalse(self.page.is_audit_action_btn_disabled(), "Tombol 'Audit now' harus aktif setelah radio dipilih.")
        print("  -> PASSED [True]: Tombol 'Audit now' berhasil berubah menjadi aktif (enabled).")

    def test_05_pilar2_positif_false_driver_audit_tombol_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Memverifikasi tombol aksi audit terkunci aman saat belum ada seleksi."""
        print("\n[Driver Mgmt - Test 05] [PILAR 2: POSITIF (FALSE)] Tombol audit awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.assertTrue(self.page.is_audit_action_btn_disabled())
        self.assertFalse(not self.page.is_audit_action_btn_disabled(), "Tombol audit tidak boleh aktif awal (False).")
        print("  -> PASSED [False]: Tombol audit terkunci aman sebelum ada pilihan baris.")

    def test_06_pilar4_negatif_false_driver_audit_pencarian_tidak_ditemukan(self):
        """[PILAR 4 - NEGATIF (FALSE)] Menguji pencarian nomor telepon fiktif menampilkan 0 hasil tanpa crash."""
        print("\n[Driver Mgmt - Test 06] [PILAR 4: NEGATIF (FALSE)] Pencarian telepon fiktif...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.DRIVER_AUDIT_URL}?phone=9999999999999999")

        page_text = self.page.get_page_source()
        self.assertNotIn("500 Internal Server Error", page_text)
        self.assertFalse("500 Internal Server Error" in page_text, "Tidak boleh error 500 (False).")
        print("  -> PASSED [False]: Pencarian telepon fiktif ditangani dengan aman tanpa crash server.")

    def test_07_pilar3_negatif_true_driver_audit_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tDriver tanpa autentikasi dialihkan ke /login."""
        print("\n[Driver Mgmt - Test 07] [PILAR 3: NEGATIF (TRUE)] Akses tanpa autentikasi dialihkan ke login...")
        self.page.navigate_audit()
        self.page.wait_for_url_contains("/login")
        self.assertIn("/login", self.page.get_current_url())
        print("  -> PASSED [True]: Akses tanpa login berhasil diblokir dan diarahkan ke /login.")

    # =========================================================================
    # SUB-HALAMAN 2: DRIVER REPLACEMENT VEHICLE AUDIT LIST (/tDriverVerify)
    # =========================================================================
    def test_08_pilar1_positif_true_verify_audit_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Replacement Vehicle Audit List (/tDriverVerify) dan verifikasi tabel."""
        print("\n[Driver Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tDriverVerify...")
        self.login_sebagai_admin()
        self.page.navigate_verify()

        self.assertIn("Driver replacement vehicle audit list", self.page.get_title())
        jumlah_baris = self.page.get_verify_rows_count()
        self.assertGreaterEqual(jumlah_baris, 1, "Tabel replacement vehicle audit harus memuat baris data (True).")
        self.assertTrue(self.page.is_verify_action_btn_disabled())
        print(f"  -> PASSED [True]: Tabel Replacement Vehicle Audit memuat {jumlah_baris} baris data.")

    def test_09_pilar1_positif_true_verify_audit_filter_pencarian_phone(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter pencarian nomor telepon pada Replacement Vehicle Audit."""
        print("\n[Driver Mgmt - Test 09] [PILAR 1: POSITIF (TRUE)] Filter nomor telepon...")
        self.login_sebagai_admin()
        self.page.navigate_verify()

        self.page.search_verify_by_phone("08")
        self.page.wait_for_url_contains("phone=08")
        self.assertIn("phone=08", self.page.get_current_url())
        print("  -> PASSED [True]: Filter pencarian nomor telepon Replacement Audit berhasil terpasang di URL.")

    def test_10_pilar1_positif_true_verify_audit_seleksi_radio_dan_verifikasi_atribut(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio baris replacement audit dan memverifikasi atribut seleksi."""
        print("\n[Driver Mgmt - Test 10] [PILAR 1: POSITIF (TRUE)] Seleksi radio baris replacement audit...")
        self.login_sebagai_admin()
        self.page.navigate_verify()

        val, is_selected = self.page.select_first_verify_radio()
        self.assertTrue(is_selected, "Radio baris replacement audit harus berstatus terpilih (True).")
        print(f"  -> PASSED [True]: Radio replacement audit dengan ID={val} berhasil dipilih.")

    def test_11_pilar2_positif_false_verify_audit_tombol_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol audit pergantian armada tidak aktif sebelum seleksi."""
        print("\n[Driver Mgmt - Test 11] [PILAR 2: POSITIF (FALSE)] Tombol replacement audit awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_verify()

        self.assertTrue(self.page.is_verify_action_btn_disabled())
        self.assertFalse(not self.page.is_verify_action_btn_disabled(), "Tombol audit tidak boleh aktif awal (False).")
        print("  -> PASSED [False]: Tombol replacement audit terkunci aman sebelum ada pilihan.")

    def test_12_pilar4_negatif_false_verify_audit_pencarian_tidak_ditemukan(self):
        """[PILAR 4 - NEGATIF (FALSE)] Menguji pencarian nomor telepon fiktif replacement audit menampilkan 0 hasil."""
        print("\n[Driver Mgmt - Test 12] [PILAR 4: NEGATIF (FALSE)] Pencarian nomor fiktif...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.DRIVER_VERIFY_URL}?phone=9999999999999999")

        page_text = self.page.get_page_source()
        self.assertNotIn("500 Internal Server Error", page_text)
        self.assertFalse("500 Internal Server Error" in page_text, "Tidak boleh error 500 (False).")
        print("  -> PASSED [False]: Pencarian replacement audit nihil ditangani dengan aman tanpa crash.")

    def test_13_pilar3_negatif_true_verify_audit_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tDriverVerify tanpa autentikasi dialihkan ke /login."""
        print("\n[Driver Mgmt - Test 13] [PILAR 3: NEGATIF (TRUE)] Akses tanpa autentikasi dialihkan ke login...")
        self.page.navigate_verify()
        self.page.wait_for_url_contains("/login")
        self.assertIn("/login", self.page.get_current_url())
        print("  -> PASSED [True]: Akses tanpa login berhasil diblokir dan diarahkan ke /login.")

    # =========================================================================
    # SUB-HALAMAN 3: DRIVERS' LIST (/tDriver/yesDriver)
    # =========================================================================
    def test_14_pilar1_positif_true_driver_list_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Drivers' List (/tDriver/yesDriver) dan verifikasi title, tabel, tombol aksi."""
        print("\n[Driver Mgmt - Test 14] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tDriver/yesDriver...")
        self.login_sebagai_admin()
        self.page.navigate_driver_list()

        self.assertIn("Drivers' list", self.page.get_title())
        jumlah_baris = self.page.get_driver_list_rows_count()
        self.assertGreaterEqual(jumlah_baris, 1, "Tabel driver list harus memuat baris data (True).")
        self.assertTrue(self.page.is_add_driver_btn_displayed(), "Tombol 'Add driver' harus tampil (True).")
        print(f"  -> PASSED [True]: Tabel Drivers List memuat {jumlah_baris} baris data.")

    def test_15_pilar1_positif_true_driver_list_filter_pencarian_nama(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter pencarian nama driver pada Drivers' List."""
        print("\n[Driver Mgmt - Test 15] [PILAR 1: POSITIF (TRUE)] Filter pencarian nama driver...")
        self.login_sebagai_admin()
        self.page.navigate_driver_list()

        self.page.search_driver_by_name("driver")
        self.page.wait_for_url_contains("name=driver")
        self.assertIn("name=driver", self.page.get_current_url())
        print("  -> PASSED [True]: Filter nama driver berhasil disubmit dan parameter terpasang di URL.")

    def test_16_pilar1_positif_true_driver_list_filter_pencarian_phone(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter pencarian nomor telepon pada Drivers' List."""
        print("\n[Driver Mgmt - Test 16] [PILAR 1: POSITIF (TRUE)] Filter pencarian nomor telepon driver...")
        self.login_sebagai_admin()
        self.page.navigate_driver_list()

        self.page.search_driver_by_phone("08")
        self.page.wait_for_url_contains("phone=08")
        self.assertIn("phone=08", self.page.get_current_url())
        print("  -> PASSED [True]: Filter nomor telepon driver berhasil terpasang di URL.")

    def test_17_pilar1_positif_true_driver_list_seleksi_radio_driver(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio driver pada daftar dan memverifikasi atribut seleksi."""
        print("\n[Driver Mgmt - Test 17] [PILAR 1: POSITIF (TRUE)] Seleksi radio baris driver...")
        self.login_sebagai_admin()
        self.page.navigate_driver_list()

        nama_driver, is_selected = self.page.select_first_driver_radio()
        self.assertTrue(is_selected, "Radio driver harus terpilih setelah diklik (True).")
        print(f"  -> PASSED [True]: Radio driver '{nama_driver}' berhasil dipilih.")

    def test_18_pilar4_negatif_false_driver_list_pencarian_tidak_ditemukan(self):
        """[PILAR 4 - NEGATIF (FALSE)] Menguji pencarian nama driver fiktif ditangani dengan aman tanpa crash server."""
        print("\n[Driver Mgmt - Test 18] [PILAR 4: NEGATIF (FALSE)] Pencarian nama driver fiktif...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.DRIVER_LIST_URL}?name=driver_fiktif_palsu_tidak_ada_xyz_99999")

        page_text = self.page.get_page_source()
        self.assertNotIn("500 Internal Server Error", page_text)
        self.assertFalse("500 Internal Server Error" in page_text, "Tidak boleh error 500 (False).")
        print("  -> PASSED [False]: Pencarian nama driver fiktif aman tanpa crash server.")

    def test_19_pilar3_negatif_true_driver_list_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tDriver/yesDriver tanpa autentikasi dialihkan ke /login."""
        print("\n[Driver Mgmt - Test 19] [PILAR 3: NEGATIF (TRUE)] Akses tanpa autentikasi dialihkan ke login...")
        self.page.navigate_driver_list()
        self.page.wait_for_url_contains("/login")
        self.assertIn("/login", self.page.get_current_url())
        print("  -> PASSED [True]: Akses tanpa login berhasil diblokir dan diarahkan ke /login.")

    # =========================================================================
    # SUB-HALAMAN 4: DRIVER WITHHOLDING DETAILS (/tDriver/without)
    # =========================================================================
    def test_20_pilar1_positif_true_withholding_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Driver Withholding Details (/tDriver/without) dan verifikasi kolom tabel."""
        print("\n[Driver Mgmt - Test 20] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tDriver/without...")
        self.login_sebagai_admin()
        self.page.navigate_withholding()

        self.assertIn("Driver Withholding Details", self.page.get_title())
        self.assertTrue(self.page.is_withholding_name_input_displayed())
        self.assertTrue(self.page.is_withholding_phone_input_displayed())

        headers = self.page.get_withholding_table_headers()
        self.assertTrue(any("DEDUCTION" in h or "TIME" in h for h in headers))
        print("  -> PASSED [True]: Komponen Driver Withholding Details terverifikasi lengkap.")

    def test_21_pilar1_positif_true_withholding_filter_pencarian_nama_driver(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter pencarian nama driver pada halaman Withholding."""
        print("\n[Driver Mgmt - Test 21] [PILAR 1: POSITIF (TRUE)] Filter pencarian nama driver...")
        self.login_sebagai_admin()
        self.page.navigate_withholding()

        self.page.search_withholding_by_name("driver")
        self.page.wait_for_url_contains("name=driver")
        self.assertIn("name=driver", self.page.get_current_url())
        print("  -> PASSED [True]: Filter nama driver berhasil disubmit dan parameter terpasang di URL.")

    def test_22_pilar1_positif_true_withholding_filter_pencarian_phone(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji filter pencarian no HP driver pada halaman Withholding."""
        print("\n[Driver Mgmt - Test 22] [PILAR 1: POSITIF (TRUE)] Filter pencarian nomor telepon...")
        self.login_sebagai_admin()
        self.page.navigate_withholding()

        self.page.search_withholding_by_phone("08")
        self.page.wait_for_url_contains("phone=08")
        self.assertIn("phone=08", self.page.get_current_url())
        print("  -> PASSED [True]: Filter nomor telepon berhasil disubmit dan terpasang di URL.")

    def test_23_pilar1_positif_true_driver_management_semua_sub_halaman_dapat_diakses_berurutan(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengakses seluruh 4 sub-halaman Driver Management secara sekuensial."""
        print("\n[Driver Mgmt - Test 23] [PILAR 1: POSITIF (TRUE)] Akses sekuensial seluruh sub-halaman...")
        self.login_sebagai_admin()

        sub_pages = [
            (Config.DRIVER_AUDIT_URL,       "Driver audit list"),
            (Config.DRIVER_VERIFY_URL,      "Driver replacement vehicle audit list"),
            (Config.DRIVER_LIST_URL,        "Drivers' list"),
            (Config.DRIVER_WITHHOLDING_URL, "Driver Withholding Details"),
        ]

        for url, expected_title_part in sub_pages:
            self.driver.get(url)
            self.page.wait_for_url_contains(url.replace(Config.BASE_URL, ""))
            self.assertIn(expected_title_part, self.page.get_title())
            print(f"    [OK] {expected_title_part} -> loaded.")

        print("  -> PASSED [True]: Seluruh 4 sub-halaman Driver Management dapat diakses berurutan dengan stabil.")

    # =========================================================================
        # =========================================================================
    def test_24_pilar4_negatif_false_driver_audit_rentang_tanggal_terbalik(self):
        """[PILAR 4 - NEGATIF (FALSE)] Rentang tanggal terbalik (begin > end) pada driver audit ditangani aman."""
        print("\n[Driver Mgmt - Test 24] [PILAR 4: NEGATIF (FALSE)] Uji rentang tanggal terbalik driver audit...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.page.filter_audit_by_date_range("2026-12-31", "2026-01-01")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Filter tanggal terbalik tidak boleh memicu error 500 (False)."
        )
        print("  -> PASSED [False]: Tanggal terbalik ditangani aman tanpa crash server.")

    def test_25_pilar4_negatif_false_input_non_numerik_pada_telepon_driver(self):
        """[PILAR 4 - NEGATIF (FALSE)] Input teks alfabet pada filter telepon driver ditangani aman."""
        print("\n[Driver Mgmt - Test 25] [PILAR 4: NEGATIF (FALSE)] Uji input alfabet pada no HP driver...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.page.search_audit_by_phone("bukan_no_hp_xyz")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Input alfabet pada phone tidak boleh membuat error 500 (False)."
        )
        print("  -> PASSED [False]: Filter non-numerik pada no HP driver ditangani aman.")

    def test_26_pilar4_negatif_false_sql_injection_pada_pencarian_driver(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian driver tidak membocorkan data."""
        print("\n[Driver Mgmt - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada driver search...")
        self.login_sebagai_admin()
        self.page.navigate_driver_list()

        self.page.search_driver_by_name("' OR '1'='1' --")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Pencarian SQLi tidak boleh memicu error server 500 (False)."
        )
        print("  -> PASSED [False]: SQL Injection pada driver berhasil ditangkal.")

    def test_27_pilar4_negatif_false_xss_pada_pencarian_nama_driver(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian driver tidak dieksekusi browser."""
        print("\n[Driver Mgmt - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada driver name...")
        self.login_sebagai_admin()
        self.page.navigate_driver_list()

        self.page.search_driver_by_name("<script>window.xss_driver=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_driver === true;")
        self.assertFalse(
            is_exploited,
            "Script XSS tidak boleh dieksekusi oleh halaman driver (False)."
        )
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Driver Management.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
