"""
Agreement & Basic Information Management Page Object
Website: <BASE_URL>/tAgreement & Sub-Halamannya
Automation Project EvMoto
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .page_base import BasePage
from config import Config


class AgreementPage(BasePage):
    """Page Object untuk Modul Agreement Management & Sub-Halamannya."""

    # Selectors Umum
    LOCATOR_LANG_SELECT         = (By.CSS_SELECTOR, "select#agreement-language, select[data-agreement-language]")
    LOCATOR_PANEL_CHINESE       = (By.CSS_SELECTOR, "section[data-agreement-panel='1']")
    LOCATOR_PANEL_ENGLISH       = (By.CSS_SELECTOR, "section[data-agreement-panel='2']")
    LOCATOR_PANEL_INDONESIAN    = (By.CSS_SELECTOR, "section[data-agreement-panel='3']")

    # Selectors Protocol Management
    LOCATOR_CATEGORY_SELECT     = (By.CSS_SELECTOR, "select#agreement-category, select[data-management-category]")
    LOCATOR_AUDIENCE_SELECT     = (By.CSS_SELECTOR, "select#agreement-audience, select[data-management-audience]")
    LOCATOR_MGMT_LANG_SELECT    = (By.CSS_SELECTOR, "select#agreement-management-language, select[data-management-language]")

    # Navigasi URL
    def navigate_logistics(self):
        self.open(Config.LOGISTICS_URL)

    def navigate_protocol(self):
        self.open(Config.AGREEMENT_BASE_URL)

    def navigate_order(self):
        self.open(Config.ORDER_AGREEMENT_URL)

    def navigate_user_guide(self):
        self.open(Config.USER_GUIDE_URL)

    def navigate_law(self):
        self.open(Config.LAW_URL)

    def navigate_about(self):
        self.open(Config.ABOUT_URL)

    def get_h2_text(self):
        """Ambil teks header h2."""
        return self.get_text((By.CSS_SELECTOR, "h2"))

    def get_selected_language_value(self):
        """Ambil nilai bahasa yang sedang terpilih."""
        select_el = self.find_visible(self.LOCATOR_LANG_SELECT)
        select_obj = Select(select_el)
        return select_obj.first_selected_option.get_attribute("value")

    def get_selected_language_text(self):
        """Ambil teks label bahasa yang sedang terpilih."""
        select_el = self.find_visible(self.LOCATOR_LANG_SELECT)
        select_obj = Select(select_el)
        return select_obj.first_selected_option.text.strip()

    def switch_language(self, value):
        """Ganti bahasa panel via select dan dispatch event change."""
        select_el = self.find_visible(self.LOCATOR_LANG_SELECT)
        select_obj = Select(select_el)
        select_obj.select_by_value(str(value))
        self.dispatch_event(select_el, "change")
        time.sleep(1)

    def is_panel_chinese_hidden(self):
        """Periksa apakah panel Chinese tersembunyi (hidden)."""
        panel = self.find(self.LOCATOR_PANEL_CHINESE)
        return bool(panel.get_attribute("hidden"))

    def is_panel_english_hidden(self):
        """Periksa apakah panel English tersembunyi (hidden)."""
        panel = self.find(self.LOCATOR_PANEL_ENGLISH)
        return bool(panel.get_attribute("hidden"))

    def is_panel_indonesian_hidden(self):
        """Periksa apakah panel Indonesian tersembunyi (hidden)."""
        panel = self.find(self.LOCATOR_PANEL_INDONESIAN)
        return bool(panel.get_attribute("hidden"))

    def get_toolbar_button_titles(self):
        """Mengambil daftar title/aria-label dari seluruh tombol formatting toolbar panel English."""
        panel_en = self.find_visible(self.LOCATOR_PANEL_ENGLISH)
        buttons = panel_en.find_elements(By.CSS_SELECTOR, "button[type='button']")
        return [b.get_attribute("title") or b.get_attribute("aria-label") or "" for b in buttons]

    def get_english_editor_text(self):
        """Mengambil teks isi dari rich text editor contenteditable."""
        panel_en = self.find_visible(self.LOCATOR_PANEL_ENGLISH)
        editor = panel_en.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
        return editor.text.strip()

    def get_english_textarea_value(self):
        """Mengambil isi textarea hidden pendamping rich text editor."""
        panel_en = self.find(self.LOCATOR_PANEL_ENGLISH)
        textarea = panel_en.find_element(By.CSS_SELECTOR, "textarea[name='context']")
        return textarea.get_attribute("value") or ""

    def get_english_submit_btn_text(self):
        """Mengambil teks tombol simpan panel English."""
        panel_en = self.find(self.LOCATOR_PANEL_ENGLISH)
        save_btn = panel_en.find_element(By.CSS_SELECTOR, "button[type='submit']")
        return save_btn.text.strip()

    # --- Protocol Management Dropdowns ---
    def get_category_options(self):
        """Mengambil list value kategori agreement yang tersedia."""
        select_el = self.find_visible(self.LOCATOR_CATEGORY_SELECT)
        select_obj = Select(select_el)
        return [opt.get_attribute("value") for opt in select_obj.options]

    def switch_category(self, cat_value):
        """Ganti kategori agreement."""
        select_el = self.find_visible(self.LOCATOR_CATEGORY_SELECT)
        select_obj = Select(select_el)
        select_obj.select_by_value(cat_value)
        self.dispatch_event(select_el, "change")
        time.sleep(0.5)

    def get_selected_category_value(self):
        """Ambil value kategori yang sedang terpilih."""
        select_el = self.find_visible(self.LOCATOR_CATEGORY_SELECT)
        return Select(select_el).first_selected_option.get_attribute("value")

    def switch_audience(self, aud_value):
        """Ganti target audience agreement."""
        select_el = self.find_visible(self.LOCATOR_AUDIENCE_SELECT)
        select_obj = Select(select_el)
        select_obj.select_by_value(str(aud_value))
        self.dispatch_event(select_el, "change")
        time.sleep(0.5)

    def get_selected_audience_value(self):
        """Ambil value audience terpilih."""
        select_el = self.find_visible(self.LOCATOR_AUDIENCE_SELECT)
        return Select(select_el).first_selected_option.get_attribute("value")

    def get_selected_audience_text(self):
        """Ambil label audience terpilih."""
        select_el = self.find_visible(self.LOCATOR_AUDIENCE_SELECT)
        return Select(select_el).first_selected_option.text.strip()

    def get_management_language_options(self):
        """Mengambil opsi bahasa pada halaman protocol management."""
        select_el = self.find_visible(self.LOCATOR_MGMT_LANG_SELECT)
        return [opt.get_attribute("value") for opt in Select(select_el).options]

    def switch_management_language(self, lang_value):
        """Ganti bahasa pada halaman protocol management."""
        select_el = self.find_visible(self.LOCATOR_MGMT_LANG_SELECT)
        select_obj = Select(select_el)
        select_obj.select_by_value(str(lang_value))
        self.dispatch_event(select_el, "change")
        time.sleep(0.5)

    def get_selected_management_language_value(self):
        """Ambil value bahasa terpilih pada protocol management."""
        select_el = self.find_visible(self.LOCATOR_MGMT_LANG_SELECT)
        return Select(select_el).first_selected_option.get_attribute("value")
