"""
Login Page Object
Website: <BASE_URL>/login
Automation Project EvMoto
"""

from selenium.webdriver.common.by import By
from .page_base import BasePage
from config import Config
from Data.user_data import UserDataProvider


class LoginPage(BasePage):
    """Page Object untuk Halaman Login EvMoto Admin."""

    # Path relatif standar untuk halaman login
    PAGE_PATH = "/login"

    # Locators Elemen ID / XPath / CSS Selector Halaman Login Dashboard
    LOCATOR_USERNAME        = (By.ID, "username")
    LOCATOR_PASSWORD        = (By.ID, "password")
    LOCATOR_SUBMIT_BTN      = (By.CSS_SELECTOR, "button[type='submit']")
    LOCATOR_ERROR_MSG       = (By.CSS_SELECTOR, "[data-login-error]")
    LOCATOR_DASHBOARD_SHELL = (By.CSS_SELECTOR, "[data-dashboard-shell]")
    LOCATOR_REMEMBER_ME     = (By.CSS_SELECTOR, "input[type='checkbox']")
    LOCATOR_FORGOT_PASSWORD = (By.LINK_TEXT, "Forgot Password?")
    LOCATOR_LOGO            = (By.CSS_SELECTOR, ".login-logo, img.logo")

    @property
    def url(self):
        """URL lengkap halaman login yang dievaluasi secara dinamis."""
        return Config.get_url(self.PAGE_PATH)

    def navigate(self, url_or_path=None):
        """
        Buka halaman login secara dinamis.
        - None                       : Menggunakan Config.LOGIN_URL aktif.
        - 'http://...' / 'https://...': Membuka custom URL langsung.
        - '/path'                    : Menggabungkan relative path dengan BASE_URL aktif.
        """
        target = url_or_path if url_or_path is not None else self.PAGE_PATH
        self.open(target)

    def enter_credentials(self, username=None, password=None):
        """Isi username dan/atau password."""
        if username is not None:
            self.type_text(self.LOCATOR_USERNAME, username)
        if password is not None:
            self.type_text(self.LOCATOR_PASSWORD, password)

    def click_submit(self):
        """Klik tombol submit login."""
        self.click(self.LOCATOR_SUBMIT_BTN)

    def login(self, username, password):
        """Alur lengkap memasukkan kredensial dan menekan tombol login."""
        self.enter_credentials(username, password)
        self.click_submit()

    def login_as_admin(self, url_or_path=None, username=None, password=None):
        """
        Helper praktis untuk login sebagai admin valid dan tunggu sampai dashboard termuat.
        Mendukung custom target URL dan kredensial kustom jika diperlukan.
        """
        self.navigate(url_or_path)
        if username is None or password is None:
            default_user, default_pass = UserDataProvider.get_credentials("super_admin")
            user = username if username is not None else default_user
            pwd = password if password is not None else default_pass
        else:
            user = username
            pwd = password
        self.login(user, pwd)
        self.wait_for_url_contains("/blackboard")

    def get_error_message(self):
        """Mengambil teks pesan error login jika kredensial salah."""
        return self.get_text(self.LOCATOR_ERROR_MSG)

    def is_dashboard_displayed(self):
        """Memeriksa apakah dashboard shell tampil setelah login berhasil."""
        return self.is_displayed(self.LOCATOR_DASHBOARD_SHELL)

    def get_username_validation_message(self):
        """Mengambil pesan validasi HTML5 bawaan browser pada field username."""
        element = self.find(self.LOCATOR_USERNAME)
        return element.get_attribute("validationMessage")

    def get_password_validation_message(self):
        """Mengambil pesan validasi HTML5 bawaan browser pada field password."""
        element = self.find(self.LOCATOR_PASSWORD)
        return element.get_attribute("validationMessage")


# Backward compatibility alias
LoginLocators = LoginPage

