"""
Enterprise Management Page Object
Website:
 - Enterprise Information : <BASE_URL>/tCompany/admin_update
 - Enterprise Audit List : <BASE_URL>/tCompany/auditPage
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class EnterprisePage(BasePage):
    """Page Object untuk Halaman Enterprise Information & Enterprise Audit List."""

    # Locators Enterprise Information (/tCompany/admin_update)
    LOCATOR_INFO_NAME_INPUT  = (By.ID, "company-name")
    LOCATOR_INFO_SUBMIT_BTN  = (By.CSS_SELECTOR, "[data-company-submit]")
    LOCATOR_INFO_FORM        = (By.CSS_SELECTOR, "form[data-company-form]")
    LOCATOR_CITY_CHECKBOXES  = (By.CSS_SELECTOR, "[data-city-checkbox]")
    LOCATOR_CITY_COUNT       = (By.CSS_SELECTOR, "[data-city-count]")

    # Locators Enterprise Audit List (/tCompany/auditPage)
    LOCATOR_AUDIT_SEARCH_NAME = (By.ID, "audit-company-name")
    LOCATOR_AUDIT_SEARCH_BTN  = (By.CSS_SELECTOR, "form[action='/tCompany/auditPage'] button[type='submit']")
    LOCATOR_AUDIT_TABLE       = (By.TAG_NAME, "table")
    LOCATOR_AUDIT_ROWS        = (By.CSS_SELECTOR, "table tbody tr")
    LOCATOR_AUDIT_ACTION_BTN  = (By.CSS_SELECTOR, "[data-company-audit-action], button[name='audit'], button.audit-btn")
    LOCATOR_AUDIT_CHOICES     = (By.CSS_SELECTOR, "[data-company-audit-choice], table tbody tr input[type='radio'], table tbody tr input[type='checkbox']")

    # --- Enterprise Information (/tCompany/admin_update) ---
    def navigate_info(self):
        """Buka halaman Enterprise Information."""
        self.open(Config.COMPANY_INFO_URL)

    def get_info_heading_text(self):
        """Mengambil teks heading h1 Enterprise Information."""
        return self.get_text((By.TAG_NAME, "h1"))

    def is_info_form_displayed(self):
        """Periksa apakah form perusahaan tampil."""
        return self.is_displayed(self.LOCATOR_INFO_FORM)

    def is_info_submit_btn_displayed(self):
        """Periksa apakah tombol submit tampil."""
        return self.is_displayed(self.LOCATOR_INFO_SUBMIT_BTN)

    def get_city_checkboxes(self):
        """Mengambil semua elemen checkbox pilihan kota."""
        return self.find_all(self.LOCATOR_CITY_CHECKBOXES)

    def get_city_count_text(self):
        """Mengambil teks badge counter kota."""
        return self.get_text(self.LOCATOR_CITY_COUNT)

    def toggle_first_city_checkbox(self):
        """Toggle checkbox kota pertama."""
        boxes = self.get_city_checkboxes()
        if boxes:
            self.click_js(boxes[0])
            self.dispatch_event(boxes[0], "change")
            return True
        return False

    def is_company_name_required(self):
        """Periksa apakah field company-name memiliki atribut required."""
        return self.get_attribute(self.LOCATOR_INFO_NAME_INPUT, "required") is not None

    def clear_company_name(self):
        """Kosongkan nama perusahaan."""
        self.find_visible(self.LOCATOR_INFO_NAME_INPUT).clear()

    def submit_info_form(self):
        """Klik tombol simpan form informasi perusahaan."""
        self.click(self.LOCATOR_INFO_SUBMIT_BTN)

    def get_company_name_validation_message(self):
        """Mengambil pesan validasi form HTML5 company-name."""
        return self.get_attribute(self.LOCATOR_INFO_NAME_INPUT, "validationMessage")

    # --- Enterprise Audit List (/tCompany/auditPage) ---
    def navigate_audit(self):
        """Buka halaman Enterprise Audit List."""
        self.open(Config.COMPANY_AUDIT_URL)

    def get_audit_heading_text(self):
        """Mengambil teks heading h1 Enterprise Audit List."""
        return self.get_text((By.TAG_NAME, "h1"))

    def is_audit_table_displayed(self):
        """Periksa apakah tabel audit tampil."""
        return self.is_displayed(self.LOCATOR_AUDIT_TABLE)

    def is_audit_action_btn_enabled(self):
        """Periksa status enabled tombol Audit."""
        return self.is_enabled(self.LOCATOR_AUDIT_ACTION_BTN)

    def get_audit_rows_count(self):
        """Mengambil jumlah baris data audit."""
        return len(self.find_all(self.LOCATOR_AUDIT_ROWS))

    def search_audit_company(self, name):
        """Cari perusahaan di daftar audit."""
        self.type_text(self.LOCATOR_AUDIT_SEARCH_NAME, name)
        form = self.find((By.CSS_SELECTOR, "form[action='/tCompany/auditPage']"))
        form.submit()

    def select_first_audit_company(self):
        """Pilih radio/checkbox perusahaan audit pertama."""
        choices = self.find_all(self.LOCATOR_AUDIT_CHOICES)
        if choices:
            self.click_js(choices[0])
            self.dispatch_event(choices[0], "change")
            return True
        return False

    def get_audit_choices_count(self):
        """Mengambil jumlah opsi pilihan perusahaan di tabel audit."""
        return len(self.find_all(self.LOCATOR_AUDIT_CHOICES))
