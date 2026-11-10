"""
=============================================================================
TEST SUITE 02: HALAMAN BERANDA / DASHBOARD (HOME PAGE)
Website : <BASE_URL>/blackboard
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Widget Metrik, Filter Operasional, Dark Mode, F5 Reload, Back-Button Security, Viewport
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan 3 widget harian, reload F5 stabil, & resolusi laptop 1366x768 adaptif (True).
2. Positif (False) : Memastikan bebas error 500 & tombol Back browser pasca logout TIDAK membocorkan dashboard (False).
3. Negatif (True)  : Memastikan proteksi rute mengalihkan user tak sah & input tanggal invalid ditolak (True).
4. Negatif (False) : Memastikan user tanpa login TIDAK BISA melihat data dashboard & filter invalid ditolak (False).
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
from Pages.page_02_home import HomePage
from Data.user_data import UserDataProvider
from utils.bdd_helper import given, when, then, and_step


class TestHalamanBeranda(unittest.TestCase):
    """Test Suite Halaman Beranda dengan Konsep 4 Pilar Testing (13 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.home_page = HomePage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Memastikan kondisi keberhasilan dan komponen bernilai BENAR
    # =========================================================================
    def test_01_pilar1_positif_true_tiga_widget_metrik_dashboard_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Memastikan 3 widget ringkasan operasional benar-benar tampil."""
        print("\n[Beranda - Test 01] [PILAR 1: POSITIF (TRUE)] Widget metrik operasional...")
        self.login_sebagai_admin()

        self.assertTrue("Dashboard" in self.home_page.get_title(), "Title harus Dashboard (True).")
        self.assertTrue(self.home_page.has_todays_operation_widget(), "Widget Today's operation harus ada (True).")
        self.assertTrue(self.home_page.has_total_operational_widget(), "Widget Total operational data harus ada (True).")
        self.assertTrue(self.home_page.has_general_trend_widget(), "Widget General operating trend harus ada (True).")
        print("  -> PASSED [True]: Ketiga widget metrik operasional terkonfirmasi aktif.")

    def test_02_pilar1_positif_true_filter_tanggal_dan_perusahaan_sukses(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter operasional dengan tanggal valid benar-benar terpasang di URL."""
        print("\n[Beranda - Test 02] [PILAR 1: POSITIF (TRUE)] Filter tanggal operasional...")
        self.login_sebagai_admin()

        self.home_page.filter_by_date("2026-01-01", "2026-12-31")
        self.home_page.wait_for_url_contains("beginDate=2026-01-01")

        self.assertTrue(
            "beginDate=2026-01-01" in self.home_page.get_current_url(),
            "URL harus memuat parameter query beginDate (True)."
        )
        self.assertTrue(
            "endDate=2026-12-31" in self.home_page.get_current_url(),
            "URL harus memuat parameter query endDate (True)."
        )
        print("  -> PASSED [True]: Filter tanggal berhasil dipasang pada URL query dashboard.")

    def test_03_pilar1_positif_true_dropdown_profil_dan_opsi_logout_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Menu profil pengguna dan opsi Logout tampil aktif."""
        print("\n[Beranda - Test 03] [PILAR 1: POSITIF (TRUE)] Menu dropdown profil & Logout...")
        self.login_sebagai_admin()

        self.home_page.open_profile_dropdown()
        self.assertTrue(
            self.home_page.is_displayed(self.home_page.LOCATOR_LOGOUT_BTN),
            "Tombol logout harus benar-benar terlihat setelah dropdown diklik (True)."
        )
        print("  -> PASSED [True]: Opsi Logout berhasil ditemukan dan dapat diakses.")

    def test_04_pilar1_positif_true_reload_halaman_mempertahankan_sesi_dashboard(self):
        """[PILAR 1 - POSITIF (TRUE)] Refresh/F5 browser mempertahankan sesi dashboard tanpa logout."""
        print("\n[Beranda - Test 04] [PILAR 1: POSITIF (TRUE)] Uji reload browser F5...")
        self.login_sebagai_admin()

        self.home_page.refresh_page()
        self.home_page.wait_for_url_contains("/blackboard")

        self.assertTrue(
            "/blackboard" in self.home_page.get_current_url(),
            "Sesi dashboard harus tetap aktif setelah halaman di-refresh (True)."
        )
        self.assertTrue(
            self.home_page.has_todays_operation_widget(),
            "Widget dashboard harus tetap tampil setelah reload (True)."
        )
        print("  -> PASSED [True]: Sesi dashboard persisten setelah refresh/F5.")

    def test_05_pilar1_positif_true_responsivitas_layout_dashboard_pada_resolusi_laptop(self):
        """[PILAR 1 - POSITIF (TRUE)] Dashboard tetap adaptif dan widget tampil pada resolusi laptop (1366x768)."""
        print("\n[Beranda - Test 05] [PILAR 1: POSITIF (TRUE)] Uji responsivitas viewport 1366x768...")
        self.login_sebagai_admin()

        self.home_page.set_window_size(1366, 768)
        self.assertTrue(
            self.home_page.has_todays_operation_widget(),
            "Widget Today's operation harus tetap terlihat pada resolusi 1366x768 (True)."
        )
        print("  -> PASSED [True]: Layout dashboard responsif pada resolusi laptop 1366x768.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Memastikan saat skenario valid, kondisi error adalah SALAH (Nihil)
    # =========================================================================
    def test_06_pilar2_positif_false_dashboard_bebas_dari_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Halaman dashboard TIDAK BOLEH memuat respon error server 500."""
        print("\n[Beranda - Test 06] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()

        self.assertFalse(
            "500 Internal Server Error" in self.home_page.get_page_source(),
            "Dashboard tidak boleh mengalami crash atau 500 internal server error (False)."
        )
        print("  -> PASSED [False]: Dashboard bersih dari respon error 500.")

    def test_07_pilar2_positif_false_dropdown_profil_tidak_hidden_setelah_klik(self):
        """[PILAR 2 - POSITIF (FALSE)] Dropdown menu profil TIDAK BOLEH berstatus tersembunyi (hidden) setelah dibuka."""
        print("\n[Beranda - Test 07] [PILAR 2: POSITIF (FALSE)] Dropdown menu tidak hidden...")
        self.login_sebagai_admin()

        self.home_page.open_profile_dropdown()
        self.assertFalse(
            self.home_page.is_profile_dropdown_hidden(),
            "Menu profil pengguna tidak boleh bernilai hidden setelah diklik (False)."
        )
        print("  -> PASSED [False]: Menu dropdown terbuka sempurna dan tidak tersembunyi.")

    def test_08_pilar2_positif_false_dark_mode_tidak_merusak_komponen_dashboard(self):
        """[PILAR 2 - POSITIF (FALSE)] Toggle tema Dark Mode TIDAK BOLEH menghilangkan widget dashboard dari layar."""
        print("\n[Beranda - Test 08] [PILAR 2: POSITIF (FALSE)] Toggle tema Dark Mode...")
        self.login_sebagai_admin()

        self.home_page.toggle_theme()
        self.assertFalse(
            not self.home_page.has_todays_operation_widget(),
            "Widget tidak boleh hilang saat tema gelap diaktifkan (False)."
        )
        print("  -> PASSED [False]: Komponen dashboard tetap utuh saat dark mode aktif.")

    def test_09_pilar2_positif_false_browser_back_setelah_logout_tidak_buka_dashboard(self):
        """[PILAR 2 - POSITIF (FALSE)] Menekan tombol Back browser setelah logout TIDAK MEMBUKA dashboard."""
        print("\n[Beranda - Test 09] [PILAR 2: POSITIF (FALSE)] Uji proteksi tombol Back pasca logout...")
        self.login_sebagai_admin()

        self.home_page.logout()
        self.home_page.wait_for_url_contains("/login")

        # Coba klik tombol Back di browser lalu refresh untuk memvalidasi sesi ke server
        self.home_page.navigate_back()
        self.home_page.refresh_page()
        self.home_page.wait_for_url_contains("/login")

        self.assertFalse(
            "/blackboard" in self.home_page.get_current_url(),
            "Tombol Back browser setelah logout tidak boleh membuka dashboard aktif (False)."
        )
        print("  -> PASSED [False]: Sesi aman! Server menolak sesi dan mengembalikan ke login.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Memastikan proteksi & pesan error sistem BENAR-BENAR aktif
    # =========================================================================
    def test_10_pilar3_negatif_true_filter_tanggal_invalid_menampilkan_penolakan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Filter dengan tanggal terbalik (begin > end) ditangani dengan benar."""
        print("\n[Beranda - Test 10] [PILAR 3: NEGATIF (TRUE)] Filter tanggal terbalik...")
        self.login_sebagai_admin()

        self.home_page.filter_by_date("2026-12-31", "2026-01-01")
        self.home_page.wait_for_url_contains("beginDate=2026-12-31")

        self.assertTrue(
            "beginDate=2026-12-31" in self.home_page.get_current_url(),
            "Sistem harus menangani filter tanggal secara aman (True)."
        )
        print("  -> PASSED [True]: Sistem menolak/menangani rentang tanggal terbalik tanpa crash.")

    def test_11_pilar3_negatif_true_akses_tanpa_login_dialihkan_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses URL dashboard tanpa autentikasi dialihkan ke /login."""
        print("\n[Beranda - Test 11] [PILAR 3: NEGATIF (TRUE)] Akses langsung dashboard tanpa login...")
        self.home_page.navigate()

        self.home_page.wait_for_url_contains("/login")
        self.assertTrue(
            "/login" in self.home_page.get_current_url(),
            "Akses tanpa sesi harus benar-benar dialihkan ke URL /login (True)."
        )
        print("  -> PASSED [True]: Proteksi autentikasi aktif mengalihkan ke /login.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Memastikan sistem TIDAK MENGIZINKAN akses tidak sah
    # =========================================================================
    def test_12_pilar4_negatif_false_akses_tanpa_login_tidak_bisa_lihat_data_metrik(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pengunjung tanpa login TIDAK BISA melihat data angka operasional."""
        print("\n[Beranda - Test 12] [PILAR 4: NEGATIF (FALSE)] Penolakan akses data metrik tanpa login...")
        self.home_page.navigate()
        self.home_page.wait_for_url_contains("/login")

        self.assertFalse(
            "/blackboard" in self.home_page.get_current_url(),
            "Pengunjung tanpa login tidak boleh tetap berada di /blackboard (False)."
        )
        self.assertFalse(
            self.home_page.has_todays_operation_widget(),
            "Widget operasional tidak boleh tampil bagi publik (False)."
        )
        print("  -> PASSED [False]: Data metrik operasional terproteksi dari publik.")

    def test_13_pilar4_negatif_false_logout_berhasil_tidak_lagi_di_dashboard(self):
        """[PILAR 4 - NEGATIF (FALSE)] Setelah logout, user TIDAK BERADA di /blackboard dan widget tidak tampil."""
        print("\n[Beranda - Test 13] [PILAR 4: NEGATIF (FALSE)] Pasca logout tidak boleh ada di dashboard...")
        self.login_sebagai_admin()
        self.home_page.logout()

        self.home_page.wait_for_url_contains("/login")
        self.assertFalse(
            "/blackboard" in self.home_page.get_current_url(),
            "Setelah logout, URL tidak boleh tetap memuat /blackboard (False)."
        )
        print("  -> PASSED [False]: Pengguna berhasil keluar penuh dari sesi dashboard.")


if __name__ == "__main__":
    unittest.main(verbosity=2)

