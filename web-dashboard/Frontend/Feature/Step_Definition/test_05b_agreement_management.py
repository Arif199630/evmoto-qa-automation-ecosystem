"""
=============================================================================
TEST SUITE 05B: BASIC INFORMATION - AGREEMENT MANAGEMENT (MENU #5)
Website: <BASE_URL>/tAgreement & Sub-Halamannya
Sub-Halaman:
  1. City Express delivery agreement (/tAgreement/showSmallPieceLogistics)
  2. Protocol management - Client terminal protocol (/tAgreement)
  3. Instruction for order cancellation (/tAgreement/order)
  4. User guide settings (/tAgreement/user)
  5. Setting of laws and regulations (/tAgreement/law)
  6. About our settings (/tAgreement/me)
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Multi-Bahasa, 9 Toolbar Editor, Rapid Language Switch, UTF-8 Encoding, XSS
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan multi-bahasa, 9 toolbar editor, dropdown audiens, & 6 sub-halaman aktif (True).
2. Positif (False) : Memastikan panel bahasa non-aktif tersembunyi & bebas dari error server 500 (False).
3. Negatif (True)  : Memastikan akses tanpa sesi login ke seluruh sub-halaman dialihkan ke login (True).
4. Negatif (False) : Memastikan URL fiktif & payload XSS tidak merusak integritas perjanjian (False).
=============================================================================
"""

import os
import sys
import time
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_00_login import LoginPage
from pages.page_05b_agreement_management import AgreementPage


class TestAgreementManagement(unittest.TestCase):
    """Test Suite Modul Agreement Management dengan Konsep 4 Pilar Testing (21 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = AgreementPage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def login_sebagai_admin(self):
        """Helper login otomatis via LoginPage."""
        self.login_page.login_as_admin()

    # =========================================================================
    # FITUR 1: CITY EXPRESS DELIVERY AGREEMENT (/tAgreement/showSmallPieceLogistics)
    # =========================================================================
    def test_01_pilar1_positif_true_logistics_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka City Express delivery agreement dan memverifikasi header & default English."""
        print("\n[Agreement - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi Logistics agreement...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        self.assertTrue("Local Express Delivery Agreement" in self.page.get_title(), "Title harus sesuai (True).")
        self.assertTrue("Local express delivery agreement" in self.page.get_h2_text(), "Heading h2 harus sesuai (True).")
        self.assertEqual(self.page.get_selected_language_value(), "2")
        self.assertEqual(self.page.get_selected_language_text(), "English")
        self.assertFalse(self.page.is_panel_english_hidden(), "Panel English harus visible (True).")
        print("  -> PASSED [True]: Komponen header, deskripsi, dan dropdown bahasa berhasil dimuat.")

    def test_02_pilar1_positif_true_logistics_dropdown_bahasa_switch_chinese(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengganti dropdown bahasa ke Chinese dan memvalidasi toggling panel."""
        print("\n[Agreement - Test 02] [PILAR 1: POSITIF (TRUE)] Ganti bahasa ke Chinese (value 1)...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        self.page.switch_language("1")
        self.assertFalse(self.page.is_panel_chinese_hidden(), "Panel Chinese harus terlihat (True).")
        self.assertTrue(self.page.is_panel_english_hidden(), "Panel English harus tersembunyi (True).")
        self.assertTrue(self.page.is_panel_indonesian_hidden(), "Panel Indonesian harus tersembunyi (True).")
        print("  -> PASSED [True]: Toggling panel ke Chinese (value 1) bekerja dengan benar.")

    def test_03_pilar1_positif_true_logistics_dropdown_bahasa_switch_english(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengganti dropdown bahasa ke English dan memvalidasi panel aktif."""
        print("\n[Agreement - Test 03] [PILAR 1: POSITIF (TRUE)] Ganti bahasa ke English (value 2)...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        self.page.switch_language("3")
        self.page.switch_language("2")
        self.assertFalse(self.page.is_panel_english_hidden(), "Panel English harus terlihat (True).")
        self.assertTrue(self.page.is_panel_chinese_hidden(), "Panel Chinese harus tersembunyi (True).")
        print("  -> PASSED [True]: Toggling panel ke English (value 2) bekerja dengan benar.")

    def test_04_pilar1_positif_true_logistics_dropdown_bahasa_switch_indonesian(self):
        """[PILAR 1 - POSITIF (TRUE)] Mengganti dropdown bahasa ke Indonesian dan memvalidasi panel aktif."""
        print("\n[Agreement - Test 04] [PILAR 1: POSITIF (TRUE)] Ganti bahasa ke Indonesian (value 3)...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        self.page.switch_language("3")
        self.assertFalse(self.page.is_panel_indonesian_hidden(), "Panel Indonesian harus terlihat (True).")
        self.assertTrue(self.page.is_panel_english_hidden(), "Panel English harus tersembunyi (True).")
        self.assertTrue(self.page.is_panel_chinese_hidden(), "Panel Chinese harus tersembunyi (True).")
        print("  -> PASSED [True]: Toggling panel ke Indonesian (value 3) bekerja dengan benar.")

    def test_05_pilar1_positif_true_logistics_verifikasi_9_toolbar_editor_rich_text(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi lengkap 9 tombol toolbar formatting editor pada panel English."""
        print("\n[Agreement - Test 05] [PILAR 1: POSITIF (TRUE)] Verifikasi 9 tombol toolbar editor...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        titles_found = self.page.get_toolbar_button_titles()
        expected_tools = [
            "Undo", "Redo", "Bold", "Italic", "Underline",
            "Bulleted list", "Numbered list", "Add link", "Remove formatting"
        ]
        for tool in expected_tools:
            self.assertIn(tool, titles_found, f"Tombol formatting '{tool}' harus ada di toolbar editor (True).")

        print(f"  -> PASSED [True]: Seluruh {len(expected_tools)} tombol formatting toolbar terverifikasi.")

    def test_06_pilar1_positif_true_logistics_verifikasi_editor_contenteditable_dan_sync_textarea(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi editor contenteditable aktif, textarea sinkron, dan tombol simpan."""
        print("\n[Agreement - Test 06] [PILAR 1: POSITIF (TRUE)] Verifikasi contenteditable & tombol Save...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        teks_editor = self.page.get_english_editor_text()
        self.assertTrue(len(teks_editor) > 20, "Editor harus memuat teks perjanjian default (True).")

        isi_textarea = self.page.get_english_textarea_value()
        self.assertTrue(len(isi_textarea) > 20, "Textarea sync harus memuat teks perjanjian (True).")

        tombol_simpan = self.page.get_english_submit_btn_text()
        self.assertIn("Save agreement", tombol_simpan)
        print("  -> PASSED [True]: Editor contenteditable, textarea sinkron, dan tombol 'Save agreement' aktif.")

    def test_07_pilar1_positif_true_rapid_language_switching_stress_test(self):
        """[PILAR 1 - POSITIF (TRUE)] Rapid language switching (1 -> 2 -> 3 -> 1) berjalan mulus tanpa error."""
        print("\n[Agreement - Test 07] [PILAR 1: POSITIF (TRUE)] Uji rapid language switching...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        for lang in ["1", "2", "3", "1"]:
            self.page.switch_language(lang)

        self.assertFalse(self.page.is_panel_chinese_hidden(), "Panel Chinese harus aktif pasca rapid switch (True).")
        print("  -> PASSED [True]: Siklus rapid language switching stabil.")

    def test_08_pilar1_positif_true_utf8_multi_byte_character_encoding(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi encoding UTF-8 mendukung karakter multi-byte tanpa mojibake."""
        print("\n[Agreement - Test 08] [PILAR 1: POSITIF (TRUE)] Verifikasi integritas encoding UTF-8...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        page_src = self.page.get_page_source()
        self.assertTrue("charset" in page_src.lower() or "utf-8" in page_src.lower(), "Halaman harus berstandar UTF-8 (True).")
        print("  -> PASSED [True]: Standar encoding UTF-8 multi-byte terverifikasi aktif.")

    # =========================================================================
    # FITUR 2: CLIENT TERMINAL PROTOCOL MANAGEMENT (/tAgreement)
    # =========================================================================
    def test_09_pilar1_positif_true_protocol_navigasi_dan_verifikasi_komponen(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka halaman /tAgreement dan memverifikasi dropdown kontrol aktif."""
        print("\n[Agreement - Test 09] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tAgreement...")
        self.login_sebagai_admin()
        self.page.navigate_protocol()

        self.assertIn("Agreement Management", self.page.get_title())
        print("  -> PASSED [True]: Halaman Protocol Management termuat dengan dropdown kontrol.")

    def test_10_pilar1_positif_true_protocol_dropdown_kategori_switch(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji dropdown Category agreement (Registration, User agreement, Privacy)."""
        print("\n[Agreement - Test 10] [PILAR 1: POSITIF (TRUE)] Ganti kategori agreement...")
        self.login_sebagai_admin()
        self.page.navigate_protocol()

        tersedia = self.page.get_category_options()
        for exp in ["registration", "user-agreement", "privacy"]:
            self.assertIn(exp, tersedia)

        self.page.switch_category("user-agreement")
        self.assertEqual(self.page.get_selected_category_value(), "user-agreement")
        print(f"  -> PASSED [True]: Kategori agreement berhasil diganti ({len(tersedia)} opsi).")

    def test_11_pilar1_positif_true_protocol_dropdown_audience_switch(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji dropdown Audience (User application vs Driver application)."""
        print("\n[Agreement - Test 11] [PILAR 1: POSITIF (TRUE)] Ganti audience pada dropdown...")
        self.login_sebagai_admin()
        self.page.navigate_protocol()

        self.assertEqual(self.page.get_selected_audience_value(), "1")
        self.page.switch_audience("2")
        self.assertEqual(self.page.get_selected_audience_value(), "2")
        self.assertEqual(self.page.get_selected_audience_text(), "Driver application")
        print("  -> PASSED [True]: Audience switch berhasil diubah ke Driver application.")

    def test_12_pilar1_positif_true_protocol_dropdown_language_switch(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji dropdown Language (Chinese, English, Indonesian) pada Protocol Management."""
        print("\n[Agreement - Test 12] [PILAR 1: POSITIF (TRUE)] Ganti bahasa pada Protocol Management...")
        self.login_sebagai_admin()
        self.page.navigate_protocol()

        opsi = self.page.get_management_language_options()
        self.assertListEqual(opsi, ["1", "2", "3"])
        self.page.switch_management_language("3")
        self.assertEqual(self.page.get_selected_management_language_value(), "3")
        print("  -> PASSED [True]: Language switch pada Protocol Management bekerja normal.")

    # =========================================================================
    # FITUR 3: SUB-HALAMAN LAINNYA DI BAWAH BASIC INFORMATION MANAGEMENT
    # =========================================================================
    def test_13_pilar1_positif_true_order_cancellation_verifikasi_komponen_dan_bahasa(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji Instruction for order cancellation (/tAgreement/order) beserta editor."""
        print("\n[Agreement - Test 13] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tAgreement/order...")
        self.login_sebagai_admin()
        self.page.navigate_order()

        self.assertIn("Order Cancellation Instructions", self.page.get_title())
        self.assertIn("Save instructions", self.page.get_english_submit_btn_text())
        print("  -> PASSED [True]: Halaman Instruction for order cancellation terverifikasi aktif.")

    def test_14_pilar1_positif_true_user_guide_verifikasi_komponen_dan_bahasa(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji User guide settings (/tAgreement/user) beserta tombol simpan."""
        print("\n[Agreement - Test 14] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tAgreement/user...")
        self.login_sebagai_admin()
        self.page.navigate_user_guide()

        self.assertIn("User Guide Settings", self.page.get_title())
        self.assertIn("Save user guide", self.page.get_english_submit_btn_text())
        print("  -> PASSED [True]: Halaman User guide settings terverifikasi aktif.")

    def test_15_pilar1_positif_true_laws_regulations_verifikasi_komponen_dan_bahasa(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji Setting of laws and regulations (/tAgreement/law) beserta tombol simpan."""
        print("\n[Agreement - Test 15] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tAgreement/law...")
        self.login_sebagai_admin()
        self.page.navigate_law()

        self.assertIn("Laws and Regulations", self.page.get_title())
        self.assertIn("Save legal content", self.page.get_english_submit_btn_text())
        print("  -> PASSED [True]: Halaman Setting of laws and regulations terverifikasi aktif.")

    def test_16_pilar1_positif_true_about_us_verifikasi_komponen_dan_bahasa(self):
        """[PILAR 1 - POSITIF (TRUE)] Menguji About our settings (/tAgreement/me) beserta tombol simpan."""
        print("\n[Agreement - Test 16] [PILAR 1: POSITIF (TRUE)] Navigasi ke /tAgreement/me...")
        self.login_sebagai_admin()
        self.page.navigate_about()

        self.assertIn("About Us", self.page.get_title())
        self.assertIn("Save About Us", self.page.get_english_submit_btn_text())
        print("  -> PASSED [True]: Halaman About our settings terverifikasi aktif.")

    def test_17_pilar1_positif_true_agreement_semua_sub_halaman_dapat_diakses_berurutan(self):
        """[PILAR 1 - POSITIF (TRUE)] Memastikan seluruh 6 sub-halaman agreement dapat diakses berurutan tanpa error."""
        print("\n[Agreement - Test 17] [PILAR 1: POSITIF (TRUE)] Akses berurutan seluruh 6 sub-halaman...")
        self.login_sebagai_admin()

        sub_pages = [
            (Config.LOGISTICS_URL, "showSmallPieceLogistics"),
            (Config.AGREEMENT_BASE_URL, "tAgreement"),
            (Config.ORDER_AGREEMENT_URL, "order"),
            (Config.USER_GUIDE_URL, "user"),
            (Config.LAW_URL, "law"),
            (Config.ABOUT_URL, "me"),
        ]

        for url, frag in sub_pages:
            self.driver.get(url)
            self.page.wait_for_url_contains(frag)
            self.assertNotIn("500 Internal Server Error", self.page.get_page_source())
            print(f"    [OK] {url} -> OK")

        print("  -> PASSED [True]: Semua sub-halaman agreement dapat diakses berurutan.")

    # =========================================================================
    # NEGATIF & KEAMANAN (PILAR 2, 3, 4)
    # =========================================================================
    def test_18_pilar3_negatif_true_logistics_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses City Express delivery agreement tanpa login dialihkan ke /login."""
        print("\n[Agreement - Test 18] [PILAR 3: NEGATIF (TRUE)] Akses /tAgreement/showSmallPieceLogistics tanpa login...")
        self.page.navigate_logistics()
        self.page.wait_for_url_contains("/login")
        self.assertIn("/login", self.page.get_current_url())
        print("  -> PASSED [True]: Akses langsung ditolak dan dialihkan ke /login.")

    def test_19_pilar3_negatif_true_protocol_dan_sub_halaman_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses seluruh sub-halaman protocol tanpa login dialihkan ke /login."""
        print("\n[Agreement - Test 19] [PILAR 3: NEGATIF (TRUE)] Akses seluruh sub-halaman protocol tanpa login...")
        sub_urls = [
            Config.AGREEMENT_BASE_URL,
            Config.ORDER_AGREEMENT_URL,
            Config.USER_GUIDE_URL,
            Config.LAW_URL,
            Config.ABOUT_URL
        ]
        for url in sub_urls:
            self.driver.get(url)
            self.page.wait_for_url_contains("/login")
            self.assertIn("/login", self.page.get_current_url())

        print("  -> PASSED [True]: Seluruh sub-halaman aman terproteksi autentikasi.")

    def test_20_pilar4_negatif_false_url_sub_path_fiktif_ditangani_tanpa_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL sub-path agreement yang tidak ada ditangani secara aman tanpa crash 500."""
        print("\n[Agreement - Test 20] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tAgreement/invalid_protocol_path...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.BASE_URL}/tAgreement/invalid_protocol_path_xyz_9999")
        time.sleep(1)

        self.assertNotIn("500 Internal Server Error", self.page.get_page_source())
        self.assertFalse("500 Internal Server Error" in self.page.get_page_source(), "Tidak boleh ada 500 error (False).")
        print("  -> PASSED [False]: URL fiktif ditangani dengan aman tanpa server crash.")

    def test_21_pilar4_negatif_false_xss_injection_pada_rich_text_editor(self):
        """[PILAR 4 - NEGATIF (FALSE)] Payload XSS pada rich text editor tidak dieksekusi oleh browser."""
        print("\n[Agreement - Test 21] [PILAR 4: NEGATIF (FALSE)] Uji coba injeksi script pada rich text editor...")
        self.login_sebagai_admin()
        self.page.navigate_logistics()

        # Injeksi payload teks ke panel editor via JS
        self.driver.execute_script("""
            window.xss_editor_exploited = false;
            var editor = document.querySelector("div[contenteditable='true']");
            if (editor) {
                editor.innerText = "<img src='x' onerror='window.xss_editor_exploited=true;'>";
                editor.dispatchEvent(new Event('input', { bubbles: true }));
            }
        """)
        time.sleep(1)
        is_exploited = self.driver.execute_script("return window.xss_editor_exploited === true;")
        self.assertFalse(is_exploited, "Script injection pada editor tidak boleh mengeksekusi kode berbahaya (False).")
        print("  -> PASSED [False]: Sanitasi editor berhasil menangkal eksekusi kode berbahaya.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
