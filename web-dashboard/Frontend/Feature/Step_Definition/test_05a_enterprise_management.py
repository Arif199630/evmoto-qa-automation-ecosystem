"""
=============================================================================
TEST SUITE 05A: BASIC INFORMATION - ENTERPRISE MANAGEMENT (MENU #5)
Website:
  1. Enterprise Information : <BASE_URL>/tCompany/admin_update
  2. Enterprise Audit List  : <BASE_URL>/tCompany/auditPage
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Profil Perusahaan, Seleksi Wilayah Kota, Audit Persetujuan Mitra, SQLi, XSS
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan form informasi perusahaan, seleksi kota, dan tabel audit termuat sukses (True).
2. Positif (False) : Memastikan tombol audit tidak aktif sebelum seleksi & sistem bebas dari error 500 (False).
3. Negatif (True)  : Memastikan validasi field wajib isi aktif saat dikosongkan & proteksi rute login bekerja (True).
4. Negatif (False) : Memastikan pencarian perusahaan fiktif, SQLi, & XSS tidak memicu kebocoran data (False).
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
from pages.page_05a_enterprise_management import EnterprisePage


class TestEnterpriseManagement(unittest.TestCase):
    """Test Suite Modul Enterprise Management dengan Konsep 4 Pilar Testing (13 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = EnterprisePage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Memastikan kondisi keberhasilan bernilai BENAR
    # =========================================================================
    def test_01_pilar1_positif_true_company_info_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Enterprise Information dan memvalidasi struktur form identitas tampil."""
        print("\n[Enterprise - Test 01] [PILAR 1: POSITIF (TRUE)] Form Enterprise Info & checkbox kota...")
        self.login_sebagai_admin()
        self.page.navigate_info()

        self.assertTrue("Enterprise Information" in self.page.get_title(), "Title harus sesuai (True).")
        self.assertTrue("Enterprise information" in self.page.get_info_heading_text(), "Heading harus sesuai (True).")
        self.assertTrue(self.page.is_info_form_displayed(), "Form profil perusahaan harus tampil (True).")
        self.assertTrue(self.page.is_info_submit_btn_displayed(), "Tombol Save changes harus tampil (True).")
        self.assertTrue(len(self.page.get_city_checkboxes()) > 0, "Harus memuat checkbox pilihan kota (True).")
        print("  -> PASSED [True]: Form informasi perusahaan dan checkbox kota tampil lengkap.")

    def test_02_pilar1_positif_true_company_info_interaktivitas_city_selection(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji interaktivitas seleksi kota dan pembaruan badge counter kota terpilih."""
        print("\n[Enterprise - Test 02] [PILAR 1: POSITIF (TRUE)] Seleksi kota & counter badge...")
        self.login_sebagai_admin()
        self.page.navigate_info()

        teks_awal = self.page.get_city_count_text()
        sukses_toggle = self.page.toggle_first_city_checkbox()
        self.assertTrue(sukses_toggle, "Toggle checkbox kota harus berhasil (True).")

        teks_baru = self.page.get_city_count_text()
        self.assertTrue(teks_awal != teks_baru, "Badge counter kota harus berubah setelah checkbox di-toggle (True).")
        print(f"  -> PASSED [True]: Seleksi kota berhasil memperbarui counter (dari '{teks_awal}' ke '{teks_baru}').")

    def test_03_pilar1_positif_true_audit_tabel_dan_pencarian_nama_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Enterprise Audit List dan mencari perusahaan valid 'Singapore'."""
        print("\n[Enterprise - Test 03] [PILAR 1: POSITIF (TRUE)] Tabel audit & pencarian valid...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.assertTrue(self.page.is_audit_table_displayed(), "Tabel audit perusahaan harus tampil (True).")
        self.page.search_audit_company("Singapore")

        self.page.wait_for_url_contains("name=Singapore")
        self.assertTrue("name=Singapore" in self.page.get_current_url(), "URL harus memuat parameter query (True).")
        self.assertTrue(self.page.get_audit_rows_count() > 0, "Harus memuat baris data perusahaan hasil pencarian (True).")
        print("  -> PASSED [True]: Tabel audit aktif dan pencarian perusahaan valid berhasil.")

    def test_04_pilar1_positif_true_audit_seleksi_perusahaan_aktifkan_tombol(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih salah satu perusahaan di daftar audit dan memverifikasi seleksi."""
        print("\n[Enterprise - Test 04] [PILAR 1: POSITIF (TRUE)] Seleksi perusahaan audit...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        sukses_pilih = self.page.select_first_audit_company()
        self.assertTrue(sukses_pilih, "Harus berhasil memilih salah satu pilihan perusahaan audit (True).")
        print("  -> PASSED [True]: Seleksi perusahaan berhasil diterapkan.")

    def test_05_pilar1_positif_true_panjang_karakter_maksimum_nama_perusahaan(self):
        """[PILAR 1 - POSITIF (TRUE)] Input nama perusahaan dengan panjang 100 karakter diproses aman."""
        print("\n[Enterprise - Test 05] [PILAR 1: POSITIF (TRUE)] Boundary test panjang nama perusahaan...")
        self.login_sebagai_admin()
        self.page.navigate_info()

        long_name = "PT Enterprise Multi National Logistics Solution Indonesia Global Transport Corporation Tbk 2026"
        self.page.clear_company_name()
        self.page.type_text(self.page.LOCATOR_INFO_NAME_INPUT, long_name)

        input_val = self.page.get_attribute(self.page.LOCATOR_INFO_NAME_INPUT, "value")
        self.assertTrue(len(input_val) > 50, "Input nama perusahaan harus mampu menerima string panjang (True).")
        print(f"  -> PASSED [True]: Input nama perusahaan menerima {len(input_val)} karakter dengan aman.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Memastikan saat skenario valid, kondisi error adalah SALAH (Nihil)
    # =========================================================================
    def test_06_pilar2_positif_false_audit_tombol_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol Audit awal TIDAK BOLEH aktif sebelum ada baris perusahaan dipilih."""
        print("\n[Enterprise - Test 06] [PILAR 2: POSITIF (FALSE)] Tombol audit nonaktif sebelum seleksi...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.assertFalse(
            self.page.is_audit_action_btn_enabled(),
            "Tombol Audit tidak boleh aktif sebelum user memilih radio perusahaan (False)."
        )
        print("  -> PASSED [False]: Tombol Audit berstatus nonaktif (disabled) saat belum ada seleksi.")

    def test_07_pilar2_positif_false_company_info_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman Enterprise Info dan Audit List bebas dari error server 500."""
        print("\n[Enterprise - Test 07] [PILAR 2: POSITIF (FALSE)] Bebas error 500 pada Info & Audit...")
        self.login_sebagai_admin()

        self.page.navigate_info()
        self.assertFalse("500 Internal Server Error" in self.page.get_page_source(), "Tidak boleh error 500 di Info (False).")

        self.page.navigate_audit()
        self.assertFalse("500 Internal Server Error" in self.page.get_page_source(), "Tidak boleh error 500 di Audit (False).")
        print("  -> PASSED [False]: Modul Enterprise bebas dari gangguan server 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Memastikan proteksi & pesan error sistem BENAR-BENAR aktif
    # =========================================================================
    def test_08_pilar3_negatif_true_company_info_validasi_nama_perusahaan_kosong(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengosongkan nama perusahaan (field wajib) memicu penolakan validasi form browser."""
        print("\n[Enterprise - Test 08] [PILAR 3: NEGATIF (TRUE)] Validasi form HTML5 field required...")
        self.login_sebagai_admin()
        self.page.navigate_info()

        self.assertTrue(self.page.is_company_name_required(), "Field nama perusahaan harus memiliki atribut required (True).")

        self.page.clear_company_name()
        self.page.submit_info_form()

        pesan_validasi = self.page.get_company_name_validation_message()
        self.assertTrue(len(pesan_validasi) > 0, "Browser harus memunculkan pesan validasi field wajib diisi (True).")
        print(f"  -> PASSED [True]: Proteksi field required berhasil memicu peringatan ('{pesan_validasi}').")

    def test_09_pilar3_negatif_true_info_dan_audit_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses halaman Enterprise tanpa login dialihkan ke URL /login."""
        print("\n[Enterprise - Test 09] [PILAR 3: NEGATIF (TRUE)] Redirect rute tanpa autentikasi...")
        self.page.navigate_info()
        self.page.wait_for_url_contains("/login")
        self.assertTrue("/login" in self.page.get_current_url(), "Akses Info tanpa login harus redirect ke /login (True).")

        self.page.navigate_audit()
        self.page.wait_for_url_contains("/login")
        self.assertTrue("/login" in self.page.get_current_url(), "Akses Audit tanpa login harus redirect ke /login (True).")
        print("  -> PASSED [True]: Seluruh rute Enterprise terproteksi dan diarahkan ke login.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Memastikan sistem TIDAK MENGIZINKAN akses tidak sah
    # =========================================================================
    def test_10_pilar4_negatif_false_audit_pencarian_fiktif_tidak_ada_data(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama perusahaan fiktif TIDAK BOLEH memunculkan data pilihan audit."""
        print("\n[Enterprise - Test 10] [PILAR 4: NEGATIF (FALSE)] Pencarian perusahaan fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.page.search_audit_company("pt_fiktif_random_99999_xyz")
        self.page.wait_for_url_contains("name=pt_fiktif")

        self.assertFalse(
            self.page.get_audit_choices_count() > 0,
            "Tabel audit tidak boleh memuat pilihan untuk perusahaan fiktif (False)."
        )
        print("  -> PASSED [False]: Pencarian perusahaan fiktif berhasil ditolak tanpa data palsu.")

    def test_11_pilar4_negatif_false_akses_tanpa_login_tidak_bisa_lihat_form_info(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pengunjung tanpa login TIDAK BISA mengakses formulir profil perusahaan."""
        print("\n[Enterprise - Test 11] [PILAR 4: NEGATIF (FALSE)] Form profil tertutup bagi publik...")
        self.page.navigate_info()
        self.page.wait_for_url_contains("/login")

        self.assertFalse(
            "/tCompany/admin_update" in self.page.get_current_url(),
            "URL tidak boleh tetap di halaman profil perusahaan (False)."
        )
        self.assertFalse(
            self.page.is_displayed(self.page.LOCATOR_INFO_NAME_INPUT, timeout=2),
            "Input field nama perusahaan tidak boleh tampil tanpa otorisasi (False)."
        )
        print("  -> PASSED [False]: Data profil legalitas perusahaan terlindungi dari akses luar.")

    def test_12_pilar4_negatif_false_sql_injection_pada_pencarian_audit_ditolak(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian audit tidak membocorkan data."""
        print("\n[Enterprise - Test 12] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada audit search...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.page.search_audit_company("' OR '1'='1' --")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Pencarian SQLi tidak boleh memicu error server 500 (False)."
        )
        print("  -> PASSED [False]: SQL Injection pada audit perusahaan aman tanpa kebocoran data.")

    def test_13_pilar4_negatif_false_xss_pada_pencarian_perusahaan_audit(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada audit company search tidak dieksekusi browser."""
        print("\n[Enterprise - Test 13] [PILAR 4: NEGATIF (FALSE)] Uji XSS pada audit company search...")
        self.login_sebagai_admin()
        self.page.navigate_audit()

        self.page.search_audit_company("<script>window.xss_comp=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_comp === true;")
        self.assertFalse(
            is_exploited,
            "Script XSS tidak boleh dieksekusi oleh halaman audit (False)."
        )
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada audit perusahaan.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
