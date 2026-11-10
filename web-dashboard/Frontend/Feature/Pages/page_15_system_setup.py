"""
System Setup Page Object
Sub-Halaman:
  1. System Setup (/tSysReformist)
  2. Unblock Cancellation Debt (/userDebtUnblock)
Website: <BASE_URL>/
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class SystemSetupPage(BasePage):
    """Page Object untuk Modul System Setup & Sub-Halamannya."""

    # =========================================================================
    # LOCATORS: Sub-Halaman 1 - System Setup (/tSysReformist)
    # =========================================================================
    LOCATOR_REFORMIST_FORM       = (By.CSS_SELECTOR, "form[action*='/tSysReformist/setUp']")
    LOCATOR_INTEGRAL_SPEND       = (By.NAME, "integralSpend")
    LOCATOR_INTEGRAL_POINTS      = (By.NAME, "integralPoints")
    LOCATOR_WAIT_MINUTES         = (By.NAME, "waitMinutes")
    LOCATOR_WAIT_DEDUCT          = (By.NAME, "waitDeduct")
    LOCATOR_WAIT_MAX_CANCEL      = (By.NAME, "waitMaxCancel")
    LOCATOR_MIN_MONEY            = (By.NAME, "minMoney")
    LOCATOR_NORMAL_CANCEL_MINUTES= (By.NAME, "normalCancelMinutes")
    LOCATOR_NORMAL_CANCEL_FEE    = (By.NAME, "normalCancelFee")
    LOCATOR_APPT_CANCEL_MINUTES  = (By.NAME, "apptCancelMinutes")
    LOCATOR_APPT_CANCEL_FEE      = (By.NAME, "apptCancelFee")
    LOCATOR_ALARM_PHONE          = (By.NAME, "alarmPhone")
    LOCATOR_SERVICE_PHONE        = (By.NAME, "servicePhone")
    LOCATOR_REFORMIST_SAVE_BTN   = (By.CSS_SELECTOR, "form[action*='/tSysReformist/setUp'] button[type='submit']")
    LOCATOR_ADD_ROW_BTNS         = (By.XPATH, "//button[contains(text(), 'Add row')]")

    # =========================================================================
    # LOCATORS: Sub-Halaman 2 - Unblock Cancellation Debt (/userDebtUnblock)
    # =========================================================================
    LOCATOR_DEBT_SEARCH_FORM     = (By.CSS_SELECTOR, "form[action*='/userDebtUnblock']")
    LOCATOR_DEBT_SEARCH_USER_ID  = (By.CSS_SELECTOR, "form[action*='/userDebtUnblock'] input[name='userId']")
    LOCATOR_DEBT_SEARCH_BTN      = (By.CSS_SELECTOR, "form[action*='/userDebtUnblock']:not([action*='unblock']) button")
    LOCATOR_UNBLOCK_FORM         = (By.CSS_SELECTOR, "form[action*='/userDebtUnblock/unblock']")
    LOCATOR_UNBLOCK_USER_ID      = (By.CSS_SELECTOR, "form[action*='/userDebtUnblock/unblock'] input[name='userId']")
    LOCATOR_REASON_CATEGORY      = (By.NAME, "reasonCategory")
    LOCATOR_MARK_PAID_BTN        = (By.CSS_SELECTOR, "form[action*='/userDebtUnblock/unblock'] button")
    LOCATOR_DEBT_TABLE           = (By.TAG_NAME, "table")
    LOCATOR_DEBT_ROWS            = (By.CSS_SELECTOR, "table tbody tr")

    # =========================================================================
    # ACTIONS: Sub-Halaman 1 - System Setup (/tSysReformist)
    # =========================================================================
    def navigate_reformist(self):
        """Membuka halaman konfigurasi parameter sistem (/tSysReformist)."""
        self.open(Config.SYS_REFORMIST_URL)

    def is_reformist_form_displayed(self, timeout=10):
        """Memeriksa apakah formulir konfigurasi parameter sistem tampil di layar."""
        return self.is_displayed(self.LOCATOR_REFORMIST_FORM, timeout=timeout)

    def is_service_phone_displayed(self):
        """Memeriksa apakah field hotline customer service tampil di form."""
        return self.is_displayed(self.LOCATOR_SERVICE_PHONE)

    def is_alarm_phone_displayed(self):
        """Memeriksa apakah field nomor darurat SOS tampil di form."""
        return self.is_displayed(self.LOCATOR_ALARM_PHONE)

    def get_service_phone_value(self):
        """Mengambil nomor telepon hotline layanan pelanggan."""
        return self.get_attribute(self.LOCATOR_SERVICE_PHONE, "value")

    def get_alarm_phone_value(self):
        """Mengambil nomor telepon darurat/SOS (Alarm Phone)."""
        return self.get_attribute(self.LOCATOR_ALARM_PHONE, "value")

    def get_normal_cancel_fee(self):
        """Mengambil biaya pembatalan pesanan reguler (Normal Cancel Fee)."""
        return self.get_attribute(self.LOCATOR_NORMAL_CANCEL_FEE, "value")

    def get_appt_cancel_fee(self):
        """Mengambil biaya pembatalan pesanan janji temu (Appointment Cancel Fee)."""
        return self.get_attribute(self.LOCATOR_APPT_CANCEL_FEE, "value")

    def get_wait_minutes(self):
        """Mengambil waktu tunggu penalti pembatalan."""
        return self.get_attribute(self.LOCATOR_WAIT_MINUTES, "value")

    def is_save_button_displayed(self):
        """Memeriksa apakah tombol Save konfigurasi tampil di layar."""
        return self.is_displayed(self.LOCATOR_REFORMIST_SAVE_BTN)

    # =========================================================================
    # ACTIONS: Sub-Halaman 2 - Unblock Cancellation Debt (/userDebtUnblock)
    # =========================================================================
    def navigate_debt_unblock(self):
        """Membuka halaman pengelolaan hutang pembatalan pesanan (/userDebtUnblock)."""
        self.open(Config.USER_DEBT_UNBLOCK_URL)

    def is_debt_table_displayed(self, timeout=10):
        """Memeriksa apakah tabel daftar hutang pembatalan tampil di layar."""
        return self.is_displayed(self.LOCATOR_DEBT_TABLE, timeout=timeout)

    def search_debt_by_user_id(self, user_id):
        """Mencari hutang pembatalan berdasarkan User ID pemesan."""
        self.driver.get(f"{Config.USER_DEBT_UNBLOCK_URL}?userId={user_id}")

    def get_debt_rows_count(self):
        """Menghitung jumlah baris data hutang pada tabel."""
        rows = self.find_all(self.LOCATOR_DEBT_ROWS)
        valid = [
            r for r in rows
            if not any(msg in r.text.lower() for msg in ["enter a user id", "no outstanding", "no debts", "tidak ada", "no "])
        ]
        return len(valid)

    def is_mark_paid_btn_displayed(self):
        """Memeriksa apakah tombol 'Mark paid' tampil di layar."""
        return self.is_displayed(self.LOCATOR_MARK_PAID_BTN)

    def is_unblock_form_present(self):
        """Memeriksa apakah formulir unblock hutang ada di DOM."""
        forms = self.find_all(self.LOCATOR_UNBLOCK_FORM)
        return len(forms) > 0
