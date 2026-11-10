"""
TEMPLATE TEST FITUR BARU (Admin Dashboard)

Cara pakai:
  1. Salin file ini ke Frontend/Feature/Step_Definition/test_<nomor>_<nama_modul>.py
  2. Buat Page Object di Frontend/Feature/Pages/page_<nomor>_<nama_modul>.py (locator + aksi).
  3. Ganti semua bagian bertanda GANTI.
  4. Jalankan: python ../evmoto-qa-tools/run_all.py --suite admin

Aturan:
  - Kata kunci pencarian diambil dari data yang ada di environment aktif (get_first_row_value),
    bukan nilai tetap dari production.
  - Tidak ada domain yang ditulis langsung; pakai Config.BASE_URL.
  - Setiap test punya assertion yang bisa gagal dengan pesan jelas. Bila datanya tidak ada,
    pakai self.skipTest("alasan"), jangan self.assertTrue(True).
"""
import unittest

from config import Config
from pages.page_00_login import LoginPage
from pages.page_08_vehicle_management import VehiclePage   # GANTI dengan Page Object fitur baru


class TestFiturBaru(unittest.TestCase):                      # GANTI nama class
    """GANTI: nama modul dan menu admin yang diuji."""

    def setUp(self):
        self.driver = Config.get_driver()
        self.page = VehiclePage(self.driver)                   # GANTI

    def tearDown(self):
        self.driver.quit()

    def login_sebagai_admin(self):
        login_page = LoginPage(self.driver)
        login_page.navigate()
        login_page.login_as_admin()
        login_page.wait_for_url_contains("/blackboard")

    def test_01_pilar1_positif_true_pencarian_data_yang_ada(self):
        """[PILAR 1] Pencarian dengan data yang benar-benar ada di environment aktif mengembalikan baris itu."""
        # GIVEN: halaman daftar terbuka dan ada minimal satu baris data
        self.login_sebagai_admin()
        self.page.navigate_brand()                             # GANTI
        keyword = self.page.get_first_row_value("BRAND NAME")  # GANTI judul kolom
        if not keyword:
            self.skipTest("Belum ada data di environment ini; tambahkan data uji.")

        # WHEN: pengguna mencari data tersebut
        self.page.search_brand_by_name(keyword)                # GANTI

        # THEN: hasil memuat data yang dicari
        self.assertTrue(self.page.get_brand_rows_count() > 0, f"Pencarian '{keyword}' harus menemukan data")
        self.assertIn(keyword, self.page.get_brand_first_row_text())

    def test_02_pilar3_negatif_true_pencarian_tidak_ada(self):
        """[PILAR 3] Kata kunci yang tidak ada menampilkan keadaan kosong, bukan error."""
        self.login_sebagai_admin()
        self.page.navigate_brand()                             # GANTI
        self.page.search_brand_by_name("ZZZ-TIDAK-ADA-9999")
        self.assertEqual(self.page.get_brand_rows_count(), 0, "Kata kunci yang tidak ada harus menghasilkan 0 baris")


if __name__ == "__main__":
    unittest.main()
