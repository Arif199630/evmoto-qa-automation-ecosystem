"""
=============================================================================
PAGE OBJECT: PRICE CONTROL MANAGEMENT (MODUL 25)
Target Endpoint :
1. Motorcycle Price Settings                  : /tSystemPrice/special
2. Intra-city Express Delivery Price Setting  : /tSystemPrice/small
3. Price Review Queue / List                 : /tSystemPrice/check
4. Add Special Car Price                      : /tSystemPrice/tSystemPrice_add
=============================================================================
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from pages.page_base import BasePage
from config import Config


class PricePage(BasePage):
    """Page Object Model untuk Modul Price Control beserta seluruh sub-halamannya."""

    def wait_for_page_ready(self, timeout=5):
        """Menunggu document.readyState bernilai complete."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass

    def type(self, locator, text, clear_first=True):
        """Helper alias untuk type_text."""
        return self.type_text(locator, text, clear_first=clear_first)

    # =========================================================================
    # LOCATORS: Motorcycle Price Settings (/tSystemPrice/special)
    # =========================================================================
    LOCATOR_SPECIAL_SEARCH_INPUT   = (By.CSS_SELECTOR, "input[name='name']")
    LOCATOR_SPECIAL_STATE_SELECT   = (By.CSS_SELECTOR, "select[name='state']")
    LOCATOR_SPECIAL_SEARCH_BTN     = (By.XPATH, "//button[contains(text(), 'Search')] | //button[@type='submit' and contains(., 'Search')]")
    LOCATOR_SPECIAL_ADD_BTN        = (By.XPATH, "//a[contains(@href, 'tSystemPrice_add') and contains(text(), 'Add')] | //main//a[contains(text(), 'Add')]")
    LOCATOR_SPECIAL_UPDATE_BTN     = (By.XPATH, "//button[contains(text(), 'Update')]")
    LOCATOR_SPECIAL_DELETE_BTN     = (By.XPATH, "//button[contains(text(), 'Delete')]")
    LOCATOR_SPECIAL_FREEZE_BTN     = (By.XPATH, "//button[contains(text(), 'Freeze')]")
    LOCATOR_SPECIAL_UNFREEZE_BTN   = (By.XPATH, "//button[contains(text(), 'Unfreeze')]")
    LOCATOR_SPECIAL_TABLE_HEADERS  = (By.CSS_SELECTOR, "table thead th")
    LOCATOR_SPECIAL_TABLE_ROWS     = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_SPECIAL_RADIO          = (By.CSS_SELECTOR, "input[name='selected-price']")

    # =========================================================================
    # LOCATORS: Intra-city Express Delivery Price Setting (/tSystemPrice/small)
    # =========================================================================
    LOCATOR_SMALL_USER_TYPE_RADIO  = (By.CSS_SELECTOR, "input[name='userType']")
    LOCATOR_SMALL_CITY_SELECT      = (By.CSS_SELECTOR, "select[name='openCityId']")
    LOCATOR_SMALL_NUM1             = (By.CSS_SELECTOR, "input[name='num1']")
    LOCATOR_SMALL_NUM2             = (By.CSS_SELECTOR, "input[name='num2']")
    LOCATOR_SMALL_NUM3             = (By.CSS_SELECTOR, "input[name='num3']")
    LOCATOR_SMALL_NUM4             = (By.CSS_SELECTOR, "input[name='num4']")
    LOCATOR_SMALL_NIGHT_TIME       = (By.CSS_SELECTOR, "input[name='nightTime']")
    LOCATOR_SMALL_NIGHT_START      = (By.CSS_SELECTOR, "input[name='nightStart']")
    LOCATOR_SMALL_CANCEL_BTN       = (By.XPATH, "//a[contains(@href, 'check') and normalize-space(.)='Cancel']")
    LOCATOR_SMALL_SUBMIT_BTN       = (By.XPATH, "//button[contains(text(), 'Submit')]")

    # =========================================================================
    # LOCATORS: Price Review Queue (/tSystemPrice/check)
    # =========================================================================
    LOCATOR_CHECK_BEGIN_DATE       = (By.CSS_SELECTOR, "input[name='beginDate']")
    LOCATOR_CHECK_END_DATE         = (By.CSS_SELECTOR, "input[name='endDate']")
    LOCATOR_CHECK_COMPANY          = (By.CSS_SELECTOR, "input[name='company']")
    LOCATOR_CHECK_PHONE            = (By.CSS_SELECTOR, "input[name='phone']")
    LOCATOR_CHECK_ACCOUNT          = (By.CSS_SELECTOR, "input[name='account']")
    LOCATOR_CHECK_STATE_SELECT     = (By.CSS_SELECTOR, "select[name='state']")
    LOCATOR_CHECK_SEARCH_BTN       = (By.XPATH, "//button[contains(text(), 'Search')] | //button[@type='submit' and contains(., 'Search')]")
    LOCATOR_CHECK_RESET_BTN        = (By.XPATH, "//a[contains(text(), 'Reset')]")
    LOCATOR_CHECK_AUDIT_BTN        = (By.XPATH, "//button[contains(text(), 'Audit')]")
    LOCATOR_CHECK_DETAILS_BTN      = (By.XPATH, "//button[contains(text(), 'Details')]")
    LOCATOR_CHECK_DELETE_BTN       = (By.XPATH, "//button[contains(text(), 'Delete')]")
    LOCATOR_CHECK_TABLE_HEADERS    = (By.CSS_SELECTOR, "table thead th")
    LOCATOR_CHECK_TABLE_ROWS       = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_CHECK_RADIO            = (By.CSS_SELECTOR, "input[name='selected-check']")

    # =========================================================================
    # LOCATORS: Add Special Car Price (/tSystemPrice/tSystemPrice_add)
    # =========================================================================
    LOCATOR_ADD_USER_TYPE_RADIO    = (By.CSS_SELECTOR, "input[name='userType']")
    LOCATOR_ADD_MODEL_SELECT       = (By.CSS_SELECTOR, "select[name='serverCarModelId']")
    LOCATOR_ADD_CITY_SELECT        = (By.CSS_SELECTOR, "select[name='openCityId']")
    LOCATOR_ADD_START_PRICE        = (By.CSS_SELECTOR, "input[name='startPrice']")
    LOCATOR_ADD_START_KM           = (By.CSS_SELECTOR, "input[name='startKm']")
    LOCATOR_ADD_MILEAGE_FEE        = (By.CSS_SELECTOR, "input[name='mileageFee']")
    LOCATOR_ADD_SUBMIT_BTN         = (By.XPATH, "//button[contains(text(), 'Submit')]")
    LOCATOR_ADD_CANCEL_BTN         = (By.XPATH, "//a[contains(@href, 'special') and normalize-space(.)='Cancel']")

    # =========================================================================
    # NAVIGATION METHODS
    # =========================================================================
    def open_special_price(self):
        """Membuka halaman Motorcycle Price Settings (/tSystemPrice/special)."""
        self.open(Config.PRICE_SPECIAL_URL)
        self.wait_for_page_ready()
        time.sleep(0.5)

    def open_small_price(self):
        """Membuka halaman Intra-city Express Delivery Price Setting (/tSystemPrice/small)."""
        self.open(Config.PRICE_SMALL_URL)
        self.wait_for_page_ready()
        time.sleep(0.5)

    def open_check_price(self):
        """Membuka halaman Price Review Queue (/tSystemPrice/check)."""
        self.open(Config.PRICE_CHECK_URL)
        self.wait_for_page_ready()
        time.sleep(0.5)

    def open_add_special_price(self):
        """Membuka sub-halaman Add Special Car Price (/tSystemPrice/tSystemPrice_add)."""
        self.open(Config.PRICE_SPECIAL_ADD_URL)
        self.wait_for_page_ready()
        time.sleep(0.5)

    # =========================================================================
    # MOTORCYCLE PRICE SETTING INTERACTION METHODS
    # =========================================================================
    def search_special(self, name="", state=""):
        """Melakukan pencarian pada tabel Motorcycle Price."""
        if name:
            self.type(self.LOCATOR_SPECIAL_SEARCH_INPUT, name)
        if state:
            elem = self.find(self.LOCATOR_SPECIAL_STATE_SELECT)
            select = Select(elem)
            select.select_by_visible_text(state)
        self.click(self.LOCATOR_SPECIAL_SEARCH_BTN)
        self.wait_for_page_ready()
        time.sleep(0.5)

    def get_special_headers(self):
        """Mengambil teks seluruh kolom header tabel Motorcycle Price."""
        elements = self.find_all(self.LOCATOR_SPECIAL_TABLE_HEADERS)
        return [el.text.strip() for el in elements if el.text.strip()]

    def get_special_rows_count(self):
        """Mengambil jumlah baris data tabel Motorcycle Price."""
        elements = self.find_all(self.LOCATOR_SPECIAL_TABLE_ROWS)
        return len(elements)

    def click_special_add(self):
        """Mengklik tombol Add pada Motorcycle Price Settings."""
        self.click(self.LOCATOR_SPECIAL_ADD_BTN)
        self.wait_for_page_ready()
        time.sleep(0.5)

    def is_special_update_disabled(self):
        """Mengecek apakah tombol Update terkunci aman (disabled)."""
        btn = self.find(self.LOCATOR_SPECIAL_UPDATE_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") is not None

    def is_special_delete_disabled(self):
        """Mengecek apakah tombol Delete terkunci aman (disabled)."""
        btn = self.find(self.LOCATOR_SPECIAL_DELETE_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") is not None

    def is_special_freeze_disabled(self):
        """Mengecek apakah tombol Freeze terkunci aman (disabled)."""
        btn = self.find(self.LOCATOR_SPECIAL_FREEZE_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") is not None

    def is_special_unfreeze_disabled(self):
        """Mengecek apakah tombol Unfreeze terkunci aman (disabled)."""
        btn = self.find(self.LOCATOR_SPECIAL_UNFREEZE_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") is not None

    # =========================================================================
    # INTRA-CITY EXPRESS DELIVERY PRICE SETTING METHODS
    # =========================================================================
    def is_small_form_displayed(self):
        """Memverifikasi form Intra-city express delivery tampil lengkap."""
        return (self.is_displayed(self.LOCATOR_SMALL_CITY_SELECT) and
                self.is_displayed(self.LOCATOR_SMALL_NUM1) and
                self.is_displayed(self.LOCATOR_SMALL_SUBMIT_BTN))

    def click_small_cancel(self):
        """Mengklik tombol Cancel pada form Intra-city express delivery."""
        btn = self.find(self.LOCATOR_SMALL_CANCEL_BTN)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        self.click_js(btn)
        self.wait_for_page_ready()
        time.sleep(0.5)

    # =========================================================================
    # PRICE REVIEW QUEUE METHODS
    # =========================================================================
    def search_check(self, company="", phone="", account="", state=""):
        """Melakukan filter pada Price Review Queue."""
        if company:
            self.type(self.LOCATOR_CHECK_COMPANY, company)
        if phone:
            self.type(self.LOCATOR_CHECK_PHONE, phone)
        if account:
            self.type(self.LOCATOR_CHECK_ACCOUNT, account)
        if state:
            elem = self.find(self.LOCATOR_CHECK_STATE_SELECT)
            select = Select(elem)
            select.select_by_visible_text(state)
        self.click(self.LOCATOR_CHECK_SEARCH_BTN)
        self.wait_for_page_ready()
        time.sleep(0.5)

    def click_check_reset(self):
        """Mengklik tombol Reset pada Price Review Queue."""
        self.click(self.LOCATOR_CHECK_RESET_BTN)
        self.wait_for_page_ready()
        time.sleep(0.5)

    def get_check_headers(self):
        """Mengambil teks header tabel Price Review Queue."""
        elements = self.find_all(self.LOCATOR_CHECK_TABLE_HEADERS)
        return [el.text.strip() for el in elements if el.text.strip()]

    def get_check_rows_count(self):
        """Mengambil jumlah baris data Price Review Queue."""
        elements = self.find_all(self.LOCATOR_CHECK_TABLE_ROWS)
        return len(elements)

    def is_check_audit_disabled(self):
        """Mengecek apakah tombol Audit terkunci aman (disabled)."""
        btn = self.find(self.LOCATOR_CHECK_AUDIT_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") is not None

    def is_check_details_disabled(self):
        """Mengecek apakah tombol Details terkunci aman (disabled)."""
        btn = self.find(self.LOCATOR_CHECK_DETAILS_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") is not None

    def is_check_delete_disabled(self):
        """Mengecek apakah tombol Delete terkunci aman (disabled)."""
        btn = self.find(self.LOCATOR_CHECK_DELETE_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") is not None

    # =========================================================================
    # ADD SPECIAL CAR PRICE FORM METHODS
    # =========================================================================
    def is_add_form_displayed(self):
        """Memverifikasi form Add special car price tampil lengkap."""
        return (self.is_displayed(self.LOCATOR_ADD_MODEL_SELECT) and
                self.is_displayed(self.LOCATOR_ADD_CITY_SELECT) and
                self.is_displayed(self.LOCATOR_ADD_START_PRICE) and
                self.is_displayed(self.LOCATOR_ADD_SUBMIT_BTN))

    def click_add_cancel(self):
        """Mengklik tombol Cancel pada form Add special car price."""
        btn = self.find(self.LOCATOR_ADD_CANCEL_BTN)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        self.click_js(btn)
        self.wait_for_page_ready()
        time.sleep(0.5)
