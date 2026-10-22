"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - REGISTER PAGE OBJECT
================================================================================
Target: Layar Pendaftaran Akun Pengguna EVMoto (Flutter App)
Mendukung Bahasa Inggris (Default) dan Bahasa Indonesia.
Urutan Field Sign Up:
1. Phone Number (hint: 'e.g. +62 812-3456-7890')
2. Full Name (hint: 'Enter your full name')
3. OTP Code (hint: 'Enter the OTP code') + Tombol 'Request OTP'
4. Referral Code (hint: 'Enter referral code')
5. Button 'Create Account'
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage

class RegisterPage(BasePage):
    """Page Object untuk Halaman Pendaftaran Akun Pengguna Baru EvMoto."""

    # Locators Elemen ID / XPath Layar Registrasi Pengguna Baru
    TITLE_REGISTER = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Sign Up') or contains(@content-desc, 'Daftar Akun')]")
    FIELD_PHONE = (AppiumBy.XPATH, "(//android.widget.EditText)[1]")
    FIELD_FULL_NAME = (AppiumBy.XPATH, "(//android.widget.EditText)[2]")
    FIELD_OTP = (AppiumBy.XPATH, "(//android.widget.EditText)[3]")
    BTN_REQUEST_OTP = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Request OTP') or contains(@content-desc, 'Minta Kode OTP')]")
    FIELD_REFERRAL = (AppiumBy.XPATH, "(//android.widget.EditText)[4]")
    BTN_SUBMIT_REGISTER = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Create Account') or contains(@content-desc, 'Buat Akun')]")
    BTN_BACK = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Back') or contains(@content-desc, 'Kembali')]")
    LINK_ALREADY_HAVE_ACCOUNT = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Already have an account') or contains(@content-desc, 'Sudah punya akun') or contains(@content-desc, 'Sign In') or contains(@content-desc, 'Masuk')]")
    TITLE_SUCCESS = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Success') or contains(@content-desc, 'Berhasil')]")
    BTN_GO_TO_HOME = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Home') or contains(@content-desc, 'Beranda')]")

    def is_register_screen_displayed(self, timeout: int = 15) -> bool:
        """Memeriksa apakah layar Sign Up aktif."""
        return self.is_displayed(self.TITLE_REGISTER, timeout=timeout)

    def fill_phone(self, phone: str):
        """Mengisi nomor telepon (misal: 81299990001)."""
        self.type_text(self.FIELD_PHONE, phone, label="Nomor Telepon Dev")

    def fill_name(self, name: str):
        """Mengisi nama lengkap."""
        self.type_text(self.FIELD_FULL_NAME, name, label="Nama Lengkap")
        try:
            self.driver.hide_keyboard()
        except Exception:
            try:
                self.driver.press_keycode(4)
            except Exception:
                pass
        time.sleep(0.5)

    def request_otp(self):
        """Menekan tombol 'Request OTP'."""
        try:
            self.driver.hide_keyboard()
        except Exception:
            try:
                self.driver.press_keycode(4)
            except Exception:
                pass
        time.sleep(0.5)
        self.click(self.BTN_REQUEST_OTP, label="Tombol 'Request OTP'")

    def fill_otp(self, otp_code: str = "1234"):
        """Mengisi kode OTP (default dev: 1234)."""
        self.type_text(self.FIELD_OTP, otp_code, label=f"Kode OTP Dev ({otp_code})")
        try:
            self.driver.hide_keyboard()
        except Exception:
            try:
                self.driver.press_keycode(4)
            except Exception:
                pass
        time.sleep(0.5)

    def fill_referral(self, referral: str):
        """Mengisi kode referral."""
        if referral:
            self.type_text(self.FIELD_REFERRAL, referral, label="Kode Referral")

    def submit_register(self):
        """Menekan tombol 'Create Account'."""
        try:
            self.driver.hide_keyboard()
        except Exception:
            try:
                self.driver.press_keycode(4)
            except Exception:
                pass
        time.sleep(0.5)
        self.click(self.BTN_SUBMIT_REGISTER, label="Tombol 'Create Account'")

    def clear_phone(self):
        """Mengosongkan field nomor telepon."""
        field = self.find(self.FIELD_PHONE)
        field.click()
        field.clear()

    def clear_name(self):
        """Mengosongkan field nama lengkap."""
        field = self.find(self.FIELD_FULL_NAME)
        field.click()
        field.clear()

    def get_phone_value(self) -> str:
        """Mengambil teks nilai pada field nomor telepon."""
        return self.get_text(self.FIELD_PHONE)

    def get_name_value(self) -> str:
        """Mengambil teks nilai pada field nama lengkap."""
        return self.get_text(self.FIELD_FULL_NAME)

    def is_create_account_enabled(self) -> bool:
        """Memeriksa apakah tombol 'Create Account' aktif."""
        btn = self.find(self.BTN_SUBMIT_REGISTER)
        return btn.is_enabled()

    def is_error_displayed(self, text_snippet: str = "", timeout: int = 5) -> bool:
        """Memeriksa apakah pesan kesalahan validasi muncul di layar."""
        if not text_snippet:
            loc = (AppiumBy.XPATH, "//*[contains(@content-desc, 'error') or contains(@content-desc, 'salah') or contains(@content-desc, 'invalid') or contains(@content-desc, 'wajib')]")
        else:
            loc = (AppiumBy.XPATH, f"//*[contains(@content-desc, '{text_snippet}') or contains(@text, '{text_snippet}')]")
        return self.is_displayed(loc, timeout=timeout)

    def click_go_to_home(self):
        """Menekan tombol menuju Beranda pada pop-up sukses."""
        self.click(self.BTN_GO_TO_HOME, label="Tombol 'Home / Beranda'")

    def click_back(self):
        """Kembali ke halaman login."""
        self.click(self.BTN_BACK, label="Tombol 'Back'")

    def navigate_to_login_via_link(self):
        """Menekan link 'Sudah Punya Akun? Masuk' untuk kembali ke halaman Login."""
        if self.is_displayed(self.LINK_ALREADY_HAVE_ACCOUNT, timeout=3):
            self.click(self.LINK_ALREADY_HAVE_ACCOUNT, label="Tautan 'Sudah Punya Akun? Masuk'")
        else:
            self.click_back()


# Backward compatibility alias
RegisterLocators = RegisterPage


