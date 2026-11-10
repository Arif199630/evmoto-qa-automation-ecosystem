"""
Withdrawal Management Page Object
Website: <BASE_URL>/tPubWithdrawal & /withdrawalConfig
Sub-Halaman:
  1. Withdrawal List (/tPubWithdrawal)
  2. Withdrawal Configuration (/withdrawalConfig)
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class WithdrawalPage(BasePage):
    """Page Object untuk Modul Withdrawal Management beserta 2 sub-halamannya."""

    # =========================================================================
    # 1. WITHDRAWAL LIST (/tPubWithdrawal)
    # =========================================================================
    LOCATOR_WITHDRAWAL_HEADING       = (By.TAG_NAME, "h1")
    LOCATOR_WITHDRAWAL_BEGIN_DATE    = (By.CSS_SELECTOR, "form[action*='/tPubWithdrawal'] input[name='beginDate']")
    LOCATOR_WITHDRAWAL_END_DATE      = (By.CSS_SELECTOR, "form[action*='/tPubWithdrawal'] input[name='endDate']")
    LOCATOR_WITHDRAWAL_NAME_INPUT    = (By.CSS_SELECTOR, "form[action*='/tPubWithdrawal'] input[name='name']")
    LOCATOR_WITHDRAWAL_USER_TYPE     = (By.CSS_SELECTOR, "form[action*='/tPubWithdrawal'] select[name='userType']")
    LOCATOR_WITHDRAWAL_SEARCH_BTN    = (By.CSS_SELECTOR, "form[action*='/tPubWithdrawal'] button[type='submit']")

    LOCATOR_WITHDRAWAL_TABLE         = (By.TAG_NAME, "table")
    LOCATOR_WITHDRAWAL_ROWS          = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_WITHDRAWAL_PROCESS_BTN   = (By.XPATH, "//button[normalize-space()='Process']")

    def navigate_list(self):
        """Membuka halaman Withdrawal List (/tPubWithdrawal)."""
        self.open(Config.PUB_WITHDRAWAL_URL)

    def is_table_displayed(self):
        """Memeriksa apakah tabel daftar penarikan dana tampil di layar."""
        return self.is_displayed(self.LOCATOR_WITHDRAWAL_TABLE)

    def get_rows_count(self):
        """Menghitung baris data aktual penarikan dana pada tabel."""
        rows = self.find_all(self.LOCATOR_WITHDRAWAL_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def search_by_name(self, name):
        """Mencari pengajuan penarikan dana berdasarkan nama pemohon."""
        self.type_text(self.LOCATOR_WITHDRAWAL_NAME_INPUT, name)
        self.click(self.LOCATOR_WITHDRAWAL_SEARCH_BTN)

    def filter_by_user_type(self, type_val="2"):
        """Filter tipe entitas penarik dana (1=User, 2=Driver)."""
        self.select_dropdown_by_value(self.LOCATOR_WITHDRAWAL_USER_TYPE, type_val)
        self.click(self.LOCATOR_WITHDRAWAL_SEARCH_BTN)

    def filter_by_date(self, start_date, end_date):
        """Filter rentang tanggal permohonan penarikan dana."""
        self.driver.get(f"{Config.PUB_WITHDRAWAL_URL}?beginDate={start_date}&endDate={end_date}")

    def is_process_btn_enabled(self):
        """Memeriksa status tombol Process (harus disabled sebelum memilih data)."""
        return self.is_enabled(self.LOCATOR_WITHDRAWAL_PROCESS_BTN)

    # =========================================================================
    # 2. WITHDRAWAL CONFIGURATION (/withdrawalConfig)
    # =========================================================================
    LOCATOR_CONFIG_HEADING           = (By.TAG_NAME, "h1")
    LOCATOR_CONFIG_MIN_AMOUNT        = (By.CSS_SELECTOR, "form[action*='/withdrawalConfig'] input[name='minWithdrawalAmount']")
    LOCATOR_CONFIG_SAVE_BTN          = (By.CSS_SELECTOR, "form[action*='/withdrawalConfig'] button[type='submit']")

    def navigate_config(self):
        """Membuka halaman Withdrawal Configuration (/withdrawalConfig)."""
        self.open(Config.WITHDRAWAL_CONFIG_URL)

    def is_config_input_displayed(self):
        """Memeriksa apakah input batas minimum penarikan dana tampil."""
        return self.is_displayed(self.LOCATOR_CONFIG_MIN_AMOUNT)

    def get_min_withdrawal_amount(self):
        """Mendapatkan nilai nominal batas minimum penarikan saat ini."""
        elem = self.find(self.LOCATOR_CONFIG_MIN_AMOUNT)
        return elem.get_attribute("value") if elem else ""

    def is_save_btn_enabled(self):
        """Memeriksa apakah tombol Save konfigurasi aktif."""
        return self.is_enabled(self.LOCATOR_CONFIG_SAVE_BTN)
