"""
=============================================================================
TEST SUITE 14: COMMENT MANAGEMENT (MENU #14)
Website : <BASE_URL>/tOrderEvaluate
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Comment List Management, Filter Pencarian Lengkap, Verifikasi Header Kolom,
          Proteksi Privasi Nomor HP Penumpang/Driver, Ketahanan Resiliensi Siber
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel komentar/ulasan, filter nama user/driver, order num, tipe, rating, & tanggal aktif (True).
2. Positif (False) : Memastikan halaman ulasan bebas dari respon error server 500, whitelabel exception, & distorsi DOM (False).
3. Negatif (True)  : Memastikan akses rute ulasan tanpa login dicegat & tanggal terbalik ditangani aman (True).
4. Negatif (False) : Memastikan data fiktif 0 baris & data privasi nomor HP pemberi ulasan terlindungi dari publik (False).
=============================================================================
"""

import os
import sys
import unittest
from selenium.webdriver.common.by import By

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import Config
from pages.page_00_login import LoginPage
from pages.page_14_comment_management import CommentPage


class TestCommentManagement(unittest.TestCase):
    """Test Suite Comment Management dengan Konsep 4 Pilar Testing (25 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = CommentPage(self.driver)

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
    def test_01_pilar1_positif_true_comment_list_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Comment Management (/tOrderEvaluate) dan memverifikasi tabel aktif."""
        print("\n[Comment Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Comment Management...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertTrue(self.page.is_table_displayed(), "Tabel komentar harus tampil (True).")
        self.assertIn("comment list management", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Comment Management aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_comment_search_user_name(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari ulasan berdasarkan nama pemesan/user."""
        print("\n[Comment Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian ulasan nama user...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_user_name("Arif")
        self.page.wait_for_url_contains("userName=Arif")

        self.assertIn("userName=Arif", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel ulasan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter pencarian nama pengguna berhasil diaplikasikan.")

    def test_03_pilar1_positif_true_comment_search_driver_name(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari ulasan berdasarkan nama pengemudi/driver."""
        print("\n[Comment Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian ulasan nama driver...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_driver_name("Driver")
        self.page.wait_for_url_contains("driverName=Driver")

        self.assertIn("driverName=Driver", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel ulasan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter pencarian nama driver berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_comment_search_order_num(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari ulasan berdasarkan nomor pesanan (Order Number)."""
        print("\n[Comment Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Pencarian ulasan nomor order...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_order_num("ORD-COMMENT-2026")
        self.page.wait_for_url_contains("orderNum=ORD-COMMENT-2026")

        self.assertIn("orderNum=ORD-COMMENT-2026", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel ulasan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter pencarian nomor order ulasan berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_comment_filter_order_type_motorcycle(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter ulasan tipe layanan pesanan motor (orderType=1)."""
        print("\n[Comment Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Filter ulasan pesanan motor...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_order_type("1")
        self.page.wait_for_url_contains("orderType=1")

        self.assertIn("orderType=1", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah filter tipe (True).")
        print("  -> PASSED [True]: Filter tipe pesanan motor berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_comment_filter_order_type_express(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter ulasan tipe layanan ekspres dalam kota (orderType=4)."""
        print("\n[Comment Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Filter ulasan ekspres dalam kota...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_order_type("4")
        self.page.wait_for_url_contains("orderType=4")

        self.assertIn("orderType=4", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah filter ekspres (True).")
        print("  -> PASSED [True]: Filter tipe pesanan ekspres berhasil diaplikasikan.")

    def test_07_pilar1_positif_true_comment_filter_rating_skor(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter ulasan berdasarkan skor bintang penilaian (fraction=5)."""
        print("\n[Comment Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Filter ulasan skor bintang 5...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_rating("5")
        self.page.wait_for_url_contains("fraction=5")

        self.assertIn("fraction=5", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel ulasan harus tampil setelah filter skor (True).")
        print("  -> PASSED [True]: Filter skor bintang 5 berhasil diaplikasikan.")

    def test_08_pilar1_positif_true_comment_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang waktu ulasan pada Comment Management terpasang di URL."""
        print("\n[Comment Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Filter rentang waktu ulasan...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-01-01", "2026-12-31")
        self.page.wait_for_url_contains("beginTime=2026-01-01")

        self.assertIn("beginTime=2026-01-01", self.page.get_current_url())
        self.assertIn("endTime=2026-12-31", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(timeout=10), "Tabel harus tampil dengan filter waktu (True).")
        print("  -> PASSED [True]: Filter rentang tanggal ulasan berhasil diaplikasikan.")

    def test_09_pilar1_positif_true_comment_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel ulasan komentar di DOM."""
        print("\n[Comment Mgmt - Test 09] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom komentar...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("COMMENT TIME" in page_src, "Kolom Comment Time harus ada (True).")
        self.assertTrue("ORDER NUMBER" in page_src, "Kolom Order Number harus ada (True).")
        self.assertTrue("RATING SCORE" in page_src, "Kolom Rating Score harus ada (True).")
        self.assertTrue("REASON FOR COMMENT" in page_src, "Kolom Reason harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel ulasan terkonfirmasi lengkap.")

    def test_10_pilar1_positif_true_comment_deep_link_dengan_parameter(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[Comment Mgmt - Test 10] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query ulasan...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.COMMENT_URL}?orderNum=EVAL9988")
        self.page.wait_for_url_contains("orderNum=EVAL9988")

        self.assertIn("orderNum=EVAL9988", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel ulasan harus tampil melalui deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Error 500
    # =========================================================================
    def test_11_pilar2_positif_false_halaman_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan halaman Comment Management bebas dari respon error server 500."""
        print("\n[Comment Mgmt - Test 11] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
        self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")
        print("  -> PASSED [False]: Halaman Comment Management bersih dari error 500.")

    def test_12_pilar2_positif_false_tidak_ada_duplikasi_header_tabel(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan DOM tabel ulasan bebas dari duplikasi elemen thead."""
        print("\n[Comment Mgmt - Test 12] [PILAR 2: POSITIF (FALSE)] Uji ketiadaan duplikasi header tabel...")
        self.login_sebagai_admin()
        self.page.navigate()

        theads = self.driver.find_elements(By.TAG_NAME, "thead")
        self.assertFalse(len(theads) > 1, "Tabel ulasan tidak boleh memuat thead ganda (False).")
        print("  -> PASSED [False]: Header tabel ulasan bersih tanpa duplikasi.")

    def test_13_pilar2_positif_false_halaman_bebas_whitelabel_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan antarmuka bebas dari exception whitelabel Spring Boot."""
        print("\n[Comment Mgmt - Test 13] [PILAR 2: POSITIF (FALSE)] Memastikan bebas whitelabel error...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source()
        self.assertFalse("There was an unexpected error" in page_src, "Tidak boleh ada exception whitelabel (False).")
        print("  -> PASSED [False]: Antarmuka Comment Management bersih dari pesan exception sistem.")

    def test_14_pilar2_positif_false_rating_filter_bukan_karakter_rusak(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan input skor ulasan tidak menimbulkan crash visual layout."""
        print("\n[Comment Mgmt - Test 14] [PILAR 2: POSITIF (FALSE)] Uji stabilitas layout saat filter rating...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_rating("4")
        self.page.wait_for_url_contains("fraction=4")

        page_src = self.page.get_page_source()
        self.assertFalse("crash" in page_src.lower() or "exception" in page_src.lower(), "Layout stabil (False).")
        self.assertTrue(self.page.is_table_displayed(timeout=10), "Tabel ulasan tetap tampil utuh (True).")
        print("  -> PASSED [False]: Layout antarmuka tetap konsisten dan utuh.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_15_pilar3_negatif_true_akses_comment_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tOrderEvaluate tanpa login dialihkan ke /login."""
        print("\n[Comment Mgmt - Test 15] [PILAR 3: NEGATIF (TRUE)] Akses /tOrderEvaluate tanpa login...")
        self.page.navigate()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute ulasan komentar aktif (dialihkan ke /login).")

    def test_16_pilar3_negatif_true_rentang_tanggal_terbalik_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Rentang tanggal terbalik (begin > end) ditangani aman tanpa server crash."""
        print("\n[Comment Mgmt - Test 16] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada komentar...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-12-31", "2026-01-01")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_table_displayed() or "500" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Filter tanggal terbalik ulasan ditangani aman oleh sistem.")

    def test_17_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[Comment Mgmt - Test 17] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Sistem harus mengalihkan ke /login saat sesi habis (True).")
        print("  -> PASSED [True]: Sistem aktif mencegat request dan redirect ke /login saat sesi habis.")

    def test_18_pilar3_negatif_true_parameter_rating_non_angka_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Parameter rating non-angka ditangani secara aman dengan tabel tetap tampil."""
        print("\n[Comment Mgmt - Test 18] [PILAR 3: NEGATIF (TRUE)] Uji parameter rating non-angka...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.COMMENT_URL}?fraction=abc")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_table_displayed(), "Tabel ulasan harus tetap tampil aktif saat parameter anomali (True).")
        self.assertTrue("500 Internal Server Error" not in page_src and "Whitelabel Error Page" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Sistem aman menangani input rating non-angka tanpa crash server.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Pencegahan Manipulasi & Keamanan Data
    # =========================================================================
    def test_19_pilar4_negatif_false_pencarian_nomor_order_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nomor pesanan ulasan fiktif menghasilkan tabel tanpa data aman."""
        print("\n[Comment Mgmt - Test 19] [PILAR 4: NEGATIF (FALSE)] Pencarian nomor order fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_order_num("ORD_COMMENT_NONEXISTENT_9999999")
        self.page.wait_for_url_contains("ORD_COMMENT_NONEXISTENT_9999999")

        row_count = self.page.get_rows_count()
        self.assertFalse(row_count > 0, "Pencarian nomor order fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian nomor order fiktif ditangani dengan aman (0 data).")

    def test_20_pilar4_negatif_false_pencarian_nama_user_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama user fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Comment Mgmt - Test 20] [PILAR 4: NEGATIF (FALSE)] Pencarian user ulasan fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_user_name("USER_COMMENT_NONEXISTENT_9999999")
        self.page.wait_for_url_contains("USER_COMMENT_NONEXISTENT_9999999")

        row_count = self.page.get_rows_count()
        self.assertFalse(row_count > 0, "Pencarian nama user fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian nama user fiktif ditangani dengan aman (0 data).")

    def test_21_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_nomor_telepon_komentar(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA membaca nomor HP pemberi ulasan."""
        print("\n[Comment Mgmt - Test 21] [PILAR 4: NEGATIF (FALSE)] Penolakan akses nomor HP ulasan tanpa login...")
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("MOBILE PHONE NUMBER OF USER" in page_src, "Nomor HP pemberi ulasan tidak boleh bocor (False).")
        print("  -> PASSED [False]: Data privasi nomor HP pemberi ulasan terlindungi dari akses publik.")

    def test_22_pilar4_negatif_false_sql_injection_pada_pencarian_user_name(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian nama user tidak membobol data."""
        print("\n[Comment Mgmt - Test 22] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nama user ulasan...")
        self.login_sebagai_admin()
        self.page.navigate()

        sqli_payload = "' OR '1'='1"
        self.page.search_by_user_name(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada pencarian user ulasan berhasil ditangkal.")

    def test_23_pilar4_negatif_false_sql_injection_pada_pencarian_order_num(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada nomor order ulasan tidak merusak database."""
        print("\n[Comment Mgmt - Test 23] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nomor order ulasan...")
        self.login_sebagai_admin()
        self.page.navigate()

        sqli_payload = "'; DROP TABLE t_order_evaluate; --"
        self.page.search_by_order_num(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada order number berhasil ditangkal.")

    def test_24_pilar4_negatif_false_xss_script_pada_pencarian_nama_driver(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian driver tidak dieksekusi browser."""
        print("\n[Comment Mgmt - Test 24] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian driver...")
        self.login_sebagai_admin()
        self.page.navigate()

        xss_payload = "<script>alert('xss_comment')</script>"
        self.page.search_by_driver_name(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Comment Management.")

    def test_25_pilar4_negatif_false_url_subpath_fiktif_comment_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tOrderEvaluate/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[Comment Mgmt - Test 25] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tOrderEvaluate/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.COMMENT_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif ulasan ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
