"""
Vehicle Model Setting Page Object
Website: <BASE_URL>/tMotorModel
Sub-Halaman: <BASE_URL>/tMotorModel/tMotorModel_add
Automation Project EvMoto
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .page_base import BasePage
from config import Config


class VehicleModelPage(BasePage):
    """Page Object untuk Halaman Vehicle Model Setting dan Sub-Halamannya."""

    # =========================================================================
    # LOCATORS - HALAMAN UTAMA (/tMotorModel)
    # =========================================================================
    LOCATOR_SELECT_YY          = (By.CSS_SELECTOR, "select[name='yy']")
    LOCATOR_SEARCH_BTN         = (By.XPATH, "//button[contains(., 'Search') and @type='submit']")
    LOCATOR_RESET_LINK         = (By.XPATH, "//a[contains(@href, '/tMotorModel') and contains(text(), 'Reset')]")
    LOCATOR_ADD_LINK           = (By.XPATH, "//a[contains(@href, 'tMotorModel_add') and contains(text(), 'Add')]")
    LOCATOR_TABLE_HEADERS      = (By.CSS_SELECTOR, "table thead th")
    LOCATOR_TABLE_ROWS         = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_DISABLE_BTNS       = (By.XPATH, "//button[contains(., 'disable')]")
    LOCATOR_TOAST              = (By.CSS_SELECTOR, "[data-toast], .toast, .alert, .notification, [role='alert']")

    # =========================================================================
    # LOCATORS - SUB-HALAMAN ADD (/tMotorModel/tMotorModel_add)
    # =========================================================================
    LOCATOR_ADD_INPUT_NAME     = (By.CSS_SELECTOR, "input[name='name']")
    LOCATOR_ADD_INPUT_ENAME    = (By.CSS_SELECTOR, "input[name='ename']")
    LOCATOR_ADD_INPUT_YNAME    = (By.CSS_SELECTOR, "input[name='yname']")
    LOCATOR_ADD_INPUT_FILE     = (By.CSS_SELECTOR, "input[type='file'], #tmm-file")
    LOCATOR_ADD_SELECT_LANG    = (By.CSS_SELECTOR, "select[name='language']")
    LOCATOR_ADD_SUBMIT_BTN     = (By.XPATH, "//button[contains(., 'Submit')]")
    LOCATOR_ADD_CANCEL_LINK    = (By.XPATH, "//a[contains(@href, 'tMotorModel') and contains(text(), 'Cancel')]")

    # =========================================================================
    # NAVIGATION METHODS
    # =========================================================================
    def open_model_setting(self):
        """Buka halaman utama Motorcycle model setting."""
        self.open(Config.MOTOR_MODEL_URL)

    def open_model_setting_add(self):
        """Buka sub-halaman tambah Motorcycle model setting."""
        self.open(Config.MOTOR_MODEL_ADD_URL)

    # =========================================================================
    # FILTER & SEARCH METHODS
    # =========================================================================
    def filter_by_language(self, language_text):
        """Filter data model kendaraan berdasarkan pilihan bahasa."""
        select_elem = Select(self.find(self.LOCATOR_SELECT_YY))
        select_elem.select_by_visible_text(language_text)
        self.click(self.LOCATOR_SEARCH_BTN)
        time.sleep(0.5)

    def click_reset(self):
        """Klik tombol Reset untuk mengembalikan filter ke kondisi default."""
        self.click(self.LOCATOR_RESET_LINK)
        time.sleep(0.5)

    def click_add(self):
        """Klik tombol Add untuk menuju sub-halaman tambah model motor."""
        self.click(self.LOCATOR_ADD_LINK)
        time.sleep(0.5)

    # =========================================================================
    # TABLE DATA METHODS
    # =========================================================================
    def get_table_headers(self):
        """Mengambil teks seluruh header kolom tabel aktif."""
        elements = self.find_all(self.LOCATOR_TABLE_HEADERS)
        return [el.text.strip() for el in elements if el.text.strip()]

    def get_table_rows_count(self):
        """Mengambil jumlah baris data yang ada pada tabel."""
        rows = self.find_all(self.LOCATOR_TABLE_ROWS)
        return len(rows)

    def get_disable_buttons_count(self):
        """Mengambil jumlah tombol disable pada baris data tabel."""
        btns = self.find_all(self.LOCATOR_DISABLE_BTNS)
        return len(btns)

    # =========================================================================
    # SUBPAGE ADD FORM METHODS
    # =========================================================================
    def is_add_form_displayed(self):
        """Memeriksa apakah formulir tambah model tampil di layar."""
        return (self.is_displayed(self.LOCATOR_ADD_INPUT_NAME) and
                self.is_displayed(self.LOCATOR_ADD_SUBMIT_BTN))

    def fill_add_form(self, name=None, ename=None, yname=None, language=None):
        """Mengisi kolom-kolom input formulir tambah model motor."""
        if name is not None:
            self.type_text(self.LOCATOR_ADD_INPUT_NAME, name)
        if ename is not None:
            self.type_text(self.LOCATOR_ADD_INPUT_ENAME, ename)
        if yname is not None:
            self.type_text(self.LOCATOR_ADD_INPUT_YNAME, yname)
        if language is not None:
            select = Select(self.find(self.LOCATOR_ADD_SELECT_LANG))
            select.select_by_visible_text(language)

    def click_add_cancel(self):
        """Klik tombol Cancel pada formulir tambah model."""
        self.click(self.LOCATOR_ADD_CANCEL_LINK)
        time.sleep(0.5)

    def click_add_submit(self):
        """Klik tombol Submit pada formulir tambah model."""
        self.click(self.LOCATOR_ADD_SUBMIT_BTN)
        time.sleep(0.5)
