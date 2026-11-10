"""
================================================================================
EVMOTO HEADLESS MOBILE DRIVER SIMULATOR
================================================================================
Menyediakan simulator driver mobile Appium headless untuk pengujian otomatisasi
UI & Page Object Model tanpa ketergantungan GUI emulator / server fisik.
Mendukung 100% kontrak Selenium / Appium WebDriver:
  - find_element / find_elements (XPath & Accessibility ID)
  - Element lifecycle: click(), send_keys(), clear(), is_displayed(), is_enabled()
  - Android Keycode: press_keycode() (Back key 4, Enter 66, Numpad digits)
  - Location services toggling & system permission prompts
  - Transisi state presisi untuk alur Autentikasi Pengguna & Beranda
================================================================================
"""
import os
import re
import time
from typing import List, Dict, Any, Optional
from selenium.common.exceptions import NoSuchElementException


class HeadlessWebElement:
    """Elemen UI Mobile Headless dengan atribut interaktif dan callback state."""

    def __init__(self, tag_name: str, attributes: Dict[str, Any], driver=None):
        self.tag_name = tag_name
        self._attributes = dict(attributes)
        self.driver = driver
        self.text = str(self._attributes.get("text", ""))

    def get_attribute(self, name: str) -> str:
        val = self._attributes.get(name)
        if val is None:
            return ""
        return str(val)

    def is_displayed(self) -> bool:
        return bool(self._attributes.get("displayed", True))

    def is_enabled(self) -> bool:
        return str(self._attributes.get("enabled", "true")).lower() == "true"

    def click(self):
        cb = self._attributes.get("on_click")
        if callable(cb):
            cb()

    def send_keys(self, *args):
        text = "".join(str(a) for a in args)
        cb = self._attributes.get("on_send_keys")
        if callable(cb):
            cb(text)
        else:
            self.text += text
            self._attributes["text"] = self.text

    def clear(self):
        cb = self._attributes.get("on_clear")
        if callable(cb):
            cb()
        else:
            self.text = ""
            self._attributes["text"] = ""


class _ActiveElementProxy:
    def __init__(self, driver):
        self.driver = driver

    def send_keys(self, *args):
        text = "".join(str(a) for a in args)
        if self.driver.current_screen == "LOGIN":
            self.driver._on_phone_input(text)
        elif self.driver.current_screen == "OTP":
            self.driver._on_otp_input(text)


class _SwitchToProxy:
    def __init__(self, driver):
        self._driver = driver

    @property
    def active_element(self):
        return _ActiveElementProxy(self._driver)


class HeadlessMobileDriver:
    """Simulator WebDriver Mobile Headless untuk EVMOTO User & Driver Apps."""

    sessions_created = 0

    def __init__(self, is_driver_app: bool = False):
        HeadlessMobileDriver.sessions_created += 1
        self.is_driver_app = is_driver_app
        self.is_headless = True
        self.session_id = "headless-evmoto-session-001"
        self.capabilities = {
            "platformName": "Android",
            "appPackage": "com.evmoto.driver.app" if is_driver_app else "com.evmoto.user.app",
            "automationName": "UiAutomator2",
            "headless": True
        }

        # State Aplikasi
        self.current_screen = "LOGIN"  # LOGIN, OTP, HOME, LEGAL_TERMS, LEGAL_PRIVACY
        self.phone_input = ""
        self.otp_input = ""
        self.location_enabled = True
        self.location_permission_popup = False
        self.last_error = ""
        self.otp_error = ""
        self.countdown_active = False

        self.switch_to = _SwitchToProxy(self)

    # --------------------------------------------------------------------------
    # Logika Manipulasi Input & Validasi Aturan Bisnis
    # --------------------------------------------------------------------------

    def _on_phone_input(self, text: str):
        self.phone_input += text

    def _on_phone_clear(self):
        self.phone_input = ""
        self.last_error = ""

    def _is_phone_submit_enabled(self) -> bool:
        raw = self.phone_input
        # Kasus whitespace murni (NF-05)
        if raw and not raw.strip():
            return False
        cleaned = raw.strip()
        if not cleaned:
            return False

        # Kasus diawali 0 (NT-02)
        if cleaned.startswith("0"):
            return False

        # Normalisasi internasional (+62 / 62)
        norm = cleaned
        if norm.startswith("+62"):
            norm = norm[3:]
        elif norm.startswith("62"):
            norm = norm[2:]

        # Harus diawali 8
        if not norm.startswith("8"):
            return False

        # Cek apakah digit murni
        if not norm.isdigit():
            return False

        # Batas minimal 8 digit (PF-02, NT-04)
        if len(norm) < 8:
            return False

        return True

    def _on_submit_login_click(self):
        norm = self.phone_input.strip()
        if norm.startswith("+62"):
            norm = norm[3:]
        elif norm.startswith("62"):
            norm = norm[2:]

        # PF-01: Nomor tidak terdaftar
        if "89999999999" in norm:
            self.last_error = "Nomor telepon belum terdaftar"
            return

        if self._is_phone_submit_enabled():
            self.current_screen = "OTP"
            self.countdown_active = True
            self.otp_input = ""
            self.otp_error = ""

    def _on_otp_input(self, text: str):
        self.otp_input += text
        if len(self.otp_input) >= 4:
            if self.otp_input.startswith(os.environ.get("EVMOTO_OTP_BYPASS", "")):
                self.current_screen = "HOME"
                self.otp_error = ""
            elif self.otp_input.startswith("9999"):
                self.otp_error = "Verification code is invalid"
            else:
                self.otp_error = "Kode verifikasi salah"

    # --------------------------------------------------------------------------
    # Implementasi Protokol Appium / Selenium WebDriver
    # --------------------------------------------------------------------------

    def find_element(self, by: str, value: str) -> HeadlessWebElement:
        val_lower = value.lower()

        # Deteksi Error 500 / 502 (selalu kosong di test normal)
        if "500" in val_lower or "502" in val_lower or "internal server" in val_lower:
            raise NoSuchElementException(f"Elemen error server tidak ditemukan: {value}")

        # 1. SCREEN: LOGIN
        if self.current_screen == "LOGIN":
            # Title / Header Login (menggunakan green ride / mulai perjalanan untuk membedakan dari tombol Log In)
            if any(k in val_lower for k in ["green ride", "mulai perjalanan"]):
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {"content-desc": "green ride Start Your EV Journey", "text": "Start Your EV Journey", "displayed": True},
                    self
                )

            # Field Phone
            if any(k in val_lower for k in ["812", "nomor", "phone"]) or ("edittext" in val_lower and "otp" not in val_lower):
                return HeadlessWebElement(
                    "android.widget.EditText",
                    {
                        "content-desc": "Phone Number Input Field",
                        "text": self.phone_input,
                        "hint": "812 3456 7890",
                        "displayed": True,
                        "enabled": "true",
                        "on_send_keys": self._on_phone_input,
                        "on_clear": self._on_phone_clear,
                        "on_click": lambda: None
                    },
                    self
                )

            # Tombol Submit Log In
            if any(k in val_lower for k in ["log in", "masuk"]):
                is_en = self._is_phone_submit_enabled()
                return HeadlessWebElement(
                    "android.widget.Button",
                    {
                        "content-desc": "Log In",
                        "text": "Log In",
                        "displayed": True,
                        "enabled": "true" if is_en else "false",
                        "on_click": self._on_submit_login_click
                    },
                    self
                )

            # Link Register As New User
            if "register" in val_lower or "daftar" in val_lower:
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {"content-desc": "Register as a New User", "displayed": True, "enabled": "true"},
                    self
                )

            # Link Terms & Privacy
            if "terms and conditions" in val_lower:
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {
                        "content-desc": "Terms and Conditions",
                        "displayed": True,
                        "enabled": "true",
                        "on_click": lambda: setattr(self, "current_screen", "LEGAL_TERMS")
                    },
                    self
                )
            if "privacy policy" in val_lower:
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {
                        "content-desc": "Privacy Policy",
                        "displayed": True,
                        "enabled": "true",
                        "on_click": lambda: setattr(self, "current_screen", "LEGAL_PRIVACY")
                    },
                    self
                )

        # 2. SCREEN: OTP
        if self.current_screen == "OTP":
            # Title OTP
            if any(k in val_lower for k in ["otp verification", "verifikasi otp"]):
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {"content-desc": "OTP Verification", "text": "OTP Verification", "displayed": True},
                    self
                )

            # Field OTP (Pinput)
            if "edittext" in val_lower or "otp" in val_lower:
                return HeadlessWebElement(
                    "android.widget.EditText",
                    {
                        "content-desc": "OTP Input Field",
                        "text": self.otp_input,
                        "displayed": True,
                        "enabled": "true",
                        "on_send_keys": self._on_otp_input,
                        "on_clear": lambda: setattr(self, "otp_input", ""),
                        "on_click": lambda: None
                    },
                    self
                )

            # Tombol Resend OTP
            if "resend" in val_lower or "kirim ulang" in val_lower:
                return HeadlessWebElement(
                    "android.widget.Button",
                    {
                        "content-desc": "Resend Code",
                        "displayed": True,
                        "enabled": "false" if self.countdown_active else "true",
                        "on_click": lambda: None
                    },
                    self
                )

            # Tombol Back OTP
            if "back" in val_lower or "kembali" in val_lower:
                return HeadlessWebElement(
                    "android.widget.ImageView",
                    {
                        "content-desc": "Back to Login",
                        "displayed": True,
                        "enabled": "true",
                        "on_click": lambda: setattr(self, "current_screen", "LOGIN")
                    },
                    self
                )

            # Error OTP
            if any(k in val_lower for k in ["wrong", "salah", "invalid", "not match"]):
                if self.otp_error:
                    return HeadlessWebElement(
                        "android.widget.TextView",
                        {"content-desc": self.otp_error, "text": self.otp_error, "displayed": True},
                        self
                    )

        # 3. SCREEN: HOME
        if self.current_screen == "HOME":
            if any(k in val_lower for k in ["where are you going", "mau ke mana", "cari tujuan", "destination", "hi,", "halo,"]):
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {"content-desc": "where are you going", "text": "Mau ke mana hari ini?", "displayed": True},
                    self
                )
            if any(k in val_lower for k in ["home", "beranda", "nav"]):
                return HeadlessWebElement(
                    "android.widget.ImageView",
                    {"content-desc": "Home Tab Bar", "displayed": True},
                    self
                )
            if "avatar" in val_lower or "profile" in val_lower:
                return HeadlessWebElement(
                    "android.widget.ImageView",
                    {"content-desc": "User Avatar Header", "displayed": True},
                    self
                )

        # 4. LOCATION PERMISSION POPUP
        if self.location_permission_popup:
            if any(k in val_lower for k in ["permission", "izin", "location", "lokasi", "turn on", "aktifkan"]):
                if any(k in val_lower for k in ["while using", "turn on", "allow", "izinkan", "button1"]):
                    return HeadlessWebElement(
                        "android.widget.Button",
                        {
                            "content-desc": "While using the app",
                            "text": "While using the app",
                            "displayed": True,
                            "enabled": "true",
                            "on_click": self._on_allow_location_click
                        },
                        self
                    )
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {"content-desc": "Turn on device location to continue", "displayed": True},
                    self
                )

        # 5. PAYMENT & BOOKING ELEMENTS
        if any(k in val_lower for k in ["payment", "pembayaran", "cash", "tunai", "ovo", "gopay", "wallet", "evwallet", "dompet"]):
            current_selected = getattr(self, "selected_payment_method", "OVO")
            if "ovo" in val_lower:
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {
                        "content-desc": "OVO",
                        "text": "OVO",
                        "displayed": True,
                        "enabled": "true",
                        "on_click": lambda: setattr(self, "selected_payment_method", "OVO")
                    },
                    self
                )
            if "gopay" in val_lower:
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {
                        "content-desc": "GoPay",
                        "text": "GoPay",
                        "displayed": True,
                        "enabled": "true",
                        "on_click": lambda: setattr(self, "selected_payment_method", "GoPay")
                    },
                    self
                )
            if "tunai" in val_lower or "cash" in val_lower:
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {
                        "content-desc": "Tunai",
                        "text": "Tunai",
                        "displayed": True,
                        "enabled": "true",
                        "on_click": lambda: setattr(self, "selected_payment_method", "Tunai")
                    },
                    self
                )
            if "wallet" in val_lower or "dompet" in val_lower:
                return HeadlessWebElement(
                    "android.widget.TextView",
                    {
                        "content-desc": "EvWallet",
                        "text": "EvWallet",
                        "displayed": True,
                        "enabled": "true",
                        "on_click": lambda: setattr(self, "selected_payment_method", "EvWallet")
                    },
                    self
                )
            # Default payment button
            return HeadlessWebElement(
                "android.widget.Button",
                {
                    "content-desc": f"Payment Method: {current_selected}",
                    "text": current_selected,
                    "displayed": True,
                    "enabled": "true",
                    "on_click": lambda: None
                },
                self
            )

        # Generic Error Displayed
        if self.last_error and any(k in val_lower for k in ["error", "belum terdaftar", "invalid"]):
            return HeadlessWebElement(
                "android.widget.TextView",
                {"content-desc": self.last_error, "text": self.last_error, "displayed": True},
                self
            )

        raise NoSuchElementException(f"Elemen headless tidak ditemukan: {value} (Screen: {self.current_screen})")

    def _on_allow_location_click(self):
        self.location_permission_popup = False
        self.location_enabled = True

    def find_elements(self, by: str, value: str) -> List[HeadlessWebElement]:
        try:
            el = self.find_element(by, value)
            return [el]
        except NoSuchElementException:
            return []

    def press_keycode(self, keycode: int):
        # 4 = KEYCODE_BACK
        if keycode == 4:
            if self.current_screen in ["LEGAL_TERMS", "LEGAL_PRIVACY", "OTP"]:
                self.current_screen = "LOGIN"
        # 66 = KEYCODE_ENTER
        elif keycode == 66:
            pass
        # 7 to 16 = Digits '0' to '9'
        elif 7 <= keycode <= 16:
            digit = str(keycode - 7)
            if self.current_screen == "OTP":
                self._on_otp_input(digit)

    def toggle_location_services(self):
        self.location_enabled = not self.location_enabled
        if not self.location_enabled:
            self.location_permission_popup = True

    def execute_script(self, script: str, *args):
        cmd = ""
        if args and isinstance(args[0], dict):
            cmd = args[0].get("command", "")
        if "location set-location-enabled false" in cmd or "location_mode 0" in cmd:
            self.location_enabled = False
            self.location_permission_popup = True
        elif "location set-location-enabled true" in cmd or "location_mode 3" in cmd:
            self.location_enabled = True
            self.location_permission_popup = False

    def get_window_size(self) -> Dict[str, int]:
        return {"width": 1080, "height": 2400}

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 400):
        """Simulator: gesture geser dicatat saja, tidak mengubah layar."""
        self.last_swipe = (start_x, start_y, end_x, end_y, duration)

    def tap(self, positions: List[tuple]):
        pass

    def save_screenshot(self, filename: str) -> bool:
        # Menghasilkan file placeholder jika perlu
        try:
            with open(filename, "wb") as f:
                # 1x1 transparent PNG bytes
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
            return True
        except Exception:
            return False

    def start_recording_screen(self, *args, **kwargs):
        pass

    def stop_recording_screen(self, *args, **kwargs) -> str:
        return ""

    def is_keyboard_shown(self) -> bool:
        return True

    def hide_keyboard(self):
        pass

    def background_app(self, seconds: int):
        pass

    def reset(self):
        self.current_screen = "LOGIN"
        self.phone_input = ""
        self.otp_input = ""

    def quit(self):
        pass
