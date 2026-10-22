"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - LOGIN PAGE OBJECT
================================================================================
Target: Layar Masuk / Login Pengguna EVMoto (Flutter App)
Mendukung Bahasa Inggris (Default) dan Bahasa Indonesia.
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("LoginPage")

class LoginPage(BasePage):
    """Page Object untuk Halaman Login / Masuk Akun Pengguna EvMoto."""

    # Locators Elemen ID / XPath Layar Login
    TITLE_LOGIN = (AppiumBy.XPATH, "//*[contains(@content-desc, 'green ride') or contains(@content-desc, 'Mulai perjalanan') or contains(@content-desc, 'Log In') or contains(@content-desc, 'Masuk')]")
    FIELD_PHONE = (AppiumBy.XPATH, "//android.widget.EditText[contains(@hint, '812') or contains(@hint, 'Nomor') or @class='android.widget.EditText']")
    BTN_SUBMIT_LOGIN = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Log In') or contains(@content-desc, 'Masuk') or contains(@text, 'Log In')]")
    LINK_REGISTER_NEW_USER = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Register as a New User') or contains(@content-desc, 'Daftar sebagai Pengguna baru')]")

    # Locators Layar Verifikasi OTP
    TITLE_OTP = (AppiumBy.XPATH, "//*[contains(@content-desc, 'OTP Verification') or contains(@content-desc, 'Verifikasi OTP')]")
    FIELD_OTP = (AppiumBy.XPATH, "//android.widget.EditText")
    BTN_CONFIRM_OTP = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Confirm') or contains(@content-desc, 'Konfirmasi')]")
    TEXT_ERROR_OTP = (AppiumBy.XPATH, "//*[contains(@content-desc, 'wrong') or contains(@content-desc, 'salah') or contains(@content-desc, 'not match')]")

    # Legalitas & Navigasi
    LINK_TERMS = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Terms and Conditions')]")
    LINK_PRIVACY = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Privacy Policy')]")
    BTN_RESEND_OTP = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Resend') or contains(@content-desc, 'Kirim ulang')]")
    BTN_BACK_OTP = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Back') or contains(@content-desc, 'Kembali')]")

    # Dialog / Popup Izin Lokasi Android OS (System Dialog & In-App Prompt)
    POPUP_LOCATION_PERMISSION = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'permission_message') or "
        "contains(@resource-id, 'permission_icon') or "
        "contains(@resource-id, 'grant_dialog') or "
        "contains(@resource-id, 'alertTitle') or "
        "contains(@text, 'Location') or contains(@text, 'Lokasi') or "
        "contains(@text, 'Turn on') or contains(@text, 'Aktifkan') or "
        "contains(@text, 'device location') or contains(@text, 'lokasi perangkat') or "
        "contains(@text, 'permission') or contains(@text, 'izin') or "
        "contains(@content-desc, 'Location') or contains(@content-desc, 'Lokasi') or "
        "contains(@content-desc, 'Aktifkan') or contains(@content-desc, 'Turn on')]"
    )
    BTN_TURN_ON_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'permission_allow_foreground_only_button') or "
        "contains(@resource-id, 'permission_allow_one_time_button') or "
        "contains(@resource-id, 'android:id/button1') or "
        "contains(@text, 'While using the app') or "
        "contains(@text, 'Saat aplikasi digunakan') or "
        "contains(@text, 'Only this time') or "
        "contains(@text, 'Hanya kali ini') or "
        "contains(@text, 'Turn on') or "
        "contains(@text, 'Aktifkan') or "
        "contains(@text, 'Allow') or "
        "contains(@text, 'Izinkan') or "
        "contains(@content-desc, 'While using the app') or "
        "contains(@content-desc, 'Turn on') or "
        "contains(@content-desc, 'Aktifkan') or "
        "contains(@content-desc, 'Allow') or "
        "contains(@content-desc, 'Izinkan')]"
    )
    BTN_DENY_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'permission_deny_button') or "
        "contains(@resource-id, 'android:id/button2') or "
        "contains(@text, 'Don\'t allow') or "
        "contains(@text, 'Jangan izinkan') or "
        "contains(@text, 'No thanks') or "
        "contains(@text, 'Batal') or "
        "contains(@content-desc, 'Don\'t allow') or "
        "contains(@content-desc, 'Batal')]"
    )

    def is_login_screen_displayed(self, timeout: int = 15) -> bool:
        """Memeriksa apakah layar Login aktif."""
        return self.is_displayed(self.TITLE_LOGIN, timeout=timeout) or self.is_displayed(self.FIELD_PHONE, timeout=timeout)

    def input_phone_number(self, phone: str):
        """Memasukkan nomor handphone (misal: 81299990001)."""
        field = self.find(self.FIELD_PHONE)
        field.click()
        time.sleep(0.5)
        field.clear()
        time.sleep(0.5)
        field.send_keys(phone)
        time.sleep(1)

    def click_submit_login(self):
        """Menekan tombol Log In / Masuk."""
        self.click(self.BTN_SUBMIT_LOGIN, label="Tombol 'Log In'")

    def is_otp_screen_displayed(self, timeout: int = 15) -> bool:
        """Memeriksa apakah layar Verifikasi OTP muncul."""
        return self.is_displayed(self.TITLE_OTP, timeout=timeout)

    def input_otp_dev(self, otp_code: str = "1234", fast_transition: bool = True):
        """Memasukkan kode OTP (default dev/prod: 1234) secara andal di emulator maupun physical device."""
        self.find(self.TITLE_OTP, timeout=15)
        field = self.find(self.FIELD_OTP, timeout=10)
        field.click()
        time.sleep(0.3)
        # Kirim kode OTP digit per digit via keycode untuk men-trigger Flutter Pinput onCompleted callback
        for ch in otp_code:
            if ch.isdigit():
                keycode = int(ch) + 7  # '0' = 7, '1' = 8, ..., '4' = 11
                try:
                    self.driver.press_keycode(keycode)
                except Exception:
                    pass
                time.sleep(0.15)
        time.sleep(0.5)
        # Fallback send_keys jika field belum terisi
        try:
            field_text = field.text or ""
            if len(field_text) < 4:
                field.send_keys(otp_code)
        except Exception:
            pass
        try:
            self.driver.press_keycode(66)  # KEYCODE_ENTER
        except Exception:
            pass

    def disable_device_location(self):
        """
        Mematikan fitur lokasi / GPS pada perangkat atau mencabut izin lokasi aplikasi.
        Mensimulasikan skenario ketika pengguna menonaktifkan fitur Location pada perangkatnya.
        """
        logger.info("Menonaktifkan Location Service perangkat & mencabut izin lokasi aplikasi...")
        # 1. Nonaktifkan location services via Appium toggle jika didukung
        try:
            self.driver.toggle_location_services()
        except Exception:
            pass
        # 2. Nonaktifkan location via Android cmd / settings
        try:
            self.driver.execute_script("mobile: shell", {"command": "cmd location set-location-enabled false"})
        except Exception:
            pass
        try:
            self.driver.execute_script("mobile: shell", {"command": "settings put secure location_mode 0"})
        except Exception:
            pass
        # 3. Cabut permission lokasi aplikasi (ACCESS_FINE_LOCATION & ACCESS_COARSE_LOCATION)
        try:
            from config import config
            self.driver.execute_script("mobile: shell", {
                "command": f"pm revoke {config.APP_PACKAGE} android.permission.ACCESS_FINE_LOCATION"
            })
            self.driver.execute_script("mobile: shell", {
                "command": f"pm revoke {config.APP_PACKAGE} android.permission.ACCESS_COARSE_LOCATION"
            })
        except Exception:
            pass
        time.sleep(1.0)

    def enable_device_location(self):
        """
        Mengaktifkan kembali fitur lokasi / GPS pada perangkat Android.
        """
        logger.info("Mengaktifkan kembali Location Service pada perangkat...")
        try:
            self.driver.execute_script("mobile: shell", {"command": "cmd location set-location-enabled true"})
        except Exception:
            pass
        try:
            self.driver.execute_script("mobile: shell", {"command": "settings put secure location_mode 3"})
        except Exception:
            pass
        time.sleep(1.0)

    def is_location_permission_popup_displayed(self, timeout: int = 8) -> bool:
        """
        Memeriksa apakah popup / dialog izin lokasi muncul di layar saat lokasi perangkat mati.
        """
        return self.is_displayed(self.POPUP_LOCATION_PERMISSION, timeout=timeout) or \
               self.is_displayed(self.BTN_TURN_ON_LOCATION, timeout=timeout)

    def grant_location_permission_from_popup(self, timeout: int = 5) -> bool:
        """
        Menekan tombol izin lokasi (misal: 'While using the app' / 'Saat aplikasi digunakan' / 'Turn on').
        """
        try:
            location_btns = self.find_all(self.BTN_TURN_ON_LOCATION, timeout=timeout)
            if location_btns:
                location_btns[0].click()
                logger.info("Tombol izin lokasi berhasil ditekan dari popup.")
                time.sleep(1.5)
                return True
        except Exception as e:
            logger.warning(f"Gagal menekan tombol izin lokasi dari popup: {e}")
        return False

    def handle_location_prompt_if_present(self, timeout: int = 5):
        """Menekan 'While using the app' atau 'Turn on' jika muncul dialog izin lokasi."""
        self.grant_location_permission_from_popup(timeout=timeout)

    def click_confirm_otp(self):
        """Menekan tombol Konfirmasi OTP jika tersedia."""
        try:
            btns = self.find_all(self.BTN_CONFIRM_OTP, timeout=3)
            if btns:
                btns[0].click()
        except Exception:
            pass

    def navigate_to_register(self):
        """Menekan 'Register as a New User' untuk menuju form registrasi."""
        try:
            self.click(self.LINK_REGISTER_NEW_USER, label="Tombol 'Register as a New User'")
        except Exception:
            logger.info("Mencoba fallback klik 'Register as a New User' via Accessibility ID...")
            try:
                el = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Register as a New User")
                el.click()
            except Exception:
                logger.info("Mencoba fallback tap koordinat bawah untuk 'Register as a New User'...")
                size = self.driver.get_window_size()
                self.driver.tap([(int(size["width"] * 0.5), int(size["height"] * 0.94))])

    def clear_phone_number(self):
        """Mengosongkan field nomor handphone."""
        field = self.find(self.FIELD_PHONE)
        field.click()
        field.clear()

    def is_submit_button_enabled(self) -> bool:
        """Memeriksa apakah tombol 'Log In' dalam status aktif / clickable."""
        btn = self.find(self.BTN_SUBMIT_LOGIN)
        return btn.get_attribute("enabled") == "true"

    def click_terms(self):
        """Menekan link Terms and Conditions."""
        self.click(self.LINK_TERMS, label="Link 'Terms and Conditions'")

    def click_privacy(self):
        """Menekan link Privacy Policy."""
        self.click(self.LINK_PRIVACY, label="Link 'Privacy Policy'")

    def click_resend_otp(self):
        """Menekan tombol Resend OTP."""
        self.click(self.BTN_RESEND_OTP, label="Tombol 'Resend OTP'")

    def click_back_from_otp(self):
        """Kembali dari layar OTP ke layar login."""
        self.click(self.BTN_BACK_OTP, label="Tombol 'Back' Layar OTP")

    def is_error_displayed(self, text_snippet: str = "", timeout: int = 5) -> bool:
        """Memeriksa apakah pesan error atau validasi muncul di layar."""
        if not text_snippet:
            loc = (AppiumBy.XPATH, "//*[contains(@content-desc, 'error') or contains(@content-desc, 'salah') or contains(@content-desc, 'invalid') or contains(@content-desc, 'belum terdaftar')]")
        else:
            loc = (AppiumBy.XPATH, f"//*[contains(@content-desc, '{text_snippet}') or contains(@text, '{text_snippet}')]")
        return self.is_displayed(loc, timeout=timeout)


# Backward compatibility alias
LoginLocators = LoginPage


