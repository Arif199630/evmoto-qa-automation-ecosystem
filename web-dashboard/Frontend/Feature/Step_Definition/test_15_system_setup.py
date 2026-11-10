"""
=============================================================================
TEST SUITE 15: SYSTEM SETUP (MENU #15)
Websites : 1. System Setup (/tSysReformist)
           2. Unblock Cancellation Debt (/userDebtUnblock)
Desain   : Page Object Model (POM)
Konsep   : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan  : Parameter Poin Loyalti, Biaya & Waktu Pembatalan (Normal & Janji Temu),
           Nomor Kontak SOS & Hotline, Unblock Hutang Biaya Pembatalan,
           Resiliensi Sesi, Sanitasi SQLi & XSS, dan Penolakan Akses Publik
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan form konfigurasi sistem, parameter kontak darurat/hotline,
                     biaya cancel, tabel hutang, & pencarian user ID aktif (True).
2. Positif (False) : Memastikan kedua sub-halaman bebas dari respon error server 500,
                     whitelabel exception, biaya bernilai negatif, & distorsi layout (False).
3. Negatif (True)  : Memastikan akses rute konfigurasi tanpa login dicegat & sesi kedaluwarsa
                     mengarahkan kembali ke /login (True).
4. Negatif (False) : Memastikan data fiktif 0 baris, data nomor darurat & rincian hutang
                     terlindungi dari tamu publik, serta aman dari SQLi & XSS (False).
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
from pages.page_15_system_setup import SystemSetupPage


class TestSystemSetup(unittest.TestCase):
    """Test Suite System Setup & Sub-Halamannya dengan Konsep 4 Pilar Testing (30 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = SystemSetupPage(self.driver)

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
    def test_01_pilar1_positif_true_reformist_form_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka System Setup (/tSysReformist) dan memverifikasi form tampil."""
        print("\n[System Setup - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi form konfigurasi sistem...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        self.assertTrue(self.page.is_reformist_form_displayed(), "Form konfigurasi sistem harus tampil (True).")
        self.assertIn("system setup", self.driver.title.lower())
        print("  -> PASSED [True]: Form konfigurasi System Setup aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_reformist_service_phone_terisi(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi hotline layanan pelanggan (servicePhone) hadir di formulir."""
        print("\n[System Setup - Test 02] [PILAR 1: POSITIF (TRUE)] Verifikasi hotline layanan pelanggan...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        self.assertTrue(self.page.is_service_phone_displayed(), "Field hotline layanan pelanggan harus tampil (True).")
        print("  -> PASSED [True]: Field hotline layanan pelanggan aktif terverifikasi di formulir.")

    def test_03_pilar1_positif_true_reformist_alarm_phone_terisi(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi nomor kontak darurat/SOS (alarmPhone) hadir di formulir."""
        print("\n[System Setup - Test 03] [PILAR 1: POSITIF (TRUE)] Verifikasi nomor kontak darurat SOS...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        self.assertTrue(self.page.is_alarm_phone_displayed(), "Field kontak darurat SOS harus tampil (True).")
        print("  -> PASSED [True]: Field nomor kontak darurat SOS aktif terverifikasi di formulir.")

    def test_04_pilar1_positif_true_reformist_normal_cancel_fee_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi parameter biaya pembatalan pesanan reguler terisi sah."""
        print("\n[System Setup - Test 04] [PILAR 1: POSITIF (TRUE)] Verifikasi biaya pembatalan pesanan reguler...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        fee = self.page.get_normal_cancel_fee()
        self.assertTrue(fee is not None and len(fee) > 0, "Biaya pembatalan reguler harus terisi (True).")
        print(f"  -> PASSED [True]: Biaya pembatalan pesanan reguler valid: {fee}.")

    def test_05_pilar1_positif_true_reformist_appt_cancel_fee_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi parameter biaya pembatalan janji temu terisi sah."""
        print("\n[System Setup - Test 05] [PILAR 1: POSITIF (TRUE)] Verifikasi biaya pembatalan janji temu...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        fee = self.page.get_appt_cancel_fee()
        self.assertTrue(fee is not None and len(fee) > 0, "Biaya pembatalan janji temu harus terisi (True).")
        print(f"  -> PASSED [True]: Biaya pembatalan janji temu valid: {fee}.")

    def test_06_pilar1_positif_true_reformist_tombol_save_aktif(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi tombol Save konfigurasi parameter tampil di layar."""
        print("\n[System Setup - Test 06] [PILAR 1: POSITIF (TRUE)] Verifikasi tombol simpan konfigurasi...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        self.assertTrue(self.page.is_save_button_displayed(), "Tombol Save konfigurasi harus tampil (True).")
        print("  -> PASSED [True]: Tombol Save formulir konfigurasi sistem aktif terverifikasi.")

    def test_07_pilar1_positif_true_debt_unblock_tabel_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Unblock Cancellation Debt (/userDebtUnblock) dan tabel tampil."""
        print("\n[System Setup - Test 07] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel hutang pembatalan...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        self.assertTrue(self.page.is_debt_table_displayed(), "Tabel hutang pembatalan harus tampil (True).")
        self.assertIn("debt", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Unblock Cancellation Debt aktif terkonfirmasi di layar.")

    def test_08_pilar1_positif_true_debt_unblock_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas header kolom tabel hutang pembatalan di DOM."""
        print("\n[System Setup - Test 08] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom tabel hutang...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("USER ID" in page_src, "Kolom User ID harus ada (True).")
        self.assertTrue("ORDER ID" in page_src, "Kolom Order ID harus ada (True).")
        self.assertTrue("AMOUNT" in page_src, "Kolom Amount harus ada (True).")
        self.assertTrue("REASON" in page_src, "Kolom Reason harus ada (True).")
        self.assertTrue("ROLLED_INTO_ORDER_ID" in page_src, "Kolom Rolled Order ID harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel hutang pembatalan terkonfirmasi lengkap.")

    def test_09_pilar1_positif_true_debt_unblock_pencarian_user_id(self):
        """[PILAR 1 - POSITIF (TRUE)] Melakukan pencarian hutang pembatalan berdasarkan User ID pemesan."""
        print("\n[System Setup - Test 09] [PILAR 1: POSITIF (TRUE)] Pencarian hutang berdasarkan User ID...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        self.page.search_debt_by_user_id("1001")
        self.page.wait_for_url_contains("userId=1001")

        self.assertIn("userId=1001", self.page.get_current_url())
        self.assertTrue(self.page.is_debt_table_displayed(), "Tabel hutang harus tampil setelah filter (True).")
        print("  -> PASSED [True]: Filter pencarian User ID hutang pembatalan berhasil diaplikasikan.")

    def test_10_pilar1_positif_true_debt_unblock_form_mark_paid_hadir(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi tombol 'Mark paid' hadir pada sub-halaman unblock hutang."""
        print("\n[System Setup - Test 10] [PILAR 1: POSITIF (TRUE)] Verifikasi tombol Mark paid...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        self.assertTrue(self.page.is_mark_paid_btn_displayed(), "Tombol Mark paid harus hadir di layar (True).")
        print("  -> PASSED [True]: Tombol Mark paid pelunasan hutang pembatalan aktif terkonfirmasi.")

    def test_11_pilar1_positif_true_navigasi_sekuensial_antar_sub_halaman(self):
        """[PILAR 1 - POSITIF (TRUE)] Navigasi sekuensial antar sub-halaman System Setup stabil dalam 1 sesi."""
        print("\n[System Setup - Test 11] [PILAR 1: POSITIF (TRUE)] Uji alur navigasi antar sub-halaman...")
        self.login_sebagai_admin()

        self.page.navigate_reformist()
        self.assertTrue(self.page.is_reformist_form_displayed(), "System Setup harus aktif (True).")

        self.page.navigate_debt_unblock()
        self.assertTrue(self.page.is_debt_table_displayed(), "Unblock Debt harus aktif (True).")
        print("  -> PASSED [True]: Navigasi antar sub-halaman System Setup berjalan mulus dalam 1 sesi.")

    def test_12_pilar1_positif_true_deep_link_dengan_parameter_url(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL ke /userDebtUnblock memuat filter akurat."""
        print("\n[System Setup - Test 12] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan query URL...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.USER_DEBT_UNBLOCK_URL}?userId=8888")
        self.page.wait_for_url_contains("userId=8888")

        self.assertIn("userId=8888", self.page.get_current_url())
        self.assertTrue(self.page.is_debt_table_displayed(), "Tabel hutang harus tampil via deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter User ID bekerja akurat.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Error 500
    # =========================================================================
    def test_13_pilar2_positif_false_kedua_sub_halaman_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan kedua sub-halaman System Setup bebas dari error server 500."""
        print("\n[System Setup - Test 13] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()

        for url in [Config.SYS_REFORMIST_URL, Config.USER_DEBT_UNBLOCK_URL]:
            self.driver.get(url)
            page_src = self.driver.page_source
            self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
            self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")

        print("  -> PASSED [False]: Seluruh sub-halaman System Setup bersih dari error 500.")

    def test_14_pilar2_positif_false_halaman_bebas_whitelabel_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan antarmuka bebas dari exception whitelabel Spring Boot."""
        print("\n[System Setup - Test 14] [PILAR 2: POSITIF (FALSE)] Memastikan bebas whitelabel error...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        page_src = self.page.get_page_source()
        self.assertFalse("There was an unexpected error" in page_src, "Tidak boleh ada exception whitelabel (False).")
        print("  -> PASSED [False]: Antarmuka System Setup bersih dari pesan exception sistem.")

    def test_15_pilar2_positif_false_tidak_ada_duplikasi_header_tabel(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan DOM tabel hutang bebas dari duplikasi elemen thead."""
        print("\n[System Setup - Test 15] [PILAR 2: POSITIF (FALSE)] Uji ketiadaan duplikasi header tabel...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        theads = self.driver.find_elements(By.TAG_NAME, "thead")
        self.assertFalse(len(theads) > 1, "Tabel hutang tidak boleh memuat thead ganda (False).")
        print("  -> PASSED [False]: Header tabel hutang pembatalan bersih tanpa duplikasi.")

    def test_16_pilar2_positif_false_biaya_pembatalan_tidak_bernilai_negatif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memverifikasi biaya pembatalan pesanan reguler tidak bernilai angka negatif."""
        print("\n[System Setup - Test 16] [PILAR 2: POSITIF (FALSE)] Memastikan biaya cancel tidak negatif...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        fee_val = float(self.page.get_normal_cancel_fee() or "0")
        self.assertFalse(fee_val < 0, "Biaya cancel reguler tidak boleh bernilai negatif (False).")
        print("  -> PASSED [False]: Biaya pembatalan reguler terkonfigurasi secara sah non-negatif.")

    def test_17_pilar2_positif_false_waktu_tunggu_pembatalan_tidak_negatif(self):
        """[PILAR 2 - POSITIF (FALSE)] Memverifikasi waktu tunggu penalti pembatalan (waitMinutes) tidak negatif."""
        print("\n[System Setup - Test 17] [PILAR 2: POSITIF (FALSE)] Memastikan waktu tunggu tidak negatif...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        mins_val = int(self.page.get_wait_minutes() or "0")
        self.assertFalse(mins_val < 0, "Waktu tunggu pembatalan tidak boleh bernilai negatif (False).")
        print("  -> PASSED [False]: Waktu tunggu pembatalan bernilai sah non-negatif.")

    def test_18_pilar2_positif_false_hotline_tidak_berisi_karakter_rusak(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan nomor hotline tidak memuat nilai undefined atau NaN."""
        print("\n[System Setup - Test 18] [PILAR 2: POSITIF (FALSE)] Memastikan nomor hotline bersih...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        phone = self.page.get_service_phone_value().lower()
        self.assertFalse("undefined" in phone or "nan" in phone, "Nomor hotline tidak boleh rusak (False).")
        print("  -> PASSED [False]: Hotline layanan pelanggan bersih tanpa karakter error/undefined.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_19_pilar3_negatif_true_akses_reformist_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tSysReformist tanpa login dialihkan ke /login."""
        print("\n[System Setup - Test 19] [PILAR 3: NEGATIF (TRUE)] Akses /tSysReformist tanpa login...")
        self.page.navigate_reformist()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute System Setup aktif (dialihkan ke /login).")

    def test_20_pilar3_negatif_true_akses_debt_unblock_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /userDebtUnblock tanpa login dialihkan ke /login."""
        print("\n[System Setup - Test 20] [PILAR 3: NEGATIF (TRUE)] Akses /userDebtUnblock tanpa login...")
        self.page.navigate_debt_unblock()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute Unblock Debt aktif (dialihkan ke /login).")

    def test_21_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[System Setup - Test 21] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
        self.login_sebagai_admin()
        self.page.navigate_reformist()

        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Sistem harus mengalihkan ke /login saat sesi habis (True).")
        print("  -> PASSED [True]: Sistem aktif mencegat request dan redirect ke /login saat sesi habis.")

    def test_22_pilar3_negatif_true_parameter_query_anomali_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Parameter query anomali pada /userDebtUnblock ditangani aman dengan tabel tetap tampil."""
        print("\n[System Setup - Test 22] [PILAR 3: NEGATIF (TRUE)] Uji parameter query anomali...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.USER_DEBT_UNBLOCK_URL}?userId=non_numeric_user_id_test")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_debt_table_displayed(timeout=10), "Tabel hutang harus tetap tampil saat input anomali (True).")
        self.assertTrue("500 Internal Server Error" not in page_src and "Whitelabel Error Page" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Parameter query anomali ditangani secara aman tanpa server crash.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Pencegahan Manipulasi & Keamanan Data
    # =========================================================================
    def test_23_pilar4_negatif_false_pencarian_user_id_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian User ID fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[System Setup - Test 23] [PILAR 4: NEGATIF (FALSE)] Pencarian User ID fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        self.page.search_debt_by_user_id("999999999999")
        self.page.wait_for_url_contains("userId=999999999999")

        row_count = self.page.get_debt_rows_count()
        self.assertFalse(row_count > 0, "Pencarian User ID fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian User ID fiktif ditangani dengan aman (0 data).")

    def test_24_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_nomor_sos(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA membaca form nomor kontak darurat SOS."""
        print("\n[System Setup - Test 24] [PILAR 4: NEGATIF (FALSE)] Penolakan akses nomor SOS tanpa login...")
        self.page.navigate_reformist()

        page_src = self.page.get_page_source()
        self.assertFalse("alarmPhone" in page_src, "Nomor kontak SOS tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Form nomor kontak darurat SOS terlindungi dari akses publik.")

    def test_25_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_data_hutang(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA membaca tabel rincian hutang pembatalan."""
        print("\n[System Setup - Test 25] [PILAR 4: NEGATIF (FALSE)] Penolakan akses tabel hutang tanpa login...")
        self.page.navigate_debt_unblock()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("ROLLED_INTO_ORDER_ID" in page_src, "Rincian hutang tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Data rincian hutang pembatalan terlindungi dari akses publik.")

    def test_26_pilar4_negatif_false_sql_injection_pada_pencarian_user_id(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada form pencarian User ID tidak merusak sistem."""
        print("\n[System Setup - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada pencarian User ID...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        sqli_payload = "' OR '1'='1"
        self.page.search_debt_by_user_id(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada form User ID berhasil ditangkal.")

    def test_27_pilar4_negatif_false_sql_injection_drop_table_pada_user_id(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection bertipe destructive drop table tidak merusak database."""
        print("\n[System Setup - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji SQLi destructive drop table...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        sqli_payload = "'; DROP TABLE t_sys_reformist; --"
        self.page.search_debt_by_user_id(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection destruktif berhasil ditangkal aman.")

    def test_28_pilar4_negatif_false_xss_script_pada_pencarian_user_id(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada form User ID tidak dieksekusi browser."""
        print("\n[System Setup - Test 28] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada User ID...")
        self.login_sebagai_admin()
        self.page.navigate_debt_unblock()

        xss_payload = "<script>alert('xss_system_setup')</script>"
        self.page.search_debt_by_user_id(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada formulir User ID.")

    def test_29_pilar4_negatif_false_url_subpath_fiktif_reformist_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tSysReformist/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[System Setup - Test 29] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tSysReformist/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.SYS_REFORMIST_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif System Setup ditangani secara aman tanpa server crash.")

    def test_30_pilar4_negatif_false_url_subpath_fiktif_debt_unblock_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /userDebtUnblock/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[System Setup - Test 30] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /userDebtUnblock/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.USER_DEBT_UNBLOCK_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif Unblock Debt ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
