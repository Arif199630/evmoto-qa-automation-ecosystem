"""
Urban Management Page Object
Website:
 - Urban Management              : <BASE_URL>/tOpenCity
 - City search address settings  : <BASE_URL>/THotAddress
 - Service Area                  : <BASE_URL>/service-area
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class UrbanPage(BasePage):
    """Page Object untuk Halaman Opening Up Urban Management & Seluruh Sub-Halamannya."""

    # Locators Urban Management (/tOpenCity)
    LOCATOR_CITY_FORM           = (By.CSS_SELECTOR, "form[action='/tOpenCity']")
    LOCATOR_CITY_NAME_INPUT     = (By.ID, "open-city-name")
    LOCATOR_CITY_TABLE          = (By.TAG_NAME, "table")
    LOCATOR_CITY_TABLE_ROWS     = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_CITY_RADIOS         = (By.CSS_SELECTOR, "[data-open-city-choice]")
    LOCATOR_CITY_EDIT_BTN       = (By.CSS_SELECTOR, "[data-open-city-edit]")
    LOCATOR_CITY_DELETE_BTN     = (By.CSS_SELECTOR, "[data-open-city-delete]")
    LOCATOR_CITY_AUDIT_BTN      = (By.CSS_SELECTOR, "[data-open-city-audit]")

    # Locators City Search Address Settings (/THotAddress)
    LOCATOR_HOT_ADDR_FORM       = (By.CSS_SELECTOR, "form[action='/THotAddress']")
    LOCATOR_HOT_ADDR_INPUT      = (By.CSS_SELECTOR, "form[action='/THotAddress'] input[name='name']")
    LOCATOR_HOT_ADDR_TABLE      = (By.TAG_NAME, "table")
    LOCATOR_HOT_ADDR_TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_HOT_ADDR_RADIOS     = (By.CSS_SELECTOR, "[data-hot-address-choice]")
    LOCATOR_HOT_ADDR_EDIT_BTN   = (By.CSS_SELECTOR, "[data-hot-address-edit]")
    LOCATOR_HOT_ADDR_DELETE_BTN = (By.CSS_SELECTOR, "[data-hot-address-delete]")

    # Locators Service Area
    LOCATOR_SIDEBAR_SERVICE_LINK = (
        By.XPATH,
        "//a[contains(@href, '/tOpenCity') or contains(@href, '/service-area') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'urban')]"
    )

    # --- 1. Urban Management (/tOpenCity) ---
    def navigate_open_city(self):
        """Buka halaman Urban Management."""
        self.open(Config.OPEN_CITY_URL)

    def get_open_city_heading_text(self):
        """Ambil heading h1 Urban Management."""
        return self.get_text((By.CSS_SELECTOR, "h1"))

    def is_city_table_displayed(self):
        """Periksa apakah tabel kota tampil."""
        return self.is_displayed(self.LOCATOR_CITY_TABLE)

    def is_city_edit_btn_enabled(self):
        """Periksa apakah tombol Update kota aktif."""
        return self.is_enabled(self.LOCATOR_CITY_EDIT_BTN)

    def is_city_delete_btn_enabled(self):
        """Periksa apakah tombol Delete kota aktif."""
        return self.is_enabled(self.LOCATOR_CITY_DELETE_BTN)

    def get_city_rows_count(self):
        """Ambil jumlah baris data kota."""
        return len(self.find_all(self.LOCATOR_CITY_TABLE_ROWS))

    def get_city_first_row_text(self):
        """Mengambil teks baris pertama tabel kota."""
        rows = self.find_all(self.LOCATOR_CITY_TABLE_ROWS)
        return rows[0].text if rows else ""

    def search_city_by_name(self, name):
        """Filter data kota berdasarkan nama."""
        self.type_text(self.LOCATOR_CITY_NAME_INPUT, name)
        form = self.find(self.LOCATOR_CITY_FORM)
        form.submit()

    def filter_city_by_date_and_name(self, begin_date, end_date, name):
        """Filter kombinasi rentang tanggal dan nama kota."""
        form = self.find(self.LOCATOR_CITY_FORM)
        begin_input = form.find_element(By.CSS_SELECTOR, "input[name='beginDate']")
        end_input = form.find_element(By.CSS_SELECTOR, "input[name='endDate']")
        self.set_value_js(begin_input, begin_date)
        self.set_value_js(end_input, end_date)

        city_input = form.find_element(By.CSS_SELECTOR, "input[name='name']")
        city_input.clear()
        city_input.send_keys(name)
        form.submit()

    def select_first_city(self):
        """Pilih radio button kota pertama."""
        radios = self.find_all(self.LOCATOR_CITY_RADIOS)
        if radios:
            self.click_js(radios[0])
            self.dispatch_event(radios[0], "change")
            return True
        return False

    def get_city_radios_count(self):
        """Ambil jumlah radio kota di tabel."""
        return len(self.find_all(self.LOCATOR_CITY_RADIOS))

    # --- 2. City Search Address Settings (/THotAddress) ---
    def navigate_hot_address(self):
        """Buka halaman City search address settings."""
        self.open(Config.HOT_ADDRESS_URL)

    def get_hot_address_heading_text(self):
        """Ambil heading h1 Hot Address."""
        return self.get_text((By.CSS_SELECTOR, "h1"))

    def is_hot_address_table_displayed(self):
        """Periksa apakah tabel alamat tampil."""
        return self.is_displayed(self.LOCATOR_HOT_ADDR_TABLE)

    def is_hot_address_edit_btn_enabled(self):
        """Periksa apakah tombol Update alamat aktif."""
        return self.is_enabled(self.LOCATOR_HOT_ADDR_EDIT_BTN)

    def is_hot_address_delete_btn_enabled(self):
        """Periksa apakah tombol Delete alamat aktif."""
        return self.is_enabled(self.LOCATOR_HOT_ADDR_DELETE_BTN)

    def get_hot_address_rows_count(self):
        """Ambil jumlah baris data alamat."""
        return len(self.find_all(self.LOCATOR_HOT_ADDR_TABLE_ROWS))

    def get_hot_address_first_row_text(self):
        """Mengambil teks baris pertama tabel alamat."""
        rows = self.find_all(self.LOCATOR_HOT_ADDR_TABLE_ROWS)
        return rows[0].text if rows else ""

    def search_address_by_name(self, name):
        """Cari alamat berdasarkan nama."""
        self.type_text(self.LOCATOR_HOT_ADDR_INPUT, name)
        form = self.find(self.LOCATOR_HOT_ADDR_FORM)
        form.submit()

    def select_first_address(self):
        """Pilih radio button alamat pertama."""
        radios = self.find_all(self.LOCATOR_HOT_ADDR_RADIOS)
        if radios:
            self.click_js(radios[0])
            self.dispatch_event(radios[0], "change")
            return True
        return False

    def get_hot_address_radios_count(self):
        """Ambil jumlah radio alamat di tabel."""
        return len(self.find_all(self.LOCATOR_HOT_ADDR_RADIOS))

    # --- 3. Service Area (/service-area) ---
    def navigate_service_area(self):
        """Buka halaman Service Area langsung."""
        self.open(Config.SERVICE_AREA_URL)

    def get_sidebar_service_area_link(self):
        """Mengambil elemen tautan Service Area di sidebar navigasi."""
        return self.find(self.LOCATOR_SIDEBAR_SERVICE_LINK)
