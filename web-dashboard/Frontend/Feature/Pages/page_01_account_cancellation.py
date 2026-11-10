"""
Account Cancellation Management Page Object
Website: <BASE_URL>/userExit
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class AccountCancellationPage(BasePage):
    """Page Object untuk Halaman Account Cancellation Management (/userExit)."""

    # Locators
    LOCATOR_BEGIN_DATE      = (By.CSS_SELECTOR, "input[name='beginTime']")
    LOCATOR_END_DATE        = (By.CSS_SELECTOR, "input[name='endTime']")
    LOCATOR_SEARCH_NAME     = (By.CSS_SELECTOR, "input[name='name']")
    LOCATOR_STATE_SELECT    = (By.CSS_SELECTOR, "select[name='state']")
    LOCATOR_SEARCH_BTN      = (By.CSS_SELECTOR, "form[action='/userExit'] button[type='submit']")
    LOCATOR_TABLE           = (By.TAG_NAME, "table")
    LOCATOR_TABLE_ROWS      = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_RADIO_CHOICES   = (By.CSS_SELECTOR, "[data-ue-choice]")
    LOCATOR_PROCESS_BTN     = (By.CSS_SELECTOR, "[data-ue-process]")
    LOCATOR_SELECTION_ERROR = (By.CSS_SELECTOR, "[data-ue-selection-error]")

    PAGE_PATH = "/userExit"

    def navigate(self, url_or_path=None):
        """Buka halaman Account Cancellation Management secara dinamis."""
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def get_heading_text(self):
        """Mengambil teks heading h1."""
        return self.get_text((By.TAG_NAME, "h1"))

    def is_table_displayed(self, timeout=None):
        """Memeriksa apakah tabel data tampil."""
        return self.is_displayed(self.LOCATOR_TABLE)

    def is_process_button_enabled(self):
        """Memeriksa status enabled tombol Immediate processing."""
        return self.is_enabled(self.LOCATOR_PROCESS_BTN)

    # Alias untuk fleksibilitas pemanggilan
    is_process_btn_enabled = is_process_button_enabled

    def get_rows_count(self):
        """Menghitung jumlah baris data pada tabel (mengabaikan baris placeholder kosong)."""
        rows = self.find_all(self.LOCATOR_TABLE_ROWS)
        valid_rows = [r for r in rows if "No cancellation requests found" not in r.text and "No matching records found" not in r.text and "No data" not in r.text]
        return len(valid_rows)

    def filter_by_state(self, state_value="2"):
        """Filter data berdasarkan status akun (state)."""
        self.driver.get(f"{Config.USER_EXIT_URL}?state={state_value}&status={state_value}")

    filter_by_status = filter_by_state

    def search_by_name(self, name):
        """Mencari user berdasarkan field nama."""
        self.type_text(self.LOCATOR_SEARCH_NAME, name)
        self.click(self.LOCATOR_SEARCH_BTN)

    search_by_username = search_by_name

    def select_first_radio(self):
        """Memilih radio button akun pertama pada tabel."""
        radios = self.find_all(self.LOCATOR_RADIO_CHOICES)
        if radios:
            self.click_js(radios[0])
            self.dispatch_event(radios[0], "change")
            return True
        return False

    select_first_user_row = select_first_radio

    def select_cleared_account_radio(self):
        """Memilih radio button akun dengan status ueState == '2' (Cleared)."""
        cleared_radios = self.find_all((By.CSS_SELECTOR, "[data-ue-choice][data-ue-state='2']"))
        if cleared_radios:
            self.click_js(cleared_radios[0])
            self.dispatch_event(cleared_radios[0], "change")
            return True
        return False

    def click_process_button(self):
        """Klik tombol Immediate processing."""
        self.click(self.LOCATOR_PROCESS_BTN)

    def is_closed_account_error_displayed(self):
        """Memeriksa apakah ada banner error pemrosesan akun."""
        return self.is_displayed(self.LOCATOR_SELECTION_ERROR)

    def get_selection_error_text(self):
        """Mengambil teks error seleksi bisnis."""
        return self.get_text(self.LOCATOR_SELECTION_ERROR)

    def get_radio_choices_count(self):
        """Mengambil jumlah pilihan radio di tabel."""
        return len(self.find_all(self.LOCATOR_RADIO_CHOICES))
