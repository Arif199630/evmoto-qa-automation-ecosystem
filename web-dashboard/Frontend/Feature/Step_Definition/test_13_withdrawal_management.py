"""
=============================================================================
TEST SUITE 13: WITHDRAWAL MANAGEMENT (MENU #13)
Website : <BASE_URL>/tPubWithdrawal, /withdrawalConfig
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Withdrawal List (/tPubWithdrawal), Withdrawal Configuration (/withdrawalConfig),
          Filter Pencarian & Form, Status Tombol Process, Proteksi Keuangan & Resiliensi Siber
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel penarikan dana, form konfigurasi batas minimum, filter, dan navigasi aktif (True).
2. Positif (False) : Memastikan tombol Process terkunci (disabled) sebelum ada seleksi & bebas error 500 (False).
3. Negatif (True)  : Memastikan akses rute keuangan tanpa login dicegat & tanggal terbalik ditangani aman (True).
4. Negatif (False) : Memastikan data fiktif 0 baris & data perbankan mitra terlindungi dari serangan siber (False).
=============================================================================
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from selenium.webdriver.common.by import By
from config import Config
from pages.page_00_login import LoginPage
from pages.page_13_withdrawal_management import WithdrawalPage


class TestWithdrawalManagement(unittest.TestCase):
    """Test Suite Withdrawal Management dengan Konsep 4 Pilar Testing (30 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = WithdrawalPage(self.driver)

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
    def test_01_pilar1_positif_true_withdrawal_list_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Withdrawal List (/tPubWithdrawal) dan memverifikasi tabel aktif."""
        print("\n[Withdrawal Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Withdrawal List...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        self.assertTrue(self.page.is_table_displayed(), "Tabel penarikan dana harus tampil (True).")
        self.assertIn("withdrawal list", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Withdrawal List aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_withdrawal_search_nama_pemohon(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari permohonan penarikan dana berdasarkan nama pemohon."""
        print("\n[Withdrawal Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian nama pemohon penarikan...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        self.page.search_by_name("Budi")
        self.page.wait_for_url_contains("name=Budi")

        self.assertIn("name=Budi", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah pencarian (True).")
        print("  -> PASSED [True]: Filter pencarian nama pemohon berhasil disubmit.")

    def test_03_pilar1_positif_true_withdrawal_filter_user_type_driver(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter penarikan dana untuk tipe Driver (Value 2)."""
        print("\n[Withdrawal Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Filter penarikan tipe Driver...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        self.page.filter_by_user_type("2")
        self.page.wait_for_url_contains("userType=2")

        self.assertIn("userType=2", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah filter tipe (True).")
        print("  -> PASSED [True]: Filter penarikan tipe Driver berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_withdrawal_filter_user_type_user(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter penarikan dana untuk tipe Pengguna/User (Value 1)."""
        print("\n[Withdrawal Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Filter penarikan tipe User...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        self.page.filter_by_user_type("1")
        self.page.wait_for_url_contains("userType=1")

        self.assertIn("userType=1", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tetap tampil setelah filter user (True).")
        print("  -> PASSED [True]: Filter penarikan tipe User berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_withdrawal_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang tanggal pada Withdrawal List terpasang di URL."""
        print("\n[Withdrawal Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Filter rentang tanggal penarikan...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-01-01", "2026-12-31")

        self.assertIn("beginDate=2026-01-01", self.page.get_current_url())
        self.assertIn("endDate=2026-12-31", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tampil dengan filter tanggal (True).")
        print("  -> PASSED [True]: Filter rentang tanggal penarikan dana berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_withdrawal_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel penarikan dana di DOM."""
        print("\n[Withdrawal Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom penarikan dana...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("APPLICATION TIME" in page_src, "Kolom Application Time harus ada (True).")
        self.assertTrue("BANK ACCOUNT" in page_src, "Kolom Bank Account harus ada (True).")
        self.assertTrue("AMOUNT" in page_src, "Kolom Amount harus ada (True).")
        self.assertTrue("ADMIN FEE" in page_src, "Kolom Admin Fee harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel penarikan dana terkonfirmasi lengkap.")

    def test_07_pilar1_positif_true_withdrawal_config_halaman_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Withdrawal Configuration (/withdrawalConfig) dan memverifikasi form aktif."""
        print("\n[Withdrawal Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Verifikasi halaman Withdrawal Configuration...")
        self.login_sebagai_admin()
        self.page.navigate_config()

        self.assertTrue(self.page.is_config_input_displayed(), "Form konfigurasi penarikan harus tampil (True).")
        self.assertIn("withdrawal configuration", self.driver.title.lower())
        print("  -> PASSED [True]: Halaman Withdrawal Configuration aktif terkonfirmasi di layar.")

    def test_08_pilar1_positif_true_withdrawal_config_verifikasi_field_min_amount(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi field batas minimum penarikan dana terisi nilai nominal valid."""
        print("\n[Withdrawal Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Verifikasi batas minimum penarikan...")
        self.login_sebagai_admin()
        self.page.navigate_config()

        amount_val = self.page.get_min_withdrawal_amount()
        self.assertTrue(len(amount_val) > 0 and int(amount_val) > 0, "Batas minimum penarikan harus bernilai valid (True).")
        print(f"  -> PASSED [True]: Batas minimum penarikan terkonfigurasi pada nominal {amount_val}.")

    def test_09_pilar1_positif_true_withdrawal_config_tombol_save_aktif(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi tombol Save pada konfigurasi penarikan dana aktif di layar."""
        print("\n[Withdrawal Mgmt - Test 09] [PILAR 1: POSITIF (TRUE)] Verifikasi tombol Save konfigurasi...")
        self.login_sebagai_admin()
        self.page.navigate_config()

        self.assertTrue(self.page.is_save_btn_enabled(), "Tombol Save konfigurasi harus berstatus aktif (True).")
        print("  -> PASSED [True]: Tombol Save konfigurasi batas minimum penarikan aktif.")

    def test_10_pilar1_positif_true_navigasi_sekuensial_sub_halaman_withdrawal(self):
        """[PILAR 1 - POSITIF (TRUE)] Navigasi sekuensial antar sub-halaman Withdrawal Management dalam 1 sesi login."""
        print("\n[Withdrawal Mgmt - Test 10] [PILAR 1: POSITIF (TRUE)] Uji navigasi sekuensial sub-halaman penarikan...")
        self.login_sebagai_admin()

        sub_pages = [
            (Config.PUB_WITHDRAWAL_URL, "Withdrawal List"),
            (Config.WITHDRAWAL_CONFIG_URL, "Withdrawal Configuration"),
        ]

        for url, label in sub_pages:
            self.driver.get(url)
            self.assertFalse("500" in self.driver.title)
            print(f"    [OK] {label} ({url}) -> Loaded.")

        print("  -> PASSED [True]: Seluruh sub-halaman Withdrawal Management stabil diakses berurutan.")

    def test_11_pilar1_positif_true_deep_link_dengan_parameter_pencarian(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[Withdrawal Mgmt - Test 11] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.PUB_WITHDRAWAL_URL}?name=DriverArif")
        self.page.wait_for_url_contains("name=DriverArif")

        self.assertIn("name=DriverArif", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel harus tampil melalui deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    def test_12_pilar1_positif_true_refresh_browser_pertahankan_sesi(self):
        """[PILAR 1 - POSITIF (TRUE)] Refresh/F5 browser mempertahankan sesi dan tabel daftar penarikan dana."""
        print("\n[Withdrawal Mgmt - Test 12] [PILAR 1: POSITIF (TRUE)] Refresh browser pada daftar penarikan...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        self.driver.refresh()
        self.assertTrue(self.page.is_table_displayed(), "Tabel tetap aktif setelah refresh halaman (True).")
        print("  -> PASSED [True]: Sesi dan tabel daftar penarikan bertahan stabil setelah reload.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Tombol Terkunci
    # =========================================================================
    def test_13_pilar2_positif_false_tombol_process_terkunci_awal(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Process penarikan dana terkunci (disabled) sebelum memilih data."""
        print("\n[Withdrawal Mgmt - Test 13] [PILAR 2: POSITIF (FALSE)] Tombol Process awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        is_enabled = self.page.is_process_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Process harus disabled jika belum ada baris terpilih (False).")
        print("  -> PASSED [False]: Tombol Process penarikan dana terkunci aman berstatus disabled.")

    def test_14_pilar2_positif_false_field_min_amount_tidak_kosong(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan field batas minimum penarikan dana tidak bernilai kosong/null."""
        print("\n[Withdrawal Mgmt - Test 14] [PILAR 2: POSITIF (FALSE)] Memastikan batas minimum tidak kosong...")
        self.login_sebagai_admin()
        self.page.navigate_config()

        val = self.page.get_min_withdrawal_amount()
        self.assertFalse(val is None or val == "", "Nilai batas minimum tidak boleh kosong (False).")
        print("  -> PASSED [False]: Konfigurasi minimum penarikan terisi data valid tanpa nilai kosong.")

    def test_15_pilar2_positif_false_kedua_sub_halaman_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan kedua sub-halaman penarikan dana bebas dari error server 500."""
        print("\n[Withdrawal Mgmt - Test 15] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()

        for url in [Config.PUB_WITHDRAWAL_URL, Config.WITHDRAWAL_CONFIG_URL]:
            self.driver.get(url)
            page_src = self.driver.page_source
            self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
            self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")

        print("  -> PASSED [False]: Seluruh sub-halaman penarikan dana bersih dari error 500.")

    def test_16_pilar2_positif_false_tidak_ada_duplikasi_header_tabel(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan DOM tabel penarikan dana bebas dari duplikasi elemen header."""
        print("\n[Withdrawal Mgmt - Test 16] [PILAR 2: POSITIF (FALSE)] Uji ketiadaan duplikasi header...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        theads = self.driver.find_elements(By.TAG_NAME, "thead")
        self.assertFalse(len(theads) > 1, "Tabel penarikan dana tidak boleh memuat header ganda (False).")
        print("  -> PASSED [False]: Struktur header tabel penarikan bersih dan bebas duplikasi.")

    def test_17_pilar2_positif_false_nominal_penarikan_tidak_negatif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan nominal minimum penarikan dana tidak bernilai negatif."""
        print("\n[Withdrawal Mgmt - Test 17] [PILAR 2: POSITIF (FALSE)] Memastikan nominal tidak bernilai negatif...")
        self.login_sebagai_admin()
        self.page.navigate_config()

        val = int(self.page.get_min_withdrawal_amount() or "0")
        self.assertFalse(val < 0, "Nominal penarikan dana tidak boleh bernilai negatif (False).")
        print("  -> PASSED [False]: Batas minimum penarikan bernilai positif secara sah.")

    def test_18_pilar2_positif_false_halaman_bebas_whitelabel_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan antarmuka bebas dari exception whitelabel Spring Boot."""
        print("\n[Withdrawal Mgmt - Test 18] [PILAR 2: POSITIF (FALSE)] Memastikan bebas whitelabel error...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        page_src = self.page.get_page_source()
        self.assertFalse("There was an unexpected error" in page_src, "Tidak boleh ada error whitelabel (False).")
        print("  -> PASSED [False]: Halaman Withdrawal Management bersih dari pesan exception sistem.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_19_pilar3_negatif_true_akses_withdrawal_list_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tPubWithdrawal tanpa login dialihkan ke /login."""
        print("\n[Withdrawal Mgmt - Test 19] [PILAR 3: NEGATIF (TRUE)] Akses /tPubWithdrawal tanpa login...")
        self.page.navigate_list()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute daftar penarikan aktif (dialihkan ke /login).")

    def test_20_pilar3_negatif_true_akses_withdrawal_config_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /withdrawalConfig tanpa login dialihkan ke /login."""
        print("\n[Withdrawal Mgmt - Test 20] [PILAR 3: NEGATIF (TRUE)] Akses /withdrawalConfig tanpa login...")
        self.page.navigate_config()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute konfigurasi penarikan aktif (dialihkan ke /login).")

    def test_21_pilar3_negatif_true_rentang_tanggal_terbalik_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Rentang tanggal terbalik (begin > end) ditangani aman tanpa server crash."""
        print("\n[Withdrawal Mgmt - Test 21] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada penarikan dana...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-12-31", "2026-01-01")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_table_displayed() or "500" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Filter tanggal terbalik penarikan dana ditangani aman oleh sistem.")

    def test_22_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[Withdrawal Mgmt - Test 22] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Sistem harus mengalihkan ke /login saat sesi habis (True).")
        print("  -> PASSED [True]: Sistem aktif mencegat request dan redirect ke /login saat sesi habis.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Pencegahan Manipulasi & Keamanan Data
    # =========================================================================
    def test_23_pilar4_negatif_false_pencarian_nama_pemohon_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama pemohon fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Withdrawal Mgmt - Test 23] [PILAR 4: NEGATIF (FALSE)] Pencarian pemohon fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        self.page.search_by_name("PEMOHON_FIKTIF_NONEXISTENT_9999999")
        self.page.wait_for_url_contains("PEMOHON_FIKTIF_NONEXISTENT_9999999")

        row_count = self.page.get_rows_count()
        self.assertFalse(row_count > 0, "Pencarian pemohon fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian pemohon fiktif ditangani dengan aman (0 data).")

    def test_24_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_rekening_bank(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA membaca nomor rekening bank mitra."""
        print("\n[Withdrawal Mgmt - Test 24] [PILAR 4: NEGATIF (FALSE)] Penolakan akses nomor rekening tanpa login...")
        self.page.navigate_list()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("BANK ACCOUNT NAME" in page_src, "Nomor rekening mitra tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Data sensitif nomor rekening perbankan mitra terlindungi dari akses publik.")

    def test_25_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_nominal_penarikan(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA membaca rincian nominal penarikan dana."""
        print("\n[Withdrawal Mgmt - Test 25] [PILAR 4: NEGATIF (FALSE)] Penolakan akses nominal penarikan tanpa login...")
        self.page.navigate_list()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("ADMIN FEE" in page_src, "Rincian biaya admin dan nominal tidak boleh bocor (False).")
        print("  -> PASSED [False]: Data transaksi keuangan penarikan dana terlindungi dari pihak luar.")

    def test_26_pilar4_negatif_false_sql_injection_pada_pencarian_nama_pemohon(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian nama pemohon tidak membobol data."""
        print("\n[Withdrawal Mgmt - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nama pemohon...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        sqli_payload = "' OR '1'='1"
        self.page.search_by_name(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada nama pemohon berhasil ditangkal.")

    def test_27_pilar4_negatif_false_sql_injection_pada_parameter_user_type(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection via query parameter userType tidak merusak database."""
        print("\n[Withdrawal Mgmt - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada parameter userType...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.PUB_WITHDRAWAL_URL}?userType=2' OR '1'='1")

        page_src = self.page.get_page_source()
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Injeksi SQL pada filter entitas penarikan berhasil ditangkal.")

    def test_28_pilar4_negatif_false_xss_script_pada_pencarian_nama_pemohon(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada pencarian pemohon tidak dieksekusi browser."""
        print("\n[Withdrawal Mgmt - Test 28] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian pemohon...")
        self.login_sebagai_admin()
        self.page.navigate_list()

        xss_payload = "<script>alert('xss_withdrawal')</script>"
        self.page.search_by_name(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Withdrawal List.")

    def test_29_pilar4_negatif_false_url_subpath_fiktif_withdrawal_list_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tPubWithdrawal/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[Withdrawal Mgmt - Test 29] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tPubWithdrawal/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.PUB_WITHDRAWAL_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")

    def test_30_pilar4_negatif_false_url_subpath_fiktif_withdrawal_config_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /withdrawalConfig/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[Withdrawal Mgmt - Test 30] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /withdrawalConfig/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.WITHDRAWAL_CONFIG_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif konfigurasi penarikan ditangani secara aman tanpa crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
