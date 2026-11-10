"""
Branch Management Page Object
Website: <BASE_URL>/tCompany
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class BranchPage(BasePage):
    """Page Object untuk Modul Branch Management (/tCompany)."""

    LOCATOR_BRANCH_HEADING         = (By.TAG_NAME, "h1")
    LOCATOR_BRANCH_SEARCH_NAME     = (By.CSS_SELECTOR, "form[action='/tCompany'] input[name='name']")
    LOCATOR_BRANCH_PRINCIPAL_NAME  = (By.CSS_SELECTOR, "form[action='/tCompany'] input[name='principalName']")
    LOCATOR_BRANCH_PRINCIPAL_PHONE = (By.CSS_SELECTOR, "form[action='/tCompany'] input[name='principalPhone']")
    LOCATOR_BRANCH_STATE_SELECT    = (By.CSS_SELECTOR, "form[action='/tCompany'] select[name='state']")
    LOCATOR_BRANCH_BEGIN_DATE      = (By.CSS_SELECTOR, "form[action='/tCompany'] input[name='beginDate']")
    LOCATOR_BRANCH_END_DATE        = (By.CSS_SELECTOR, "form[action='/tCompany'] input[name='endDate']")
    LOCATOR_BRANCH_SEARCH_BTN      = (By.CSS_SELECTOR, "form[action='/tCompany'] button[type='submit']")
    LOCATOR_BRANCH_TABLE           = (By.TAG_NAME, "table")
    LOCATOR_BRANCH_ROWS            = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_BRANCH_UPDATE_BTN      = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_BRANCH_DELETE_BTN      = (By.XPATH, "//button[normalize-space()='Delete']")
    LOCATOR_BRANCH_DETAILS_BTN     = (By.XPATH, "//button[normalize-space()='View details']")

    PAGE_PATH = "/tCompany"

    def navigate(self, url_or_path=None):
        """Membuka halaman Branch Management (/tCompany) secara dinamis."""
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def is_table_displayed(self):
        """Memeriksa apakah tabel Branch tampil di layar."""
        return self.is_displayed(self.LOCATOR_BRANCH_TABLE)

    def get_rows_count(self):
        """Menghitung baris data aktual pada tabel Branch."""
        rows = self.find_all(self.LOCATOR_BRANCH_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def search_by_name(self, name):
        """Mencari cabang perusahaan berdasarkan nama perusahaan."""
        self.type_text(self.LOCATOR_BRANCH_SEARCH_NAME, name)
        self.click(self.LOCATOR_BRANCH_SEARCH_BTN)

    def search_by_principal(self, principal_name):
        """Mencari cabang berdasarkan nama penanggung jawab."""
        self.type_text(self.LOCATOR_BRANCH_PRINCIPAL_NAME, principal_name)
        self.click(self.LOCATOR_BRANCH_SEARCH_BTN)

    def search_by_phone(self, phone):
        """Mencari cabang berdasarkan nomor telepon penanggung jawab."""
        self.type_text(self.LOCATOR_BRANCH_PRINCIPAL_PHONE, phone)
        self.click(self.LOCATOR_BRANCH_SEARCH_BTN)

    def filter_by_state(self, state_value="2"):
        """Filter status cabang perusahaan (state). Opsi: 2=Normal, 1=Beku."""
        self.select_dropdown_by_value(self.LOCATOR_BRANCH_STATE_SELECT, state_value)
        self.click(self.LOCATOR_BRANCH_SEARCH_BTN)

    def filter_by_date(self, start_date, end_date):
        """Filter rentang tanggal pada Branch Management."""
        self.driver.get(f"{Config.BRANCH_URL}?beginDate={start_date}&endDate={end_date}")

    def is_update_btn_enabled(self):
        """Memeriksa apakah tombol Update cabang aktif atau terkunci (disabled)."""
        return self.is_enabled(self.LOCATOR_BRANCH_UPDATE_BTN)

    def is_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete cabang aktif atau terkunci (disabled)."""
        return self.is_enabled(self.LOCATOR_BRANCH_DELETE_BTN)

    def is_details_btn_enabled(self):
        """Memeriksa apakah tombol View details cabang aktif atau terkunci (disabled)."""
        return self.is_enabled(self.LOCATOR_BRANCH_DETAILS_BTN)
