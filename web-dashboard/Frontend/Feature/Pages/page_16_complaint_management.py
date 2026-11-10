"""
Complaint Management Page Object
Website: <BASE_URL>/tComplaint
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class ComplaintPage(BasePage):
    """Page Object untuk Modul Complaint Management (/tComplaint)."""

    LOCATOR_COMPLAINT_FORM   = (By.CSS_SELECTOR, "form[action*='/tComplaint']")
    LOCATOR_BEGIN_TIME       = (By.CSS_SELECTOR, "form[action*='/tComplaint'] input[name='beginTime']")
    LOCATOR_END_TIME         = (By.CSS_SELECTOR, "form[action*='/tComplaint'] input[name='endTime']")
    LOCATOR_USER_NAME        = (By.CSS_SELECTOR, "form[action*='/tComplaint'] input[name='userName']")
    LOCATOR_USER_PHONE       = (By.CSS_SELECTOR, "form[action*='/tComplaint'] input[name='userPhone']")
    LOCATOR_DRIVER_PHONE     = (By.CSS_SELECTOR, "form[action*='/tComplaint'] input[name='driverPhone']")
    LOCATOR_IS_HANDLE        = (By.CSS_SELECTOR, "form[action*='/tComplaint'] select[name='isHandle']")
    LOCATOR_SEARCH_BTN       = (By.CSS_SELECTOR, "form[action*='/tComplaint'] button[type='submit']")

    LOCATOR_TABLE            = (By.TAG_NAME, "table")
    LOCATOR_ROWS             = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_PROCESS_BTN      = (By.XPATH, "//button[contains(text(), 'Immediately process')]")
    LOCATOR_DELETE_BTN       = (By.XPATH, "//button[contains(text(), 'Delete')]")

    PAGE_PATH = "/tComplaint"

    def navigate(self, url_or_path=None):
        """Membuka halaman Complaint Management (/tComplaint) secara dinamis."""
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def is_table_displayed(self, timeout=10):
        """Memeriksa apakah tabel pengaduan/keluhan tampil di layar."""
        return self.is_displayed(self.LOCATOR_TABLE, timeout=timeout)

    def search_by_user_name(self, name):
        """Mencari pengaduan berdasarkan nama pengadu/pelapor."""
        self.type_text(self.LOCATOR_USER_NAME, name)
        self.click(self.LOCATOR_SEARCH_BTN)

    def search_by_user_phone(self, phone):
        """Mencari pengaduan berdasarkan nomor telepon pelapor."""
        self.type_text(self.LOCATOR_USER_PHONE, phone)
        self.click(self.LOCATOR_SEARCH_BTN)

    def search_by_driver_phone(self, phone):
        """Mencari pengaduan berdasarkan nomor telepon pengemudi yang dilaporkan."""
        self.type_text(self.LOCATOR_DRIVER_PHONE, phone)
        self.click(self.LOCATOR_SEARCH_BTN)

    def filter_by_status(self, status_val="1"):
        """Filter status pengaduan (1=Has been processed, 2=Fail to be disposed, ''=All)."""
        self.select_dropdown_by_value(self.LOCATOR_IS_HANDLE, status_val)
        self.click(self.LOCATOR_SEARCH_BTN)

    def filter_by_date(self, begin_time, end_time):
        """Filter rentang waktu pengaduan via URL query."""
        self.driver.get(f"{Config.COMPLAINT_URL}?beginTime={begin_time}&endTime={end_time}")

    def is_process_btn_enabled(self):
        """Memeriksa apakah tombol 'Immediately process' berstatus aktif/enabled."""
        return self.is_enabled(self.LOCATOR_PROCESS_BTN)

    def is_delete_btn_enabled(self):
        """Memeriksa apakah tombol 'Delete' berstatus aktif/enabled."""
        return self.is_enabled(self.LOCATOR_DELETE_BTN)

    def is_process_btn_displayed(self):
        """Memeriksa apakah tombol 'Immediately process' tampil di layar."""
        return self.is_displayed(self.LOCATOR_PROCESS_BTN)

    def is_delete_btn_displayed(self):
        """Memeriksa apakah tombol 'Delete' tampil di layar."""
        return self.is_displayed(self.LOCATOR_DELETE_BTN)

    def get_rows_count(self):
        """Menghitung jumlah baris data pengaduan pada tabel."""
        rows = self.find_all(self.LOCATOR_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)
