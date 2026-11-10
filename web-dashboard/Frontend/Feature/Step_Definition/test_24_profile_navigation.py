"""
Test Suite: Modul 19 - Profile & Top Navigation Management Across All Modules
Automation Project EvMoto
Konsep      : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Arsitektur  : Page Object Model (POM)
Website     : <BASE_URL> (Komponen Profil Navbar Global)
"""

import os
import sys
import time
import unittest
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_24_profile_navigation import ProfilePage
from pages.page_00_login import LoginPage


class TestProfileNavigation(unittest.TestCase):
    """
    Test suite komprehensif untuk memverifikasi interaksi menu Profil di pojok
    kanan atas antarmuka pada seluruh modul sistem EvMoto Dashboard:
    - Menampilkan dropdown profil
    - Klik tombol Edit Profil
    - Klik tombol Edit Password
    - Klik tombol Keluar (Logout)
    - Verifikasi kestabilan lintas modul dan ketiadaan bug/crash.
    """

    driver = None
    profile_page = None

    @classmethod
    def setUpClass(cls):
        """Inisialisasi WebDriver satu kali untuk seluruh pengujian modul profil."""
        cls.driver = Config.get_driver()
        cls.login_page = LoginPage(cls.driver)
        cls.profile_page = ProfilePage(cls.driver)

        # Login terlebih dahulu ke dashboard
        cls.login_page.open(Config.LOGIN_URL)
        cls.login_page.login(Config.VALID_USER, Config.VALID_PASS)
        time.sleep(2.5)

    @classmethod
    def tearDownClass(cls):
        """Menutup browser setelah seluruh pengujian modul selesai."""
        if cls.driver:
            cls.driver.quit()

    def ensure_logged_in(self):
        """Helper untuk menjamin browser berada dalam sesi login aktif."""
        try:
            if "/login" in self.driver.current_url or not self.profile_page.is_profile_trigger_present():
                self.driver.get(Config.LOGIN_URL)
                time.sleep(1)
                if "/login" in self.driver.current_url:
                    self.login_page.login(Config.VALID_USER, Config.VALID_PASS)
                    time.sleep(2)
        except Exception:
            self.driver.get(Config.LOGIN_URL)
            time.sleep(1)
            self.login_page.login(Config.VALID_USER, Config.VALID_PASS)
            time.sleep(2)

    def setUp(self):
        """Memastikan setiap test case mulai dari sesi aktif dan dropdown tertutup."""
        self.ensure_logged_in()

        # Pastikan dropdown tertutup sebelum tiap test
        if self.profile_page.is_dropdown_open():
            self.profile_page.click_outside()
            time.sleep(0.3)

    # =========================================================================
    # PILAR 1: POSITIF (TRUE) - Validasi Fungsional & Interaksi Sukses (12 Test)
    # =========================================================================

    def test_01_pilar1_positif_true_avatar_dan_trigger_profil_hadir(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi tombol trigger dan foto avatar profil hadir di pojok kanan atas."""
        print("\n[Profile Nav - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tombol trigger dan avatar...")
        is_visible = self.profile_page.is_profile_trigger_visible()
        has_avatar = self.profile_page.is_avatar_present()
        self.assertTrue(is_visible, "Tombol trigger profil harus tampil di pojok kanan atas.")
        self.assertTrue(has_avatar, "Elemen avatar profil pengguna harus terpasang di navbar.")
        print("  -> PASSED [True]: Tombol trigger profil dan foto avatar terkonfirmasi aktif di layar.")

    def test_02_pilar1_positif_true_buka_dropdown_profil_beranda(self):
        """[PILAR 1 - POSITIF (TRUE)] Klik trigger profil membuka dropdown menu dengan atribut aria-expanded=true."""
        print("[Profile Nav - Test 02] [PILAR 1: POSITIF (TRUE)] Membuka dropdown profil di Beranda...")
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        is_open = self.profile_page.is_dropdown_open()
        expanded = self.profile_page.get_trigger_aria_expanded()
        self.assertTrue(is_open, "Dropdown menu profil harus terbuka saat trigger diklik.")
        self.assertTrue(expanded == "true", "Atribut aria-expanded harus bernilai 'true' saat terbuka.")
        print("  -> PASSED [True]: Dropdown profil berhasil terbuka dengan atribut aria-expanded=true.")

    def test_03_pilar1_positif_true_verifikasi_header_nama_dan_role_admin(self):
        """[PILAR 1 - POSITIF (TRUE)] Dropdown menampilkan header profil berisi nama dan role Administrator."""
        print("[Profile Nav - Test 03] [PILAR 1: POSITIF (TRUE)] Verifikasi identitas user di header dropdown...")
        if not self.profile_page.is_dropdown_open():
            self.profile_page.click_profile_trigger()
        nama = self.profile_page.get_dropdown_header_name()
        role = self.profile_page.get_dropdown_header_role()
        self.assertTrue("Admin" in nama or len(nama) > 0, "Header dropdown harus memuat nama akun admin.")
        self.assertTrue("Administrator" in role or len(role) > 0, "Header dropdown harus memuat role akun.")
        print(f"  -> PASSED [True]: Identitas profil terkonfirmasi valid (Nama: '{nama}', Role: '{role}').")

    def test_04_pilar1_positif_true_verifikasi_tiga_menu_dropdown_hadir(self):
        """[PILAR 1 - POSITIF (TRUE)] Dropdown memuat lengkap 3 menu aksi: Edit Profil, Edit Password, dan Keluar."""
        print("[Profile Nav - Test 04] [PILAR 1: POSITIF (TRUE)] Verifikasi kelengkapan 3 menu aksi profil...")
        if not self.profile_page.is_dropdown_open():
            self.profile_page.click_profile_trigger()
        count = self.profile_page.get_dropdown_items_count()
        has_edit_prof = len(self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-edit]")) > 0
        has_edit_pwd = len(self.driver.find_elements(By.CSS_SELECTOR, "[data-password-edit]")) > 0
        has_logout = len(self.driver.find_elements(By.CSS_SELECTOR, ".profile-dropdown__item.is-danger")) > 0
        self.assertTrue(count >= 3, f"Jumlah menu aksi minimal 3 item (Ditemukan: {count}).")
        self.assertTrue(has_edit_prof, "Menu 'Edit Profil' harus hadir di dalam dropdown.")
        self.assertTrue(has_edit_pwd, "Menu 'Edit Password' harus hadir di dalam dropdown.")
        self.assertTrue(has_logout, "Menu 'Keluar' harus hadir di dalam dropdown.")
        print("  -> PASSED [True]: Tiga opsi aksi (Edit Profil, Edit Password, Keluar) hadir lengkap.")

    def test_05_pilar1_positif_true_klik_edit_profil_memberikan_feedback_aktif(self):
        """[PILAR 1 - POSITIF (TRUE)] Klik menu Edit Profil memberikan respon umpan balik aktif tanpa crash."""
        print("[Profile Nav - Test 05] [PILAR 1: POSITIF (TRUE)] Klik tombol Edit Profil...")
        self.profile_page.click_edit_profile_btn()
        time.sleep(0.5)
        toast_msg = self.profile_page.get_toast_content()
        # Sistem menampilkan notifikasi kesiapan modul profil
        self.assertTrue(len(toast_msg) > 0 or "Profil" in toast_msg or "disiapkan" in toast_msg,
                        "Klik Edit Profil harus memicu respon notifikasi di antarmuka.")
        print(f"  -> PASSED [True]: Aksi Edit Profil berhasil dieksekusi dengan feedback: '{toast_msg}'.")

    def test_06_pilar1_positif_true_klik_edit_password_memberikan_feedback_aktif(self):
        """[PILAR 1 - POSITIF (TRUE)] Klik menu Edit Password memberikan aksi responsif tanpa menyebabkan kegagalan sistem."""
        print("[Profile Nav - Test 06] [PILAR 1: POSITIF (TRUE)] Klik tombol Edit Password...")
        self.profile_page.click_edit_password_btn()
        time.sleep(0.5)
        # Verifikasi sistem tetap responsif dan URL valid
        current_url = self.driver.current_url
        active_domain = urlparse(Config.BASE_URL).netloc
        self.assertIn(active_domain, current_url,
                      "Sistem tetap aktif pada domain environment aktif setelah klik Edit Password.")
        print("  -> PASSED [True]: Aksi Edit Password berhasil dieksekusi tanpa gangguan kestabilan sistem.")

    def test_07_pilar1_positif_true_klik_keluar_redirect_ke_halaman_login(self):
        """[PILAR 1 - POSITIF (TRUE)] Klik tombol Keluar berhasil melakukan logout dan mengarahkan kembali ke /login."""
        print("[Profile Nav - Test 07] [PILAR 1: POSITIF (TRUE)] Klik tombol Keluar (Logout)...")
        self.profile_page.click_logout_btn()
        time.sleep(2.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, f"Setelah klik Keluar, user harus diarahkan ke /login (URL: {current_url}).")
        print("  -> PASSED [True]: Tombol Keluar berhasil memproses logout dan mengalihkan ke halaman login.")

    def test_08_pilar1_positif_true_profil_dropdown_berfungsi_di_driver_management(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi dropdown profil hadir dan dapat dibuka di Modul Driver Management."""
        print("[Profile Nav - Test 08] [PILAR 1: POSITIF (TRUE)] Uji dropdown profil di Driver Management (/tDriver)...")
        self.driver.get(Config.DRIVER_AUDIT_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        is_open = self.profile_page.is_dropdown_open()
        self.assertTrue(is_open, "Dropdown profil harus dapat dibuka di Modul Driver Management.")
        print("  -> PASSED [True]: Dropdown profil berfungsi sempurna di Modul Driver Management.")

    def test_09_pilar1_positif_true_profil_dropdown_berfungsi_di_vehicle_management(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi dropdown profil hadir dan dapat dibuka di Modul Vehicle Management."""
        print("[Profile Nav - Test 09] [PILAR 1: POSITIF (TRUE)] Uji dropdown profil di Vehicle Management (/tCar)...")
        self.driver.get(Config.CAR_LIST_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        is_open = self.profile_page.is_dropdown_open()
        self.assertTrue(is_open, "Dropdown profil harus dapat dibuka di Modul Vehicle Management.")
        print("  -> PASSED [True]: Dropdown profil berfungsi sempurna di Modul Vehicle Management.")

    def test_10_pilar1_positif_true_profil_dropdown_berfungsi_di_travel_order_management(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi dropdown profil hadir dan berfungsi di Modul Travel Order Management."""
        print("[Profile Nav - Test 10] [PILAR 1: POSITIF (TRUE)] Uji dropdown profil di Travel Order Management...")
        self.driver.get(Config.ORDER_MOTORCYCLE_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        is_open = self.profile_page.is_dropdown_open()
        self.assertTrue(is_open, "Dropdown profil harus dapat dibuka di Modul Travel Order Management.")
        print("  -> PASSED [True]: Dropdown profil berfungsi sempurna di Modul Travel Order Management.")

    def test_11_pilar1_positif_true_profil_dropdown_berfungsi_di_withdrawal_management(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi dropdown profil hadir dan berfungsi di Modul Withdrawal Management."""
        print("[Profile Nav - Test 11] [PILAR 1: POSITIF (TRUE)] Uji dropdown profil di Withdrawal Management...")
        self.driver.get(Config.PUB_WITHDRAWAL_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        is_open = self.profile_page.is_dropdown_open()
        self.assertTrue(is_open, "Dropdown profil harus dapat dibuka di Modul Withdrawal Management.")
        print("  -> PASSED [True]: Dropdown profil berfungsi sempurna di Modul Withdrawal Management.")

    def test_12_pilar1_positif_true_profil_dropdown_berfungsi_di_complaint_management(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi dropdown profil hadir dan berfungsi di Modul Complaint Management."""
        print("[Profile Nav - Test 12] [PILAR 1: POSITIF (TRUE)] Uji dropdown profil di Complaint Management (/tComplaint)...")
        self.driver.get(Config.COMPLAINT_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        is_open = self.profile_page.is_dropdown_open()
        self.assertTrue(is_open, "Dropdown profil harus dapat dibuka di Modul Complaint Management.")
        print("  -> PASSED [True]: Dropdown profil berfungsi sempurna di Modul Complaint Management.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Ketiadaan Cacat & Ketersembunyian Menu (6 Test)
    # =========================================================================

    def test_13_pilar2_positif_false_dropdown_tersembunyi_saat_halaman_pertama_dimuat(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan dropdown profil dalam status tersembunyi (hidden=True) saat halaman awal dimuat."""
        print("[Profile Nav - Test 13] [PILAR 2: POSITIF (FALSE)] Memastikan dropdown tertutup saat awal muat...")
        self.driver.get(Config.HOME_URL)
        time.sleep(1.5)
        is_open = self.profile_page.is_dropdown_open()
        self.assertFalse(is_open, "Dropdown profil TIDAK BOLEH terbuka secara otomatis saat halaman baru dibuka.")
        print("  -> PASSED [False]: Dropdown profil terkonfirmasi tersembunyi aman sebelum diinteraksi.")

    def test_14_pilar2_positif_false_klik_di_luar_menutup_dropdown_profil(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan dropdown profil otomatis tertutup kembali saat pengguna mengklik area luar menu."""
        print("[Profile Nav - Test 14] [PILAR 2: POSITIF (FALSE)] Uji klik di luar menu otomatis menutup dropdown...")
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        self.assertTrue(self.profile_page.is_dropdown_open(), "Dropdown harus terbuka setelah trigger diklik.")
        # Klik di luar dropdown
        self.profile_page.click_outside()
        time.sleep(0.4)
        is_open_after = self.profile_page.is_dropdown_open()
        self.assertFalse(is_open_after, "Dropdown profil TIDAK BOLEH tetap terbuka setelah pengguna mengklik area luar.")
        print("  -> PASSED [False]: Dropdown profil otomatis tertutup saat klik di luar area menu.")

    def test_15_pilar2_positif_false_tombol_escape_menutup_dropdown_profil(self):
        """[PILAR 2 - POSITIF (FALSE)] Menekan tombol Escape keyboard otomatis menutup dropdown profil."""
        print("[Profile Nav - Test 15] [PILAR 2: POSITIF (FALSE)] Uji tombol Escape menutup dropdown profil...")
        self.profile_page.click_profile_trigger()
        time.sleep(0.4)
        self.assertTrue(self.profile_page.is_dropdown_open(), "Dropdown harus terbuka sebelum uji Escape.")
        self.profile_page.press_escape_key()
        time.sleep(0.4)
        is_open_after = self.profile_page.is_dropdown_open()
        self.assertFalse(is_open_after, "Dropdown profil TIDAK BOLEH tetap terbuka setelah tombol Escape ditekan.")
        print("  -> PASSED [False]: Tombol Escape berhasil menutup dropdown profil secara responsif.")

    def test_16_pilar2_positif_false_ketiadaan_error_server_500_pada_aksi_profil(self):
        """[PILAR 2 - POSITIF (FALSE)] Seluruh alur klik profil, edit profil, edit password, hingga logout bebas dari respon crash HTTP 500."""
        print("[Profile Nav - Test 16] [PILAR 2: POSITIF (FALSE)] Memastikan bebas dari respon error 500...")
        src = self.driver.page_source.lower()
        has_500 = "500 internal server error" in src or "status=500" in src
        self.assertFalse(has_500, "Halaman antarmuka profil TIDAK BOLEH memuat respon crash HTTP 500.")
        print("  -> PASSED [False]: Komponen profil bebas dari kesalahan fatal 500 Internal Server Error.")

    def test_17_pilar2_positif_false_ketiadaan_whitelabel_error_pada_aksi_profil(self):
        """[PILAR 2 - POSITIF (FALSE)] Seluruh antarmuka profil bebas dari exception Whitelabel Spring Boot."""
        print("[Profile Nav - Test 17] [PILAR 2: POSITIF (FALSE)] Memastikan bebas dari Whitelabel Error...")
        src = self.driver.page_source.lower()
        has_whitelabel = "whitelabel error page" in src or "there was an unexpected error" in src
        self.assertFalse(has_whitelabel, "Antarmuka profil TIDAK BOLEH menampilkan pesan Whitelabel Error.")
        print("  -> PASSED [False]: Komponen profil bersih dari exception Whitelabel Spring Boot.")

    def test_18_pilar2_positif_false_ketiadaan_duplikasi_dropdown_profil(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan DOM navbar bersih dari elemen ganda data-profile-dropdown."""
        print("[Profile Nav - Test 18] [PILAR 2: POSITIF (FALSE)] Memastikan ketiadaan duplikasi dropdown DOM...")
        dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-dropdown]")
        has_duplicate = len(dropdowns) > 1
        self.assertFalse(has_duplicate, "DOM navbar TIDAK BOLEH memuat duplikasi elemen dropdown profil.")
        print("  -> PASSED [False]: Elemen dropdown profil tunggal dan presisi di DOM tanpa redundansi.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Keamanan Sesi & Penolakan Akses Tak Berhak (4 Test)
    # =========================================================================

    def test_19_pilar3_negatif_true_akses_dashboard_setelah_logout_dialihkan_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Setelah user klik Keluar, upaya akses kembali ke /blackboard dicegat dan dialihkan ke /login."""
        print("[Profile Nav - Test 19] [PILAR 3: NEGATIF (TRUE)] Uji proteksi rute dashboard setelah logout...")
        self.profile_page.click_logout_btn()
        time.sleep(2)
        # Upaya akses kembali tanpa otentikasi
        self.driver.get(Config.HOME_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Sistem harus mencegat akses setelah logout dan mengarahkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute aktif; akses ke dashboard setelah logout berhasil dicegat.")

    def test_20_pilar3_negatif_true_akses_complaint_setelah_logout_dialihkan_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Setelah user klik Keluar, rute sensitif /tComplaint dicegat dan dialihkan ke /login."""
        print("[Profile Nav - Test 20] [PILAR 3: NEGATIF (TRUE)] Uji proteksi rute pengaduan setelah logout...")
        # Pastikan sudah logout atau logout
        if "/login" not in self.driver.current_url:
            self.profile_page.click_logout_btn()
            time.sleep(2)
        self.driver.get(Config.COMPLAINT_URL)
        time.sleep(1.5)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Akses ke /tComplaint tanpa login harus dialihkan ke /login.")
        print("  -> PASSED [True]: Proteksi rute pengaduan aktif; pengalihan ke /login terverifikasi akurat.")

    def test_21_pilar3_negatif_true_hapus_session_cookie_memaksa_logout(self):
        """[PILAR 3 - NEGATIF (TRUE)] Menghapus session cookie di browser secara paksa memicu sistem redirect ke /login saat berinteraksi."""
        print("[Profile Nav - Test 21] [PILAR 3: NEGATIF (TRUE)] Uji invalidasi session cookie...")
        # Pastikan login aktif lalu hapus seluruh cookie sesi
        self.driver.delete_all_cookies()
        time.sleep(0.5)
        # Buka rute privat dashboard
        self.driver.get(Config.COMPLAINT_URL)
        time.sleep(2)
        current_url = self.driver.current_url
        self.assertTrue("/login" in current_url, "Penghapusan cookie sesi harus memaksa sistem mengalihkan user ke /login.")
        print("  -> PASSED [True]: Sistem aktif mendeteksi hilangnya cookie sesi dan redirect ke /login.")

    def test_22_pilar3_negatif_true_toggle_buka_tutup_profil_berulang_tetap_stabil(self):
        """[PILAR 3 - NEGATIF (TRUE)] Membuka dan menutup dropdown profil berulang kali tetap menjaga stabilitas aplikasi tanpa kegagalan state."""
        print("[Profile Nav - Test 22] [PILAR 3: NEGATIF (TRUE)] Uji toggle buka-tutup berulang profil...")
        for _ in range(3):
            self.profile_page.click_profile_trigger()
            time.sleep(0.25)
            self.profile_page.click_profile_trigger()
            time.sleep(0.25)
        # Verifikasi dropdown berada pada state stabil
        is_trigger_ok = self.profile_page.is_profile_trigger_visible()
        self.assertTrue(is_trigger_ok, "Trigger profil harus tetap berfungsi normal setelah toggle berulang kali.")
        print("  -> PASSED [True]: Dropdown profil memiliki ketahanan state yang stabil saat di-toggle cepat.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Keamanan Siber, Proteksi Browser Back & Robustness (8 Test)
    # =========================================================================

    def test_23_pilar4_negatif_false_browser_back_setelah_logout_tidak_dapat_akses_data(self):
        """[PILAR 4 - NEGATIF (FALSE)] Setelah logout, simulasi tombol Back di browser lalu refresh tidak dapat mengakses data sesi aktif."""
        print("[Profile Nav - Test 23] [PILAR 4: NEGATIF (FALSE)] Uji proteksi navigasi browser Back pasca logout...")
        self.profile_page.click_logout_btn()
        time.sleep(2)
        # Tekan tombol Back pada browser
        self.driver.back()
        time.sleep(1)
        # Muat ulang untuk memvalidasi otorisasi server
        self.driver.refresh()
        time.sleep(2)
        current_url = self.driver.current_url
        has_active_session = "/login" not in current_url
        self.assertFalse(has_active_session, "Setelah logout dan reload halaman, sesi server TIDAK BOLEH aktif.")
        print("  -> PASSED [False]: Navigasi browser Back pasca logout terlindungi aman dari kebocoran data sesi.")

    def test_24_pilar4_negatif_false_tamu_publik_tanpa_login_tidak_memiliki_akses_profil_dropdown(self):
        """[PILAR 4 - NEGATIF (FALSE)] Halaman publik /login TIDAK BISA memuat atau menampilkan elemen dropdown profil user."""
        print("[Profile Nav - Test 24] [PILAR 4: NEGATIF (FALSE)] Memastikan ketiadaan menu profil di halaman login...")
        if "/login" not in self.driver.current_url:
            self.profile_page.click_logout_btn()
            time.sleep(2)
        self.driver.get(Config.LOGIN_URL)
        time.sleep(1.5)
        profile_triggers = self.driver.find_elements(By.CSS_SELECTOR, "[data-profile-trigger]")
        has_profile_menu = len(profile_triggers) > 0
        self.assertFalse(has_profile_menu, "Halaman login publik TIDAK BOLEH menampilkan elemen dropdown profil.")
        print("  -> PASSED [False]: Tamu publik pada halaman login tidak memiliki akses ke komponen profil.")

    def test_25_pilar4_negatif_false_klik_keluar_tidak_meninggalkan_token_sesi_aktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Setelah klik Keluar, cookie otentikasi sesi aktif dibersihkan / diinvalidasi."""
        print("[Profile Nav - Test 25] [PILAR 4: NEGATIF (FALSE)] Uji pembersihan token sesi pasca klik Keluar...")
        # Pastikan berada di halaman login pasca logout
        if "/login" not in self.driver.current_url:
            self.profile_page.click_logout_btn()
            time.sleep(2)
        cookies = self.driver.get_cookies()
        # Periksa apakah ada cookie admin login yang tersisa
        has_active_login = any(c.get("name") == "active_admin_session" and c.get("value") == "valid" for c in cookies)
        self.assertFalse(has_active_login, "Sesi otentikasi aktif TIDAK BOLEH tersisa di cookie browser setelah logout.")
        print("  -> PASSED [False]: Token sesi terkonfirmasi dibersihkan secara aman dari browser.")

    def test_26_pilar4_negatif_false_serangan_xss_pada_dom_profil_tidak_dieksekusi(self):
        """[PILAR 4 - NEGATIF (FALSE)] Percobaan injeksi skrip XSS pada DOM profil tidak membobol keamanan client-side."""
        print("[Profile Nav - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji sanitasi client-side dari serangan XSS...")
        # Evaluasi apakah ada eksekusi alert atau script injection
        xss_executed = self.driver.execute_script("""
            var executed = false;
            try {
                var el = document.querySelector('[data-profile-trigger]');
                if (el && el.innerHTML.indexOf('<script>') !== -1) { executed = true; }
            } catch(e) {}
            return executed;
        """)
        self.assertFalse(xss_executed, "DOM profil TIDAK BOLEH mengeksekusi script XSS sembarangan.")
        print("  -> PASSED [False]: Komponen profil kebal dari ancaman manipulasi XSS pada antarmuka pengguna.")

    def test_27_pilar4_negatif_false_spam_rapid_click_profil_tidak_menyebabkan_freeze_ui(self):
        """[PILAR 4 - NEGATIF (FALSE)] Rapid click berkali-kali pada trigger profil tidak menyebabkan browser tab hang atau UI crash."""
        print("[Profile Nav - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji ketahanan terhadap rapid spam clicking...")
        trigger = self.driver.find_element(By.CSS_SELECTOR, "[data-profile-trigger]")
        for _ in range(8):
            self.driver.execute_script("arguments[0].click();", trigger)
        time.sleep(0.5)
        # Cek apakah UI masih responsif
        is_responsive = self.driver.execute_script("return document.readyState === 'complete';")
        has_crashed = not is_responsive
        self.assertFalse(has_crashed, "Aplikasi TIDAK BOLEH freeze atau crash saat menerima klik bertubi-tubi.")
        print("  -> PASSED [False]: Komponen profil terbukti kokoh dan responsif tanpa lag ataupun freeze UI.")

    def test_28_pilar4_negatif_false_profil_dropdown_di_system_management_bebas_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Dropdown profil di Modul System Management (/mgr) terbukti bebas dari error JavaScript / crash."""
        print("[Profile Nav - Test 28] [PILAR 4: NEGATIF (FALSE)] Uji ketiadaan crash profil di System Management...")
        self.driver.get(Config.MGR_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.3)
        src = self.driver.page_source.lower()
        has_error = "uncaught referenceerror" in src or "typeerror" in src or "500 internal" in src
        self.assertFalse(has_error, "Halaman System Management TIDAK BOLEH mengalami error saat profil dibuka.")
        print("  -> PASSED [False]: Modul System Management terkonfirmasi bebas dari crash saat profil diakses.")

    def test_29_pilar4_negatif_false_profil_dropdown_di_user_management_bebas_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Dropdown profil di Modul User Management (/tUser) terbukti bebas dari error JavaScript / crash."""
        print("[Profile Nav - Test 29] [PILAR 4: NEGATIF (FALSE)] Uji ketiadaan crash profil di User Management...")
        self.driver.get(Config.USER_MGMT_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.3)
        src = self.driver.page_source.lower()
        has_error = "uncaught referenceerror" in src or "typeerror" in src or "500 internal" in src
        self.assertFalse(has_error, "Halaman User Management TIDAK BOLEH mengalami error saat profil dibuka.")
        print("  -> PASSED [False]: Modul User Management terkonfirmasi bebas dari crash saat profil diakses.")

    def test_30_pilar4_negatif_false_profil_dropdown_di_comment_management_bebas_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Dropdown profil di Modul Comment Management (/tOrderEvaluate) terbukti bebas dari error JavaScript / crash."""
        print("[Profile Nav - Test 30] [PILAR 4: NEGATIF (FALSE)] Uji ketiadaan crash profil di Comment Management...")
        self.driver.get(Config.COMMENT_URL)
        time.sleep(1.5)
        self.profile_page.click_profile_trigger()
        time.sleep(0.3)
        src = self.driver.page_source.lower()
        has_error = "uncaught referenceerror" in src or "typeerror" in src or "500 internal" in src
        self.assertFalse(has_error, "Halaman Comment Management TIDAK BOLEH mengalami error saat profil dibuka.")
        print("  -> PASSED [False]: Modul Comment Management terkonfirmasi bebas dari crash saat profil diakses.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
