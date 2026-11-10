"""
=============================================================================
TEST SUITE 12: APP MANAGEMENT (MENU #12)
Website : <BASE_URL>/TChatSet, /tbBanner, /TVoice
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Chat Message Presets (/TChatSet), Icon Management (/tbBanner),
          Voice Broadcast Management (/TVoice), Filter & Form Search, Status Tombol,
          Proteksi Sesi & Resiliensi Siber
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel preset chat, icon, voice broadcast, filter, dan navigasi aktif (True).
2. Positif (False) : Memastikan tombol Update & Delete pada ketiga sub-halaman terkunci (disabled) sebelum ada seleksi (False).
3. Negatif (True)  : Memastikan akses rute tanpa login dicegat & sesi habis dialihkan ke /login (True).
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
from pages.page_12_app_management import AppManagementPage


class TestAppManagement(unittest.TestCase):
    """Test Suite App Management dengan Konsep 4 Pilar Testing (32 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = AppManagementPage(self.driver)

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
    def test_01_pilar1_positif_true_chat_set_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Chat Message Presets (/TChatSet) dan memverifikasi tabel aktif."""
        print("\n[App Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Chat Message Presets...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        self.assertTrue(self.page.is_chat_table_displayed(), "Tabel preset chat harus tampil (True).")
        self.assertIn("chat message presets", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Chat Message Presets aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_chat_set_filter_type_user(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter tipe pesan chat untuk User (Value 2)."""
        print("\n[App Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Filter tipe pesan User...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        self.page.filter_chat_by_type("2")
        self.page.wait_for_url_contains("type=2")

        self.assertIn("type=2", self.page.get_current_url())
        self.assertTrue(self.page.is_chat_table_displayed(), "Tabel harus tetap tampil setelah filter tipe (True).")
        print("  -> PASSED [True]: Filter tipe pesan chat User berhasil diaplikasikan.")

    def test_03_pilar1_positif_true_chat_set_filter_type_driver(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter tipe pesan chat untuk Driver (Value 1)."""
        print("\n[App Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Filter tipe pesan Driver...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        self.page.filter_chat_by_type("1")
        self.page.wait_for_url_contains("type=1")

        self.assertIn("type=1", self.page.get_current_url())
        self.assertTrue(self.page.is_chat_table_displayed(), "Tabel harus tetap tampil setelah filter driver (True).")
        print("  -> PASSED [True]: Filter tipe pesan chat Driver berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_chat_set_filter_bahasa_indonesia(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter bahasa pesan chat Bahasa Indonesia (Value 3)."""
        print("\n[App Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Filter bahasa preset Indonesian...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        self.page.filter_chat_by_language("3")
        self.page.wait_for_url_contains("yy=3")

        self.assertIn("yy=3", self.page.get_current_url())
        self.assertTrue(self.page.is_chat_table_displayed(), "Tabel harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter bahasa pesan preset Indonesian berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_chat_set_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang tanggal pada Chat Message Presets terpasang di URL."""
        print("\n[App Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal preset chat...")
        self.login_sebagai_admin()
        self.page.filter_chat_by_date("2026-01-01", "2026-12-31")

        self.assertIn("beginDate=2026-01-01", self.page.get_current_url())
        self.assertIn("endDate=2026-12-31", self.page.get_current_url())
        self.assertTrue(self.page.is_chat_table_displayed(), "Tabel harus tampil dengan filter tanggal (True).")
        print("  -> PASSED [True]: Filter rentang tanggal chat preset berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_chat_set_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel preset pesan chat di DOM."""
        print("\n[App Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom Chat Presets...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("ADD TIME" in page_src, "Kolom Add Time harus ada (True).")
        self.assertTrue("LANGUAGE" in page_src, "Kolom Language harus ada (True).")
        self.assertTrue("CONTENT" in page_src, "Kolom Content harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel Chat Presets terkonfirmasi lengkap.")

    def test_07_pilar1_positif_true_icon_mgmt_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Icon Management (/tbBanner) dan memverifikasi tabel aktif."""
        print("\n[App Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Icon Management...")
        self.login_sebagai_admin()
        self.page.navigate_icon_mgmt()

        self.assertTrue(self.page.is_icon_table_displayed(), "Tabel Icon Management harus tampil (True).")
        self.assertIn("icon management", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Icon Management aktif terkonfirmasi di layar.")

    def test_08_pilar1_positif_true_icon_mgmt_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel Icon Management di DOM."""
        print("\n[App Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom Icon Management...")
        self.login_sebagai_admin()
        self.page.navigate_icon_mgmt()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("ADD TIME" in page_src, "Kolom Add Time harus ada (True).")
        self.assertTrue("ICON NAME" in page_src, "Kolom Icon Name harus ada (True).")
        self.assertTrue("DISPLAY WINDOW" in page_src, "Kolom Display Window harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel Icon Management terkonfirmasi lengkap.")

    def test_09_pilar1_positif_true_voice_broadcast_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Voice Broadcast Management (/TVoice) dan memverifikasi tabel aktif."""
        print("\n[App Mgmt - Test 09] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Voice Broadcast Management...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        self.assertTrue(self.page.is_voice_table_displayed(), "Tabel Voice Broadcast harus tampil (True).")
        self.assertIn("voice broadcast management", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Voice Broadcast Management aktif terkonfirmasi di layar.")

    def test_10_pilar1_positif_true_voice_search_nama(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari rekaman suara berdasarkan nama suara valid."""
        print("\n[App Mgmt - Test 10] [PILAR 1: POSITIF (TRUE)] Pencarian nama rekaman suara...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        self.page.search_voice_by_name("Order")
        self.page.wait_for_url_contains("name=Order")

        self.assertIn("name=Order", self.page.get_current_url())
        self.assertTrue(self.page.is_voice_table_displayed(), "Tabel harus tetap tampil setelah pencarian (True).")
        print("  -> PASSED [True]: Filter pencarian nama rekaman suara berhasil diaplikasikan.")

    def test_11_pilar1_positif_true_voice_filter_bahasa_indonesia(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter bahasa suara voice broadcast Bahasa Indonesia (Value 3)."""
        print("\n[App Mgmt - Test 11] [PILAR 1: POSITIF (TRUE)] Filter bahasa suara Indonesian...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        self.page.filter_voice_by_language("3")
        self.page.wait_for_url_contains("language=3")

        self.assertIn("language=3", self.page.get_current_url())
        self.assertTrue(self.page.is_voice_table_displayed(), "Tabel harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter bahasa suara Indonesian berhasil diaplikasikan.")

    def test_12_pilar1_positif_true_voice_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel Voice Broadcast di DOM."""
        print("\n[App Mgmt - Test 12] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom Voice Broadcast...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("VOICE TYPE" in page_src, "Kolom Voice Type harus ada (True).")
        self.assertTrue("VOICE" in page_src, "Kolom Voice harus ada (True).")
        self.assertTrue("LANGUAGE" in page_src, "Kolom Language harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel Voice Broadcast terkonfirmasi lengkap.")

    def test_13_pilar1_positif_true_navigasi_sekuensial_seluruh_sub_halaman_app(self):
        """[PILAR 1 - POSITIF (TRUE)] Navigasi sekuensial ke 3 sub-halaman App Management dalam 1 sesi login."""
        print("\n[App Mgmt - Test 13] [PILAR 1: POSITIF (TRUE)] Uji navigasi sekuensial sub-halaman App Mgmt...")
        self.login_sebagai_admin()

        sub_pages = [
            (Config.CHAT_SET_URL, "Chat Presets"),
            (Config.ICON_MGMT_URL, "Icon Management"),
            (Config.VOICE_BROADCAST_URL, "Voice Broadcast"),
        ]

        for url, label in sub_pages:
            self.driver.get(url)
            self.assertFalse("500" in self.driver.title)
            print(f"    [OK] {label} ({url}) -> Loaded.")

        print("  -> PASSED [True]: Seluruh sub-halaman App Management stabil diakses berurutan.")

    def test_14_pilar1_positif_true_deep_link_dengan_parameter_pencarian(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[App Mgmt - Test 14] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query voice...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.VOICE_BROADCAST_URL}?name=PromptVoice")
        self.page.wait_for_url_contains("name=PromptVoice")

        self.assertIn("name=PromptVoice", self.page.get_current_url())
        self.assertTrue(self.page.is_voice_table_displayed(), "Tabel harus tampil melalui deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Tombol Terkunci
    # =========================================================================
    def test_15_pilar2_positif_false_tombol_update_chat_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Update preset chat terkunci (disabled) sebelum memilih data."""
        print("\n[App Mgmt - Test 15] [PILAR 2: POSITIF (FALSE)] Tombol Update chat awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        is_enabled = self.page.is_chat_update_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Update chat harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Update preset chat terkunci aman berstatus disabled.")

    def test_16_pilar2_positif_false_tombol_delete_chat_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete preset chat terkunci (disabled) sebelum memilih data."""
        print("\n[App Mgmt - Test 16] [PILAR 2: POSITIF (FALSE)] Tombol Delete chat awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        is_enabled = self.page.is_chat_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete chat harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Delete preset chat terkunci aman berstatus disabled.")

    def test_17_pilar2_positif_false_tombol_update_icon_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Update icon banner terkunci (disabled) sebelum memilih data."""
        print("\n[App Mgmt - Test 17] [PILAR 2: POSITIF (FALSE)] Tombol Update icon awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_icon_mgmt()

        is_enabled = self.page.is_icon_update_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Update icon harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Update icon banner terkunci aman berstatus disabled.")

    def test_18_pilar2_positif_false_tombol_delete_icon_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete icon banner terkunci (disabled) sebelum memilih data."""
        print("\n[App Mgmt - Test 18] [PILAR 2: POSITIF (FALSE)] Tombol Delete icon awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_icon_mgmt()

        is_enabled = self.page.is_icon_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete icon harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Delete icon banner terkunci aman berstatus disabled.")

    def test_19_pilar2_positif_false_tombol_update_voice_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Update voice broadcast terkunci (disabled) sebelum memilih data."""
        print("\n[App Mgmt - Test 19] [PILAR 2: POSITIF (FALSE)] Tombol Update voice awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        is_enabled = self.page.is_voice_update_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Update voice harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Update voice broadcast terkunci aman berstatus disabled.")

    def test_20_pilar2_positif_false_ketiga_sub_halaman_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan ketiga sub-halaman App Management bebas dari error server 500."""
        print("\n[App Mgmt - Test 20] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()

        for url in [Config.CHAT_SET_URL, Config.ICON_MGMT_URL, Config.VOICE_BROADCAST_URL]:
            self.driver.get(url)
            page_src = self.driver.page_source
            self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
            self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")

        print("  -> PASSED [False]: Seluruh sub-halaman App Management bersih dari error 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_21_pilar3_negatif_true_akses_chat_set_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /TChatSet tanpa login dialihkan ke /login."""
        print("\n[App Mgmt - Test 21] [PILAR 3: NEGATIF (TRUE)] Akses /TChatSet tanpa login...")
        self.page.navigate_chat_set()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute preset chat aktif (dialihkan ke /login).")

    def test_22_pilar3_negatif_true_akses_icon_mgmt_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tbBanner tanpa login dialihkan ke /login."""
        print("\n[App Mgmt - Test 22] [PILAR 3: NEGATIF (TRUE)] Akses /tbBanner tanpa login...")
        self.page.navigate_icon_mgmt()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute Icon Management aktif (dialihkan ke /login).")

    def test_23_pilar3_negatif_true_akses_voice_broadcast_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /TVoice tanpa login dialihkan ke /login."""
        print("\n[App Mgmt - Test 23] [PILAR 3: NEGATIF (TRUE)] Akses /TVoice tanpa login...")
        self.page.navigate_voice_broadcast()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute Voice Broadcast aktif (dialihkan ke /login).")

    def test_24_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[App Mgmt - Test 24] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
        self.login_sebagai_admin()
        self.page.navigate_chat_set()

        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Sistem harus mengalihkan ke /login saat sesi habis (True).")
        print("  -> PASSED [True]: Sistem aktif mencegat request dan redirect ke /login saat sesi habis.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Pencegahan Manipulasi & Keamanan Data
    # =========================================================================
    def test_25_pilar4_negatif_false_pencarian_nama_voice_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama rekaman suara fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[App Mgmt - Test 25] [PILAR 4: NEGATIF (FALSE)] Pencarian suara fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        self.page.search_voice_by_name("VOICE_FIKTIF_NONEXISTENT_9999999")
        self.page.wait_for_url_contains("VOICE_FIKTIF_NONEXISTENT_9999999")

        row_count = self.page.get_voice_rows_count()
        self.assertFalse(row_count > 0, "Pencarian suara fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian suara fiktif ditangani dengan aman (0 data).")

    def test_26_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_preset_chat(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu tanpa login TIDAK BISA membaca konten teks preset pesan internal."""
        print("\n[App Mgmt - Test 26] [PILAR 4: NEGATIF (FALSE)] Penolakan akses preset chat tanpa login...")
        self.page.navigate_chat_set()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("CHAT CONTENT" in page_src, "Konten chat tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Data konten preset chat terlindungi dari akses luar.")

    def test_27_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_asset_icon(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu tanpa login TIDAK BISA membaca rincian window icon aplikasi."""
        print("\n[App Mgmt - Test 27] [PILAR 4: NEGATIF (FALSE)] Penolakan akses icon banner tanpa login...")
        self.page.navigate_icon_mgmt()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("DISPLAY WINDOW" in page_src, "Konfigurasi window banner tidak boleh bocor (False).")
        print("  -> PASSED [False]: Konfigurasi aset ikon aplikasi terlindungi dari akses publik.")

    def test_28_pilar4_negatif_false_sql_injection_pada_pencarian_voice_name(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian nama suara tidak membobol data."""
        print("\n[App Mgmt - Test 28] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nama suara...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        sqli_payload = "' OR '1'='1"
        self.page.search_voice_by_name(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada nama suara berhasil ditangkal.")

    def test_29_pilar4_negatif_false_sql_injection_pada_filter_language(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection via query parameter language tidak merusak database."""
        print("\n[App Mgmt - Test 29] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada parameter bahasa...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.VOICE_BROADCAST_URL}?language=3' OR '1'='1")

        page_src = self.page.get_page_source()
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Injeksi parameter bahasa berhasil ditangkal.")

    def test_30_pilar4_negatif_false_xss_script_pada_pencarian_voice_name(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian suara tidak dieksekusi browser."""
        print("\n[App Mgmt - Test 30] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian suara...")
        self.login_sebagai_admin()
        self.page.navigate_voice_broadcast()

        xss_payload = "<script>alert('xss_voice')</script>"
        self.page.search_voice_by_name(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Voice Broadcast Management.")

    def test_31_pilar4_negatif_false_url_subpath_fiktif_chat_set_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /TChatSet/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[App Mgmt - Test 31] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /TChatSet/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.CHAT_SET_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")

    def test_32_pilar4_negatif_false_url_subpath_fiktif_voice_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /TVoice/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[App Mgmt - Test 32] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /TVoice/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.VOICE_BROADCAST_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
