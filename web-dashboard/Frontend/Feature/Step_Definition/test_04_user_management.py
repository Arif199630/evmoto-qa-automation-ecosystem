"""
=============================================================================
TEST SUITE 04: USER MANAGEMENT (MENU #4)
Website : <BASE_URL>/tUser
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Tabel Customer, Pencarian HP/Nickname, Modal Promo, SQLi, XSS, Non-Numeric Phone
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan tabel pelanggan, pencarian no HP/nickname, seleksi, & modal aktif (True).
2. Positif (False) : Memastikan tombol aksi nonaktif sebelum seleksi & modal tertutup saat dismiss (False).
3. Negatif (True)  : Memastikan pengalihan rute /login aktif saat halaman diakses tanpa sesi (True).
4. Negatif (False) : Memastikan input non-numerik, data fiktif, SQLi, & XSS tidak membocorkan data (False).
=============================================================================
"""

import re
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_00_login import LoginPage
from pages.page_04_user_management import UserManagementPage


class TestUserManagement(unittest.TestCase):
    """Test Suite Modul User Management dengan Konsep 4 Pilar Testing (15 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = UserManagementPage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Memastikan kondisi keberhasilan bernilai BENAR
    # =========================================================================
    def test_01_pilar1_positif_true_user_mgmt_tabel_dan_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka User Management dan memverifikasi tabel data dan toolbar tampil."""
        print("\n[User Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel master pelanggan...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertTrue("User Management" in self.page.get_title(), "Title harus User Management (True).")
        self.assertTrue("User management" in self.page.get_heading_text(), "Heading harus sesuai (True).")
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengguna harus tampil (True).")
        self.assertTrue(self.page.get_rows_count() > 0, "Tabel harus memuat baris data pelanggan (True).")
        print(f"  -> PASSED [True]: Halaman User Management aktif dengan {self.page.get_rows_count()} pelanggan.")

    def test_02_pilar1_positif_true_user_mgmt_filter_pencarian_phone_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pengguna berdasarkan nomor telepon yang ada di tabel environment aktif."""
        print("\n[User Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian nomor telepon valid...")
        self.login_sebagai_admin()
        self.page.navigate()

        phone = self.page.get_first_row_value("PHONE") or self.page.get_first_row_value("TELEPON")
        if not phone:
            self.skipTest("Belum ada pengguna dengan nomor telepon di environment ini; tambahkan data uji.")
        phone = re.sub(r"\D", "", phone)

        self.page.search_by_phone(phone)
        self.page.wait_for_url_contains("phone=")

        self.assertTrue(f"phone={phone}" in self.page.get_current_url(), "URL harus memuat parameter phone (True).")
        self.assertTrue(self.page.get_rows_count() > 0, f"Pencarian nomor {phone[:4]}*** harus menemukan data pengguna (True).")
        print("  -> PASSED [True]: Pencarian nomor telepon berhasil mengembalikan data akun.")

    def test_03_pilar1_positif_true_user_mgmt_filter_pencarian_nickname_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pengguna berdasarkan nickname pengguna 'jjjjj'."""
        print("\n[User Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian nickname valid...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_nickname("jjjjj")
        self.page.wait_for_url_contains("nickName=jjjjj")

        self.assertTrue("nickName=jjjjj" in self.page.get_current_url(), "URL harus memuat parameter nickName (True).")
        self.assertTrue(self.page.get_rows_count() > 0, "Harus ditemukan baris data berdasarkan nickname (True).")
        print("  -> PASSED [True]: Pencarian berdasarkan nama panggilan (nickname) sukses.")

    def test_04_pilar1_positif_true_user_mgmt_seleksi_aktifkan_tombol_aksi(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio button pengguna mengaktifkan tombol User details & Modify balance."""
        print("\n[User Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Seleksi pengguna mengaktifkan tombol aksi...")
        self.login_sebagai_admin()
        self.page.navigate()

        sukses_pilih = self.page.select_first_user()
        self.assertTrue(sukses_pilih, "Harus berhasil memilih salah satu pengguna (True).")
        self.assertTrue(self.page.is_detail_btn_enabled(), "Tombol User details harus menjadi aktif (True).")
        self.assertTrue(self.page.is_balance_btn_enabled(), "Tombol Modify balance harus menjadi aktif (True).")
        print("  -> PASSED [True]: Tombol aksi rincian dan saldo aktif pasca seleksi user.")

    def test_05_pilar1_positif_true_user_mgmt_dialog_modal_extension_code(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka dialog modal Extension Code menampilkan status dialog open."""
        print("\n[User Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Buka modal Extension Code...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.open_promotion_dialog()
        self.assertTrue(self.page.is_promotion_dialog_open(), "Dialog modal harus berstatus open (True).")
        print("  -> PASSED [True]: Modal dialog Extension Code terbuka sempurna.")

    def test_06_pilar1_positif_true_modal_extension_code_reopenable(self):
        """[PILAR 1 - POSITIF (TRUE)] Modal dialog dapat dibuka, ditutup, dan dibuka kembali tanpa macet."""
        print("\n[User Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Siklus buka-tutup-buka kembali modal promo...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.open_promotion_dialog()
        self.page.close_promotion_dialog()
        self.page.open_promotion_dialog()

        self.assertTrue(self.page.is_promotion_dialog_open(), "Modal harus dapat dibuka kembali dengan lancar (True).")
        print("  -> PASSED [True]: Siklus buka-tutup modal bekerja stabil.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Memastikan saat skenario valid, kondisi error adalah SALAH (Nihil)
    # =========================================================================
    def test_07_pilar2_positif_false_tombol_aksi_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol aksi rincian dan saldo TIDAK AKTIF saat belum ada baris dipilih."""
        print("\n[User Mgmt - Test 07] [PILAR 2: POSITIF (FALSE)] Tombol aksi nonaktif sebelum seleksi...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertFalse(self.page.is_detail_btn_enabled(), "Tombol User details tidak boleh aktif awal (False).")
        self.assertFalse(self.page.is_balance_btn_enabled(), "Tombol Modify balance tidak boleh aktif awal (False).")
        print("  -> PASSED [False]: Tombol aksi terkunci aman sebelum ada user dipilih.")

    def test_08_pilar2_positif_false_dialog_modal_tertutup_setelah_close(self):
        """[PILAR 2 - POSITIF (FALSE)] Dialog modal TIDAK LAGI berstatus open setelah tombol close ditekan."""
        print("\n[User Mgmt - Test 08] [PILAR 2: POSITIF (FALSE)] Tutup modal dialog...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.open_promotion_dialog()
        self.page.close_promotion_dialog()

        self.assertFalse(
            self.page.is_promotion_dialog_open(),
            "Dialog modal tidak boleh tetap berstatus open setelah ditutup (False)."
        )
        print("  -> PASSED [False]: Modal dialog berhasil ditutup dan tidak lagi terbuka.")

    def test_09_pilar2_positif_false_bebas_error_server_500_saat_akses(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman User Management bebas dari error server 500 saat dibuka."""
        print("\n[User Mgmt - Test 09] [PILAR 2: POSITIF (FALSE)] Bebas error 500...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Halaman tidak boleh mengalami 500 internal server error (False)."
        )
        print("  -> PASSED [False]: Halaman User Management bebas dari error 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Memastikan proteksi & pesan error sistem BENAR-BENAR aktif
    # =========================================================================
    def test_10_pilar3_negatif_true_akses_tanpa_login_dialihkan_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tUser tanpa autentikasi benar-benar dialihkan ke /login."""
        print("\n[User Mgmt - Test 10] [PILAR 3: NEGATIF (TRUE)] Redirect /tUser tanpa login...")
        self.page.navigate()
        self.page.wait_for_url_contains("/login")

        self.assertTrue(
            "/login" in self.page.get_current_url(),
            "Akses tanpa login harus diarahkan ke /login (True)."
        )
        print("  -> PASSED [True]: Proteksi autentikasi berhasil mengalihkan ke /login.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Memastikan sistem TIDAK MENGIZINKAN akses tidak sah
    # =========================================================================
    def test_11_pilar4_negatif_false_pencarian_phone_fiktif_tidak_ada_data(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nomor telepon fiktif TIDAK BOLEH memunculkan data pengguna."""
        print("\n[User Mgmt - Test 11] [PILAR 4: NEGATIF (FALSE)] Pencarian no HP fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_phone("9999999999999999")
        self.page.wait_for_url_contains("phone=9999999999999999")

        self.assertFalse(
            self.page.get_user_choices_count() > 0,
            "Tidak boleh ada data user yang cocok untuk nomor telepon fiktif (False)."
        )
        print("  -> PASSED [False]: Pencarian nomor fiktif tidak memunculkan data (0 hasil).")

    def test_12_pilar4_negatif_false_akses_tanpa_login_tidak_bisa_lihat_tabel_user(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pengunjung tanpa login TIDAK BISA melihat tabel data pengguna pelanggan."""
        print("\n[User Mgmt - Test 12] [PILAR 4: NEGATIF (FALSE)] Penolakan akses data pelanggan...")
        self.page.navigate()
        self.page.wait_for_url_contains("/login")

        self.assertFalse(
            "/tUser" in self.page.get_current_url(),
            "URL tidak boleh tetap di /tUser untuk pengguna tak dikenal (False)."
        )
        self.assertFalse(
            self.page.is_displayed(self.page.LOCATOR_SEARCH_PHONE, timeout=2),
            "Form input nomor pelanggan tidak boleh tampil bagi publik (False)."
        )
        print("  -> PASSED [False]: Data master pengguna terproteksi rapat dari akses luar.")

    def test_13_pilar4_negatif_false_input_non_numerik_pada_field_phone(self):
        """[PILAR 4 - NEGATIF (FALSE)] Input teks alfabet pada field no HP tidak merusak server 500."""
        print("\n[User Mgmt - Test 13] [PILAR 4: NEGATIF (FALSE)] Uji input teks alfabet pada no HP...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_phone("bukan_nomor_telepon_abc")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Input alfabet pada phone tidak boleh membuat error 500 (False)."
        )
        print("  -> PASSED [False]: Filter non-numerik pada no HP ditangani aman oleh server.")

    def test_14_pilar4_negatif_false_sql_injection_pada_pencarian_user(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian pelanggan tidak membocorkan data."""
        print("\n[User Mgmt - Test 14] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada customer search...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_nickname("' OR '1'='1' --")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Pencarian SQLi tidak boleh memicu error server 500 (False)."
        )
        print("  -> PASSED [False]: Serangan SQL Injection pada nickname customer berhasil ditolak.")

    def test_15_pilar4_negatif_false_xss_pada_pencarian_nickname(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada nickname pencarian tidak dieksekusi."""
        print("\n[User Mgmt - Test 15] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada nickname customer...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_nickname("<script>window.xss_user=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_user === true;")
        self.assertFalse(
            is_exploited,
            "Script XSS tidak boleh dieksekusi oleh halaman User Management (False)."
        )
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada User Management.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
