"""
=============================================================================
TEST SUITE 00: HALAMAN LOGIN (AUTENTIKASI & PREKONDISI)
Website : <BASE_URL>/login
Desain  : Page Object Model (POM) & BDD (Given - When - Then)
Data    : Multi-User Repository (test_data/users.json via UserDataProvider)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Autentikasi Multi-User, Resiliensi Keamanan (SQLi & XSS), Cookie Sesi Browser
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan login sukses, title sesuai, & cookie sesi resmi terbentuk (True).
2. Positif (False) : Memastikan saat login valid, pesan error nihil & form login tidak bocor (False).
3. Negatif (True)  : Memastikan password salah, form kosong, & payload SQLi memicu pertahanan error (True).
4. Negatif (False) : Memastikan penyerang SQLi, XSS script, & user fiktif DITOLAK total dari dashboard (False).
=============================================================================
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from Pages.page_00_login import LoginPage
from Data.user_data import UserDataProvider
from utils.bdd_helper import given, when, then, and_step


class TestHalamanLogin(unittest.TestCase):
    """Test Suite Halaman Login dengan Metode POM, Multi-User Data, dan Logic BDD Given-When-Then."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.login_page.navigate()

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Memastikan respon & kondisi keberhasilan bernilai BENAR
    # =========================================================================
    def test_01_pilar1_positif_true_login_berhasil_masuk_dashboard(self):
        """[PILAR 1 - POSITIF (TRUE)] Login dengan kredensial valid berhasil mengarahkan ke dashboard."""
        print("\n[Login - Test 01] [PILAR 1: POSITIF (TRUE)] Login berhasil kredensial valid...")
        user, pwd = UserDataProvider.get_credentials("super_admin")

        # BDD: Given - When - Then
        given("Pengguna membuka halaman Login EvMoto Dashboard")
        self.assertTrue("/login" in self.login_page.get_current_url() or self.driver.current_url != "")

        when(f"Pengguna menginput username '{user}' dan password valid lalu menekan tombol submit")
        self.login_page.enter_credentials(user, pwd)
        self.login_page.click_submit()

        then("Sistem mengarahkan pengguna ke halaman Dashboard (/blackboard)")
        self.login_page.wait_for_url_contains("/blackboard")
        self.assertTrue(
            "/blackboard" in self.login_page.get_current_url(),
            "URL harus memuat /blackboard setelah login sukses (True)."
        )

        and_step("Dashboard shell utama berhasil ditampilkan di layar")
        self.assertTrue(
            self.login_page.is_dashboard_displayed(),
            "Dashboard shell harus benar-benar terlihat di layar (True)."
        )
        print("  -> PASSED [True]: Pengguna berhasil masuk ke dashboard.")

    def test_02_pilar1_positif_true_judul_halaman_dashboard_sesuai(self):
        """[PILAR 1 - POSITIF (TRUE)] Judul tab browser benar-benar memuat 'Dashboard' setelah login."""
        print("\n[Login - Test 02] [PILAR 1: POSITIF (TRUE)] Verifikasi title dashboard...")
        user, pwd = UserDataProvider.get_credentials("super_admin")

        given("Pengguna berada di form Login EvMoto")
        when(f"Pengguna login dengan akun administrator ('{user}')")
        self.login_page.login(user, pwd)

        then("Halaman Dashboard selesai dimuat dengan title memuat 'Dashboard'")
        self.login_page.wait_for_url_contains("/blackboard")
        self.login_page.wait_for_title_contains("Dashboard")
        self.assertTrue(
            "Dashboard" in self.login_page.get_title(),
            "Judul halaman browser harus memuat teks Dashboard (True)."
        )
        print("  -> PASSED [True]: Judul halaman Dashboard terkonfirmasi sesuai.")

    def test_03_pilar1_positif_true_cookie_sesi_terbentuk_pasca_login(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi cookie sesi browser resmi terbentuk setelah login."""
        print("\n[Login - Test 03] [PILAR 1: POSITIF (TRUE)] Verifikasi cookie sesi login...")
        user, pwd = UserDataProvider.get_credentials("super_admin")

        given("Pengguna menginisialisasi sesi browser pada form login")
        when(f"Pengguna melakukan otentikasi login dengan kredensial '{user}'")
        self.login_page.login(user, pwd)
        self.login_page.wait_for_url_contains("/blackboard")

        then("Cookie sesi resmi berhasil di-generate dan tersimpan di browser")
        cookies = self.login_page.get_cookies()
        self.assertTrue(len(cookies) > 0, "Cookie sesi harus terbentuk di browser setelah login sukses (True).")
        cookie_names = [c.get("name") for c in cookies]
        print(f"  -> PASSED [True]: Cookie sesi aktif terdeteksi ({len(cookies)} cookies: {cookie_names}).")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Memastikan saat skenario valid, kondisi error adalah SALAH (Nihil)
    # =========================================================================
    def test_04_pilar2_positif_false_tidak_ada_pesan_error_saat_login_sukses(self):
        """[PILAR 2 - POSITIF (FALSE)] Login berhasil tidak boleh memunculkan banner/pesan error."""
        print("\n[Login - Test 04] [PILAR 2: POSITIF (FALSE)] Banner error tidak boleh ada...")
        user, pwd = UserDataProvider.get_credentials("super_admin")

        given("Pengguna membuka halaman autentikasi login")
        when(f"Pengguna login sukses menggunakan user valid '{user}'")
        self.login_page.login(user, pwd)
        self.login_page.wait_for_url_contains("/blackboard")

        then("URL browser tidak memuat parameter error dan pesan error tidak tampil")
        self.assertFalse(
            "error=" in self.login_page.get_current_url(),
            "URL tidak boleh memiliki parameter error saat login sukses (False)."
        )
        self.assertFalse(
            self.login_page.is_displayed(self.login_page.LOCATOR_ERROR_MSG),
            "Pesan error login tidak boleh tampil pada sesi yang berhasil (False)."
        )
        print("  -> PASSED [False]: Bebas dari pesan error saat login valid.")

    def test_05_pilar2_positif_false_form_login_tidak_lagi_terlihat(self):
        """[PILAR 2 - POSITIF (FALSE)] Setelah login berhasil, form login tidak boleh lagi tampil di dashboard."""
        print("\n[Login - Test 05] [PILAR 2: POSITIF (FALSE)] Form login hilang dari tampilan...")
        user, pwd = UserDataProvider.get_credentials("super_admin")

        given("Pengguna berada di layar otentikasi awal")
        when(f"Pengguna menyelesaikan alur login dengan akun '{user}'")
        self.login_page.login(user, pwd)
        self.login_page.wait_for_url_contains("/blackboard")

        then("Input field login (username) sudah tidak lagi tampil di layar dashboard")
        self.assertFalse(
            self.login_page.is_displayed(self.login_page.LOCATOR_USERNAME, timeout=2),
            "Input field username login tidak boleh tampil lagi di halaman dashboard (False)."
        )
        print("  -> PASSED [False]: Form login sudah tidak berada di layar.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Memastikan proteksi & pesan error sistem BENAR-BENAR aktif
    # =========================================================================
    def test_06_pilar3_negatif_true_pesan_error_muncul_password_salah(self):
        """[PILAR 3 - NEGATIF (TRUE)] Password salah memicu banner error dengan pesan yang sesuai."""
        print("\n[Login - Test 06] [PILAR 3: NEGATIF (TRUE)] Pesan error password salah...")
        user, wrong_pwd = UserDataProvider.get_credentials("wrong_password_user")

        given("Pengguna membuka form login sistem EvMoto")
        when(f"Pengguna memasukkan username valid '{user}' dengan password salah")
        self.login_page.login(user, wrong_pwd)

        then("Sistem menampilkan notifikasi error 'Account atau password salah.'")
        self.login_page.wait_for_url_contains("error=invalid_credentials")
        err_msg = self.login_page.get_error_message()
        self.assertTrue(
            len(err_msg) > 0,
            "Pesan error penolakan kredensial harus benar-benar ada (True)."
        )
        self.assertEqual(err_msg, "Account atau password salah.")
        print(f"  -> PASSED [True]: Sistem memunculkan notifikasi valid ('{err_msg}').")

    def test_07_pilar3_negatif_true_validasi_browser_saat_field_kosong(self):
        """[PILAR 3 - NEGATIF (TRUE)] Submit form kosong memicu pesan validasi HTML5 browser."""
        print("\n[Login - Test 07] [PILAR 3: NEGATIF (TRUE)] Validasi form HTML5...")
        given("Pengguna membuka form login tanpa mengisi field kredensial")
        when("Pengguna langsung menekan tombol submit")
        self.login_page.click_submit()

        then("Browser memicu validasi native HTML5 bahwa field wajib diisi")
        val_msg = self.login_page.get_username_validation_message()
        self.assertTrue(
            len(val_msg) > 0,
            "Browser harus benar-benar memicu pesan validasi field wajib diisi (True)."
        )
        print(f"  -> PASSED [True]: Validasi field required aktif ('{val_msg}').")

    def test_08_pilar3_negatif_true_sql_injection_payload_ditolak_dengan_error(self):
        """[PILAR 3 - NEGATIF (TRUE)] Percobaan login dengan SQL injection payload memicu penolakan sistem."""
        print("\n[Login - Test 08] [PILAR 3: NEGATIF (TRUE)] Uji coba serangan SQL Injection...")
        sqli_data = UserDataProvider.get_sqli_payload("classic")
        payload = sqli_data["username"]
        dummy_pass = sqli_data["password"]

        given("Penyerang berada pada form login")
        when(f"Penyerang menginputkan payload SQL Injection '{payload}'")
        self.login_page.login(payload, dummy_pass)

        then("Sistem keamanan mendeteksi dan menolak login dengan memunculkan pesan error")
        self.login_page.wait_for_url_contains("error=invalid_credentials")
        err_msg = self.login_page.get_error_message()
        self.assertTrue(
            len(err_msg) > 0,
            "Sistem harus menampilkan error saat menerima payload SQL Injection (True)."
        )
        print("  -> PASSED [True]: Serangan SQL Injection berhasil ditangkal dengan banner error.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Memastikan sistem TIDAK MENGIZINKAN akses tidak sah
    # =========================================================================
    def test_09_pilar4_negatif_false_password_salah_tidak_boleh_masuk_dashboard(self):
        """[PILAR 4 - NEGATIF (FALSE)] Percobaan login password salah TIDAK BOLEH masuk ke dashboard."""
        print("\n[Login - Test 09] [PILAR 4: NEGATIF (FALSE)] Penolakan masuk dashboard...")
        user, wrong_pwd = UserDataProvider.get_credentials("wrong_password_user")

        given("Pengguna berada di layar login")
        when(f"Pengguna mencoba login dengan kredensial salah '{user}'")
        self.login_page.login(user, wrong_pwd)
        self.login_page.wait_for_url_contains("error=invalid_credentials")

        then("Pengguna TIDAK diizinkan dialihkan ke /blackboard dan shell dashboard tidak terbuka")
        self.assertFalse(
            "/blackboard" in self.login_page.get_current_url(),
            "Pengguna dengan password salah tidak boleh dialihkan ke /blackboard (False)."
        )
        self.assertFalse(
            self.login_page.is_dashboard_displayed(),
            "Dashboard shell tidak boleh diizinkan terbuka (False)."
        )
        print("  -> PASSED [False]: Akses ke dashboard berhasil diblokir total.")

    def test_10_pilar4_negatif_false_user_fiktif_tidak_boleh_masuk_dashboard(self):
        """[PILAR 4 - NEGATIF (FALSE)] Percobaan login user tidak terdaftar TIDAK BOLEH masuk ke dashboard."""
        print("\n[Login - Test 10] [PILAR 4: NEGATIF (FALSE)] Penolakan user fiktif...")
        fake_user, fake_pass = UserDataProvider.get_credentials("invalid_user")

        given("Seseorang memasukkan akun fiktif yang tidak terdaftar")
        when(f"Mencoba login dengan username '{fake_user}'")
        self.login_page.login(fake_user, fake_pass)
        self.login_page.wait_for_url_contains("error=invalid_credentials")

        then("Akses menuju /blackboard ditolak secara tegas oleh sistem")
        self.assertFalse(
            "/blackboard" in self.login_page.get_current_url(),
            "User fiktif tidak boleh mendapatkan akses ke /blackboard (False)."
        )
        print("  -> PASSED [False]: Akses user fiktif berhasil ditolak.")

    def test_11_pilar4_negatif_false_sql_injection_tidak_bisa_bypass_autentikasi(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection TIDAK BOLEH membobol akses dashboard sistem."""
        print("\n[Login - Test 11] [PILAR 4: NEGATIF (FALSE)] Bypass auth SQLi harus gagal...")
        sqli_data = UserDataProvider.get_sqli_payload("bypass")
        payload = sqli_data["username"]
        dummy_pass = sqli_data["password"]

        given("Penyerang menyusupkan bypass SQL payload")
        when(f"Melakukan percobaan bypass login dengan payload '{payload}'")
        self.login_page.login(payload, dummy_pass)

        then("Dashboard shell tidak terbuka dan navigasi ke /blackboard gagal")
        self.assertFalse(
            "/blackboard" in self.login_page.get_current_url(),
            "Payload SQL injection tidak boleh berhasil membuka /blackboard (False)."
        )
        self.assertFalse(
            self.login_page.is_dashboard_displayed(),
            "Dashboard shell tidak boleh terbuka oleh serangan SQLi (False)."
        )
        print("  -> PASSED [False]: SQL injection dicegah total dari kebocoran akses.")

    def test_12_pilar4_negatif_false_xss_script_injection_tidak_dieksekusi(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script TIDAK BOLEH dieksekusi atau merusak browser."""
        print("\n[Login - Test 12] [PILAR 4: NEGATIF (FALSE)] Uji coba serangan XSS script payload...")
        xss_data = UserDataProvider.get_xss_payload()
        xss_payload = xss_data["username"]
        dummy_pass = xss_data["password"]

        given("Penyerang memasukkan script tag XSS pada field username")
        when("Formulir disubmit ke server")
        self.login_page.login(xss_payload, dummy_pass)

        then("Script XSS tidak pernah dieksekusi di DOM window browser")
        is_exploited = self.driver.execute_script("return window.xss_exploited === true;")
        self.assertFalse(
            is_exploited,
            "Payload script XSS tidak boleh dieksekusi oleh browser (False)."
        )
        print("  -> PASSED [False]: Input XSS berhasil disanitasi tanpa eksekusi kode berbahaya.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
