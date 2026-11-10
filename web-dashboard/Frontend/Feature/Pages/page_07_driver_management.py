"""
Driver Management Page Object
Website: <BASE_URL>/tDriver & Sub-Halamannya
Sub-Halaman:
  1. Driver Audit list (/tDriver)
  2. Driver Replacement Vehicle audit list management (/tDriverVerify)
  3. Driver's list (/tDriver/yesDriver)
  4. Driver Withholding Details (/tDriver/without)
Automation Project EvMoto
"""

import time
from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class DriverPage(BasePage):
    """Page Object untuk Modul Driver Management dan 4 sub-halamannya."""

    # Locators Sub 1: Driver Audit list (/tDriver)
    LOCATOR_AUDIT_FORM            = (By.CSS_SELECTOR, "form[action*='/tDriver']")
    LOCATOR_AUDIT_PHONE_INP       = (By.CSS_SELECTOR, "form[action*='/tDriver'] input[name='phone']")
    LOCATOR_AUDIT_ACCOUNT_INP     = (By.CSS_SELECTOR, "form[action*='/tDriver'] input[name='account']")
    LOCATOR_AUDIT_BEGIN_TIME      = (By.CSS_SELECTOR, "form[action*='/tDriver'] input[name='beginTime']")
    LOCATOR_AUDIT_END_TIME        = (By.CSS_SELECTOR, "form[action*='/tDriver'] input[name='endTime']")
    LOCATOR_AUDIT_TABLE           = (By.TAG_NAME, "table")
    LOCATOR_AUDIT_ROWS            = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_AUDIT_RADIOS          = (By.CSS_SELECTOR, "[data-t-driver-choice]")
    LOCATOR_AUDIT_ACTION_BTN      = (By.CSS_SELECTOR, "[data-t-driver-audit]")

    # Locators Sub 2: Driver Replacement Vehicle Audit List (/tDriverVerify)
    LOCATOR_VERIFY_FORM           = (By.CSS_SELECTOR, "form[action*='/tDriverVerify']")
    LOCATOR_VERIFY_PHONE_INP      = (By.CSS_SELECTOR, "form[action*='/tDriverVerify'] input[name='phone']")
    LOCATOR_VERIFY_TABLE          = (By.TAG_NAME, "table")
    LOCATOR_VERIFY_ROWS           = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_VERIFY_RADIOS         = (By.CSS_SELECTOR, "[data-t-driver-verify-choice]")
    LOCATOR_VERIFY_ACTION_BTN     = (By.CSS_SELECTOR, "[data-t-driver-verify-audit]")

    # Locators Sub 3: Drivers' List (/tDriver/yesDriver)
    LOCATOR_LIST_FORM             = (By.CSS_SELECTOR, "form[action*='/tDriver/yesDriver']")
    LOCATOR_LIST_NAME_INP         = (By.CSS_SELECTOR, "form[action*='/tDriver/yesDriver'] input[name='name']")
    LOCATOR_LIST_PHONE_INP        = (By.CSS_SELECTOR, "form[action*='/tDriver/yesDriver'] input[name='phone']")
    LOCATOR_LIST_TABLE            = (By.TAG_NAME, "table")
    LOCATOR_LIST_ROWS             = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_LIST_RADIOS           = (By.CSS_SELECTOR, "[data-yes-driver-choice]")
    LOCATOR_LIST_ADD_BTN          = (By.CSS_SELECTOR, "[data-yes-driver-add]")

    # Locators Sub 4: Driver Withholding Details (/tDriver/without)
    LOCATOR_WITHHOLDING_FORM      = (By.CSS_SELECTOR, "form[action*='/tDriver/without']")
    LOCATOR_WITHHOLDING_NAME_INP  = (By.CSS_SELECTOR, "form[action*='/tDriver/without'] input[name='name']")
    LOCATOR_WITHHOLDING_PHONE_INP = (By.CSS_SELECTOR, "form[action*='/tDriver/without'] input[name='phone']")
    LOCATOR_WITHHOLDING_TABLE     = (By.TAG_NAME, "table")
    LOCATOR_WITHHOLDING_ROWS      = (By.CSS_SELECTOR, "table tbody tr")

    # =========================================================================
    # SUB-HALAMAN 1: DRIVER AUDIT LIST (/tDriver)
    # =========================================================================
    def navigate_audit(self):
        """Buka halaman Driver Audit List."""
        self.open(Config.DRIVER_AUDIT_URL)

    def get_audit_rows_count(self):
        """Ambil jumlah baris data driver audit."""
        return len(self.find_all(self.LOCATOR_AUDIT_ROWS))

    def is_audit_action_btn_disabled(self):
        """Periksa apakah tombol 'Audit now' berstatus disabled."""
        btn = self.find(self.LOCATOR_AUDIT_ACTION_BTN)
        return btn.get_attribute("disabled") is not None

    def search_audit_by_phone(self, phone):
        """Filter pencarian nomor telepon pada Driver Audit List."""
        self.type_text(self.LOCATOR_AUDIT_PHONE_INP, phone)
        form = self.find(self.LOCATOR_AUDIT_FORM)
        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()

    def filter_audit_by_date_range(self, begin_time, end_time):
        """Filter rentang tanggal pada Driver Audit List."""
        begin_input = self.find(self.LOCATOR_AUDIT_BEGIN_TIME)
        end_input = self.find(self.LOCATOR_AUDIT_END_TIME)
        self.set_value_js(begin_input, begin_time)
        self.set_value_js(end_input, end_time)

        form = self.find(self.LOCATOR_AUDIT_FORM)
        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()

    def select_first_audit_radio(self):
        """Pilih radio button driver audit pertama."""
        radios = self.find_all(self.LOCATOR_AUDIT_RADIOS)
        if radios:
            self.click_js(radios[0])
            self.dispatch_event(radios[0], "change")
            time.sleep(1)
            return True
        return False

    # =========================================================================
    # SUB-HALAMAN 2: DRIVER REPLACEMENT VEHICLE AUDIT LIST (/tDriverVerify)
    # =========================================================================
    def navigate_verify(self):
        """Buka halaman Driver Replacement Vehicle Audit List."""
        self.open(Config.DRIVER_VERIFY_URL)

    def get_verify_rows_count(self):
        """Ambil jumlah baris data replacement audit."""
        return len(self.find_all(self.LOCATOR_VERIFY_ROWS))

    def is_verify_action_btn_disabled(self):
        """Periksa apakah tombol audit replacement vehicle disabled."""
        btn = self.find(self.LOCATOR_VERIFY_ACTION_BTN)
        return btn.get_attribute("disabled") is not None

    def search_verify_by_phone(self, phone):
        """Filter nomor telepon pada replacement vehicle audit."""
        self.type_text(self.LOCATOR_VERIFY_PHONE_INP, phone)
        form = self.find(self.LOCATOR_VERIFY_FORM)
        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()

    def select_first_verify_radio(self):
        """Pilih radio baris replacement audit pertama."""
        radios = self.find_all(self.LOCATOR_VERIFY_RADIOS)
        if radios:
            first_radio = radios[0]
            val = first_radio.get_attribute("value")
            self.click_js(first_radio)
            self.dispatch_event(first_radio, "change")
            time.sleep(1)
            return val, first_radio.is_selected()
        return None, False

    # =========================================================================
    # SUB-HALAMAN 3: DRIVERS' LIST (/tDriver/yesDriver)
    # =========================================================================
    def navigate_driver_list(self):
        """Buka halaman Drivers' List."""
        self.open(Config.DRIVER_LIST_URL)

    def get_driver_list_rows_count(self):
        """Ambil jumlah baris data driver list."""
        return len(self.find_all(self.LOCATOR_LIST_ROWS))

    def is_add_driver_btn_displayed(self):
        """Periksa apakah tombol 'Add driver' tampil."""
        return self.is_displayed(self.LOCATOR_LIST_ADD_BTN)

    def search_driver_by_name(self, name):
        """Cari driver berdasarkan nama."""
        self.type_text(self.LOCATOR_LIST_NAME_INP, name)
        form = self.find(self.LOCATOR_LIST_FORM)
        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()

    def search_driver_by_phone(self, phone):
        """Cari driver berdasarkan nomor telepon."""
        self.type_text(self.LOCATOR_LIST_PHONE_INP, phone)
        form = self.find(self.LOCATOR_LIST_FORM)
        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()

    def select_first_driver_radio(self):
        """Pilih radio driver pertama."""
        radios = self.find_all(self.LOCATOR_LIST_RADIOS)
        if radios:
            first_radio = radios[0]
            driver_name = first_radio.get_attribute("data-yes-driver-name") or "Driver"
            self.click_js(first_radio)
            self.dispatch_event(first_radio, "change")
            time.sleep(1)
            return driver_name, first_radio.is_selected()
        return None, False

    # =========================================================================
    # SUB-HALAMAN 4: DRIVER WITHHOLDING DETAILS (/tDriver/without)
    # =========================================================================
    def navigate_withholding(self):
        """Buka halaman Driver Withholding Details."""
        self.open(Config.DRIVER_WITHHOLDING_URL)

    def is_withholding_name_input_displayed(self):
        """Periksa apakah input nama driver tampil."""
        return self.is_displayed(self.LOCATOR_WITHHOLDING_NAME_INP)

    def is_withholding_phone_input_displayed(self):
        """Periksa apakah input telepon driver tampil."""
        return self.is_displayed(self.LOCATOR_WITHHOLDING_PHONE_INP)

    def get_withholding_table_headers(self):
        """Mengambil nama header kolom tabel Withholding."""
        table = self.find(self.LOCATOR_WITHHOLDING_TABLE)
        return [th.text.strip().upper() for th in table.find_elements(By.TAG_NAME, "th") if th.text.strip()]

    def search_withholding_by_name(self, name):
        """Cari data withholding berdasarkan nama driver."""
        self.type_text(self.LOCATOR_WITHHOLDING_NAME_INP, name)
        form = self.find(self.LOCATOR_WITHHOLDING_FORM)
        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()

    def search_withholding_by_phone(self, phone):
        """Cari data withholding berdasarkan nomor telepon."""
        self.type_text(self.LOCATOR_WITHHOLDING_PHONE_INP, phone)
        form = self.find(self.LOCATOR_WITHHOLDING_FORM)
        submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()
