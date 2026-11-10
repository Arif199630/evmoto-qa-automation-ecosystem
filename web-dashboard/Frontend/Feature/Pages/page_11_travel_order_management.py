"""
Travel Order Management Page Object
Website: <BASE_URL>/tOrderPrivateCar & /tOrderLogistics
Sub-Halaman:
  1. Motorcycle Orders (/tOrderPrivateCar)
  2. City Express Orders / Intra-city Express Delivery of Orders (/tOrderLogistics)
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class TravelOrderPage(BasePage):
    """Page Object untuk Modul Travel Order Management beserta sub-halamannya."""

    # =========================================================================
    # 1. MOTORCYCLE ORDERS (/tOrderPrivateCar)
    # =========================================================================
    LOCATOR_MC_HEADING             = (By.TAG_NAME, "h1")
    LOCATOR_MC_BEGIN_DATE          = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='beginDate']")
    LOCATOR_MC_END_DATE            = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='endDate']")
    LOCATOR_MC_ORDER_NUM           = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='orderNum']")
    LOCATOR_MC_ORDER_SOURCE        = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] select[name='orderSource']")
    LOCATOR_MC_USER_NAME           = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='userName']")
    LOCATOR_MC_USER_PHONE          = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='userPhone']")
    LOCATOR_MC_PASSENGERS          = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='passengers']")
    LOCATOR_MC_PASSENGERS_PHONE    = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='passengersPhone']")
    LOCATOR_MC_CAR_MODEL           = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] select[name='serverCarModelId']")
    LOCATOR_MC_DRIVER              = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] input[name='driver']")
    LOCATOR_MC_STATE               = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] select[name='state']")
    LOCATOR_MC_SEARCH_BTN          = (By.CSS_SELECTOR, "form[action='/tOrderPrivateCar'] button[type='submit']")

    LOCATOR_MC_TABLE               = (By.TAG_NAME, "table")
    LOCATOR_MC_ROWS                = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_MC_VIEW_DETAILS_BTN    = (By.XPATH, "//button[normalize-space()='View details']")
    LOCATOR_MC_CANCEL_BTN          = (By.XPATH, "//button[normalize-space()='Cancel order']")
    LOCATOR_MC_DELETE_BTN          = (By.XPATH, "//button[normalize-space()='Delete']")

    def navigate_motorcycle_orders(self):
        """Buka sub-halaman Motorcycle Orders (/tOrderPrivateCar)."""
        self.open(Config.ORDER_MOTORCYCLE_URL)

    def is_motorcycle_table_displayed(self):
        """Memeriksa apakah tabel pesanan motor tampil di layar."""
        return self.is_displayed(self.LOCATOR_MC_TABLE)

    def get_motorcycle_rows_count(self):
        """Menghitung baris data pesanan motor pada tabel."""
        rows = self.find_all(self.LOCATOR_MC_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def search_motorcycle_by_order_num(self, order_num):
        """Cari pesanan motor berdasarkan nomor order."""
        self.type_text(self.LOCATOR_MC_ORDER_NUM, order_num)
        self.click(self.LOCATOR_MC_SEARCH_BTN)

    def search_motorcycle_by_user_phone(self, phone):
        """Cari pesanan motor berdasarkan nomor HP pemesan."""
        self.type_text(self.LOCATOR_MC_USER_PHONE, phone)
        self.click(self.LOCATOR_MC_SEARCH_BTN)

    def search_motorcycle_by_driver(self, driver_name):
        """Cari pesanan motor berdasarkan nama driver."""
        self.type_text(self.LOCATOR_MC_DRIVER, driver_name)
        self.click(self.LOCATOR_MC_SEARCH_BTN)

    def filter_motorcycle_by_source(self, source_val="1"):
        """Filter sumber pesanan (1=APP order, 2=Scan code, 3=Mini program, 4=Driver, 5=Dispatch)."""
        self.select_dropdown_by_value(self.LOCATOR_MC_ORDER_SOURCE, source_val)
        self.click(self.LOCATOR_MC_SEARCH_BTN)

    def filter_motorcycle_by_state(self, state_val="9"):
        """Filter status pesanan (9=Completed, 10=Cancelled, 1=Waiting for accept)."""
        self.select_dropdown_by_value(self.LOCATOR_MC_STATE, state_val)
        self.click(self.LOCATOR_MC_SEARCH_BTN)

    def filter_motorcycle_by_date(self, start_date, end_date):
        """Filter rentang tanggal pesanan motor."""
        self.driver.get(f"{Config.ORDER_MOTORCYCLE_URL}?beginDate={start_date}&endDate={end_date}")

    def is_motorcycle_details_btn_enabled(self):
        """Memeriksa status tombol View details (harus disabled sebelum memilih order)."""
        return self.is_enabled(self.LOCATOR_MC_VIEW_DETAILS_BTN)

    def is_motorcycle_cancel_btn_enabled(self):
        """Memeriksa status tombol Cancel order (harus disabled sebelum memilih order)."""
        return self.is_enabled(self.LOCATOR_MC_CANCEL_BTN)

    def is_motorcycle_delete_btn_enabled(self):
        """Memeriksa status tombol Delete (harus disabled sebelum memilih order)."""
        return self.is_enabled(self.LOCATOR_MC_DELETE_BTN)

    # =========================================================================
    # 2. CITY EXPRESS ORDERS / LOGISTICS (/tOrderLogistics)
    # =========================================================================
    LOCATOR_LOG_HEADING            = (By.TAG_NAME, "h1")
    LOCATOR_LOG_BEGIN_DATE         = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='beginDate']")
    LOCATOR_LOG_END_DATE           = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='endDate']")
    LOCATOR_LOG_ORDER_NUM          = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='orderNum']")
    LOCATOR_LOG_ORDER_SOURCE       = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] select[name='orderSource']")
    LOCATOR_LOG_USER_NAME          = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='userName']")
    LOCATOR_LOG_USER_PHONE         = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='userPhone']")
    LOCATOR_LOG_RECIPIENT          = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='recipient']")
    LOCATOR_LOG_RECIPIENT_PHONE    = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='recipientPhone']")
    LOCATOR_LOG_DRIVER             = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] input[name='driver']")
    LOCATOR_LOG_STATE              = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] select[name='state']")
    LOCATOR_LOG_SEARCH_BTN         = (By.CSS_SELECTOR, "form[action='/tOrderLogistics'] button[type='submit']")

    LOCATOR_LOG_TABLE              = (By.TAG_NAME, "table")
    LOCATOR_LOG_ROWS               = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_LOG_VIEW_DETAILS_BTN   = (By.XPATH, "//button[normalize-space()='View details']")
    LOCATOR_LOG_CANCEL_BTN         = (By.XPATH, "//button[normalize-space()='Cancel order']")
    LOCATOR_LOG_DELETE_BTN         = (By.XPATH, "//button[normalize-space()='Delete']")

    def navigate_logistics_orders(self):
        """Buka sub-halaman City Express Orders (/tOrderLogistics)."""
        self.open(Config.ORDER_LOGISTICS_URL)

    def is_logistics_table_displayed(self):
        """Memeriksa apakah tabel pesanan express tampil di layar."""
        return self.is_displayed(self.LOCATOR_LOG_TABLE)

    def get_logistics_rows_count(self):
        """Menghitung baris data pesanan express pada tabel."""
        rows = self.find_all(self.LOCATOR_LOG_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def search_logistics_by_order_num(self, order_num):
        """Cari pesanan ekspres berdasarkan nomor order."""
        self.type_text(self.LOCATOR_LOG_ORDER_NUM, order_num)
        self.click(self.LOCATOR_LOG_SEARCH_BTN)

    def search_logistics_by_recipient(self, recipient_name):
        """Cari pesanan ekspres berdasarkan nama penerima."""
        self.type_text(self.LOCATOR_LOG_RECIPIENT, recipient_name)
        self.click(self.LOCATOR_LOG_SEARCH_BTN)

    def search_logistics_by_recipient_phone(self, phone):
        """Cari pesanan ekspres berdasarkan nomor telepon penerima."""
        self.type_text(self.LOCATOR_LOG_RECIPIENT_PHONE, phone)
        self.click(self.LOCATOR_LOG_SEARCH_BTN)

    def filter_logistics_by_source(self, source_val="1"):
        """Filter sumber pesanan ekspres."""
        self.select_dropdown_by_value(self.LOCATOR_LOG_ORDER_SOURCE, source_val)
        self.click(self.LOCATOR_LOG_SEARCH_BTN)

    def filter_logistics_by_state(self, state_val="9"):
        """Filter status pesanan ekspres."""
        self.select_dropdown_by_value(self.LOCATOR_LOG_STATE, state_val)
        self.click(self.LOCATOR_LOG_SEARCH_BTN)

    def filter_logistics_by_date(self, start_date, end_date):
        """Filter rentang tanggal pesanan ekspres."""
        self.driver.get(f"{Config.ORDER_LOGISTICS_URL}?beginDate={start_date}&endDate={end_date}")

    def is_logistics_details_btn_enabled(self):
        """Memeriksa status tombol View details (harus disabled sebelum memilih order)."""
        return self.is_enabled(self.LOCATOR_LOG_VIEW_DETAILS_BTN)

    def is_logistics_cancel_btn_enabled(self):
        """Memeriksa status tombol Cancel order (harus disabled sebelum memilih order)."""
        return self.is_enabled(self.LOCATOR_LOG_CANCEL_BTN)

    def is_logistics_delete_btn_enabled(self):
        """Memeriksa status tombol Delete (harus disabled sebelum memilih order)."""
        return self.is_enabled(self.LOCATOR_LOG_DELETE_BTN)
