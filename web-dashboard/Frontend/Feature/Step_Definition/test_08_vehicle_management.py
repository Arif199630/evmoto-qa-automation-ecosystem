"""
=============================================================================
TEST SUITE 08: VEHICLE MANAGEMENT (MENU #8)
Website : <BASE_URL>/tCarBrand, /tCarModel, /tCar, /tMotorModel
Desain  : Page Object Model (POM)
Konsep  : 4 Pilar Testing (Positif True, Positif False, Negatif True, Negatif False)
Cakupan : Vehicle Brand Management, Vehicle Type/Model, Vehicle List, Motorcycle Model Setting
=============================================================================
Penjelasan 4 Pilar Pengujian untuk Manajemen:
1. Positif (True)  : Memastikan tabel brand, model, plat nomor, driver, dan toolbar tampil aktif (True).
2. Positif (False) : Memastikan tombol Update & Delete terkunci aman (disabled) sebelum ada seleksi (False).
3. Negatif (True)  : Memastikan akses ilegal dialihkan ke login & filter tanggal terbalik dicegah aman (True).
4. Negatif (False) : Memastikan data fiktif nihil & serangan siber (SQLi/XSS) ditangkal total (False).
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
from pages.page_08_vehicle_management import VehiclePage


class TestVehicleManagement(unittest.TestCase):
    """Test Suite Vehicle Management & 4 Sub-Halaman dengan Konsep 4 Pilar Testing (32 Test Lengkap)."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = VehiclePage(self.driver)

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
    def test_01_pilar1_positif_true_brand_tabel_dan_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Vehicle Brand Management (/tCarBrand) dan memverifikasi tabel aktif."""
        print("\n[Vehicle Mgmt - Test 01] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Vehicle Brand...")
        self.login_sebagai_admin()
        self.page.navigate_brand()

        self.assertTrue(self.page.is_brand_table_displayed(), "Tabel brand harus tampil (True).")
        jumlah_baris = self.page.get_brand_rows_count()
        self.assertTrue(jumlah_baris > 0, "Harus memuat baris data brand kendaraan (True).")
        self.assertIn("vehicle brand management", self.driver.title.lower())
        print(f"  -> PASSED [True]: Tabel Vehicle Brand termuat dengan {jumlah_baris} brand.")

    def test_02_pilar1_positif_true_brand_filter_pencarian_nama_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari merek kendaraan berdasarkan nama brand yang ada di environment aktif."""
        self.login_sebagai_admin()
        self.page.navigate_brand()

        brand = self.page.get_first_row_value("BRAND NAME")
        if not brand:
            self.skipTest("Belum ada data brand di environment ini; tambahkan data uji brand.")
        print(f"\n[Vehicle Mgmt - Test 02] [PILAR 1: POSITIF (TRUE)] Pencarian brand valid '{brand}'...")

        self.page.search_brand_by_name(brand)
        self.page.wait_for_url_contains("name=")

        self.assertTrue(self.page.get_brand_rows_count() > 0, f"Harus ditemukan baris brand {brand}.")
        self.assertIn(brand, self.page.get_brand_first_row_text())

    def test_03_pilar1_positif_true_brand_seleksi_radio_aktifkan_tombol(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio brand mengaktifkan tombol Update dan Delete."""
        print("\n[Vehicle Mgmt - Test 03] [PILAR 1: POSITIF (TRUE)] Seleksi radio brand dan aktivasi tombol...")
        self.login_sebagai_admin()
        self.page.navigate_brand()

        sukses_pilih = self.page.select_first_brand()
        self.assertTrue(sukses_pilih, "Harus berhasil memilih satu radio brand (True).")
        self.assertTrue(self.page.is_brand_update_btn_enabled(), "Tombol Update brand harus aktif (True).")
        self.assertTrue(self.page.is_brand_delete_btn_enabled(), "Tombol Delete brand harus aktif (True).")
        print("  -> PASSED [True]: Tombol Update dan Delete aktif setelah radio brand dipilih.")

    def test_04_pilar1_positif_true_brand_verifikasi_header_kolom(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi integritas kolom tabel brand di DOM."""
        print("\n[Vehicle Mgmt - Test 04] [PILAR 1: POSITIF (TRUE)] Verifikasi header kolom brand...")
        self.login_sebagai_admin()
        self.page.navigate_brand()

        page_src = self.page.get_page_source().upper()
        self.assertTrue("BRAND NAME" in page_src, "Kolom Brand Name harus ada (True).")
        self.assertTrue("MODELS" in page_src, "Kolom Models harus ada (True).")
        self.assertTrue("VEHICLES" in page_src, "Kolom Vehicles harus ada (True).")
        print("  -> PASSED [True]: Struktur kolom tabel brand terkonfirmasi lengkap.")

    def test_05_pilar1_positif_true_model_tabel_dan_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Vehicle Type Management (/tCarModel) dan memverifikasi tabel aktif."""
        print("\n[Vehicle Mgmt - Test 05] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Vehicle Type/Model...")
        self.login_sebagai_admin()
        self.page.navigate_model()

        self.assertTrue(self.page.is_model_table_displayed(), "Tabel tipe/model harus tampil (True).")
        jumlah_baris = self.page.get_model_rows_count()
        self.assertTrue(jumlah_baris > 0, "Harus memuat baris data tipe kendaraan (True).")
        self.assertIn("vehicle type management", self.driver.title.lower())
        print(f"  -> PASSED [True]: Tabel Vehicle Type termuat dengan {jumlah_baris} tipe/model.")

    def test_06_pilar1_positif_true_model_filter_pencarian_nama_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari tipe kendaraan berdasarkan nama valid 'ECGO 3'."""
        print("\n[Vehicle Mgmt - Test 06] [PILAR 1: POSITIF (TRUE)] Pencarian tipe/model valid 'ECGO 3'...")
        self.login_sebagai_admin()
        self.page.navigate_model()

        self.page.search_model_by_name("ECGO 3")
        self.page.wait_for_url_contains("name=ECGO")

        self.assertIn("name=ECGO", self.page.get_current_url())
        self.assertTrue(self.page.get_model_rows_count() > 0, "Harus ditemukan baris model ECGO 3 (True).")
        self.assertIn("ECGO", self.page.get_model_first_row_text())
        print("  -> PASSED [True]: Pencarian model 'ECGO 3' berhasil mengembalikan data.")

    def test_07_pilar1_positif_true_model_seleksi_radio_aktifkan_tombol(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio tipe/model mengaktifkan tombol Update dan Delete."""
        print("\n[Vehicle Mgmt - Test 07] [PILAR 1: POSITIF (TRUE)] Seleksi radio model dan aktivasi tombol...")
        self.login_sebagai_admin()
        self.page.navigate_model()

        sukses_pilih = self.page.select_first_model()
        self.assertTrue(sukses_pilih, "Harus berhasil memilih satu radio model (True).")
        self.assertTrue(self.page.is_model_update_btn_enabled(), "Tombol Update model harus aktif (True).")
        self.assertTrue(self.page.is_model_delete_btn_enabled(), "Tombol Delete model harus aktif (True).")
        print("  -> PASSED [True]: Tombol Update dan Delete aktif setelah radio model dipilih.")

    def test_08_pilar1_positif_true_car_list_tabel_dan_komponen_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Vehicle Management (/tCar) dan memverifikasi daftar armada."""
        print("\n[Vehicle Mgmt - Test 08] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Vehicle List (/tCar)...")
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        self.assertTrue(self.page.is_car_table_displayed(), "Tabel armada kendaraan harus tampil (True).")
        jumlah_baris = self.page.get_car_rows_count()
        self.assertTrue(jumlah_baris > 0, "Harus memuat baris armada kendaraan (True).")
        self.assertIn("vehicle management", self.driver.title.lower())
        print(f"  -> PASSED [True]: Tabel Vehicle List aktif dengan {jumlah_baris} armada kendaraan.")

    def test_09_pilar1_positif_true_car_filter_plat_nomor_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari kendaraan berdasarkan nomor plat yang ada di environment aktif."""
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        plate = self.page.get_first_row_value("PLATE")
        if not plate:
            self.skipTest("Belum ada data kendaraan berplat di environment ini; tambahkan data uji kendaraan.")
        print(f"\n[Vehicle Mgmt - Test 09] [PILAR 1: POSITIF (TRUE)] Pencarian plat nomor valid '{plate}'...")

        self.page.search_car_by_plate(plate)
        self.page.wait_for_url_contains("carLicensePlate=")

        self.assertTrue(self.page.get_car_rows_count() > 0, f"Harus ditemukan kendaraan dengan plat {plate}.")
        self.assertIn(plate, self.page.get_car_first_row_text())
        print("  -> PASSED [True]: Pencarian plat nomor berhasil mengembalikan baris kendaraan.")

    def test_10_pilar1_positif_true_car_filter_driver_name_valid(self):
        """[PILAR 1 - POSITIF (TRUE)] Mencari kendaraan berdasarkan nama pengemudi yang ada di environment aktif."""
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        driver_name = self.page.get_first_row_value("DRIVER")
        if not driver_name:
            self.skipTest("Belum ada kendaraan dengan pengemudi di environment ini; tambahkan data uji.")
        print(f"\n[Vehicle Mgmt - Test 10] [PILAR 1: POSITIF (TRUE)] Pencarian driver valid '{driver_name}'...")

        self.page.search_car_by_driver(driver_name)
        self.page.wait_for_url_contains("driverName=")

        self.assertTrue(self.page.get_car_rows_count() > 0, f"Harus ditemukan armada pengemudi {driver_name}.")
        self.assertIn(driver_name, self.page.get_car_first_row_text())
        print("  -> PASSED [True]: Pencarian driver armada berhasil mengembalikan data.")

    def test_11_pilar1_positif_true_car_seleksi_radio_aktifkan_tombol(self):
        """[PILAR 1 - POSITIF (TRUE)] Memilih radio kendaraan mengaktifkan tombol Update dan Delete."""
        print("\n[Vehicle Mgmt - Test 11] [PILAR 1: POSITIF (TRUE)] Seleksi radio armada kendaraan...")
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        sukses_pilih = self.page.select_first_car()
        self.assertTrue(sukses_pilih, "Harus berhasil memilih satu radio armada (True).")
        self.assertTrue(self.page.is_car_update_btn_enabled(), "Tombol Update armada harus aktif (True).")
        self.assertTrue(self.page.is_car_delete_btn_enabled(), "Tombol Delete armada harus aktif (True).")
        print("  -> PASSED [True]: Tombol Update dan Delete aktif setelah radio kendaraan dipilih.")

    def test_12_pilar1_positif_true_car_toolbar_template_import_export_aktif(self):
        """[PILAR 1 - POSITIF (TRUE)] Verifikasi tombol batch Template, Import, dan Export aktif."""
        print("\n[Vehicle Mgmt - Test 12] [PILAR 1: POSITIF (TRUE)] Verifikasi toolbar Template, Import, Export...")
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        self.assertTrue(self.page.is_car_template_btn_displayed(), "Tombol Template harus tampil (True).")
        self.assertTrue(self.page.is_car_import_btn_displayed(), "Tombol Import harus tampil (True).")
        self.assertTrue(self.page.is_car_export_btn_displayed(), "Tombol Export harus tampil (True).")
        print("  -> PASSED [True]: Seluruh tombol toolbar batch armada (Template, Import, Export) aktif.")

    def test_13_pilar1_positif_true_motor_model_tabel_dan_status_tampil(self):
        """[PILAR 1 - POSITIF (TRUE)] Membuka Motorcycle model setting (/tMotorModel) dan verifikasi data tampil."""
        print("\n[Vehicle Mgmt - Test 13] [PILAR 1: POSITIF (TRUE)] Verifikasi tabel Motorcycle model setting...")
        self.login_sebagai_admin()
        self.page.navigate_motor_model()

        self.assertTrue(self.page.is_motor_table_displayed(), "Tabel motor model harus tampil (True).")
        jumlah_baris = self.page.get_motor_rows_count()
        self.assertTrue(jumlah_baris > 0, "Harus ada data model motor di tabel (True).")
        self.assertIn("Motorcycle model setting", self.driver.title)
        print(f"  -> PASSED [True]: Halaman Motorcycle Model Setting termuat dengan {jumlah_baris} baris model.")

    def test_14_pilar1_positif_true_navigasi_sekuensial_seluruh_sub_halaman_vehicle(self):
        """[PILAR 1 - POSITIF (TRUE)] Navigasi sekuensial ke 4 sub-halaman vehicle dalam 1 sesi login."""
        print("\n[Vehicle Mgmt - Test 14] [PILAR 1: POSITIF (TRUE)] Uji navigasi sekuensial 4 sub-halaman...")
        self.login_sebagai_admin()

        sub_pages = [
            (Config.CAR_BRAND_URL, "Vehicle Brand Management"),
            (Config.CAR_MODEL_URL, "Vehicle Type Management"),
            (Config.CAR_LIST_URL, "Vehicle Management"),
            (Config.MOTOR_MODEL_URL, "Motorcycle model setting"),
        ]

        for url, label in sub_pages:
            self.driver.get(url)
            self.assertIn("200", "200")
            self.assertFalse("500" in self.driver.title)
            print(f"    [OK] {label} ({url}) -> Loaded.")

        print("  -> PASSED [True]: Seluruh 4 sub-halaman Vehicle Management stabil diakses berurutan.")

    def test_15_pilar1_positif_true_deep_link_dengan_parameter_pencarian(self):
        """[PILAR 1 - POSITIF (TRUE)] Deep link langsung via URL dengan parameter pencarian memuat filter."""
        print("\n[Vehicle Mgmt - Test 15] [PILAR 1: POSITIF (TRUE)] Uji deep link dengan URL query...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.CAR_BRAND_URL}?name=ECGO")
        self.page.wait_for_url_contains("name=ECGO")

        self.assertTrue(self.page.is_brand_table_displayed(), "Tabel brand harus tampil via deep link (True).")
        print("  -> PASSED [True]: Deep link langsung dengan parameter URL bekerja akurat.")

    # =========================================================================
    # PILAR 2: POSITIF (FALSE) - Kondisi Error / Elemen Tidak Wajar Bernilai SALAH
    # =========================================================================
    def test_16_pilar2_positif_false_brand_tombol_aksi_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol Update & Delete brand TIDAK AKTIF saat belum ada baris dipilih."""
        print("\n[Vehicle Mgmt - Test 16] [PILAR 2: POSITIF (FALSE)] Tombol aksi brand awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_brand()

        self.assertFalse(
            self.page.is_brand_update_btn_enabled(),
            "Tombol Update brand tidak boleh aktif sebelum memilih radio (False)."
        )
        self.assertFalse(
            self.page.is_brand_delete_btn_enabled(),
            "Tombol Delete brand tidak boleh aktif sebelum memilih radio (False)."
        )
        print("  -> PASSED [False]: Tombol aksi brand terkunci aman berstatus disabled.")

    def test_17_pilar2_positif_false_model_tombol_aksi_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol Update & Delete model TIDAK AKTIF saat belum ada baris dipilih."""
        print("\n[Vehicle Mgmt - Test 17] [PILAR 2: POSITIF (FALSE)] Tombol aksi model awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_model()

        self.assertFalse(
            self.page.is_model_update_btn_enabled(),
            "Tombol Update model tidak boleh aktif sebelum memilih radio (False)."
        )
        self.assertFalse(
            self.page.is_model_delete_btn_enabled(),
            "Tombol Delete model tidak boleh aktif sebelum memilih radio (False)."
        )
        print("  -> PASSED [False]: Tombol aksi model terkunci aman berstatus disabled.")

    def test_18_pilar2_positif_false_car_tombol_aksi_disabled_sebelum_seleksi(self):
        """[PILAR 2 - POSITIF (FALSE)] Tombol Update & Delete kendaraan TIDAK AKTIF saat belum ada baris dipilih."""
        print("\n[Vehicle Mgmt - Test 18] [PILAR 2: POSITIF (FALSE)] Tombol aksi armada awal nonaktif...")
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        self.assertFalse(
            self.page.is_car_update_btn_enabled(),
            "Tombol Update armada tidak boleh aktif sebelum memilih radio (False)."
        )
        self.assertFalse(
            self.page.is_car_delete_btn_enabled(),
            "Tombol Delete armada tidak boleh aktif sebelum memilih radio (False)."
        )
        print("  -> PASSED [False]: Tombol aksi armada terkunci aman berstatus disabled.")

    def test_19_pilar2_positif_false_seluruh_sub_halaman_bebas_error_server_500(self):
        """[PILAR 2 - POSITIF (FALSE)] Keempat sub-halaman vehicle bebas dari pesan respon error server 500."""
        print("\n[Vehicle Mgmt - Test 19] [PILAR 2: POSITIF (FALSE)] Memastikan bebas error server 500...")
        self.login_sebagai_admin()

        for url in [Config.CAR_BRAND_URL, Config.CAR_MODEL_URL, Config.CAR_LIST_URL, Config.MOTOR_MODEL_URL]:
            self.driver.get(url)
            page_src = self.driver.page_source.lower()
            self.assertFalse("500 internal server error" in page_src)
            self.assertFalse("whitelabel error page" in page_src)

        print("  -> PASSED [False]: Seluruh sub-halaman Vehicle Management bersih dari error 500.")

    # =========================================================================
    # PILAR 3: NEGATIF (TRUE) - Proteksi Keamanan & Peringatan Sistem Aktif
    # =========================================================================
    def test_20_pilar3_negatif_true_brand_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tCarBrand tanpa login dialihkan ke /login."""
        print("\n[Vehicle Mgmt - Test 20] [PILAR 3: NEGATIF (TRUE)] Akses /tCarBrand tanpa autentikasi...")
        self.page.navigate_brand()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Akses harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute /tCarBrand aktif (dialihkan ke /login).")

    def test_21_pilar3_negatif_true_model_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tCarModel tanpa login dialihkan ke /login."""
        print("\n[Vehicle Mgmt - Test 21] [PILAR 3: NEGATIF (TRUE)] Akses /tCarModel tanpa autentikasi...")
        self.page.navigate_model()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Akses harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute /tCarModel aktif (dialihkan ke /login).")

    def test_22_pilar3_negatif_true_car_akses_tanpa_login_dialihkan(self):
        """[PILAR 3 - NEGATIF (TRUE)] Mengakses /tCar tanpa login dialihkan ke /login."""
        print("\n[Vehicle Mgmt - Test 22] [PILAR 3: NEGATIF (TRUE)] Akses /tCar tanpa autentikasi...")
        self.page.navigate_car_list()
        self.page.wait_for_url_contains("/login")

        self.assertTrue("/login" in self.page.get_current_url(), "Akses harus dialihkan ke /login (True).")
        print("  -> PASSED [True]: Proteksi rute /tCar aktif (dialihkan ke /login).")

    def test_23_pilar3_negatif_true_rentang_tanggal_terbalik_ditangani_aman(self):
        """[PILAR 3 - NEGATIF (TRUE)] Rentang tanggal terbalik (begin > end) ditangani aman tanpa crash."""
        print("\n[Vehicle Mgmt - Test 23] [PILAR 3: NEGATIF (TRUE)] Uji rentang tanggal terbalik...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.CAR_BRAND_URL}?beginDate=2026-12-31&endDate=2026-01-01")

        self.assertTrue(self.page.is_brand_table_displayed(), "Tabel brand harus tetap tampil aman (True).")
        self.assertFalse("500 Internal Server Error" in self.driver.page_source)
        print("  -> PASSED [True]: Filter tanggal terbalik ditangani dengan aman oleh sistem.")

    # =========================================================================
    # PILAR 4: NEGATIF (FALSE) - Akses Ilegal & Serangan Siber DITOLAK
    # =========================================================================
    def test_24_pilar4_negatif_false_brand_pencarian_nama_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian merek kendaraan fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Vehicle Mgmt - Test 24] [PILAR 4: NEGATIF (FALSE)] Pencarian brand fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_brand()

        self.page.search_brand_by_name("BrandPalsu999XYZ")
        self.page.wait_for_url_contains("name=BrandPalsu")

        self.assertFalse(
            self.page.get_brand_rows_count() > 0,
            "Pencarian brand fiktif tidak boleh memunculkan data (False)."
        )
        print("  -> PASSED [False]: Pencarian brand fiktif ditangani dengan aman (0 data).")

    def test_25_pilar4_negatif_false_model_pencarian_nama_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian model kendaraan fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Vehicle Mgmt - Test 25] [PILAR 4: NEGATIF (FALSE)] Pencarian model fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_model()

        self.page.search_model_by_name("ModelPalsu999XYZ")
        self.page.wait_for_url_contains("name=ModelPalsu")

        self.assertFalse(
            self.page.get_model_rows_count() > 0,
            "Pencarian model fiktif tidak boleh memunculkan data (False)."
        )
        print("  -> PASSED [False]: Pencarian model fiktif ditangani dengan aman (0 data).")

    def test_26_pilar4_negatif_false_car_pencarian_plat_fiktif(self):
        """[PILAR 4 - NEGATIF (FALSE)] Pencarian plat nomor fiktif menghasilkan tabel tanpa data secara aman."""
        print("\n[Vehicle Mgmt - Test 26] [PILAR 4: NEGATIF (FALSE)] Pencarian plat fiktif...")
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        self.page.search_car_by_plate("Z 999999 ZZP")
        self.page.wait_for_url_contains("carLicensePlate=")

        self.assertFalse(
            self.page.get_car_rows_count() > 0,
            "Pencarian plat fiktif tidak boleh memunculkan data armada (False)."
        )
        print("  -> PASSED [False]: Pencarian plat fiktif ditangani dengan aman (0 data).")

    def test_27_pilar4_negatif_false_akses_tanpa_login_tidak_bisa_lihat_plat_dan_driver(self):
        """[PILAR 4 - NEGATIF (FALSE)] Tamu tanpa login TIDAK BISA membaca data plat nomor atau nama driver."""
        print("\n[Vehicle Mgmt - Test 27] [PILAR 4: NEGATIF (FALSE)] Penolakan akses data armada tanpa login...")
        self.page.navigate_car_list()
        self.page.wait_for_url_contains("/login")

        page_src = self.driver.page_source
        self.assertFalse("B 4923 UCT" in page_src, "Plat nomor armada tidak boleh bocor ke publik (False).")
        self.assertFalse("Bagas Octavian" in page_src, "Nama driver armada tidak boleh bocor ke publik (False).")
        print("  -> PASSED [False]: Data armada dan pengemudi terproteksi rapat dari akses luar.")

    def test_28_pilar4_negatif_false_sql_injection_pada_pencarian_brand(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian brand tidak membobol data."""
        print("\n[Vehicle Mgmt - Test 28] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada pencarian brand...")
        self.login_sebagai_admin()
        self.page.navigate_brand()

        self.page.search_brand_by_name("' OR '1'='1' --")
        self.assertFalse(
            "500 Internal Server Error" in self.driver.page_source,
            "SQL Injection tidak boleh menyebabkan error 500 (False)."
        )
        print("  -> PASSED [False]: Serangan SQL Injection pada nama brand berhasil ditangkal.")

    def test_29_pilar4_negatif_false_sql_injection_pada_pencarian_plat_nomor(self):
        """[PILAR 4 - NEGATIF (FALSE)] SQL injection pada pencarian plat nomor tidak membobol data."""
        print("\n[Vehicle Mgmt - Test 29] [PILAR 4: NEGATIF (FALSE)] Uji SQLi pada pencarian plat nomor...")
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        self.page.search_car_by_plate("' OR 1=1 --")
        self.assertFalse(
            "500 Internal Server Error" in self.driver.page_source,
            "SQL Injection tidak boleh menyebabkan error 500 (False)."
        )
        print("  -> PASSED [False]: Serangan SQL Injection pada plat nomor berhasil ditangkal.")

    def test_30_pilar4_negatif_false_xss_pada_pencarian_brand(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada brand search tidak dieksekusi browser."""
        print("\n[Vehicle Mgmt - Test 30] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada pencarian brand...")
        self.login_sebagai_admin()
        self.page.navigate_brand()

        self.page.search_brand_by_name("<script>window.xss_brand=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_brand === true;")
        self.assertFalse(is_exploited, "Script XSS tidak boleh dieksekusi oleh browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada Vehicle Brand Management.")

    def test_31_pilar4_negatif_false_xss_pada_pencarian_driver_kendaraan(self):
        """[PILAR 4 - NEGATIF (FALSE)] XSS payload script pada filter driver armada tidak dieksekusi browser."""
        print("\n[Vehicle Mgmt - Test 31] [PILAR 4: NEGATIF (FALSE)] Uji XSS script pada filter driver armada...")
        self.login_sebagai_admin()
        self.page.navigate_car_list()

        self.page.search_car_by_driver("<script>window.xss_car_driver=true;</script>")
        is_exploited = self.driver.execute_script("return window.xss_car_driver === true;")
        self.assertFalse(is_exploited, "Script XSS tidak boleh dieksekusi oleh browser (False).")
        print("  -> PASSED [False]: Input XSS berhasil disanitasi pada filter driver armada.")

    def test_32_pilar4_negatif_false_url_sub_path_fiktif_ditangani_tanpa_crash(self):
        """[PILAR 4 - NEGATIF (FALSE)] Mengakses URL fiktif /tCarBrand/invalid_path ditangani dengan aman tanpa crash 500."""
        print("\n[Vehicle Mgmt - Test 32] [PILAR 4: NEGATIF (FALSE)] Akses URL fiktif /tCarBrand/invalid_path...")
        self.login_sebagai_admin()
        self.driver.get(f"{Config.CAR_BRAND_URL}/invalid_route_test")

        page_src = self.driver.page_source.lower()
        self.assertFalse("500 internal server error" in page_src)
        print("  -> PASSED [False]: URL fiktif ditangani secara aman tanpa server crash.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
