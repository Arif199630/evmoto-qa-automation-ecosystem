"""
=============================================================================
TEST SUITE 16: COMPLAINT MANAGEMENT (MENU #16)
Website : <BASE_URL>/tComplaint
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Complaint List Management, Filter Nama & No Telepon Pelapor/Driver,
          Filter Status Pengaduan (Has Been Processed / Fail to be Disposed),
          Rentang Waktu, Tombol Immediately Process & Delete Terkunci Aman,
          Proteksi Privasi No HP, Sanitasi SQLi & XSS, dan Resiliensi Sesi
=============================================================================
Penjelasan 4 Pilar Pengujian:
1. Positif (True)  : Memastikan tabel pengaduan, filter nama pengadu, telepon pengadu,
                     telepon driver, status komplain, rentang tanggal, & deep link aktif (True).
2. Positif (False) : Memastikan tombol Immediately process & Delete terkunci awal (disabled),
                     bebas dari error 500, whitelabel exception, & duplikasi header (False).
3. Negatif (True)  : Memastikan akses /tComplaint tanpa login dicegat & sesi kedaluwarsa
                     mengarahkan kembali ke /login (True).
4. Negatif (False) : Memastikan data fiktif 0 baris, nomor telepon terlindungi dari publik,
                     serta kebal terhadap serangan siber SQLi & XSS (False).
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
from pages.page_16_complaint_management import ComplaintPage


class TestComplaintManagement(unittest.TestCase):
    """Test Suite Complaint Management dengan Konsep 4 Pilar Testing (28 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = ComplaintPage(self.driver)

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
    def test_01_pilar1_positif_true_complaint_table_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Complaint Management (/tComplaint) dan memverifikasi tabel tampil."""
        print("\n[Complaint Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Complaint Management...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tampil di layar (True).")
        self.assertIn("complaint list management", self.driver.title.lower())
        print("  -> PASSED [True]: Tabel Complaint Management aktif terkonfirmasi di layar.")

    def test_02_pilar1_positif_true_search_nama_pengadu(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pengaduan berdasarkan nama pengadu/pelapor."""
        print("\n[Complaint Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian nama pengadu...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_user_name("Arif")
        self.page.wait_for_url_contains("userName=Arif")

        self.assertIn("userName=Arif", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter pencarian nama pengadu berhasil diaplikasikan.")

    def test_03_pilar1_positif_true_search_telepon_pengadu(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pengaduan berdasarkan nomor telepon pelapor."""
        print("\n[Complaint Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Pencarian telepon pelapor...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_user_phone("0812345678")
        self.page.wait_for_url_contains("userPhone=0812345678")

        self.assertIn("userPhone=0812345678", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter pencarian telepon pelapor berhasil diaplikasikan.")

    def test_04_pilar1_positif_true_search_telepon_driver(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari pengaduan berdasarkan nomor telepon pengemudi."""
        print("\n[Complaint Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Pencarian telepon pengemudi...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_driver_phone("0898765432")
        self.page.wait_for_url_contains("driverPhone=0898765432")

        self.assertIn("driverPhone=0898765432", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter pencarian telepon pengemudi berhasil diaplikasikan.")

    def test_05_pilar1_positif_true_filter_status_processed(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter pengaduan berstatus telah diproses (isHandle=1)."""
        print("\n[Complaint Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Filter status telah diproses...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_status("1")
        self.page.wait_for_url_contains("isHandle=1")

        self.assertIn("isHandle=1", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter status telah diproses berhasil diaplikasikan.")

    def test_06_pilar1_positif_true_filter_status_fail_to_dispose(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter pengaduan berstatus gagal diproses (isHandle=2)."""
        print("\n[Complaint Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Filter status gagal diproses...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_status("2")
        self.page.wait_for_url_contains("isHandle=2")

        self.assertIn("isHandle=2", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter status gagal diproses berhasil diaplikasikan.")

    def test_07_pilar1_positif_true_filter_status_all(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter seluruh status pengaduan (isHandle=All)."""
        print("\n[Complaint Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Filter semua status pengaduan...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.filter_by_status("")
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tetap tampil (True).")
        print("  -> PASSED [True]: Filter semua status pengaduan berhasil diaplikasikan.")

    def test_08_pilar1_positif_true_filter_rentang_tanggal(self):
        """[PILAR 1 - POSITIF (TRUE)] Filter rentang waktu pengaduan diaplikasikan di URL."""
        print("\n[Complaint Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Filter rentang waktu pengaduan...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-01-01", "2026-12-31")
        self.page.wait_for_url_contains("beginTime=2026-01-01")

        self.assertIn("beginTime=2026-01-01", self.page.get_current_url())
        self.assertIn("endTime=2026-12-31", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(timeout=10), "Tabel pengaduan harus tampil (True).")
        print("  -> PASSED [True]: Filter rentang waktu pengaduan berhasil diaplikasikan.")

    def test_09_pilar1_positif_true_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel pengaduan di DOM."""
        print("\n[Complaint Mgmt - Test 09] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom pengaduan...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("COMPLAINT TIME" in page_src, "Kolom Complaint Time harus ada (True).")
        self.assertTrue("NICKNAME OF COMPLAINANTS" in page_src, "Kolom Nickname harus ada (True).")
        self.assertTrue("REASONS FOR COMPLAINT" in page_src, "Kolom Reasons harus ada (True).")
        self.assertTrue("STATE" in page_src, "Kolom State harus ada (True).")
        self.assertTrue("PROCESSING TIME" in page_src, "Kolom Processing Time harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel pengaduan terkonfirmasi lengkap.")

    def test_10_pilar1_positif_true_tombol_aksi_hadir(self):
        """[PILAR 1 - POSITIF (TRUE)] Memverifikasi tombol Immediately process dan Delete hadir di antarmuka."""
        print("\n[Complaint Mgmt - Test 10] [PILAR 1: POSITIF (TRUE)] Verifikasi kehadiran tombol aksi...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.assertTrue(self.page.is_process_btn_displayed(), "Tombol Immediately process harus hadir (True).")
        self.assertTrue(self.page.is_delete_btn_displayed(), "Tombol Delete harus hadir (True).")
        print("  -> PASSED [True]: Tombol Immediately process dan Delete aktif terkonfirmasi di layar.")

    def test_11_pilar1_positif_true_deep_link_dengan_parameter_url(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat data akurat."""
        print("\n[Complaint Mgmt - Test 11] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.COMPLAINT_URL}?userName=Ahmad")
        self.page.wait_for_url_contains("userName=Ahmad")

        self.assertIn("userName=Ahmad", self.page.get_current_url())
        self.assertTrue(self.page.is_table_displayed(), "Tabel pengaduan harus tampil via deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter pencarian bekerja akurat.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Verifikasi Ketiadaan Cacat & Tombol Terkunci
    # =========================================================================
    def test_12_pilar2_positif_false_tombol_process_terkunci_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Immediately process terkunci (disabled) sebelum ada seleksi."""
        print("\n[Complaint Mgmt - Test 12] [PILAR 2: POSITIF (FALSE)] Uji tombol Immediately process terkunci...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_process_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Immediately process harus terkunci/disabled (False).")
        print("  -> PASSED [False]: Tombol Immediately process terkunci aman sebelum ada baris yang dipilih.")

    def test_13_pilar2_positif_false_tombol_delete_terkunci_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan tombol Delete terkunci (disabled) sebelum ada seleksi."""
        print("\n[Complaint Mgmt - Test 13] [PILAR 2: POSITIF (FALSE)] Uji tombol Delete terkunci...")
        self.login_sebagai_admin()
        self.page.navigate()

        is_enabled = self.page.is_delete_btn_enabled()
        self.assertFalse(is_enabled, "Tombol Delete harus terkunci/disabled (False).")
        print("  -> PASSED [False]: Tombol Delete terkunci aman sebelum ada baris yang dipilih.")

    def test_14_pilar2_positif_false_halaman_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan halaman Complaint Management bebas dari respon error server 500."""
        print("\n[Complaint Mgmt - Test 14] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh ada error 500 (False).")
        print("  -> PASSED [False]: Halaman Complaint Management bersih dari respon error 500.")

    def test_15_pilar2_positif_false_halaman_bebas_whitelabel_error(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan antarmuka bebas dari exception whitelabel Spring Boot."""
        print("\n[Complaint Mgmt - Test 15] [PILAR 2: POSITIF (FALSE)] Memastikan bebas whitelabel error...")
        self.login_sebagai_admin()
        self.page.navigate()

        page_src = self.page.get_page_source()
        self.assertFalse("Whitelabel Error Page" in page_src, "Tidak boleh ada Whitelabel error (False).")
        self.assertFalse("There was an unexpected error" in page_src, "Tidak boleh ada exception sistem (False).")
        print("  -> PASSED [False]: Antarmuka Complaint Management bersih dari pesan exception sistem.")

    def test_16_pilar2_positif_false_tidak_ada_duplikasi_header_tabel(self):
        """[PILAR 2 - POSITIF (FALSE)] Memastikan DOM tabel pengaduan bebas dari duplikasi elemen thead."""
        print("\n[Complaint Mgmt - Test 16] [PILAR 2: POSITIF (FALSE)] Uji ketiadaan duplikasi header tabel...")
        self.login_sebagai_admin()
        self.page.navigate()

        theads = self.driver.find_elements(By.TAG_NAME, "thead")
        self.assertFalse(len(theads) > 1, "Tabel pengaduan tidak boleh memuat thead ganda (False).")
        print("  -> PASSED [False]: Header tabel pengaduan bersih tanpa duplikasi.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Penanganan Kegagalan & Proteksi Terverifikasi
    # =========================================================================
    def test_17_pilar3_negatif_true_akses_complaint_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Akses langsung ke /tComplaint tanpa login aktif dicegat dan dialihkan ke /login."""
        print("\n[Complaint Mgmt - Test 17] [PILAR 3: NEGATIF (TRUE)] Akses /tComplaint tanpa login...")
        self.page.navigate()
        self.page.wait_for_url_contains("/login")

        current_url = self.page.get_current_url()
        self.assertTrue("/login" in current_url, "Tamu tanpa login harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute pengaduan aktif (dialihkan ke /login).")

    def test_18_pilar3_negatif_true_rentang_tanggal_terbalik_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Rentang tanggal terbalik (begin > end) ditangani aman tanpa server crash."""
        print("\n[Complaint Mgmt - Test 18] [PILAR 3: NEGATIF (TRUE)] Uji tanggal terbalik pada pengaduan...")
        self.login_sebagai_admin()
        self.page.filter_by_date("2026-12-31", "2026-01-01")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_table_displayed(timeout=10), "Tabel pengaduan tetap tampil aman (True).")
        self.assertTrue("500 Internal Server Error" not in page_src, "Server tetap stabil (True).")
        print("  -> PASSED [True]: Filter tanggal terbalik pengaduan ditangani aman oleh sistem.")

    def test_19_pilar3_negatif_true_sesi_berakhir_memicu_redirect_ke_login(self):
        """[PILAR 3 - NEGATIF (TRUE)] Sesi browser berakhir/terhapus memicu sistem mengalihkan ke /login."""
        print("\n[Complaint Mgmt - Test 19] [PILAR 3: NEGATIF (TRUE)] Uji proteksi sesi kedaluwarsa...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Sistem harus mengalihkan ke /login saat sesi habis (True).")
        print("  -> PASSED [True]: Sistem aktif mencegat request dan redirect ke /login saat sesi habis.")

    def test_20_pilar3_negatif_true_parameter_status_anomali_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Parameter status pengaduan anomali ditangani aman dengan tabel tetap tampil."""
        print("\n[Complaint Mgmt - Test 20] [PILAR 3: NEGATIF (TRUE)] Uji parameter status anomali...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.COMPLAINT_URL}?isHandle=invalid_status_code")

        page_src = self.page.get_page_source()
        self.assertTrue(self.page.is_table_displayed(timeout=10), "Tabel harus tetap tampil saat input anomali (True).")
        self.assertTrue("500 Internal Server Error" not in page_src and "Whitelabel Error Page" not in page_src, "Sistem tetap stabil (True).")
        print("  -> PASSED [True]: Parameter status pengaduan anomali ditangani aman tanpa server crash.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Pencegahan Manipulasi & Keamanan Data
    # =========================================================================
    def test_21_pilar4_negatif_false_pencarian_nama_pengadu_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nama pengadu fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Complaint Mgmt - Test 21] [PILAR 4: NEGATIF (FALSE)] Pencarian nama pengadu fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_user_name("USER_COMPLAINT_NONEXISTENT_999999")
        self.page.wait_for_url_contains("USER_COMPLAINT_NONEXISTENT_999999")

        row_count = self.page.get_rows_count()
        self.assertFalse(row_count > 0, "Pencarian nama pengadu fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian nama pengadu fiktif ditangani dengan aman (0 data).")

    def test_22_pilar4_negatif_false_pencarian_nomor_telepon_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian nomor telepon fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Complaint Mgmt - Test 22] [PILAR 4: NEGATIF (FALSE)] Pencarian telepon fiktif...")
        self.login_sebagai_admin()
        self.page.navigate()

        self.page.search_by_user_phone("00000000000000000")
        self.page.wait_for_url_contains("00000000000000000")

        row_count = self.page.get_rows_count()
        self.assertFalse(row_count > 0, "Pencarian telepon fiktif tidak boleh menampilkan data (False).")
        print("  -> PASSED [False]: Pencarian nomor telepon fiktif ditangani dengan aman (0 data).")

    def test_23_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_nomor_telepon_pengadu(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA membaca nomor telepon pelapor."""
        print("\n[Complaint Mgmt - Test 23] [PILAR 4: NEGATIF (FALSE)] Penolakan akses telepon pelapor tanpa login...")
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("TELEPHONE NUMBER OF COMPLAINANTS" in page_src, "Nomor HP pelapor tidak boleh bocor (False).")
        print("  -> PASSED [False]: Data privasi nomor HP pelapor terlindungi dari akses publik.")

    def test_24_pilar4_negatif_false_tamu_tanpa_login_tidak_bisa_baca_nomor_telepon_driver(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu publik tanpa login TIDAK BISA membaca nomor telepon driver yang dilaporkan."""
        print("\n[Complaint Mgmt - Test 24] [PILAR 4: NEGATIF (FALSE)] Penolakan akses telepon driver tanpa login...")
        self.page.navigate()

        page_src = self.page.get_page_source().upper()
        self.assertFalse("COMPLAINT DRIVER TELEPHONE" in page_src, "Nomor HP driver tidak boleh bocor (False).")
        print("  -> PASSED [False]: Data privasi nomor HP pengemudi terlindungi dari akses publik.")

    def test_25_pilar4_negatif_false_sql_injection_pada_pencarian_nama(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada form pencarian nama pengadu tidak membobol data."""
        print("\n[Complaint Mgmt - Test 25] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada nama pengadu...")
        self.login_sebagai_admin()
        self.page.navigate()

        sqli_payload = "' OR '1'='1"
        self.page.search_by_user_name(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQL syntax" in page_src, "Tidak boleh muncul error SQL syntax (False).")
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection pada form nama pengadu berhasil ditangkal.")

    def test_26_pilar4_negatif_false_sql_injection_drop_table_pada_telepon(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection bertipe destructive drop table tidak merusak database."""
        print("\n[Complaint Mgmt - Test 26] [PILAR 4: NEGATIF (FALSE)] Uji SQLi drop table pada nomor telepon...")
        self.login_sebagai_admin()
        self.page.navigate()

        sqli_payload = "'; DROP TABLE t_complaint; --"
        self.page.search_by_driver_phone(sqli_payload)

        page_src = self.page.get_page_source()
        self.assertFalse("SQLException" in page_src, "Tidak boleh muncul SQLException (False).")
        print("  -> PASSED [False]: Serangan SQL Injection destruktif berhasil ditangkal aman.")

    def test_27_pilar4_negatif_false_xss_script_pada_pencarian_nama(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada form pelapor tidak dieksekusi browser."""
        print("\n[Complaint Mgmt - Test 27] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada nama pengadu...")
        self.login_sebagai_admin()
        self.page.navigate()

        xss_payload = "<script>alert('xss_complaint')</script>"
        self.page.search_by_user_name(xss_payload)

        alert_opened = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_opened = True
        except Exception:
            alert_opened = False

        self.assertFalse(alert_opened, "Payload XSS tidak boleh membuka alert box browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada formulir pengaduan.")

    def test_28_pilar4_negatif_false_url_subpath_fiktif_complaint_ditangani(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tComplaint/invalid_subpath ditangani aman tanpa crash 500."""
        print("\n[Complaint Mgmt - Test 28] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tComplaint/invalid_subpath...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.COMPLAINT_URL}/invalid_subpath")

        page_src = self.page.get_page_source()
        self.assertFalse("500 Internal Server Error" in page_src, "Tidak boleh 500 server crash (False).")
        print("  -> PASSED [False]: URL fiktif pengaduan ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
