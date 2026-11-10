"""
=============================================================================
TEST SUITE 03: SYSTEM MANAGEMENT (MENU #3)
Website:
  1. Platform Administrator : <BASE_URL>/mgr
  2. Role Management       : <BASE_URL>/role
  3. Menu Management       : <BASE_URL>/menu
  4. Divisional Management : <BASE_URL>/dept
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Hak Akses Admin, Role, Menu, Departemen, Validasi Seleksi, XSS & Karakter Khusus
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan tabel admin, role, menu, departemen, & navigasi sekuensial aktif (True).
2. Positif (False) : Memastikan halaman sistem bebas dari error server 500 saat diakses (False).
3. Negatif (True)  : Memastikan aksi edit tanpa seleksi memicu banner peringatan & route terproteksi (True).
4. Negatif (False) : Memastikan user tanpa login DITOLAK mengakses tabel hak akses internal (False).
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
from pages.page_03_system_management import SystemManagementPage


class TestSystemManagement(unittest.TestCase):
    """Test Suite Modul System Management dengan Konsep 4 Pilar Testing (15 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = SystemManagementPage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Memastikan kondisi keberhasilan bernilai BENAR
    # =========================================================================
    def test_01_pilar1_positif_true_mgr_tabel_dan_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka /mgr dan memverifikasi tabel administrator dan tombol aksi tampil."""
        print("\n[System Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel platform admin...")
        self.login_sebagai_admin()
        self.page.navigate_mgr()

        self.assertTrue("Platform Administrator" in self.page.get_title(), "Title harus sesuai (True).")
        self.assertTrue("Platform administrator" in self.page.get_mgr_heading_text(), "Heading harus sesuai (True).")
        self.assertTrue(self.page.is_mgr_table_displayed(), "Tabel administrator harus tampil (True).")
        self.assertTrue(self.page.is_mgr_edit_btn_displayed(), "Tombol Update harus tampil (True).")
        self.assertTrue(self.page.get_mgr_rows_count() > 0, "Harus memuat baris data akun admin (True).")
        print(f"  -> PASSED [True]: Tabel administrator aktif dengan {self.page.get_mgr_rows_count()} baris data.")

    def test_02_pilar1_positif_true_mgr_pencarian_admin_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Melakukan pencarian administrator dengan keyword valid 'admin'."""
        print("\n[System Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian admin valid...")
        self.login_sebagai_admin()
        self.page.navigate_mgr()

        self.page.search_admin("admin")
        self.page.wait_for_url_contains("name=admin")

        self.assertTrue("name=admin" in self.page.get_current_url(), "URL harus memuat parameter query (True).")
        print("  -> PASSED [True]: Pencarian admin berhasil dieksekusi dengan query filter.")

    def test_03_pilar1_positif_true_role_tabel_dan_pencarian_role_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka /role dan memverifikasi tabel serta pencarian nama role."""
        print("\n[System Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Tabel role & filter pencarian role...")
        self.login_sebagai_admin()
        self.page.navigate_role()

        self.assertTrue("Role Management" in self.page.get_title(), "Title harus Role Management (True).")
        self.assertTrue(self.page.is_role_table_displayed(), "Tabel role harus tampil (True).")

        self.page.search_role("admin")
        self.page.wait_for_url_contains("roleName=admin")
        self.assertTrue("roleName=admin" in self.page.get_current_url(), "URL harus memuat parameter roleName (True).")
        print("  -> PASSED [True]: Halaman role termuat dan filter pencarian aktif.")

    def test_04_pilar1_positif_true_menu_dan_dept_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka /menu dan /dept serta memverifikasi struktur tabel tampil."""
        print("\n[System Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Menu & Dept...")
        self.login_sebagai_admin()

        self.page.navigate_menu()
        self.assertTrue(self.page.is_menu_table_displayed(), "Tabel menu harus tampil (True).")

        self.page.navigate_dept()
        self.assertTrue(self.page.is_dept_table_displayed(), "Tabel divisi/departemen harus tampil (True).")
        print("  -> PASSED [True]: Tabel Menu dan Departemen terkonfirmasi tampil sempurna.")

    def test_05_pilar1_positif_true_navigasi_sekuensial_seluruh_sub_halaman_sistem(self):
        """[PILAR 1 - POSITIF (TRUE)] Navigasi sekuensial ke 4 sub-halaman sistem (/mgr -> /role -> /menu -> /dept)."""
        print("\n[System Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Uji navigasi sekuensial 4 sub-halaman...")
        self.login_sebagai_admin()

        endpoints = [
            (self.page.navigate_mgr, "/mgr"),
            (self.page.navigate_role, "/role"),
            (self.page.navigate_menu, "/menu"),
            (self.page.navigate_dept, "/dept")
        ]
        for nav_fn, path in endpoints:
            nav_fn()
            self.page.wait_for_url_contains(path)
            self.assertTrue(path in self.page.get_current_url(), f"URL harus memuat {path} (True).")

        print("  -> PASSED [True]: Seluruh 4 sub-halaman sistem dapat diakses stabil secara sekuensial.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Memastikan saat skenario valid, kondisi error adalah SALAH (Nihil)
    # =========================================================================
    def test_06_pilar2_positif_false_mgr_bebas_error_saat_akses_valid(self):
        """[PILAR 2 - POSITIF (FALSE)] Akses halaman /mgr oleh admin valid tidak memicu error server 500 atau banner error."""
        print("\n[System Mgmt - Test 06] [PILAR 2: POSITIF (FALSE)] Bebas error 500 pada /mgr...")
        self.login_sebagai_admin()
        self.page.navigate_mgr()

        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Halaman /mgr tidak boleh mengalami error 500 (False)."
        )
        self.assertFalse(
            self.page.is_mgr_selection_error_displayed(),
            "Banner error seleksi tidak boleh muncul sebelum ada aksi (False)."
        )
        print("  -> PASSED [False]: Halaman /mgr bersih dari pesan error.")

    def test_07_pilar2_positif_false_role_dan_menu_tidak_ada_error_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman /role dan /menu bebas dari respon 500 internal server error."""
        print("\n[System Mgmt - Test 07] [PILAR 2: POSITIF (FALSE)] Bebas error 500 pada /role & /menu...")
        self.login_sebagai_admin()

        self.page.navigate_role()
        self.assertFalse("500 Internal Server Error" in self.page.get_page_source(), "Tidak boleh error 500 di /role (False).")

        self.page.navigate_menu()
        self.assertFalse("500 Internal Server Error" in self.page.get_page_source(), "Tidak boleh error 500 di /menu (False).")
        print("  -> PASSED [False]: Sub-halaman /role dan /menu bebas dari error 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Memastikan proteksi & pesan error sistem BENAR-BENAR aktif
    # =========================================================================
    def test_08_pilar3_negatif_true_mgr_edit_tanpa_pilih_user_tampilkan_error(self):
        """[PILAR 3 - NEGATIF (TRUE)] Klik tombol Update tanpa memilih radio user memunculkan banner peringatan."""
        print("\n[System Mgmt - Test 08] [PILAR 3: NEGATIF (TRUE)] Validasi seleksi user /mgr...")
        self.login_sebagai_admin()
        self.page.navigate_mgr()

        self.page.click_mgr_edit_btn()
        self.assertTrue(
            self.page.is_mgr_selection_error_displayed(),
            "Banner error seleksi user harus benar-benar muncul (True)."
        )
        print("  -> PASSED [True]: Banner peringatan seleksi user berhasil terpicu.")

    def test_09_pilar3_negatif_true_role_dan_menu_edit_tanpa_seleksi_tampilkan_error(self):
        """[PILAR 3 - NEGATIF (TRUE)] Klik tombol Update pada /role dan /menu tanpa memilih radio memicu error banner."""
        print("\n[System Mgmt - Test 09] [PILAR 3: NEGATIF (TRUE)] Validasi seleksi /role dan /menu...")
        self.login_sebagai_admin()

        self.page.navigate_role()
        self.page.click_role_edit_btn()
        self.assertTrue(self.page.is_role_selection_error_displayed(), "Error seleksi role harus tampil (True).")

        self.page.navigate_menu()
        self.page.click_menu_edit_btn()
        self.assertTrue(self.page.is_menu_selection_error_displayed(), "Error seleksi menu harus tampil (True).")
        print("  -> PASSED [True]: Proteksi aksi edit tanpa radio seleksi aktif pada /role dan /menu.")

    def test_10_pilar3_negatif_true_dept_edit_tanpa_seleksi_tampilkan_error(self):
        """[PILAR 3 - NEGATIF (TRUE)] Klik Update pada /dept tanpa memilih departemen memicu banner error seleksi."""
        print("\n[System Mgmt - Test 10] [PILAR 3: NEGATIF (TRUE)] Validasi seleksi /dept...")
        self.login_sebagai_admin()
        self.page.navigate_dept()

        self.page.click_dept_edit_btn()
        self.assertTrue(
            self.page.is_dept_selection_error_displayed(),
            "Error seleksi departemen harus tampil (True)."
        )
        print("  -> PASSED [True]: Proteksi aksi edit departemen tanpa seleksi aktif.")

    def test_11_pilar3_negatif_true_akses_tanpa_login_dialihkan_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses rute /mgr tanpa login benar-benar dialihkan ke /login."""
        print("\n[System Mgmt - Test 11] [PILAR 3: NEGATIF (TRUE)] Pengalihan rute /mgr tanpa autentikasi...")
        self.page.navigate_mgr()

        self.page.wait_for_url_contains("/login")
        self.assertTrue(
            "/login" in self.page.get_current_url(),
            "Akses tanpa login harus diarahkan ke /login (True)."
        )
        print("  -> PASSED [True]: Proteksi keamanan berhasil mengalihkan ke /login.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Memastikan sistem TIDAK MENGIZINKAN akses tidak sah
    # =========================================================================
    def test_12_pilar4_negatif_false_akses_unauthorized_tidak_buka_tabel_admin(self):
        """[PILAR 4 - NEGATIF (FALSE)] User tanpa login TIDAK BISA mengakses tabel data administrator."""
        print("\n[System Mgmt - Test 12] [PILAR 4: NEGATIF (FALSE)] Penolakan akses tabel admin tanpa login...")
        self.page.navigate_mgr()
        self.page.wait_for_url_contains("/login")

        self.assertFalse(
            "/mgr" in self.page.get_current_url(),
            "URL tidak boleh tetap di /mgr untuk pengunjung tak dikenal (False)."
        )
        self.assertFalse(
            self.page.is_mgr_table_displayed(timeout=2),
            "Tabel admin tidak boleh terlihat oleh publik (False)."
        )
        print("  -> PASSED [False]: Tabel data administrator tertutup rapat bagi publik.")

    def test_13_pilar4_negatif_false_dept_tanpa_login_tidak_bisa_akses_data(self):
        """[PILAR 4 - NEGATIF (FALSE)] User tanpa login TIDAK BISA mengakses tabel divisi departemen organisasi."""
        print("\n[System Mgmt - Test 13] [PILAR 4: NEGATIF (FALSE)] Penolakan akses tabel departemen...")
        self.page.navigate_dept()
        self.page.wait_for_url_contains("/login")

        self.assertFalse(
            "/dept" in self.page.get_current_url(),
            "URL tidak boleh berada di /dept (False)."
        )
        self.assertFalse(
            self.page.is_dept_table_displayed(timeout=2),
            "Tabel departemen tidak boleh tampil bagi pengunjung tanpa login (False)."
        )
        print("  -> PASSED [False]: Data struktur divisi organisasi terlindungi sempurna.")

    def test_14_pilar4_negatif_false_karakter_khusus_pada_pencarian_admin(self):
        """[PILAR 4 - NEGATIF (FALSE)] Karakter spesial pada input admin tidak memicu error server 500."""
        print("\n[System Mgmt - Test 14] [PILAR 4: NEGATIF (FALSE)] Uji karakter khusus pencarian admin...")
        self.login_sebagai_admin()
        self.page.navigate_mgr()

        self.page.search_admin("~!@#$%^&*()_+{}[]")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Karakter khusus tidak boleh membuat server 500 internal error (False)."
        )
        print("  -> PASSED [False]: Karakter khusus ditangani secara aman oleh sistem.")

    def test_15_pilar4_negatif_false_xss_pada_pencarian_role(self):
        """[PILAR 4 - NEGATIF (FALSE)] Input XSS payload pada form roleName tidak dieksekusi oleh browser."""
        print("\n[System Mgmt - Test 15] [PILAR 4: NEGATIF (FALSE)] Uji coba serangan XSS pada role search...")
        self.login_sebagai_admin()
        self.page.navigate_role()

        self.page.search_role("<script>window.xss_role=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_role === true;")
        self.assertFalse(
            is_exploited,
            "Script XSS tidak boleh dieksekusi pada halaman role (False)."
        )
        print("  -> PASSED [False]: Sanitasi XSS berhasil pada pencarian role management.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
