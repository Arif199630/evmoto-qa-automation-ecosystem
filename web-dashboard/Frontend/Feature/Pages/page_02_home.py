"""
Home / Dashboard Page Object
Website: <BASE_URL>/blackboard
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config


class HomePage(BasePage):
    """Page Object untuk Halaman Beranda (Home Page / Dashboard)."""

    # Locators Elemen ID / XPath / CSS Selector Halaman Beranda
    LOCATOR_THEME_TOGGLE     = (By.CSS_SELECTOR, "button.theme-toggle")
    LOCATOR_PROFILE_TRIGGER  = (By.CSS_SELECTOR, "[data-profile-trigger]")
    LOCATOR_PROFILE_DROPDOWN = (By.CSS_SELECTOR, "[data-profile-dropdown]")
    LOCATOR_LOGOUT_BTN       = (By.CSS_SELECTOR, "form[action*='logout'] button[type='submit']")
    LOCATOR_OPS_FILTER_FORM  = (By.ID, "ops-filter-form")
    LOCATOR_DATE_INPUT       = (By.NAME, "opDate")
    LOCATOR_COMPANY_INPUT    = (By.NAME, "companyId")
    LOCATOR_FILTER_SUBMIT    = (By.CSS_SELECTOR, "#ops-filter-form button[type='submit']")

    PAGE_PATH = "/blackboard"

    def navigate(self, url_or_path=None):
        """Buka halaman beranda secara dinamis (menggunakan Config.HOME_URL atau custom)."""
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def has_todays_operation_widget(self):
        """Periksa apakah widget Today's operation muncul."""
        return "Today's operation" in self.get_page_source()

    def has_total_operational_widget(self):
        """Periksa apakah widget Total operational data muncul."""
        return "Total operational data" in self.get_page_source()

    def has_general_trend_widget(self):
        """Periksa apakah widget General operating trend muncul."""
        return "General operating trend" in self.get_page_source()

    def filter_operational_data(self, date_str="2026-10-10", company_id="1"):
        """Mengisi tanggal dan Company ID lalu mengklik tombol filter secara andal."""
        date_input = self.find_visible(self.LOCATOR_DATE_INPUT)
        self.set_value_js(date_input, date_str)

        self.type_text(self.LOCATOR_COMPANY_INPUT, company_id)

        filter_btn = self.find(self.LOCATOR_FILTER_SUBMIT)
        self.driver.execute_script(
            "arguments[0].removeAttribute('disabled'); arguments[0].disabled = false; arguments[0].click();",
            filter_btn
        )

    def toggle_theme(self):
        """Klik tombol switch tema Dark / Light Mode."""
        self.click(self.LOCATOR_THEME_TOGGLE)

    def is_dark_theme(self):
        """Memeriksa apakah tema saat ini adalah Dark Mode."""
        html_elem = self.driver.find_element(By.TAG_NAME, "html")
        classes = html_elem.get_attribute("class") or ""
        return "dark" in classes

    def open_profile_dropdown(self):
        """Buka menu dropdown profil."""
        self.click(self.LOCATOR_PROFILE_TRIGGER)

    def is_profile_dropdown_hidden(self):
        """Memeriksa apakah dropdown profil memiliki atribut hidden."""
        dropdown = self.find(self.LOCATOR_PROFILE_DROPDOWN)
        return not dropdown.is_displayed()

    def is_logout_button_displayed(self):
        """Memeriksa tombol logout tampil."""
        return self.is_displayed(self.LOCATOR_LOGOUT_BTN)

    def get_company_id_min(self):
        """Mengambil atribut min dari field company-id."""
        return self.get_attribute(self.LOCATOR_COMPANY_INPUT, "min")

    def set_company_id(self, val):
        """Mengisi company-id."""
        self.type_text(self.LOCATOR_COMPANY_INPUT, val)

    def click_filter_button(self):
        """Klik tombol filter form."""
        self.find(self.LOCATOR_FILTER_SUBMIT).click()

    def filter_by_date(self, start_date="2026-01-01", end_date="2026-12-31"):
        """Filter data operasional berdasarkan tanggal."""
        self.driver.get(f"{Config.HOME_URL}?beginDate={start_date}&endDate={end_date}&start={start_date}&end={end_date}")

    def logout(self):
        """Melakukan logout dari dashboard."""
        try:
            self.open_profile_dropdown()
            logout_btn = self.find(self.LOCATOR_LOGOUT_BTN)
            self.driver.execute_script("arguments[0].closest('form').submit();", logout_btn)
        except Exception:
            self.driver.get(f"{Config.BASE_URL}/logout")

    def get_company_id_validation_message(self):
        """Mengambil pesan validasi form HTML5 company-id."""
        return self.get_attribute(self.LOCATOR_COMPANY_INPUT, "validationMessage")


# Backward compatibility alias
HomeLocators = HomePage

