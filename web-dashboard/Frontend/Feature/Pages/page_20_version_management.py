"""
Page Object: Version Management Page
Website: <BASE_URL>/tVersionManagement
Sub-halaman Add: <BASE_URL>/tVersionManagement/tVersionManagement_add
Sub-halaman Edit: <BASE_URL>/tVersionManagement/tVersionManagement_update/43
Automation Project EvMoto
"""

import time
from selenium.webdriver.common.by import By
from pages.page_base import BasePage
from config import Config


class VersionPage(BasePage):
    """Page Object untuk Halaman Version Management dan Seluruh Sub-Halamannya."""

    # --- Locators Filter & Pencarian Utama (/tVersionManagement) ---
    INPUT_BEGIN_TIME = (By.NAME, "beginTime")
    INPUT_END_TIME   = (By.NAME, "endTime")
    INPUT_VERSION    = (By.NAME, "version")
    BTN_SEARCH       = (By.XPATH, "//button[contains(., 'Search')]")
    LINK_RESET       = (By.XPATH, "//a[contains(., 'Reset') and contains(@href, 'tVersionManagement')]")
    LINK_ADD         = (By.XPATH, "//a[contains(., 'Add') and contains(@href, 'tVersionManagement_add')]")
    BTN_UPDATE       = (By.XPATH, "//button[contains(., 'Update')]")
    BTN_DELETE       = (By.XPATH, "//button[contains(., 'Delete')]")

    # --- Locators Tabel & Baris Versi ---
    TABLE            = (By.TAG_NAME, "table")
    TABLE_HEADERS    = (By.XPATH, "//table//th")
    TABLE_ROWS       = (By.XPATH, "//table//tbody/tr")
    RADIO_ROWS       = (By.CSS_SELECTOR, "input[name='selected-tvm']")
    BTNS_COPY        = (By.CSS_SELECTOR, "button[data-tvm-copy]")

    # --- Locators Sub-Halaman Add / Edit Form ---
    FORM_ADD                   = (By.XPATH, "//form[contains(@action, 'tVersionManagement/add')]")
    INPUT_ADD_VERSION          = (By.CSS_SELECTOR, "form[action*='Version'] input[name='version']")
    RADIO_ADD_TYPE             = (By.CSS_SELECTOR, "form[action*='Version'] input[name='type']")
    INPUT_ADD_GOOGLE_PLAY      = (By.CSS_SELECTOR, "form[action*='Version'] input[name='googlePlayLink']")
    INPUT_ADD_APPLE_STORE      = (By.CSS_SELECTOR, "form[action*='Version'] input[name='appleStoreLink']")
    RADIO_ADD_MANDATORY        = (By.CSS_SELECTOR, "form[action*='Version'] input[name='mandatory']")
    INPUT_ADD_MINIMUM_VERSION  = (By.CSS_SELECTOR, "form[action*='Version'] input[name='minimumVersion']")
    TEXTAREA_ADD_CONTENT       = (By.CSS_SELECTOR, "form[action*='Version'] textarea[name='content']")
    BTN_ADD_SUBMIT             = (By.XPATH, "//form[contains(@action, 'Version')]//button[contains(., 'Submit')]")
    LINK_ADD_CANCEL            = (By.XPATH, "//form[contains(@action, 'Version')]//a[contains(., 'Cancel')] | //form[contains(@action, 'Version')]//button[contains(., 'Cancel')]")

    def __init__(self, driver):
        super().__init__(driver)

    # --- Navigasi Halaman & Sub-Halaman ---
    def navigate(self):
        """Membuka halaman utama Version Management."""
        self.open(Config.VERSION_MGMT_URL)

    def navigate_add(self):
        """Membuka sub-halaman Add Version."""
        self.open(Config.VERSION_ADD_URL)

    def navigate_update(self):
        """Membuka sub-halaman Edit Version."""
        self.open(Config.VERSION_UPDATE_URL)

    # --- Operasi Pencarian & Filter ---
    def filter_by_version(self, version_str):
        """Filter berdasarkan nomor versi aplikasi."""
        self.type_text(self.INPUT_VERSION, version_str)
        self.click(self.BTN_SEARCH)
        time.sleep(1)

    def filter_by_date(self, begin_date, end_date):
        """Filter berdasarkan rentang waktu penambahan versi."""
        url = f"{Config.VERSION_MGMT_URL}?beginTime={begin_date}&endTime={end_date}"
        self.open(url)
        time.sleep(1)

    def click_reset(self):
        """Klik tombol Reset untuk membersihkan filter."""
        btn = self.find(self.LINK_RESET, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    def click_add(self):
        """Klik tombol Add untuk berpindah ke sub-halaman tambah versi."""
        btn = self.find(self.LINK_ADD, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    # --- Operasi Seleksi & Tombol Aksi Tabel ---
    def select_first_version_radio(self):
        """Memilih baris versi pertama menggunakan radio button."""
        radios = self.find_all(self.RADIO_ROWS)
        if radios:
            self.driver.execute_script("arguments[0].click();", radios[0])
            time.sleep(0.5)
            return True
        return False

    def is_update_btn_enabled(self):
        """Memeriksa apakah tombol Update aktif."""
        return self.is_enabled(self.BTN_UPDATE)

    def is_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete aktif."""
        return self.is_enabled(self.BTN_DELETE)

    def click_update(self):
        """Klik tombol Update setelah memilih baris data."""
        btn = self.find(self.BTN_UPDATE, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    # --- Verifikasi Tabel & Elemen ---
    def is_table_displayed(self):
        """Memeriksa apakah tabel versi terlihat di layar."""
        return self.is_displayed(self.TABLE)

    def get_table_header_texts(self):
        """Mengambil daftar teks header kolom tabel."""
        headers = self.find_all(self.TABLE_HEADERS)
        return [h.text.strip() for h in headers if h.text.strip()]

    def is_add_form_displayed(self):
        """Memeriksa apakah formulir tambah versi tampil di layar."""
        return self.is_displayed(self.INPUT_ADD_VERSION)
