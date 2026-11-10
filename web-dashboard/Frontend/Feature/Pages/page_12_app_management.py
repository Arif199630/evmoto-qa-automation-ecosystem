"""
App Management Page Object
Website: <BASE_URL>/TChatSet, /tbBanner, /TVoice
Sub-Halaman:
  1. Chat Message Preset Settings (/TChatSet)
  2. Icon Management (/tbBanner)
  3. Voice Broadcast Management (/TVoice)
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class AppManagementPage(BasePage):
    """Page Object untuk Modul App Management beserta 3 sub-halamannya."""

    # =========================================================================
    # 1. CHAT MESSAGE PRESET SETTINGS (/TChatSet)
    # =========================================================================
    LOCATOR_CHAT_HEADING       = (By.TAG_NAME, "h1")
    LOCATOR_CHAT_BEGIN_DATE    = (By.CSS_SELECTOR, "form[action*='/TChatSet'] input[name='beginDate']")
    LOCATOR_CHAT_END_DATE      = (By.CSS_SELECTOR, "form[action*='/TChatSet'] input[name='endDate']")
    LOCATOR_CHAT_TYPE_SELECT   = (By.CSS_SELECTOR, "form[action*='/TChatSet'] select[name='type']")
    LOCATOR_CHAT_LANG_SELECT   = (By.CSS_SELECTOR, "form[action*='/TChatSet'] select[name='yy']")
    LOCATOR_CHAT_SEARCH_BTN    = (By.CSS_SELECTOR, "form[action*='/TChatSet'] button[type='submit']")

    LOCATOR_CHAT_TABLE         = (By.TAG_NAME, "table")
    LOCATOR_CHAT_ROWS          = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_CHAT_UPDATE_BTN    = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_CHAT_DELETE_BTN    = (By.XPATH, "//button[normalize-space()='Delete']")

    def navigate_chat_set(self):
        """Membuka halaman Chat Message Preset Settings (/TChatSet)."""
        self.open(Config.CHAT_SET_URL)

    def is_chat_table_displayed(self):
        """Memeriksa apakah tabel preset pesan chat tampil di layar."""
        return self.is_displayed(self.LOCATOR_CHAT_TABLE)

    def get_chat_rows_count(self):
        """Menghitung baris data preset pesan chat pada tabel."""
        rows = self.find_all(self.LOCATOR_CHAT_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def filter_chat_by_type(self, type_val="2"):
        """Filter tipe penerima pesan chat (2=User, 1=Driver)."""
        self.select_dropdown_by_value(self.LOCATOR_CHAT_TYPE_SELECT, type_val)
        self.click(self.LOCATOR_CHAT_SEARCH_BTN)

    def filter_chat_by_language(self, lang_val="3"):
        """Filter bahasa preset chat (1=Chinese, 2=English, 3=Indonesian)."""
        self.select_dropdown_by_value(self.LOCATOR_CHAT_LANG_SELECT, lang_val)
        self.click(self.LOCATOR_CHAT_SEARCH_BTN)

    def filter_chat_by_date(self, start_date, end_date):
        """Filter rentang tanggal preset chat."""
        self.driver.get(f"{Config.CHAT_SET_URL}?beginDate={start_date}&endDate={end_date}")

    def is_chat_update_btn_enabled(self):
        """Memeriksa apakah tombol Update preset chat berstatus enabled/disabled."""
        return self.is_enabled(self.LOCATOR_CHAT_UPDATE_BTN)

    def is_chat_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete preset chat berstatus enabled/disabled."""
        return self.is_enabled(self.LOCATOR_CHAT_DELETE_BTN)

    # =========================================================================
    # 2. ICON MANAGEMENT (/tbBanner)
    # =========================================================================
    LOCATOR_ICON_HEADING       = (By.TAG_NAME, "h1")
    LOCATOR_ICON_TABLE         = (By.TAG_NAME, "table")
    LOCATOR_ICON_ROWS          = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_ICON_UPDATE_BTN    = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_ICON_DELETE_BTN    = (By.XPATH, "//button[normalize-space()='Delete']")

    def navigate_icon_mgmt(self):
        """Membuka halaman Icon Management (/tbBanner)."""
        self.open(Config.ICON_MGMT_URL)

    def is_icon_table_displayed(self):
        """Memeriksa apakah tabel ikon aplikasi tampil di layar."""
        return self.is_displayed(self.LOCATOR_ICON_TABLE)

    def get_icon_rows_count(self):
        """Menghitung baris data ikon aplikasi pada tabel."""
        rows = self.find_all(self.LOCATOR_ICON_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def is_icon_update_btn_enabled(self):
        """Memeriksa apakah tombol Update ikon aplikasi berstatus enabled/disabled."""
        return self.is_enabled(self.LOCATOR_ICON_UPDATE_BTN)

    def is_icon_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete ikon aplikasi berstatus enabled/disabled."""
        return self.is_enabled(self.LOCATOR_ICON_DELETE_BTN)

    # =========================================================================
    # 3. VOICE BROADCAST MANAGEMENT (/TVoice)
    # =========================================================================
    LOCATOR_VOICE_HEADING      = (By.TAG_NAME, "h1")
    LOCATOR_VOICE_NAME_INPUT   = (By.CSS_SELECTOR, "form[action*='/TVoice'] input[name='name']")
    LOCATOR_VOICE_LANG_SELECT  = (By.CSS_SELECTOR, "form[action*='/TVoice'] select[name='language']")
    LOCATOR_VOICE_SEARCH_BTN   = (By.CSS_SELECTOR, "form[action*='/TVoice'] button[type='submit']")

    LOCATOR_VOICE_TABLE        = (By.TAG_NAME, "table")
    LOCATOR_VOICE_ROWS         = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_VOICE_UPDATE_BTN   = (By.XPATH, "//button[normalize-space()='Update']")
    LOCATOR_VOICE_DELETE_BTN   = (By.XPATH, "//button[normalize-space()='Delete']")

    def navigate_voice_broadcast(self):
        """Membuka halaman Voice Broadcast Management (/TVoice)."""
        self.open(Config.VOICE_BROADCAST_URL)

    def is_voice_table_displayed(self):
        """Memeriksa apakah tabel rekaman suara voice broadcast tampil di layar."""
        return self.is_displayed(self.LOCATOR_VOICE_TABLE)

    def get_voice_rows_count(self):
        """Menghitung baris data rekaman suara pada tabel."""
        rows = self.find_all(self.LOCATOR_VOICE_ROWS)
        valid = [r for r in rows if "no " not in r.text.lower() and "tidak ada" not in r.text.lower()]
        return len(valid)

    def search_voice_by_name(self, name):
        """Mencari rekaman suara berdasarkan nama file/keterangan suara."""
        self.type_text(self.LOCATOR_VOICE_NAME_INPUT, name)
        self.click(self.LOCATOR_VOICE_SEARCH_BTN)

    def filter_voice_by_language(self, lang_val="3"):
        """Filter bahasa voice broadcast (1=Chinese, 2=English, 3=Indonesian)."""
        self.select_dropdown_by_value(self.LOCATOR_VOICE_LANG_SELECT, lang_val)
        self.click(self.LOCATOR_VOICE_SEARCH_BTN)

    def is_voice_update_btn_enabled(self):
        """Memeriksa apakah tombol Update suara berstatus enabled/disabled."""
        return self.is_enabled(self.LOCATOR_VOICE_UPDATE_BTN)

    def is_voice_delete_btn_enabled(self):
        """Memeriksa apakah tombol Delete suara berstatus enabled/disabled."""
        return self.is_enabled(self.LOCATOR_VOICE_DELETE_BTN)
