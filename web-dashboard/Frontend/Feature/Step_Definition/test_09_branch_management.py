"""
=============================================================================
TEST SUITE 09: BRANCH MANAGEMENT (MENU #9)
Website : <BASE_URL>/tCompany
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Branch Management, Form Pencarian, Status Tombol Aksi, Resiliensi Keamanan
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel cabang, filter pencarian, dan kolom tampil aktif (True).
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
from pages.page_09_branch_management import BranchPage


class TestBranchManagement(unittest.TestCase):
    """Test Suite Branch Management dengan Konsep 4 Pilar Testing (20 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = BranchPage(self.driver)

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
    def test_01_pilar1_positif_true_branch_tabel_dan_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Branch Management (/tCompany) dan memverifikasi tabel aktif."""
        print("\n[Branch Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Branch Management...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertTrue(self.page.is_table_displayed(), "Tabel Branch harus tampil (True).")
        self.assertIn("branch management", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Branch Management aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_branch_search_nama_perusahaan(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari cabang perusahaan berdasarkan nama perusahaan valid."""
        print("\n[Branch Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian nama cabang perusahaan...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_name("Jakarta")
        self.page.wait_for_url_contains("name=Jakarta")

        self.assertIn("name=Jakarta", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah pencarian (True).")
        print("  -> PASSED [True]: Filter pencarian nama cabang berhasil disubmit.")

    def test_03_pilar1_positif_true_branch_search_nama_penanggung_jawab(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari cabang berdasarkan nama penanggung jawab valid."""
        print("\n[Branch Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian nama penanggung jawab cabang...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_principal("Manager")
        self.page.wait_for_url_contains("principalName=Manager")

        self.assertIn("principalName=Manager", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah pencarian (True).")
        print("  -> PASSED [True]: Filter pencarian penanggung jawab cabang berhasil disubmit.")

    def test_04_pilar1_positif_true_branch_search_telepon_penanggung_jawab(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari cabang berdasarkan nomor telepon penanggung jawab."""
        print("\n[Branch Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Pencarian nomor telepon cabang...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_phone("0812")
        self.page.wait_for_url_contains("principalPhone=0812")

        self.assertIn("principalPhone=0812", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel cabang harus tampil (True).")
        print("  -> PASSED [True]: Filter nomor telepon cabang berhasil disubmit.")

    def test_05_pilar1_positif_true_branch_filter_state_normal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter status cabang dengan opsi Normal (Value 2)."""
        print("\n[Branch Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Filter status cabang Normal...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_state("2")
        self.page.wait_for_url_contains("state=2")

        self.assertIn("state=2", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah filter status (True).")
        print("  -> PASSED [True]: Filter status cabang berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_branch_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang tanggal pada Branch Management terpasang di URL."""
        print("\n[Branch Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal cabang...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-01-01", "2026-12-31")

        self.assertIn("beginDate=2026-01-01", self.page.get_current_url())
        self.assertIn("endDate=2026-12-31", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tampil dengan filter tanggal (True).")
        print("  -> PASSED [True]: Filter rentang tanggal berhasil diaplikasikan.")

    def test_07_pilar1_positif_true_branch_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel cabang di DOM."""
        print("\n[Branch Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom tabel cabang...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("COMPANY NAME" in page_src, "Kolom Company Name harus ada (True).")
        self.assertTrue("COMPANY ADDRESS" in page_src, "Kolom Company Address harus ada (True).")
        self.assertTrue("PERSON IN CHARGE" in page_src, "Kolom Person in charge harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel cabang terkonfirmasi lengkap.")

    def test_08_pilar1_positif_true_deep_link_dengan_parameter_pencarian(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[Branch Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.BRANCH_URL}?name=JakartaBranch")
        self.page.wait_for_url_contains("name=JakartaBranch")

        self.assertIn("name=JakartaBranch", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tampil melalui deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Tombol Terkunci
    # =========================================================================
    def test_09_pilar2_positif_false_tombol_update_cabang_awal_nonaktif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Update cabang terkunci (disabled) sebelum memilih data."""
        print("\n[Branch Mgmt - Test 09] [PILAR 2: POSITIF (FALSE)] Tombol Update cabang awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_update_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Update cabang harus disabled jika belum ada baris terpilih (False).")
        print("  -> PASSED [False]: Tombol Update cabang terkunci aman berstatus disabled.")

    def test_10_pilar2_positif_false_tombol_delete_cabang_awal_nonaktif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete cabang terkunci (disabled) sebelum memilih data."""
        print("\n[Branch Mgmt - Test 10] [PILAR 2: POSITIF (FALSE)] Tombol Delete cabang awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete cabang harus disabled jika belum ada baris terpilih (False).")
        print("  -> PASSED [False]: Tombol Delete cabang terkunci aman berstatus disabled.")

    def test_11_pilar2_positif_false_tombol_details_cabang_awal_nonaktif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol View details cabang terkunci (disabled) sebelum memilih data."""
        print("\n[Branch Mgmt - Test 11] [PILAR 2: POSITIF (FALSE)] Tombol View details cabang awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_details_btn_enabled()
        self.assertFalse(is_enabled, "Tombol View details cabang harus disabled jika belum ada baris terpilih (False).")
        print("  -> PASSED [False]: Tombol View details cabang terkunci aman berstatus disabled.")

    def test_12_pilar2_positif_false_tidak_ada_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan halaman Branch Management bebas dari respon error server 500."""
        print("\n[Branch Mgmt - Test 12] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
        self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")
        print("  -> PASSED [False]: Halaman Branch Management bersih dari error 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_13_pilar3_negatif_true_akses_branch_tanpa_autentikasi_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tCompany tanpa login harus dialihkan ke /login."""
        print("\n[Branch Mgmt - Test 13] [PILAR 3: NEGATIF (TRUE)] Akses /tCompany tanpa autentikasi...")
        self.page.navigate()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute /tCompany aktif (dialihkan ke /login).")

    def test_14_pilar3_negatif_true_rentang_tanggal_terbalik_pada_branch_ditangani(self):
        """[PILAR 3 - NEGATIF (TRUE)] Rentang tanggal terbalik pada branch ditangani aman tanpa crash."""
        print("\n[Branch Mgmt - Test 14] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada cabang...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-12-31", "2026-01-01")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_table_displayed() or "500" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Filter tanggal terbalik cabang ditangani aman oleh sistem.")

    def test_15_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[Branch Mgmt - Test 15] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
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
    def test_16_pilar4_negatif_false_pencarian_nama_cabang_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama cabang fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Branch Mgmt - Test 16] [PILAR 4: NEGATIF (FALSE)] Pencarian cabang fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_name("CABANG_FIKTIF_NONEXISTENT_99999")
        self.page.wait_for_url_contains("CABANG_FIKTIF_NONEXISTENT_99999")

        row_count = self.page.get_rows_count()
        self.assertFalse(row_count > 0, "Pencarian cabang fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian cabang fiktif ditangani dengan aman (0 data).")

    def test_17_pilar4_negatif_false_akses_tanpa_login_tidak_bisa_lihat_data_rekening_cabang(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu tanpa login TIDAK BISA membaca nomor rekening atau kontak cabang."""
        print("\n[Branch Mgmt - Test 17] [PILAR 4: NEGATIF (FALSE)] Penolakan akses data cabang tanpa login...")
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("BANK ACCOUNT" in page_src, "Data sensitif cabang tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Data nomor rekening dan kontak cabang terproteksi dari luar.")

    def test_18_pilar4_negatif_false_sql_injection_pada_pencarian_nama_cabang(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian nama cabang tidak membobol data."""
        print("\n[Branch Mgmt - Test 18] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada pencarian nama cabang...")
        self.login_sebagai_admin()
        self.page.navigate()

        sqli_payload = "' OR '1'='1"
        self.page.search_by_name(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada nama cabang berhasil ditangkal.")

    def test_19_pilar4_negatif_false_xss_pada_pencarian_nama_cabang(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian cabang tidak dieksekusi browser."""
        print("\n[Branch Mgmt - Test 19] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian cabang...")
        self.login_sebagai_admin()
        self.page.navigate()

        xss_payload = "<script>alert('xss_branch')</script>"
        self.page.search_by_name(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Branch Management.")

    def test_20_pilar4_negatif_false_url_sub_path_fiktif_ditangani_tanpa_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tCompany/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[Branch Mgmt - Test 20] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tCompany/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.BRANCH_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
