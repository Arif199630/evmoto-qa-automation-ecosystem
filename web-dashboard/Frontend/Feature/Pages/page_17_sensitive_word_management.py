"""
Page Object: Sensitive Word Management Page
Website: <BASE_URL>/tSysSensitiveWords
Sub-halaman: <BASE_URL>/tSysSensitiveWords/tSysSensitiveWords_add
Automation Project EvMoto
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.page_base import BasePage
from config import Config


class SensitiveWordPage(BasePage):
    """Page Object untuk Halaman Sensitive Word Management dan Sub-Halamannya."""

    # --- Locators Filter & Pencarian Utama ---
    INPUT_BEGIN_TIME = (By.NAME, "beginTime")
    INPUT_END_TIME   = (By.NAME, "endTime")
    INPUT_CONTENT    = (By.NAME, "content")
    SELECT_LANGUAGE  = (By.NAME, "yy")
    BTN_SEARCH       = (By.XPATH, "//button[contains(., 'Search')]")
    LINK_RESET       = (By.XPATH, "//a[contains(., 'Reset')]")
    LINK_ADD         = (By.XPATH, "//a[contains(., 'Add') and contains(@href, 'tSysSensitiveWords_add')]")
    BTN_DELETE       = (By.XPATH, "//button[contains(., 'Delete')]")

    # --- Locators Tabel Kata Sensitif ---
    TABLE            = (By.TAG_NAME, "table")
    TABLE_HEADERS    = (By.XPATH, "//table//th")
    TABLE_ROWS       = (By.XPATH, "//table//tbody/tr")

    # --- Locators Sub-Halaman Tambah Kata Sensitif (Add Page) ---
    INPUT_ADD_CONTENT   = (By.CSS_SELECTOR, "form[action*='tSysSensitiveWords/add'] input[name='content']")
    SELECT_ADD_LANGUAGE = (By.CSS_SELECTOR, "form[action*='tSysSensitiveWords/add'] select[name='language']")
    BTN_ADD_SUBMIT      = (By.XPATH, "//form[contains(@action, 'tSysSensitiveWords/add')]//button[contains(., 'Submit')]")
    FORM_ADD            = (By.XPATH, "//form[contains(@action, 'tSysSensitiveWords/add')]")

    def __init__(self, driver):
        super().__init__(driver)

    def navigate(self):
        """Buka halaman utama Sensitive Word Management."""
        self.open(Config.SENSITIVE_WORDS_URL)

    def navigate_add(self):
        """Buka sub-halaman Add Sensitive Word."""
        self.open(Config.SENSITIVE_WORDS_ADD_URL)

    # --- Operasi Pencarian & Filter ---
    def filter_by_content(self, content_text):
        """Filter berdasarkan isi kata sensitif."""
        self.type_text(self.INPUT_CONTENT, content_text)
        self.click(self.BTN_SEARCH)
        time.sleep(1)

    def filter_by_language(self, lang_value):
        """Filter berdasarkan bahasa: '' (All), '1' (Chinese), '2' (English), '3' (Indonesian)."""
        element = self.find(self.SELECT_LANGUAGE)
        select = Select(element)
        select.select_by_value(str(lang_value))
        self.click(self.BTN_SEARCH)
        time.sleep(1)

    def filter_by_date(self, begin_date, end_date):
        """Filter berdasarkan rentang waktu pembuatan."""
        url = f"{Config.SENSITIVE_WORDS_URL}?beginTime={begin_date}&endTime={end_date}"
        self.open(url)
        time.sleep(1)

    def click_reset(self):
        """Klik tombol Reset untuk membersihkan filter."""
        btn = self.find(self.LINK_RESET, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    def click_add(self):
        """Klik tombol Add untuk berpindah ke sub-halaman tambah kata."""
        btn = self.find(self.LINK_ADD, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    # --- Verifikasi Tabel & Elemen ---
    def is_table_displayed(self):
        """Memeriksa apakah tabel daftar kata sensitif terlihat di layar."""
        return self.is_displayed(self.TABLE)

    def get_table_header_texts(self):
        """Mengambil daftar teks header kolom tabel."""
        headers = self.find_all(self.TABLE_HEADERS)
        return [h.text.strip() for h in headers if h.text.strip()]

    def is_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete aktif (default: False terkunci)."""
        return self.is_enabled(self.BTN_DELETE)

    def is_delete_btn_present(self):
        """Memeriksa apakah tombol Delete hadir di DOM."""
        elems = self.find_all(self.BTN_DELETE)
        return len(elems) > 0

    # --- Operasi Sub-Halaman Tambah Kata ---
    def fill_add_form(self, content, language_val=None):
        """Mengisi formulir sub-halaman tambah kata sensitif."""
        self.type_text(self.INPUT_ADD_CONTENT, content)
        if language_val:
            elem = self.find(self.SELECT_ADD_LANGUAGE)
            select = Select(elem)
            select.select_by_value(str(language_val))

    def is_add_form_displayed(self):
        """Memeriksa apakah form penambahan kata sensitif tampil di layar."""
        return self.is_displayed(self.INPUT_ADD_CONTENT)
