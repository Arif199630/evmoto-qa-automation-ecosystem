"""
Page Object: Feedback Management Page
Website: <BASE_URL>/tFeedback (Driver Feedback)
Sub-halaman 1: <BASE_URL>/tFeedback/userFeedback (User Feedback)
Sub-halaman 2: <BASE_URL>/tFeedback/lookDetail/81/1 (Feedback Detail View)
Automation Project EvMoto
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.page_base import BasePage
from config import Config


class FeedbackPage(BasePage):
    """Page Object untuk Halaman Feedback Management dan Seluruh Sub-Halamannya."""

    # --- Locators Filter & Pencarian Driver Feedback (/tFeedback) ---
    INPUT_DRIVER_NAME  = (By.NAME, "driverName")
    INPUT_DRIVER_PHONE = (By.NAME, "driverPhone")

    # --- Locators Filter & Pencarian User Feedback (/tFeedback/userFeedback) ---
    INPUT_USER_NAME    = (By.NAME, "userName")
    INPUT_USER_PHONE   = (By.NAME, "userPhone")

    # --- Locators Filter Bersama (Shared Filters) ---
    INPUT_BEGIN_TIME   = (By.NAME, "beginTime")
    INPUT_END_TIME     = (By.NAME, "endTime")
    SELECT_STATE       = (By.NAME, "state")

    # --- Locators Tombol Aksi Utama ---
    BTN_SEARCH         = (By.XPATH, "//button[contains(., 'Search')]")
    LINK_RESET_DRIVER  = (By.XPATH, "//a[contains(., 'Reset') and contains(@href, '/tFeedback')]")
    LINK_RESET_USER    = (By.XPATH, "//a[contains(., 'Reset') and contains(@href, 'userFeedback')]")
    BTN_PROCESS        = (By.XPATH, "//button[contains(., 'Immediately process')]")

    # --- Locators Sub-Halaman & Detail View ---
    LINK_VIEW_MORE     = (By.XPATH, "//a[contains(., 'view more') or contains(@href, 'lookDetail')]")
    BTN_BACK_DETAIL    = (By.XPATH, "//a[contains(., 'Back') or contains(@href, 'history.back')] | //button[contains(., 'Back')]")

    # --- Locators Tabel & Baris Feedback ---
    TABLE              = (By.TAG_NAME, "table")
    TABLE_HEADERS      = (By.XPATH, "//table//th")
    TABLE_ROWS         = (By.XPATH, "//table//tbody/tr")
    RADIO_ROWS         = (By.XPATH, "//input[@type='radio' and contains(@name, 'selected')]")

    def __init__(self, driver):
        super().__init__(driver)

    # --- Navigasi Halaman & Sub-Halaman ---
    def navigate_driver(self):
        """Membuka halaman Driver Feedback Management."""
        self.open(Config.FEEDBACK_DRIVER_URL)

    def navigate_user(self):
        """Membuka sub-halaman User Feedback Management."""
        self.open(Config.FEEDBACK_USER_URL)

    def navigate_detail(self):
        """Membuka detail feedback pertama yang ada di daftar Driver Feedback environment aktif.

        Mengembalikan False bila daftar tidak punya tautan detail (data feedback belum ada).
        ID detail tidak ditulis tetap karena ID production (mis. 81) tidak ada di staging.
        """
        self.navigate_driver()
        links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='lookDetail']")
        if not links:
            return False
        self.open(links[0].get_attribute("href"))
        return True

    # --- Operasi Pencarian & Filter Driver Feedback ---
    def filter_driver_feedback(self, driver_name=None, driver_phone=None, state=None):
        """Melakukan filter data pada halaman Driver Feedback."""
        if driver_name:
            self.type_text(self.INPUT_DRIVER_NAME, driver_name)
        if driver_phone:
            self.type_text(self.INPUT_DRIVER_PHONE, driver_phone)
        if state is not None:
            elem = self.find(self.SELECT_STATE)
            select = Select(elem)
            select.select_by_value(str(state))
        self.click(self.BTN_SEARCH)
        time.sleep(1)

    # --- Operasi Pencarian & Filter User Feedback ---
    def filter_user_feedback(self, user_name=None, user_phone=None, state=None):
        """Melakukan filter data pada halaman User Feedback."""
        if user_name:
            self.type_text(self.INPUT_USER_NAME, user_name)
        if user_phone:
            self.type_text(self.INPUT_USER_PHONE, user_phone)
        if state is not None:
            elem = self.find(self.SELECT_STATE)
            select = Select(elem)
            select.select_by_value(str(state))
        self.click(self.BTN_SEARCH)
        time.sleep(1)

    def filter_by_date(self, base_url, begin_date, end_date):
        """Filter rentang waktu pada feedback management."""
        url = f"{base_url}?beginTime={begin_date}&endTime={end_date}"
        self.open(url)
        time.sleep(1)

    def click_reset_driver(self):
        """Klik tombol Reset pada halaman Driver Feedback."""
        btn = self.find(self.LINK_RESET_DRIVER, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    def click_reset_user(self):
        """Klik tombol Reset pada halaman User Feedback."""
        btn = self.find(self.LINK_RESET_USER, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    # --- Verifikasi Tabel & Elemen ---
    def is_table_displayed(self):
        """Memeriksa apakah tabel daftar umpan balik terlihat di layar."""
        return self.is_displayed(self.TABLE)

    def get_table_header_texts(self):
        """Mengambil daftar teks header kolom tabel."""
        headers = self.find_all(self.TABLE_HEADERS)
        return [h.text.strip() for h in headers if h.text.strip()]

    def is_process_btn_enabled(self):
        """Memeriksa apakah tombol Immediately process aktif (default: False terkunci)."""
        return self.is_enabled(self.BTN_PROCESS)

    def is_process_btn_present(self):
        """Memeriksa apakah tombol Immediately process hadir di DOM."""
        elems = self.find_all(self.BTN_PROCESS)
        return len(elems) > 0

    def select_first_item_radio(self):
        """Memilih baris umpan balik pertama menggunakan radio button."""
        radios = self.find_all(self.RADIO_ROWS)
        if radios:
            self.driver.execute_script("arguments[0].click();", radios[0])
            time.sleep(0.5)
            return True
        return False
