"""
=============================================================================
TEST SUITE 10: FRANCHISEE MANAGEMENT (MENU #10)
Website : <BASE_URL>/tCompany/franchisee
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Franchisee Management, Form Pencarian, Status Tombol Aksi, Resiliensi Keamanan
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel franchisee, filter pencarian, dan kolom tampil aktif (True).
2. Positif (False) : Memastikan tombol Update, Delete, & View details terkunci (disabled) sebelum ada seleksi (False).
3. Negatif (True)  : Memastikan akses rute tanpa login dicegat & tanggal terbalik ditangani secara aman (True).
4. Negatif (False) : Memastikan data fiktif 0 baris & serangan siber (SQLi/XSS) ditangkal total (False).
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
from pages.page_10_franchisee_management import FranchiseePage


class TestFranchiseeManagement(unittest.TestCase):
    """Test Suite Franchisee Management dengan Konsep 4 Pilar Testing (20 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = FranchiseePage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper untuk login sebagai administrator."""
        login_page = LoginPage(self.driver)
        login_page.navigate()
        login_page.login_as_admin()
        login_page.wait_for_url_contains("/blackboard")

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Respon dan Keberhasilan Bernilai BENAR
    # =========================================================================
    def test_01_pilar1_positif_true_franchisee_tabel_dan_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Franchisee Management (/tCompany/franchisee) dan memverifikasi tabel aktif."""
        print("\n[Franchisee Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Franchisee Management...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertTrue(self.page.is_table_displayed(), "Tabel Franchisee harus tampil (True).")
        self.assertIn("franchisee management", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Franchisee Management aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_franchisee_search_nama_mitra(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari franchisee berdasarkan nama franchisee valid."""
        print("\n[Franchisee Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian nama franchisee...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_name("Mitra")
        self.page.wait_for_url_contains("name=Mitra")

        self.assertIn("name=Mitra", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel franchisee harus tampil (True).")
        print("  -> PASSED [True]: Filter pencarian nama franchisee berhasil disubmit.")

    def test_03_pilar1_positif_true_franchisee_search_nomor_akun(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari franchisee berdasarkan nomor akun mitra."""
        print("\n[Franchisee Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian nomor akun franchisee...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_account("ACC123")
        self.page.wait_for_url_contains("account=ACC123")

        self.assertIn("account=ACC123", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel franchisee harus tampil (True).")
        print("  -> PASSED [True]: Filter nomor akun franchisee berhasil disubmit.")

    def test_04_pilar1_positif_true_franchisee_filter_state_normal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter status franchisee dengan opsi Normal (Value 2)."""
        print("\n[Franchisee Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Filter status franchisee Normal...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_state("2")
        self.page.wait_for_url_contains("state=2")

        self.assertIn("state=2", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah filter status (True).")
        print("  -> PASSED [True]: Filter status franchisee berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_franchisee_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang tanggal pada Franchisee Management terpasang di URL."""
        print("\n[Franchisee Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal franchisee...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-01-01", "2026-12-31")

        self.assertIn("beginDate=2026-01-01", self.page.get_current_url())
        self.assertIn("endDate=2026-12-31", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tampil dengan filter tanggal (True).")
        print("  -> PASSED [True]: Filter rentang tanggal franchisee berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_franchisee_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel franchisee di DOM."""
        print("\n[Franchisee Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom tabel franchisee...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("FRANCHISEE NAME" in page_src, "Kolom Franchisee Name harus ada (True).")
        self.assertTrue("BRANCH COMPANY" in page_src, "Kolom Branch Company harus ada (True).")
        self.assertTrue("ACCOUNT NUMBER" in page_src, "Kolom Account Number harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel franchisee terkonfirmasi lengkap.")

    def test_07_pilar1_positif_true_franchisee_deep_link_dengan_parameter(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[Franchisee Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.FRANCHISEE_URL}?name=MitraUtama")
        self.page.wait_for_url_contains("name=MitraUtama")

        self.assertIn("name=MitraUtama", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tampil melalui deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    def test_08_pilar1_positif_true_franchisee_refresh_browser_pertahankan_data(self):
        """[PILAR 1 - POSITIF (TRUE)] Refresh/F5 browser mempertahankan sesi dan tabel Franchisee."""
        print("\n[Franchisee Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Refresh browser pada Franchisee...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.driver.refresh()
        self.assertTrue(self.page.is_table_displayed(), "Tabel Franchisee tetap aktif setelah refresh (True).")
        print("  -> PASSED [True]: Refresh halaman mempertahankan sesi Franchisee secara stabil.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Tombol Terkunci
    # =========================================================================
    def test_09_pilar2_positif_false_tombol_update_franchisee_awal_nonaktif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Update franchisee terkunci (disabled) sebelum memilih data."""
        print("\n[Franchisee Mgmt - Test 09] [PILAR 2: POSITIF (FALSE)] Tombol Update franchisee awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_update_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Update franchisee harus disabled jika belum ada baris terpilih (False).")
        print("  -> PASSED [False]: Tombol Update franchisee terkunci aman berstatus disabled.")

    def test_10_pilar2_positif_false_tombol_delete_franchisee_awal_nonaktif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete franchisee terkunci (disabled) sebelum memilih data."""
        print("\n[Franchisee Mgmt - Test 10] [PILAR 2: POSITIF (FALSE)] Tombol Delete franchisee awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete franchisee harus disabled jika belum ada baris terpilih (False).")
        print("  -> PASSED [False]: Tombol Delete franchisee terkunci aman berstatus disabled.")

    def test_11_pilar2_positif_false_tombol_details_franchisee_awal_nonaktif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol View details franchisee terkunci (disabled) sebelum memilih data."""
        print("\n[Franchisee Mgmt - Test 11] [PILAR 2: POSITIF (FALSE)] Tombol View details franchisee awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_details_btn_enabled()
        self.assertFalse(is_enabled, "Tombol View details franchisee harus disabled jika belum ada baris terpilih (False).")
        print("  -> PASSED [False]: Tombol View details franchisee terkunci aman berstatus disabled.")

    def test_12_pilar2_positif_false_halaman_franchisee_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan halaman Franchisee Management bebas dari respon error server 500."""
        print("\n[Franchisee Mgmt - Test 12] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
        self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")
        print("  -> PASSED [False]: Halaman Franchisee Management bersih dari error 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_13_pilar3_negatif_true_akses_franchisee_tanpa_autentikasi_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tCompany/franchisee tanpa login harus dialihkan ke /login."""
        print("\n[Franchisee Mgmt - Test 13] [PILAR 3: NEGATIF (TRUE)] Akses /tCompany/franchisee tanpa login...")
        self.page.navigate()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute /tCompany/franchisee aktif (dialihkan ke /login).")

    def test_14_pilar3_negatif_true_rentang_tanggal_terbalik_pada_franchisee_ditangani(self):
        """[PILAR 3 - NEGATIF (TRUE)] Rentang tanggal terbalik pada franchisee ditangani aman tanpa crash."""
        print("\n[Franchisee Mgmt - Test 14] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada franchisee...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-12-31", "2026-01-01")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_table_displayed() or "500" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Filter tanggal terbalik franchisee ditangani aman oleh sistem.")

    def test_15_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[Franchisee Mgmt - Test 15] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Sistem harus mengalihkan ke /login saat sesi habis (True).")
        print("  -> PASSED [True]: Sistem aktif mencegat request dan redirect ke /login saat sesi habis.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Pencegahan Manipulasi & Keamanan Data
    # =========================================================================
    def test_16_pilar4_negatif_false_pencarian_nama_franchisee_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama franchisee fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Franchisee Mgmt - Test 16] [PILAR 4: NEGATIF (FALSE)] Pencarian franchisee fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_name("FRANCHISEE_FIKTIF_NONEXISTENT_99999")
        self.page.wait_for_url_contains("FRANCHISEE_FIKTIF_NONEXISTENT_99999")

        row_count = self.page.get_rows_count()
        self.assertFalse(row_count > 0, "Pencarian franchisee fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian franchisee fiktif ditangani dengan aman (0 data).")

    def test_17_pilar4_negatif_false_akses_tanpa_login_tidak_bisa_lihat_data_franchisee(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu tanpa login TIDAK BISA membaca data franchisee."""
        print("\n[Franchisee Mgmt - Test 17] [PILAR 4: NEGATIF (FALSE)] Penolakan akses data franchisee tanpa login...")
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("ACCOUNT NUMBER" in page_src, "Data sensitif franchisee tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Data franchisee terproteksi rapat dari akses publik.")

    def test_18_pilar4_negatif_false_sql_injection_pada_pencarian_nama_franchisee(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian franchisee tidak membobol data."""
        print("\n[Franchisee Mgmt - Test 18] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada pencarian franchisee...")
        self.login_sebagai_admin()
        self.page.navigate()

        sqli_payload = "' OR '1'='1"
        self.page.search_by_name(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada franchisee berhasil ditangkal.")

    def test_19_pilar4_negatif_false_xss_pada_pencarian_nama_franchisee(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian franchisee tidak dieksekusi browser."""
        print("\n[Franchisee Mgmt - Test 19] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian franchisee...")
        self.login_sebagai_admin()
        self.page.navigate()

        xss_payload = "<script>alert('xss_franchisee')</script>"
        self.page.search_by_name(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Franchisee Management.")

    def test_20_pilar4_negatif_false_url_sub_path_fiktif_ditangani_tanpa_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tCompany/franchisee/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[Franchisee Mgmt - Test 20] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tCompany/franchisee/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.FRANCHISEE_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
