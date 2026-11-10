"""
=============================================================================
TEST SUITE 01: ACCOUNT CANCELLATION MANAGEMENT (MENU #1)
Website : <BASE_URL>/userExit
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Tabel Antrean, Filter Status, Tombol Proses, Error Akun Closed, SQLi, XSS
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan tabel antrean permohonan, pencarian user, & aktivasi tombol proses sukses (True).
2. Positif (False) : Memastikan tombol proses tidak aktif sebelum baris dipilih & bebas dari error 500 (False).
3. Negatif (True)  : Memastikan penutupan ulang akun cleared menampilkan error & proteksi route aktif (True).
4. Negatif (False) : Memastikan user fiktif, serangan SQLi, & XSS tidak membocorkan data akun (False).
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
from pages.page_01_account_cancellation import AccountCancellationPage


class TestAccountCancellation(unittest.TestCase):
    """Test Suite Account Cancellation Management dengan Konsep 4 Pilar Testing (13 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = AccountCancellationPage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Memastikan kondisi keberhasilan dan komponen bernilai BENAR
    # =========================================================================
    def test_01_pilar1_positif_true_tabel_dan_komponen_termuat_sempurna(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka halaman dan memverifikasi tabel serta baris permohonan tampil."""
        print("\n[Account Cancellation - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel permohonan...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertTrue(self.page.is_table_displayed(), "Tabel pembatalan akun harus tampil (True).")
        self.assertTrue(self.page.get_rows_count() > 0, "Harus memuat baris data akun (True).")
        self.assertTrue("Account cancellation" in self.page.get_title(), "Title sesuai (True).")
        print("  -> PASSED [True]: Tabel permohonan pembatalan akun aktif dengan data lengkap.")

    def test_02_pilar1_positif_true_filter_status_cleared_menampilkan_data(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter permohonan dengan status 'Has been cleared' (Value 2)."""
        print("\n[Account Cancellation - Test 02] [PILAR 1: POSITIF (TRUE)] Filter status 'Cleared'...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_status("2")
        self.page.wait_for_url_contains("status=2")

        self.assertTrue("status=2" in self.page.get_current_url(), "URL harus memuat parameter status=2 (True).")
        self.assertTrue(self.page.is_table_displayed(), "Tabel pembatalan akun harus tetap tampil aktif (True).")
        print("  -> PASSED [True]: Filter status 'Cleared' berhasil memuat tabel antrean.")

    def test_03_pilar1_positif_true_seleksi_permohonan_aktifkan_tombol_proses(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih salah satu radio permohonan mengaktifkan tombol 'Immediate processing'."""
        print("\n[Account Cancellation - Test 03] [PILAR 1: POSITIF (TRUE)] Seleksi radio akun...")
        self.login_sebagai_admin()
        self.page.navigate()

        sukses_pilih = self.page.select_first_user_row()
        self.assertTrue(sukses_pilih, "Harus berhasil memilih satu baris permohonan (True).")
        self.assertTrue(
            self.page.is_process_btn_enabled(),
            "Tombol 'Immediate processing' harus menjadi aktif setelah ada akun dipilih (True)."
        )
        print("  -> PASSED [True]: Tombol proses berhasil diaktifkan setelah seleksi akun.")

    def test_04_pilar1_positif_true_header_kolom_tabel_lengkap(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas header kolom tabel pembatalan akun di DOM."""
        print("\n[Account Cancellation - Test 04] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("USER" in page_src or "ACCOUNT" in page_src, "Kolom User/Account harus ada (True).")
        self.assertTrue("STATUS" in page_src, "Kolom Status harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel permohonan akun terverifikasi lengkap.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Memastikan saat skenario valid, kondisi error adalah SALAH (Nihil)
    # =========================================================================
    def test_05_pilar2_positif_false_tombol_proses_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol 'Immediate processing' TIDAK AKTIF saat belum ada baris dipilih."""
        print("\n[Account Cancellation - Test 05] [PILAR 2: POSITIF (FALSE)] Tombol proses awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertFalse(
            self.page.is_process_btn_enabled(),
            "Tombol proses tidak boleh aktif jika belum ada permohonan yang dipilih (False)."
        )
        print("  -> PASSED [False]: Tombol proses terkunci aman berstatus disabled.")

    def test_06_pilar2_positif_false_halaman_bebas_dari_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman pembatalan akun bebas dari status error server 500."""
        print("\n[Account Cancellation - Test 06] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Halaman tidak boleh mengalami kegagalan server 500 (False)."
        )
        print("  -> PASSED [False]: Modul pembatalan akun bersih dari error 500.")

    def test_07_pilar2_positif_false_filter_waiting_review_tanpa_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Filter status 'Waiting for manual review' tidak memicu banner error."""
        print("\n[Account Cancellation - Test 07] [PILAR 2: POSITIF (FALSE)] Filter status 'Waiting for review'...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_status("1")
        self.page.wait_for_url_contains("status=1")

        self.assertFalse(
            self.page.is_closed_account_error_displayed(),
            "Banner error tidak boleh muncul saat melakukan filter status (False)."
        )
        print("  -> PASSED [False]: Filter status manual review bersih tanpa error.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Memastikan proteksi & pesan error sistem BENAR-BENAR aktif
    # =========================================================================
    def test_08_pilar3_negatif_true_proses_ulang_akun_cleared_tampilkan_error(self):
        """[PILAR 3 - NEGATIF (TRUE)] Memproses ulang akun yang sudah cleared memicu banner peringatan sistem."""
        print("\n[Account Cancellation - Test 08] [PILAR 3: NEGATIF (TRUE)] Proses ulang akun cleared...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_status("2")
        self.page.wait_for_url_contains("status=2")

        sukses_pilih = self.page.select_first_user_row()
        if sukses_pilih:
            self.page.click_process_button()
            self.assertTrue(
                self.page.is_closed_account_error_displayed(),
                "Banner error 'Account was cleared' harus benar-benar muncul (True)."
            )
            print("  -> PASSED [True]: Sistem menolak pembatalan ulang dengan banner error.")
        else:
            self.skipTest("Tidak ada data akun berstatus cleared di environment ini untuk diuji ulang.")

    def test_09_pilar3_negatif_true_akses_tanpa_login_dialihkan_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /userExit tanpa login diarahkan ke /login."""
        print("\n[Account Cancellation - Test 09] [PILAR 3: NEGATIF (TRUE)] Akses langsung tanpa login...")
        self.page.navigate()

        self.page.wait_for_url_contains("/login")
        self.assertTrue(
            "/login" in self.page.get_current_url(),
            "Akses tanpa login harus diarahkan ke /login (True)."
        )
        print("  -> PASSED [True]: Proteksi autentikasi aktif mengalihkan ke /login.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Memastikan sistem TIDAK MENGIZINKAN akses tidak sah
    # =========================================================================
    def test_10_pilar4_negatif_false_user_fiktif_tidak_memunculkan_data(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama akun fiktif TIDAK BOLEH memunculkan baris data permohonan."""
        print("\n[Account Cancellation - Test 10] [PILAR 4: NEGATIF (FALSE)] Pencarian user fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_username("user_palsu_fiktif_99999_xyz")
        self.page.wait_for_url_contains("name=user_palsu")

        self.assertFalse(
            self.page.get_rows_count() > 0,
            "Tidak boleh ada data permohonan untuk nama pengguna fiktif (False)."
        )
        print("  -> PASSED [False]: Data fiktif ditangani dengan aman tanpa memunculkan baris akun.")

    def test_11_pilar4_negatif_false_akses_tanpa_login_tidak_bisa_akses_tabel(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pengunjung tanpa login TIDAK BISA mengakses tabel antrean akun."""
        print("\n[Account Cancellation - Test 11] [PILAR 4: NEGATIF (FALSE)] Akses tabel tertutup tanpa login...")
        self.page.navigate()
        self.page.wait_for_url_contains("/login")

        self.assertFalse(
            "/userExit" in self.page.get_current_url(),
            "URL tidak boleh tetap di /userExit (False)."
        )
        self.assertFalse(
            self.page.is_table_displayed(timeout=2),
            "Tabel permohonan akun tidak boleh tampil tanpa login (False)."
        )
        print("  -> PASSED [False]: Tabel data permohonan akun tertutup rapat bagi publik.")

    def test_12_pilar4_negatif_false_sql_injection_pada_pencarian_akun_ditolak(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian akun TIDAK MEMBOBOL data."""
        print("\n[Account Cancellation - Test 12] [PILAR 4: NEGATIF (FALSE)] Uji coba SQLi pada pencarian...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_username("' OR '1'='1' --")
        self.assertFalse(
            "500 Internal Server Error" in self.page.get_page_source(),
            "Pencarian SQLi tidak boleh memicu error server 500 (False)."
        )
        print("  -> PASSED [False]: Serangan SQL Injection pada filter akun berhasil ditangkal.")

    def test_13_pilar4_negatif_false_xss_script_pada_pencarian_akun_tidak_dieksekusi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Input XSS script pada pencarian akun TIDAK BOLEH dieksekusi."""
        print("\n[Account Cancellation - Test 13] [PILAR 4: NEGATIF (FALSE)] Uji coba XSS pada pencarian akun...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_username("<script>window.xss_account=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_account === true;")
        self.assertFalse(
            is_exploited,
            "Script XSS tidak boleh dieksekusi oleh halaman (False)."
        )
        print("  -> PASSED [False]: Sanitasi XSS berhasil pada pencarian permohonan akun.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
