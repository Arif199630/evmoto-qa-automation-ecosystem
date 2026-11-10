"""
Franchisee Management Page Object
Website: <BASE_URL>/tCompany/franchisee
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class FranchiseePage(BasePage):
    """Page Object untuk Modul Franchisee Management (/tCompany/franchisee)."""

    LOCATOR_FRANCHISEE_HEADING         = (By.TAG_NAME, "h1")
    LOCATOR_FRANCHISEE_SEARCH_NAME     = (By.CSS_SELECTOR, "form[action='/tCompany/franchisee'] input[name='name']")
    LOCATOR_FRANCHISEE_ACCOUNT         = (By.CSS_SELECTOR, "form[action='/tCompany/franchisee'] input[name='account']")
    LOCATOR_FRANCHISEE_STATE_SELECT    = (By.CSS_SELECTOR, "form[action='/tCompany/franchisee'] select[name='state']")
    LOCATOR_FRANCHISEE_BEGIN_DATE      = (By.CSS_SELECTOR, "form[action='/tCompany/franchisee'] input[name='beginDate']")
    LOCATOR_FRANCHISEE_END_DATE        = (By.CSS_SELECTOR, "form[action='/tCompany/franchisee'] input[name='endDate']")
    LOCATOR_FRANCHISEE_SEARCH_BTN      = (By.CSS_SELECTOR, "form[action='/tCompany/franchisee'] button[type='submit']")
    LOCATOR_FRANCHISEE_TABLE           = (By.TAG_NAME, "table")
    LOCATOR_FRANCHISEE_ROWS            = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_FRANCHISEE_UPDATE_BTN      = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_FRANCHISEE_DELETE_BTN      = (By.XPATH, "//button[normalize-space()='Delete']")
    LOCATOR_FRANCHISEE_DETAILS_BTN     = (By.XPATH, "//button[normalize-space()='View details']")

    PAGE_PATH = "/tCompany/franchisee"

    def navigate(self, url_or_path=None):
        """Membuka halaman Franchisee Management (/tCompany/franchisee) secara dinamis."""
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def is_table_displayed(self):
        """Memeriksa apakah tabel Franchisee tampil di layar."""
        return self.is_displayed(self.LOCATOR_FRANCHISEE_TABLE)

    def get_rows_count(self):
        """Menghitung baris data aktual pada tabel Franchisee."""
        rows = self.find_all(self.LOCATOR_FRANCHISEE_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def search_by_name(self, name):
        """Mencari franchisee berdasarkan nama."""
        self.type_text(self.LOCATOR_FRANCHISEE_SEARCH_NAME, name)
        self.click(self.LOCATOR_FRANCHISEE_SEARCH_BTN)

    def search_by_account(self, account):
        """Mencari franchisee berdasarkan nomor akun."""
        self.type_text(self.LOCATOR_FRANCHISEE_ACCOUNT, account)
        self.click(self.LOCATOR_FRANCHISEE_SEARCH_BTN)

    def filter_by_state(self, state_value="2"):
        """Filter status franchisee (state). Opsi: 2=Normal, 1=Beku."""
        self.select_dropdown_by_value(self.LOCATOR_FRANCHISEE_STATE_SELECT, state_value)
        self.click(self.LOCATOR_FRANCHISEE_SEARCH_BTN)

    def filter_by_date(self, start_date, end_date):
        """Filter rentang tanggal pada Franchisee Management."""
        self.driver.get(f"{Config.FRANCHISEE_URL}?beginDate={start_date}&endDate={end_date}")

    def is_update_btn_enabled(self):
        """Memeriksa apakah tombol Update franchisee aktif atau terkunci (disabled)."""
        return self.is_enabled(self.LOCATOR_FRANCHISEE_UPDATE_BTN)

    def is_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete franchisee aktif atau terkunci (disabled)."""
        return self.is_enabled(self.LOCATOR_FRANCHISEE_DELETE_BTN)

    def is_details_btn_enabled(self):
        """Memeriksa apakah tombol View details franchisee aktif atau terkunci (disabled)."""
        return self.is_enabled(self.LOCATOR_FRANCHISEE_DETAILS_BTN)
