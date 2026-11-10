"""
Comment Management Page Object
Website: <BASE_URL>/tOrderEvaluate
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class CommentPage(BasePage):
    """Page Object untuk Modul Comment Management (/tOrderEvaluate)."""

    LOCATOR_COMMENT_HEADING       = (By.TAG_NAME, "h1")
    LOCATOR_COMMENT_BEGIN_TIME    = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] input[name='beginTime']")
    LOCATOR_COMMENT_END_TIME      = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] input[name='endTime']")
    LOCATOR_COMMENT_USER_NAME     = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] input[name='userName']")
    LOCATOR_COMMENT_DRIVER_NAME   = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] input[name='driverName']")
    LOCATOR_COMMENT_ORDER_NUM     = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] input[name='orderNum']")
    LOCATOR_COMMENT_ORDER_TYPE    = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] select[name='orderType']")
    LOCATOR_COMMENT_FRACTION      = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] input[name='fraction']")
    LOCATOR_COMMENT_SEARCH_BTN    = (By.CSS_SELECTOR, "form[action*='/tOrderEvaluate'] button[type='submit']")

    LOCATOR_COMMENT_TABLE         = (By.TAG_NAME, "table")
    LOCATOR_COMMENT_ROWS          = (By.CSS_SELECTOR, "table tbody tr")

    PAGE_PATH = "/tOrderEvaluate"

    def navigate(self, url_or_path=None):
        """Membuka halaman Comment Management (/tOrderEvaluate) secara dinamis."""
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def is_table_displayed(self, timeout=10):
        """Memeriksa apakah tabel ulasan/komentar tampil di layar."""
        return self.is_displayed(self.LOCATOR_COMMENT_TABLE, timeout=timeout)

    def get_rows_count(self):
        """Menghitung baris data ulasan pada tabel."""
        rows = self.find_all(self.LOCATOR_COMMENT_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def search_by_user_name(self, user_name):
        """Mencari ulasan berdasarkan nama pengguna/penumpang."""
        self.type_text(self.LOCATOR_COMMENT_USER_NAME, user_name)
        self.click(self.LOCATOR_COMMENT_SEARCH_BTN)

    def search_by_driver_name(self, driver_name):
        """Mencari ulasan berdasarkan nama driver/pengemudi."""
        self.type_text(self.LOCATOR_COMMENT_DRIVER_NAME, driver_name)
        self.click(self.LOCATOR_COMMENT_SEARCH_BTN)

    def search_by_order_num(self, order_num):
        """Mencari ulasan berdasarkan nomor pesanan (Order Number)."""
        self.type_text(self.LOCATOR_COMMENT_ORDER_NUM, order_num)
        self.click(self.LOCATOR_COMMENT_SEARCH_BTN)

    def filter_by_order_type(self, type_val="1"):
        """Filter tipe layanan ulasan (1=motorcycle, 4=Intra-city express delivery)."""
        self.select_dropdown_by_value(self.LOCATOR_COMMENT_ORDER_TYPE, type_val)
        self.click(self.LOCATOR_COMMENT_SEARCH_BTN)

    def filter_by_rating(self, rating="5"):
        """Filter ulasan berdasarkan skor bintang/rating (fraction)."""
        self.type_text(self.LOCATOR_COMMENT_FRACTION, rating)
        self.click(self.LOCATOR_COMMENT_SEARCH_BTN)

    def filter_by_date(self, begin_time, end_time):
        """Filter rentang waktu komentar/ulasan."""
        self.driver.get(f"{Config.COMMENT_URL}?beginTime={begin_time}&endTime={end_time}")
