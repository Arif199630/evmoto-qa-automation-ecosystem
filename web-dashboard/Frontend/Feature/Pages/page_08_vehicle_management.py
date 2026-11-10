"""
Vehicle Management Page Object
Website: <BASE_URL>/tCarBrand, /tCarModel, /tCar, /tMotorModel
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class VehiclePage(BasePage):
    """Page Object untuk Modul Vehicle Management & 4 Sub-Halamannya."""

    # =========================================================================
    # 1. VEHICLE BRAND MANAGEMENT (/tCarBrand)
    # =========================================================================
    LOCATOR_BRAND_HEADING       = (By.TAG_NAME, "h1")
    LOCATOR_BRAND_SEARCH_INPUT  = (By.CSS_SELECTOR, "form[action='/tCarBrand'] input[name='name']")
    LOCATOR_BRAND_BEGIN_DATE    = (By.CSS_SELECTOR, "form[action='/tCarBrand'] input[name='beginDate']")
    LOCATOR_BRAND_END_DATE      = (By.CSS_SELECTOR, "form[action='/tCarBrand'] input[name='endDate']")
    LOCATOR_BRAND_SEARCH_BTN    = (By.CSS_SELECTOR, "form[action='/tCarBrand'] button[type='submit']")
    LOCATOR_BRAND_TABLE         = (By.TAG_NAME, "table")
    LOCATOR_BRAND_ROWS          = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_BRAND_RADIOS        = (By.CSS_SELECTOR, "input[name='selected-car-brand']")
    LOCATOR_BRAND_UPDATE_BTN    = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_BRAND_DELETE_BTN    = (By.XPATH, "//button[normalize-space()='Delete']")

    def navigate_brand(self):
        """Buka halaman Vehicle Brand Management (/tCarBrand)."""
        self.open(Config.CAR_BRAND_URL)

    def is_brand_table_displayed(self):
        """Memeriksa apakah tabel Brand tampil."""
        return self.is_displayed(self.LOCATOR_BRAND_TABLE)

    def get_brand_rows_count(self):
        """Menghitung baris data aktual pada tabel Brand."""
        rows = self.find_all(self.LOCATOR_BRAND_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def get_brand_first_row_text(self):
        """Mengambil teks baris pertama pada tabel Brand."""
        rows = self.find_all(self.LOCATOR_BRAND_ROWS)
        return rows[0].text if rows else ""

    def search_brand_by_name(self, name):
        """Mencari merek kendaraan berdasarkan nama."""
        self.type_text(self.LOCATOR_BRAND_SEARCH_INPUT, name)
        self.click(self.LOCATOR_BRAND_SEARCH_BTN)

    def select_first_brand(self):
        """Memilih radio button brand pertama di tabel."""
        radios = self.find_all(self.LOCATOR_BRAND_RADIOS)
        if radios:
            self.click_js(radios[0])
            self.dispatch_event(radios[0], "change")
            return True
        return False

    def is_brand_update_btn_enabled(self):
        """Memeriksa apakah tombol Update brand aktif."""
        return self.is_enabled(self.LOCATOR_BRAND_UPDATE_BTN)

    def is_brand_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete brand aktif."""
        return self.is_enabled(self.LOCATOR_BRAND_DELETE_BTN)

    # =========================================================================
    # 2. VEHICLE TYPE / MODEL MANAGEMENT (/tCarModel)
    # =========================================================================
    LOCATOR_MODEL_HEADING       = (By.TAG_NAME, "h1")
    LOCATOR_MODEL_SEARCH_INPUT  = (By.CSS_SELECTOR, "form[action='/tCarModel'] input[name='name']")
    LOCATOR_MODEL_BEGIN_DATE    = (By.CSS_SELECTOR, "form[action='/tCarModel'] input[name='beginDate']")
    LOCATOR_MODEL_END_DATE      = (By.CSS_SELECTOR, "form[action='/tCarModel'] input[name='endDate']")
    LOCATOR_MODEL_SEARCH_BTN    = (By.CSS_SELECTOR, "form[action='/tCarModel'] button[type='submit']")
    LOCATOR_MODEL_TABLE         = (By.TAG_NAME, "table")
    LOCATOR_MODEL_ROWS          = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_MODEL_RADIOS        = (By.CSS_SELECTOR, "input[name='selected-car-model']")
    LOCATOR_MODEL_UPDATE_BTN    = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_MODEL_DELETE_BTN    = (By.XPATH, "//button[normalize-space()='Delete']")

    def navigate_model(self):
        """Buka halaman Vehicle Type Management (/tCarModel)."""
        self.open(Config.CAR_MODEL_URL)

    def is_model_table_displayed(self):
        """Memeriksa apakah tabel Model tampil."""
        return self.is_displayed(self.LOCATOR_MODEL_TABLE)

    def get_model_rows_count(self):
        """Menghitung baris data aktual pada tabel Model."""
        rows = self.find_all(self.LOCATOR_MODEL_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def get_model_first_row_text(self):
        """Mengambil teks baris pertama pada tabel Model."""
        rows = self.find_all(self.LOCATOR_MODEL_ROWS)
        return rows[0].text if rows else ""

    def search_model_by_name(self, name):
        """Mencari tipe/model kendaraan berdasarkan nama."""
        self.type_text(self.LOCATOR_MODEL_SEARCH_INPUT, name)
        self.click(self.LOCATOR_MODEL_SEARCH_BTN)

    def select_first_model(self):
        """Memilih radio button tipe/model pertama di tabel."""
        radios = self.find_all(self.LOCATOR_MODEL_RADIOS)
        if radios:
            self.click_js(radios[0])
            self.dispatch_event(radios[0], "change")
            return True
        return False

    def is_model_update_btn_enabled(self):
        """Memeriksa apakah tombol Update tipe/model aktif."""
        return self.is_enabled(self.LOCATOR_MODEL_UPDATE_BTN)

    def is_model_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete tipe/model aktif."""
        return self.is_enabled(self.LOCATOR_MODEL_DELETE_BTN)

    # =========================================================================
    # 3. VEHICLE LIST / VEHICLE MANAGEMENT (/tCar)
    # =========================================================================
    LOCATOR_CAR_HEADING         = (By.TAG_NAME, "h1")
    LOCATOR_CAR_PLATE_INPUT     = (By.CSS_SELECTOR, "form[action='/tCar'] input[name='carLicensePlate']")
    LOCATOR_CAR_DRIVER_INPUT    = (By.CSS_SELECTOR, "form[action='/tCar'] input[name='driverName']")
    LOCATOR_CAR_BRAND_INPUT     = (By.CSS_SELECTOR, "form[action='/tCar'] input[name='brandName']")
    LOCATOR_CAR_MODEL_INPUT     = (By.CSS_SELECTOR, "form[action='/tCar'] input[name='modelName']")
    LOCATOR_CAR_COLOR_INPUT     = (By.CSS_SELECTOR, "form[action='/tCar'] input[name='carColor']")
    LOCATOR_CAR_SEARCH_BTN      = (By.CSS_SELECTOR, "form[action='/tCar'] button[type='submit']")
    LOCATOR_CAR_TABLE           = (By.TAG_NAME, "table")
    LOCATOR_CAR_ROWS            = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_CAR_RADIOS          = (By.CSS_SELECTOR, "input[name='selected-t-car']")
    LOCATOR_CAR_UPDATE_BTN      = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_CAR_DELETE_BTN      = (By.XPATH, "//button[normalize-space()='Delete']")
    LOCATOR_CAR_TEMPLATE_BTN    = (By.XPATH, "//button[normalize-space()='Template']")
    LOCATOR_CAR_IMPORT_BTN      = (By.XPATH, "//button[normalize-space()='Import']")
    LOCATOR_CAR_EXPORT_BTN      = (By.XPATH, "//button[normalize-space()='Export']")

    def navigate_car_list(self):
        """Buka halaman Vehicle Management (/tCar)."""
        self.open(Config.CAR_LIST_URL)

    def is_car_table_displayed(self):
        """Memeriksa apakah tabel Kendaraan tampil."""
        return self.is_displayed(self.LOCATOR_CAR_TABLE)

    def get_car_rows_count(self):
        """Menghitung baris data aktual pada tabel Kendaraan."""
        rows = self.find_all(self.LOCATOR_CAR_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def get_car_first_row_text(self):
        """Mengambil teks baris pertama pada tabel Kendaraan."""
        rows = self.find_all(self.LOCATOR_CAR_ROWS)
        return rows[0].text if rows else ""

    def search_car_by_plate(self, plate):
        """Mencari kendaraan berdasarkan plat nomor."""
        self.type_text(self.LOCATOR_CAR_PLATE_INPUT, plate)
        self.click(self.LOCATOR_CAR_SEARCH_BTN)

    def search_car_by_driver(self, driver_name):
        """Mencari kendaraan berdasarkan nama pengemudi."""
        self.type_text(self.LOCATOR_CAR_DRIVER_INPUT, driver_name)
        self.click(self.LOCATOR_CAR_SEARCH_BTN)

    def select_first_car(self):
        """Memilih radio button kendaraan pertama di tabel."""
        radios = self.find_all(self.LOCATOR_CAR_RADIOS)
        if radios:
            self.click_js(radios[0])
            self.dispatch_event(radios[0], "change")
            return True
        return False

    def is_car_update_btn_enabled(self):
        """Memeriksa apakah tombol Update kendaraan aktif."""
        return self.is_enabled(self.LOCATOR_CAR_UPDATE_BTN)

    def is_car_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete kendaraan aktif."""
        return self.is_enabled(self.LOCATOR_CAR_DELETE_BTN)

    def is_car_template_btn_displayed(self):
        """Memeriksa apakah tombol Template tampil."""
        return self.is_displayed(self.LOCATOR_CAR_TEMPLATE_BTN)

    def is_car_import_btn_displayed(self):
        """Memeriksa apakah tombol Import tampil."""
        return self.is_displayed(self.LOCATOR_CAR_IMPORT_BTN)

    def is_car_export_btn_displayed(self):
        """Memeriksa apakah tombol Export tampil."""
        return self.is_displayed(self.LOCATOR_CAR_EXPORT_BTN)

    # =========================================================================
    # 4. MOTORCYCLE MODEL SETTING (/tMotorModel)
    # =========================================================================
    LOCATOR_MOTOR_HEADING = (By.TAG_NAME, "h1")
    LOCATOR_MOTOR_TABLE   = (By.TAG_NAME, "table")
    LOCATOR_MOTOR_ROWS    = (By.CSS_SELECTOR, "table tbody tr")

    def navigate_motor_model(self):
        """Buka halaman Motorcycle model setting (/tMotorModel)."""
        self.open(Config.MOTOR_MODEL_URL)

    def is_motor_table_displayed(self):
        """Memeriksa apakah tabel model motor tampil."""
        return self.is_displayed(self.LOCATOR_MOTOR_TABLE)

    def get_motor_rows_count(self):
        """Menghitung jumlah baris data model motor."""
        return len(self.find_all(self.LOCATOR_MOTOR_ROWS))
