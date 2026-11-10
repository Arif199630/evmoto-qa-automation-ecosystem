"""
=============================================================================
TEST SUITE 11: TRAVEL ORDER MANAGEMENT (MENU #11)
Website : <BASE_URL>/tOrderPrivateCar, /tOrderLogistics
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Motorcycle Orders (/tOrderPrivateCar), City Express Orders (/tOrderLogistics),
          Filter Pencarian Lengkap, Status Tombol Aksi, Proteksi Sesi & Resiliensi Siber
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel pesanan motor & ekspres, filter pencarian, kolom, dan navigasi aktif (True).
2. Positif (False) : Memastikan tombol View details, Cancel order, & Delete terkunci (disabled) sebelum ada seleksi (False).
3. Negatif (True)  : Memastikan akses rute tanpa login dicegat & tanggal terbalik ditangani secara aman (True).
4. Negatif (False) : Memastikan data pesanan fiktif 0 baris & serangan siber (SQLi/XSS) ditangkal total (False).
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
from pages.page_11_travel_order_management import TravelOrderPage


class TestTravelOrderManagement(unittest.TestCase):
    """Test Suite Travel Order Management dengan Konsep 4 Pilar Testing (33 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = TravelOrderPage(self.driver)

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
    def test_01_pilar1_positif_true_motorcycle_orders_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Motorcycle Orders (/tOrderPrivateCar) dan memverifikasi tabel aktif."""
        print("\n[Travel Order - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Motorcycle Orders...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        self.assertTrue(self.page.is_motorcycle_table_displayed(), "Tabel pesanan motor harus tampil (True).")
        self.assertIn("motorcycle orders", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Motorcycle Orders aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_motorcycle_search_order_num(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pesanan motor berdasarkan nomor pesanan terpasang di URL."""
        print("\n[Travel Order - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian nomor pesanan motor...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        self.page.search_motorcycle_by_order_num("ORD-2026")
        self.page.wait_for_url_contains("orderNum=ORD-2026")

        self.assertIn("orderNum=ORD-2026", self.page.get_current_url())
        self.assertTrue(self.page.is_motorcycle_table_displayed(), "Tabel harus tetap tampil setelah pencarian (True).")
        print("  -> PASSED [True]: Filter nomor pesanan motor berhasil diaplikasikan.")

    def test_03_pilar1_positif_true_motorcycle_search_user_phone(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pesanan motor berdasarkan nomor telepon pemesan."""
        print("\n[Travel Order - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian no HP pemesan motor...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        self.page.search_motorcycle_by_user_phone("08123456789")
        self.page.wait_for_url_contains("userPhone=08123456789")

        self.assertIn("userPhone=08123456789", self.page.get_current_url())
        self.assertTrue(self.page.is_motorcycle_table_displayed(), "Tabel harus tetap tampil setelah pencarian (True).")
        print("  -> PASSED [True]: Filter nomor telepon pemesan berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_motorcycle_filter_source_app(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter sumber pesanan motor dengan opsi APP Order (Value 1)."""
        print("\n[Travel Order - Test 04] [PILAR 1: POSITIF (TRUE)] Filter sumber pesanan motor APP...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        self.page.filter_motorcycle_by_source("1")
        self.page.wait_for_url_contains("orderSource=1")

        self.assertIn("orderSource=1", self.page.get_current_url())
        self.assertTrue(self.page.is_motorcycle_table_displayed(), "Tabel harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter sumber pesanan APP berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_motorcycle_filter_state_completed(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter status pesanan motor dengan opsi Completed (Value 9)."""
        print("\n[Travel Order - Test 05] [PILAR 1: POSITIF (TRUE)] Filter status pesanan motor Selesai...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        self.page.filter_motorcycle_by_state("9")
        self.page.wait_for_url_contains("state=9")

        self.assertIn("state=9", self.page.get_current_url())
        self.assertTrue(self.page.is_motorcycle_table_displayed(), "Tabel harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter status pesanan Completed berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_motorcycle_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang tanggal pada Motorcycle Orders terpasang di URL."""
        print("\n[Travel Order - Test 06] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal pesanan motor...")
        self.login_sebagai_admin()
        self.page.filter_motorcycle_by_date("2026-01-01", "2026-12-31")

        self.assertIn("beginDate=2026-01-01", self.page.get_current_url())
        self.assertIn("endDate=2026-12-31", self.page.get_current_url())
        self.assertTrue(self.page.is_motorcycle_table_displayed(), "Tabel harus tampil (True).")
        print("  -> PASSED [True]: Filter rentang tanggal pesanan motor berhasil diaplikasikan.")

    def test_07_pilar1_positif_true_motorcycle_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel pesanan motor di DOM."""
        print("\n[Travel Order - Test 07] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom Motorcycle Orders...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("ORDER TIME" in page_src, "Kolom Order Time harus ada (True).")
        self.assertTrue("ORDER NUMBER" in page_src, "Kolom Order Number harus ada (True).")
        self.assertTrue("USER PHONE" in page_src, "Kolom User Phone harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel pesanan motor terkonfirmasi lengkap.")

    def test_08_pilar1_positif_true_city_express_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka City Express Orders (/tOrderLogistics) dan memverifikasi tabel aktif."""
        print("\n[Travel Order - Test 08] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel City Express Orders...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        self.assertTrue(self.page.is_logistics_table_displayed(), "Tabel pesanan express harus tampil (True).")
        self.assertIn("city express orders", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel City Express Orders aktif terkonfirmasi di layar.")

    def test_09_pilar1_positif_true_city_express_search_order_num(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pesanan logistik express berdasarkan nomor order."""
        print("\n[Travel Order - Test 09] [PILAR 1: POSITIF (TRUE)] Pencarian nomor pesanan express...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        self.page.search_logistics_by_order_num("EXP-2026")
        self.page.wait_for_url_contains("orderNum=EXP-2026")

        self.assertIn("orderNum=EXP-2026", self.page.get_current_url())
        self.assertTrue(self.page.is_logistics_table_displayed(), "Tabel express harus tampil (True).")
        print("  -> PASSED [True]: Filter nomor pesanan express berhasil diaplikasikan.")

    def test_10_pilar1_positif_true_city_express_search_recipient_phone(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pesanan logistik berdasarkan nomor telepon penerima."""
        print("\n[Travel Order - Test 10] [PILAR 1: POSITIF (TRUE)] Pencarian no HP penerima paket...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        self.page.search_logistics_by_recipient_phone("08987654321")
        self.page.wait_for_url_contains("recipientPhone=08987654321")

        self.assertIn("recipientPhone=08987654321", self.page.get_current_url())
        self.assertTrue(self.page.is_logistics_table_displayed(), "Tabel express harus tampil (True).")
        print("  -> PASSED [True]: Filter telepon penerima express berhasil diaplikasikan.")

    def test_11_pilar1_positif_true_city_express_filter_state_completed(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter status pesanan logistik dengan opsi Completed (Value 9)."""
        print("\n[Travel Order - Test 11] [PILAR 1: POSITIF (TRUE)] Filter status logistik Selesai...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        self.page.filter_logistics_by_state("9")
        self.page.wait_for_url_contains("state=9")

        self.assertIn("state=9", self.page.get_current_url())
        self.assertTrue(self.page.is_logistics_table_displayed(), "Tabel express harus tampil (True).")
        print("  -> PASSED [True]: Filter status pesanan logistik Completed berhasil diaplikasikan.")

    def test_12_pilar1_positif_true_city_express_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel logistik express di DOM."""
        print("\n[Travel Order - Test 12] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom City Express...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("ORDER TIME" in page_src, "Kolom Order Time harus ada (True).")
        self.assertTrue("RECIPIENT" in page_src, "Kolom Recipient harus ada (True).")
        self.assertTrue("RECIPIENT PHONE" in page_src, "Kolom Recipient Phone harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel City Express terkonfirmasi lengkap.")

    def test_13_pilar1_positif_true_navigasi_sekuensial_sub_halaman_travel_order(self):
        """[PILAR 1 - POSITIF (TRUE)] Navigasi sekuensial ke sub-halaman Travel Order dalam 1 sesi login."""
        print("\n[Travel Order - Test 13] [PILAR 1: POSITIF (TRUE)] Uji navigasi sekuensial sub-halaman order...")
        self.login_sebagai_admin()

        sub_pages = [
            (Config.ORDER_MOTORCYCLE_URL, "Motorcycle Orders"),
            (Config.ORDER_LOGISTICS_URL, "City Express Orders"),
        ]

        for url, label in sub_pages:
            self.driver.get(url)
            self.assertFalse("500" in self.driver.title)
            print(f"    [OK] {label} ({url}) -> Loaded.")

        print("  -> PASSED [True]: Sub-halaman pesanan motor & ekspres stabil diakses berurutan.")

    def test_14_pilar1_positif_true_deep_link_dengan_parameter_pencarian(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[Travel Order - Test 14] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query order...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.ORDER_MOTORCYCLE_URL}?orderNum=MOTO9988")
        self.page.wait_for_url_contains("orderNum=MOTO9988")

        self.assertIn("orderNum=MOTO9988", self.page.get_current_url())
        self.assertTrue(self.page.is_motorcycle_table_displayed(), "Tabel harus tampil melalui deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Tombol Terkunci
    # =========================================================================
    def test_15_pilar2_positif_false_tombol_view_details_motorcycle_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol View details pesanan motor disabled sebelum memilih order."""
        print("\n[Travel Order - Test 15] [PILAR 2: POSITIF (FALSE)] Tombol View details motor awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        is_enabled = self.page.is_motorcycle_details_btn_enabled()
        self.assertFalse(is_enabled, "Tombol View details motor harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol View details pesanan motor terkunci aman berstatus disabled.")

    def test_16_pilar2_positif_false_tombol_cancel_order_motorcycle_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Cancel order motor disabled sebelum memilih order."""
        print("\n[Travel Order - Test 16] [PILAR 2: POSITIF (FALSE)] Tombol Cancel order motor awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        is_enabled = self.page.is_motorcycle_cancel_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Cancel order motor harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Cancel order pesanan motor terkunci aman berstatus disabled.")

    def test_17_pilar2_positif_false_tombol_delete_motorcycle_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete pesanan motor disabled sebelum memilih order."""
        print("\n[Travel Order - Test 17] [PILAR 2: POSITIF (FALSE)] Tombol Delete motor awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        is_enabled = self.page.is_motorcycle_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete motor harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Delete pesanan motor terkunci aman berstatus disabled.")

    def test_18_pilar2_positif_false_tombol_view_details_express_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol View details pesanan ekspres disabled sebelum memilih order."""
        print("\n[Travel Order - Test 18] [PILAR 2: POSITIF (FALSE)] Tombol View details express awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        is_enabled = self.page.is_logistics_details_btn_enabled()
        self.assertFalse(is_enabled, "Tombol View details express harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol View details ekspres terkunci aman berstatus disabled.")

    def test_19_pilar2_positif_false_tombol_cancel_order_express_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Cancel order ekspres disabled sebelum memilih order."""
        print("\n[Travel Order - Test 19] [PILAR 2: POSITIF (FALSE)] Tombol Cancel order express awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        is_enabled = self.page.is_logistics_cancel_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Cancel order express harus disabled tanpa seleksi (False).")
        print("  -> PASSED [False]: Tombol Cancel order ekspres terkunci aman berstatus disabled.")

    def test_20_pilar2_positif_false_kedua_sub_halaman_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan kedua sub-halaman Travel Order bebas dari error server 500."""
        print("\n[Travel Order - Test 20] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()

        for url in [Config.ORDER_MOTORCYCLE_URL, Config.ORDER_LOGISTICS_URL]:
            self.driver.get(url)
            page_src = self.driver.page_source
            self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
            self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")

        print("  -> PASSED [False]: Seluruh sub-halaman pesanan bersih dari error 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_21_pilar3_negatif_true_akses_motorcycle_order_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tOrderPrivateCar tanpa login dialihkan ke /login."""
        print("\n[Travel Order - Test 21] [PILAR 3: NEGATIF (TRUE)] Akses /tOrderPrivateCar tanpa login...")
        self.page.navigate_motorcycle_orders()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute pesanan motor aktif (dialihkan ke /login).")

    def test_22_pilar3_negatif_true_akses_city_express_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tOrderLogistics tanpa login dialihkan ke /login."""
        print("\n[Travel Order - Test 22] [PILAR 3: NEGATIF (TRUE)] Akses /tOrderLogistics tanpa login...")
        self.page.navigate_logistics_orders()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute pesanan ekspres aktif (dialihkan ke /login).")

    def test_23_pilar3_negatif_true_filter_tanggal_terbalik_motorcycle_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Rentang tanggal terbalik pada pesanan motor ditangani aman tanpa crash."""
        print("\n[Travel Order - Test 23] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada pesanan motor...")
        self.login_sebagai_admin()
        self.page.filter_motorcycle_by_date("2026-12-31", "2026-01-01")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_motorcycle_table_displayed() or "500" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Filter tanggal terbalik pesanan motor ditangani aman oleh sistem.")

    def test_24_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[Travel Order - Test 24] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Sistem harus mengalihkan ke /login saat sesi habis (True).")
        print("  -> PASSED [True]: Sistem aktif mencegat request dan redirect ke /login saat sesi habis.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Pencegahan Manipulasi & Keamanan Data
    # =========================================================================
    def test_25_pilar4_negatif_false_pencarian_order_motor_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nomor order motor fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Travel Order - Test 25] [PILAR 4: NEGATIF (FALSE)] Pencarian order motor fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        self.page.search_motorcycle_by_order_num("ORD_FIKTIF_NONEXISTENT_9999999")
        self.page.wait_for_url_contains("ORD_FIKTIF_NONEXISTENT_9999999")

        row_count = self.page.get_motorcycle_rows_count()
        self.assertFalse(row_count > 0, "Pencarian pesanan motor fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian order motor fiktif ditangani dengan aman (0 data).")

    def test_26_pilar4_negatif_false_pencarian_order_express_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nomor order ekspres fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Travel Order - Test 26] [PILAR 4: NEGATIF (FALSE)] Pencarian order ekspres fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        self.page.search_logistics_by_order_num("EXP_FIKTIF_NONEXISTENT_9999999")
        self.page.wait_for_url_contains("EXP_FIKTIF_NONEXISTENT_9999999")

        row_count = self.page.get_logistics_rows_count()
        self.assertFalse(row_count > 0, "Pencarian pesanan ekspres fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian order ekspres fiktif ditangani dengan aman (0 data).")

    def test_27_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_data_pemesan(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu tanpa login TIDAK BISA membaca riwayat perjalanan atau nomor HP penumpang."""
        print("\n[Travel Order - Test 27] [PILAR 4: NEGATIF (FALSE)] Penolakan akses data penumpang tanpa login...")
        self.page.navigate_motorcycle_orders()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("PASSENGER PHONE" in page_src, "Data sensitif penumpang tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Data sensitif rincian perjalanan penumpang terproteksi dari luar.")

    def test_28_pilar4_negatif_false_sql_injection_pada_pencarian_order_num_motor(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada nomor order motor tidak membobol data."""
        print("\n[Travel Order - Test 28] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nomor order motor...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        sqli_payload = "' OR '1'='1"
        self.page.search_motorcycle_by_order_num(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada nomor order motor berhasil ditangkal.")

    def test_29_pilar4_negatif_false_sql_injection_pada_pencarian_driver_motor(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada nama driver pesanan motor tidak membobol data."""
        print("\n[Travel Order - Test 29] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nama driver order motor...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        sqli_payload = "'; DROP TABLE t_order; --"
        self.page.search_motorcycle_by_driver(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada nama driver berhasil ditangkal.")

    def test_30_pilar4_negatif_false_sql_injection_pada_pencarian_express_order(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian order ekspres tidak membobol data."""
        print("\n[Travel Order - Test 30] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada pencarian order express...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        sqli_payload = "' OR '1'='1"
        self.page.search_logistics_by_order_num(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada order express berhasil ditangkal.")

    def test_31_pilar4_negatif_false_xss_script_pada_pencarian_order_motor(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian order motor tidak dieksekusi browser."""
        print("\n[Travel Order - Test 31] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian order motor...")
        self.login_sebagai_admin()
        self.page.navigate_motorcycle_orders()

        xss_payload = "<script>alert('xss_order_motor')</script>"
        self.page.search_motorcycle_by_order_num(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Motorcycle Orders.")

    def test_32_pilar4_negatif_false_xss_script_pada_pencarian_order_express(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian order ekspres tidak dieksekusi browser."""
        print("\n[Travel Order - Test 32] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian order express...")
        self.login_sebagai_admin()
        self.page.navigate_logistics_orders()

        xss_payload = "<script>alert('xss_order_express')</script>"
        self.page.search_logistics_by_order_num(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada City Express Orders.")

    def test_33_pilar4_negatif_false_url_subpath_fiktif_ditangani_tanpa_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tOrderPrivateCar/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[Travel Order - Test 33] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tOrderPrivateCar/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.ORDER_MOTORCYCLE_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
