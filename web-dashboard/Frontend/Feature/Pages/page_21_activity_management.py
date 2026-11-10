"""
Activity Management Page Object
Website: <BASE_URL>/driverActivity & Sub-Halamannya
Sub-Halaman:
  1. Driver Activity Management (/driverActivity) & Add (/driverActivity/driverActivity_add)
  2. Gift Activity Management (/sysCouponActivity) & Add (/sysCouponActivity/sysCouponActivity_add)
  3. User Activity Management (/userActivity) & Add (/userActivity/userActivity_add)
  4. Large Coupon Activities (/tUserLarge) & Add (/tUserLarge/tUserLarge_add)
  5. Driver Guaranteed Income (/tEnsureIncomeRule) & Add (/tEnsureIncomeRule/tEnsureIncomeRule_add)
  6. Coupon Distribution (/couponDistribution) & Add (/couponDistribution/couponDistribution_add)
  7. Coupon Usage (/couponUsage)
  8. Coupon Record Management (/sysCouponRecord) & Add (/sysCouponRecord/sysCouponRecord_add)
Automation Project EvMoto
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .page_base import BasePage
from config import Config


class ActivityPage(BasePage):
    """Page Object untuk Modul Activity Management dan seluruh sub-halamannya."""

    # =========================================================================
    # LOCATORS - GLOBAL NAVBAR & PROFILE DROPDOWN
    # =========================================================================
    LOCATOR_PROFILE_TRIGGER    = (By.XPATH, "//button[contains(., 'Admin eVMOTO')] | //a[contains(., 'Admin eVMOTO')]")
    LOCATOR_PROFILE_DROPDOWN   = (By.CSS_SELECTOR, ".dropdown-menu, ul.dropdown-menu")
    LOCATOR_PROFILE_NAME_ROLE  = (By.XPATH, "//*[contains(text(), 'Admin eVMOTO')]/following-sibling::*[contains(text(), 'Administrator')] | //*[contains(text(), 'Administrator')]")
    LOCATOR_EDIT_PROFILE_BTN   = (By.XPATH, "//a[contains(text(), 'Edit Profil') or contains(text(), 'Edit Profile')] | //button[contains(text(), 'Edit Profil')]")
    LOCATOR_EDIT_PASSWORD_BTN  = (By.XPATH, "//a[contains(text(), 'Edit Password') or contains(text(), 'Ubah Password')] | //button[contains(text(), 'Edit Password')]")
    LOCATOR_LOGOUT_BTN         = (By.XPATH, "//a[contains(text(), 'Keluar') or contains(text(), 'Logout')] | //button[contains(text(), 'Keluar')]")
    LOCATOR_TOAST_FEEDBACK     = (By.CSS_SELECTOR, ".toast, .alert, .notification, [role='alert'], .layui-layer-msg")

    # =========================================================================
    # LOCATORS - DRIVER ACTIVITY (/driverActivity)
    # =========================================================================
    LOCATOR_DA_INPUT_NAME      = (By.CSS_SELECTOR, "input[name='name']")
    LOCATOR_DA_INPUT_BEGIN     = (By.CSS_SELECTOR, "input[name='beginDate']")
    LOCATOR_DA_INPUT_END       = (By.CSS_SELECTOR, "input[name='endDate']")
    LOCATOR_DA_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_DA_ADD_LINK        = (By.XPATH, "//a[contains(@href, 'driverActivity_add')]")
    LOCATOR_DA_RESET_LINK      = (By.XPATH, "//a[contains(@href, '/driverActivity') and (contains(text(), 'Reset') or contains(@class, 'reset'))]")

    # =========================================================================
    # LOCATORS - GIFT ACTIVITY (/sysCouponActivity)
    # =========================================================================
    LOCATOR_GA_SELECT_USE_TYPE = (By.CSS_SELECTOR, "select[name='couponUseType']")
    LOCATOR_GA_SELECT_STATUS   = (By.CSS_SELECTOR, "select[name='status']")
    LOCATOR_GA_INPUT_BEGIN     = (By.CSS_SELECTOR, "input[name='beginTime']")
    LOCATOR_GA_INPUT_END       = (By.CSS_SELECTOR, "input[name='endTime']")
    LOCATOR_GA_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_GA_ADD_LINK        = (By.XPATH, "//a[contains(@href, 'sysCouponActivity_add')]")
    LOCATOR_GA_RADIO_ITEM      = (By.CSS_SELECTOR, "input[name='selected-sca']")
    LOCATOR_GA_UPDATE_BTN      = (By.XPATH, "//button[contains(., 'Update')]")
    LOCATOR_GA_DELETE_BTN      = (By.XPATH, "//button[contains(., 'Delete')]")
    LOCATOR_GA_AUDIT_BTN       = (By.XPATH, "//button[contains(., 'Audit')]")

    # =========================================================================
    # LOCATORS - USER ACTIVITY (/userActivity)
    # =========================================================================
    LOCATOR_UA_INPUT_NAME      = (By.CSS_SELECTOR, "input[name='name']")
    LOCATOR_UA_SELECT_STATUS   = (By.CSS_SELECTOR, "select[name='status']")
    LOCATOR_UA_INPUT_BEGIN     = (By.CSS_SELECTOR, "input[name='beginTime']")
    LOCATOR_UA_INPUT_END       = (By.CSS_SELECTOR, "input[name='endTime']")
    LOCATOR_UA_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_UA_ADD_LINK        = (By.XPATH, "//a[contains(@href, 'userActivity_add')]")

    # =========================================================================
    # LOCATORS - LARGE COUPON ACTIVITIES (/tUserLarge)
    # =========================================================================
    LOCATOR_LC_INPUT_NAME      = (By.CSS_SELECTOR, "input[name='name']")
    LOCATOR_LC_SELECT_STATUS   = (By.CSS_SELECTOR, "select[name='status']")
    LOCATOR_LC_INPUT_BEGIN     = (By.CSS_SELECTOR, "input[name='beginTime']")
    LOCATOR_LC_INPUT_END       = (By.CSS_SELECTOR, "input[name='endTime']")
    LOCATOR_LC_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_LC_ADD_LINK        = (By.XPATH, "//a[contains(@href, 'tUserLarge_add')]")
    LOCATOR_LC_RADIO_ITEM      = (By.CSS_SELECTOR, "input[name='selected-tul']")
    LOCATOR_LC_AUDIT_BTN       = (By.XPATH, "//button[contains(., 'Audit')]")

    # =========================================================================
    # LOCATORS - DRIVER GUARANTEED INCOME (/tEnsureIncomeRule)
    # =========================================================================
    LOCATOR_IR_INPUT_RULENAME  = (By.CSS_SELECTOR, "input[name='ruleName']")
    LOCATOR_IR_INPUT_BEGIN     = (By.CSS_SELECTOR, "input[name='beginDate']")
    LOCATOR_IR_INPUT_END       = (By.CSS_SELECTOR, "input[name='endDate']")
    LOCATOR_IR_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_IR_ADD_LINK        = (By.XPATH, "//a[contains(@href, 'tEnsureIncomeRule_add')]")
    LOCATOR_IR_RADIO_ITEM      = (By.CSS_SELECTOR, "input[name='selected-teir']")
    LOCATOR_IR_MODIFY_BTN      = (By.XPATH, "//button[contains(., 'Modify')]")
    LOCATOR_IR_DELETE_BTN      = (By.XPATH, "//button[contains(., 'Delete')]")
    LOCATOR_IR_AUDIT_BTN       = (By.XPATH, "//button[contains(., 'Audit')]")

    # =========================================================================
    # LOCATORS - COUPON DISTRIBUTION (/couponDistribution)
    # =========================================================================
    LOCATOR_CD_SELECT_TARGET   = (By.CSS_SELECTOR, "select[name='targetType']")
    LOCATOR_CD_INPUT_BEGIN     = (By.CSS_SELECTOR, "input[name='beginTime']")
    LOCATOR_CD_INPUT_END       = (By.CSS_SELECTOR, "input[name='endTime']")
    LOCATOR_CD_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_CD_ADD_LINK        = (By.XPATH, "//a[contains(@href, 'couponDistribution_add')]")
    LOCATOR_CD_RADIO_ITEM      = (By.CSS_SELECTOR, "input[name='selected-cd']")
    LOCATOR_CD_DELETE_BTN      = (By.XPATH, "//button[contains(., 'Delete')]")

    # =========================================================================
    # LOCATORS - COUPON USAGE (/couponUsage)
    # =========================================================================
    LOCATOR_CU_INPUT_KEYWORD   = (By.CSS_SELECTOR, "input[name='keyword']")
    LOCATOR_CU_SELECT_STATUS   = (By.CSS_SELECTOR, "select[name='status']")
    LOCATOR_CU_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_CU_SAVE_BTN        = (By.XPATH, "//button[contains(., 'Save')]")
    LOCATOR_CU_INPUT_DAILY     = (By.CSS_SELECTOR, "input[name='dailyCouponUsage']")

    # =========================================================================
    # LOCATORS - COUPON RECORD (/sysCouponRecord)
    # =========================================================================
    LOCATOR_CR_SELECT_USE_TYPE = (By.CSS_SELECTOR, "select[name='couponUseType']")
    LOCATOR_CR_SELECT_TYPE     = (By.CSS_SELECTOR, "select[name='couponType']")
    LOCATOR_CR_SELECT_LANG     = (By.CSS_SELECTOR, "select[name='yy']")
    LOCATOR_CR_INPUT_BEGIN     = (By.CSS_SELECTOR, "input[name='beginTime']")
    LOCATOR_CR_INPUT_END       = (By.CSS_SELECTOR, "input[name='endTime']")
    LOCATOR_CR_SEARCH_BTN      = (By.XPATH, "//button[contains(., 'Search')]")
    LOCATOR_CR_ADD_LINK        = (By.XPATH, "//a[contains(@href, 'sysCouponRecord_add')]")
    LOCATOR_CR_RADIO_ITEM      = (By.CSS_SELECTOR, "input[name='selected-scr']")
    LOCATOR_CR_UPDATE_BTN      = (By.XPATH, "//button[contains(., 'Update')]")
    LOCATOR_CR_DELETE_BTN      = (By.XPATH, "//button[contains(., 'Delete')]")
    LOCATOR_CR_AUDIT_BTN       = (By.XPATH, "//button[contains(., 'Audit')]")

    # =========================================================================
    # COMMON TABLE LOCATORS
    # =========================================================================
    LOCATOR_TABLE_HEADERS      = (By.CSS_SELECTOR, "table thead th")
    LOCATOR_TABLE_ROWS         = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_EMPTY_TABLE        = (By.XPATH, "//td[contains(., 'No data') or contains(., 'tidak ada data') or contains(., 'No matching records')] | //table[tbody/tr/td[@colspan]]")

    # =========================================================================
    # NAVIGATION METHODS
    # =========================================================================
    def open_driver_activity(self):
        """Buka halaman Driver Activity Management."""
        self.open(Config.ACTIVITY_DRIVER_URL)

    def open_driver_activity_add(self):
        """Buka sub-halaman tambah Driver Activity."""
        self.open(Config.ACTIVITY_DRIVER_ADD_URL)

    def open_gift_activity(self):
        """Buka halaman Gift Activity Management."""
        self.open(Config.ACTIVITY_GIFT_URL)

    def open_gift_activity_add(self):
        """Buka sub-halaman tambah Gift Activity."""
        self.open(Config.ACTIVITY_GIFT_ADD_URL)

    def open_user_activity(self):
        """Buka halaman User Activity Management."""
        self.open(Config.ACTIVITY_USER_URL)

    def open_user_activity_add(self):
        """Buka sub-halaman tambah User Activity."""
        self.open(Config.ACTIVITY_USER_ADD_URL)

    def open_large_coupon_activity(self):
        """Buka halaman Large Coupon Activities Management."""
        self.open(Config.ACTIVITY_LARGE_URL)

    def open_large_coupon_activity_add(self):
        """Buka sub-halaman tambah Large Coupon Activity."""
        self.open(Config.ACTIVITY_LARGE_ADD_URL)

    def open_income_rule(self):
        """Buka halaman Driver Guaranteed Income Management."""
        self.open(Config.ACTIVITY_INCOME_RULE_URL)

    def open_income_rule_add(self):
        """Buka sub-halaman tambah Driver Guaranteed Income."""
        self.open(Config.ACTIVITY_INCOME_ADD_URL)

    def open_coupon_distribution(self):
        """Buka halaman Coupon Distribution Management."""
        self.open(Config.ACTIVITY_DISTRIB_URL)

    def open_coupon_distribution_add(self):
        """Buka sub-halaman tambah Coupon Distribution."""
        self.open(Config.ACTIVITY_DISTRIB_ADD_URL)

    def open_coupon_usage(self):
        """Buka halaman Coupon Usage."""
        self.open(Config.ACTIVITY_USAGE_URL)

    def open_coupon_record(self):
        """Buka halaman Coupon Record Management."""
        self.open(Config.ACTIVITY_RECORD_URL)

    def open_coupon_record_add(self):
        """Buka sub-halaman tambah Coupon Record."""
        self.open(Config.ACTIVITY_RECORD_ADD_URL)

    # =========================================================================
    # FILTER & SEARCH METHODS
    # =========================================================================
    def search_driver_activity(self, name=None, begin_date=None, end_date=None):
        """Cari driver activity berdasarkan nama dan rentang tanggal."""
        if name is not None:
            self.type_text(self.LOCATOR_DA_INPUT_NAME, name)
        if begin_date is not None:
            self.type_text(self.LOCATOR_DA_INPUT_BEGIN, begin_date)
        if end_date is not None:
            self.type_text(self.LOCATOR_DA_INPUT_END, end_date)
        self.click(self.LOCATOR_DA_SEARCH_BTN)

    def search_gift_activity(self, coupon_use_type=None, status=None, begin_time=None, end_time=None):
        """Cari gift activity dengan select option & tanggal."""
        if coupon_use_type is not None:
            select = Select(self.find(self.LOCATOR_GA_SELECT_USE_TYPE))
            select.select_by_visible_text(coupon_use_type)
        if status is not None:
            select = Select(self.find(self.LOCATOR_GA_SELECT_STATUS))
            select.select_by_visible_text(status)
        if begin_time is not None:
            self.type_text(self.LOCATOR_GA_INPUT_BEGIN, begin_time)
        if end_time is not None:
            self.type_text(self.LOCATOR_GA_INPUT_END, end_time)
        self.click(self.LOCATOR_GA_SEARCH_BTN)

    def search_user_activity(self, name=None, status=None, begin_time=None, end_time=None):
        """Cari user activity dengan nama & status."""
        if name is not None:
            self.type_text(self.LOCATOR_UA_INPUT_NAME, name)
        if status is not None:
            select = Select(self.find(self.LOCATOR_UA_SELECT_STATUS))
            select.select_by_visible_text(status)
        if begin_time is not None:
            self.type_text(self.LOCATOR_UA_INPUT_BEGIN, begin_time)
        if end_time is not None:
            self.type_text(self.LOCATOR_UA_INPUT_END, end_time)
        self.click(self.LOCATOR_UA_SEARCH_BTN)

    def search_large_coupon_activity(self, name=None, status=None, begin_time=None, end_time=None):
        """Cari large coupon activity dengan nama & status."""
        if name is not None:
            self.type_text(self.LOCATOR_LC_INPUT_NAME, name)
        if status is not None:
            select = Select(self.find(self.LOCATOR_LC_SELECT_STATUS))
            select.select_by_visible_text(status)
        if begin_time is not None:
            self.type_text(self.LOCATOR_LC_INPUT_BEGIN, begin_time)
        if end_time is not None:
            self.type_text(self.LOCATOR_LC_INPUT_END, end_time)
        self.click(self.LOCATOR_LC_SEARCH_BTN)

    def search_income_rule(self, rule_name=None, begin_date=None, end_date=None):
        """Cari guaranteed income rule berdasarkan nama aturan."""
        if rule_name is not None:
            self.type_text(self.LOCATOR_IR_INPUT_RULENAME, rule_name)
        if begin_date is not None:
            self.type_text(self.LOCATOR_IR_INPUT_BEGIN, begin_date)
        if end_date is not None:
            self.type_text(self.LOCATOR_IR_INPUT_END, end_date)
        self.click(self.LOCATOR_IR_SEARCH_BTN)

    def search_coupon_distribution(self, target_type=None, begin_time=None, end_time=None):
        """Cari coupon distribution berdasarkan targetType & tanggal."""
        if target_type is not None:
            select = Select(self.find(self.LOCATOR_CD_SELECT_TARGET))
            select.select_by_visible_text(target_type)
        if begin_time is not None:
            self.type_text(self.LOCATOR_CD_INPUT_BEGIN, begin_time)
        if end_time is not None:
            self.type_text(self.LOCATOR_CD_INPUT_END, end_time)
        self.click(self.LOCATOR_CD_SEARCH_BTN)

    def search_coupon_usage(self, keyword=None, status=None):
        """Cari data penggunaan kupon berdasarkan keyword & status."""
        if keyword is not None:
            self.type_text(self.LOCATOR_CU_INPUT_KEYWORD, keyword)
        if status is not None:
            select = Select(self.find(self.LOCATOR_CU_SELECT_STATUS))
            select.select_by_visible_text(status)
        self.click(self.LOCATOR_CU_SEARCH_BTN)

    def search_coupon_record(self, use_type=None, coupon_type=None, language=None, begin_time=None, end_time=None):
        """Cari kupon di sysCouponRecord berdasarkan berbagai kriteria."""
        if use_type is not None:
            select = Select(self.find(self.LOCATOR_CR_SELECT_USE_TYPE))
            select.select_by_visible_text(use_type)
        if coupon_type is not None:
            select = Select(self.find(self.LOCATOR_CR_SELECT_TYPE))
            select.select_by_visible_text(coupon_type)
        if language is not None:
            select = Select(self.find(self.LOCATOR_CR_SELECT_LANG))
            select.select_by_visible_text(language)
        if begin_time is not None:
            self.type_text(self.LOCATOR_CR_INPUT_BEGIN, begin_time)
        if end_time is not None:
            self.type_text(self.LOCATOR_CR_INPUT_END, end_time)
        self.click(self.LOCATOR_CR_SEARCH_BTN)

    # =========================================================================
    # TABLE & BUTTON ACTION METHODS
    # =========================================================================
    def get_table_headers(self):
        """Mengambil teks seluruh header kolom tabel aktif."""
        elements = self.find_all(self.LOCATOR_TABLE_HEADERS)
        return [el.text.strip() for el in elements if el.text.strip()]

    def is_button_disabled(self, locator):
        """Memeriksa apakah sebuah tombol memiliki atribut disabled."""
        try:
            elem = self.find(locator)
            return elem.get_attribute("disabled") is not None
        except Exception:
            return False

    def select_first_radio(self, locator):
        """Memilih radio button baris pertama pada tabel data."""
        radios = self.find_all(locator)
        if radios:
            radios[0].click()
            return True
        return False

    # =========================================================================
    # PROFILE & TOP NAVIGATION METHODS (DELEGATED TO BASEPAGE)
    # =========================================================================
    LOCATOR_TOAST = (By.CSS_SELECTOR, "[data-toast], .toast, .alert, .notification, [role='alert']")

    def is_profile_dropdown_displayed(self):
        """Memeriksa apakah dropdown profil pengguna sedang terbuka dan terlihat."""
        return self.is_profile_dropdown_open()

