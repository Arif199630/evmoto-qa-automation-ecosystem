# Panduan Pemeliharaan (Maintenance Guide) Page Object Model

> Panduan praktis bagi QA Engineer atau pengembang untuk memelihara, memperbarui, atau menambahkan modul pengujian baru pada sistem otomatisasi EvMoto Admin.

---

## 1. Aturan Dasar Page Object Model (POM)

Untuk menjaga kualitas dan kerapian kode sesuai standar industri:

1. **Aturan 1 (Tidak Ada Selector di Dalam Test Script)**:
   - File di dalam folder `tests/` **DILARANG** memuat `By.ID`, `By.CSS_SELECTOR`, `By.XPATH`, atau panggilan langsung `find_element`.
   - Semua pemilih elemen (*locators*) wajib berada di dalam kelas Page Object di folder `pages/`.

2. **Aturan 2 (Nama Metode Mencerminkan Tindakan Manusia)**:
   - Gunakan nama metode yang jelas seperti `login()`, `search_by_name()`, `click_process_button()`, `is_table_displayed()`.

3. **Aturan 3 (Test Script Hanya Berisi Asersi)**:
   - File di dalam folder `tests/` fokus pada validasi hasil menggunakan `self.assertTrue()`, `self.assertEqual()`, atau `self.assertIn()`.

---

## 2. Cara Memperbarui Elemen yang Berubah (UI Change)

Jika tim pengembang web mengubah ID, tombol, atau struktur HTML suatu halaman:

1. Buka file halaman terkait di folder `pages/` (misalnya `pages/login_page.py`).
2. Cari variabel locator yang bersangkutan, misalnya:
   ```python
   # Ubah dari locator lama ke locator baru
   LOCATOR_SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
   ```
3. Simpan file tersebut.
4. **Selesai!** Anda tidak perlu menyentuh file pengujian di folder `tests/` sama sekali.

---

## 3. Cara Menambahkan Modul Pengujian Baru (Contoh: Vehicle Management)

Jika ingin menambahkan pengujian untuk halaman baru:

### Langkah 1: Buat Page Object di `pages/`
Buat file baru, misalnya `pages/vehicle_page.py`:
```python
from selenium.webdriver.common.by import By
from .base_page import BasePage
from config import Config

class VehiclePage(BasePage):
    LOCATOR_TABLE = (By.TAG_NAME, "table")
    LOCATOR_ADD_BTN = (By.CSS_SELECTOR, "[data-vehicle-add]")

    def navigate(self):
        self.open(f"{Config.BASE_URL}/tCar")

    def is_table_displayed(self):
        return self.is_displayed(self.LOCATOR_TABLE)
```

Daftarkan di `pages/__init__.py`:
```python
from .vehicle_page import VehiclePage
```

### Langkah 2: Buat Test Suite di `tests/`
Buat file baru `tests/test_10_vehicle_management.py`:
```python
import unittest
from config import Config
from pages.login_page import LoginPage
from pages.vehicle_page import VehiclePage

class TestVehicleManagement(unittest.TestCase):
    def setUp(self):
        self.driver = Config.get_driver()
        self.login_page = LoginPage(self.driver)
        self.page = VehiclePage(self.driver)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_01_navigasi_vehicle(self):
        self.login_page.login_as_admin()
        self.page.navigate()
        self.assertTrue(self.page.is_table_displayed())

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

### Langkah 3: Daftarkan ke `main_runner.py`
Tambahkan modul baru ke dalam `load_test_suite()` di `main_runner.py` agar ikut dijalankan saat unified test dijalankan.
