"""
User Management Page Object
Website: <BASE_URL>/tUser
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class UserManagementPage(BasePage):
    """Page Object untuk Halaman User Management (/tUser)."""

    # Locators
    LOCATOR_SEARCH_PHONE       = (By.ID, "customer-phone")
    LOCATOR_SEARCH_NICKNAME    = (By.ID, "customer-nickname")
    LOCATOR_SEARCH_FORM        = (By.CSS_SELECTOR, "form[action='/tUser']")
    LOCATOR_TABLE              = (By.TAG_NAME, "table")
    LOCATOR_TABLE_ROWS         = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_USER_CHOICES       = (By.CSS_SELECTOR, "[data-tuser-choice]")
    
    # Action buttons & Dialog
    LOCATOR_DETAIL_BTN         = (By.CSS_SELECTOR, "[data-tuser-detail]")
    LOCATOR_BALANCE_BTN        = (By.CSS_SELECTOR, "[data-tuser-balance]")
    LOCATOR_PROMOTION_BTN      = (By.CSS_SELECTOR, "[data-tuser-promotion-code]")
    LOCATOR_PROMOTION_DIALOG   = (By.CSS_SELECTOR, "[data-tuser-promotion-dialog]")
    LOCATOR_PROMOTION_CLOSE    = (By.CSS_SELECTOR, "[data-tuser-promotion-close]")

    PAGE_PATH = "/tUser"

    def navigate(self, url_or_path=None):
        """Buka halaman User Management secara dinamis."""
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def get_heading_text(self):
        """Mengambil teks heading h1."""
        return self.get_text((By.TAG_NAME, "h1"))

    def is_table_displayed(self):
        """Periksa apakah tabel data tampil."""
        return self.is_displayed(self.LOCATOR_TABLE)

    def is_detail_btn_enabled(self):
        """Periksa apakah tombol User details enabled."""
        return self.is_enabled(self.LOCATOR_DETAIL_BTN)

    def is_balance_btn_enabled(self):
        """Periksa apakah tombol Modify balance enabled."""
        return self.is_enabled(self.LOCATOR_BALANCE_BTN)

    def get_rows_count(self):
        """Mengambil jumlah baris data pengguna."""
        return len(self.find_all(self.LOCATOR_TABLE_ROWS))

    def search_by_phone(self, phone):
        """Cari pengguna berdasarkan nomor telepon."""
        self.type_text(self.LOCATOR_SEARCH_PHONE, phone)
        form = self.find(self.LOCATOR_SEARCH_FORM)
        form.submit()

    def search_by_nickname(self, nickname):
        """Cari pengguna berdasarkan nickname."""
        self.type_text(self.LOCATOR_SEARCH_NICKNAME, nickname)
        form = self.find(self.LOCATOR_SEARCH_FORM)
        form.submit()

    def select_first_user(self):
        """Pilih radio button pengguna pertama."""
        choices = self.find_all(self.LOCATOR_USER_CHOICES)
        if choices:
            self.click_js(choices[0])
            self.dispatch_event(choices[0], "change")
            return True
        return False

    def open_promotion_dialog(self):
        """Buka modal Extension Code."""
        self.click(self.LOCATOR_PROMOTION_BTN)

    def is_promotion_dialog_open(self):
        """Periksa status dialog modal terbuka (memiliki atribut open)."""
        dialog = self.find(self.LOCATOR_PROMOTION_DIALOG)
        return dialog.get_attribute("open") is not None

    def close_promotion_dialog(self):
        """Tutup dialog modal Extension Code."""
        self.click(self.LOCATOR_PROMOTION_CLOSE)

    def get_user_choices_count(self):
        """Mengambil jumlah pilihan radio di tabel."""
        return len(self.find_all(self.LOCATOR_USER_CHOICES))
