"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - LOGIN PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Layar Masuk / Login Mitra Driver, Input Nomor HP, OTP 4 Digit,
          Bantuan WhatsApp CS, Validasi Error, dan Penanganan Izin Sistem.
Wording : Bersumber 100% dari strings resmi APK driver_lang_id.json
================================================================================
"""
import os
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger
from config.config import Config

logger = get_logger("DrvLoginPage")


class DrvLoginPage(BasePage):
    """Page Object untuk Halaman Login / Masuk Mitra Pengemudi EvMoto."""

    # ==========================================================================
    # 1. ELEMEN LAYAR LOGIN (JOIN SEKARANG)
    # ==========================================================================
    TITLE_LOGIN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hai, Yuk Join Sekarang') or contains(@text, 'Hai, Yuk Join Sekarang') or "
        "contains(@content-desc, 'Join Sekarang') or contains(@text, 'Join Sekarang')]"
    )
    SUBTITLE_LOGIN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Masukkan nomor telepon untuk login') or contains(@text, 'Masukkan nomor telepon untuk login')]"
    )
    FIELD_PHONE = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, '812') or contains(@hint, 'nomor') or contains(@hint, 'telepon') or "
        "contains(@content-desc, 'telepon') or @class='android.widget.EditText']"
    )
    # Tombol persis 'Join Sekarang'. contains('Join Sekarang') juga cocok dengan judul 'Hai, Yuk Join Sekarang'.
    BTN_JOIN_SEKARANG = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Join Sekarang' or @text='Join Sekarang' or @content-desc='Join Now']"
    )
    LINK_REGISTER_NEW_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Daftar sebagai Driver baru') or contains(@text, 'Daftar sebagai Driver baru')]"
    )

    # Bantuan Kontak CS
    LINK_CONTACT_CS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hubungi CS') or contains(@text, 'Hubungi CS') or "
        "contains(@content-desc, 'Nomor telepon bermasalah?') or contains(@text, 'Nomor telepon bermasalah?')]"
    )

    # ==========================================================================
    # 2. ELEMEN LAYAR VERIFIKASI OTP
    # ==========================================================================
    TITLE_OTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lengkapi Verifikasi Kode') or contains(@text, 'Lengkapi Verifikasi Kode') or "
        "contains(@content-desc, 'Verifikasi Kode') or contains(@text, 'Verifikasi Kode')]"
    )
    SUBTITLE_OTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Masukan 4 kode untuk melanjutkan') or contains(@text, 'Masukan 4 kode untuk melanjutkan') or "
        "contains(@content-desc, 'Masukan 4 kode') or contains(@text, 'Masukan 4 kode')]"
    )
    FIELD_OTP = (
        AppiumBy.XPATH,
        "//android.widget.EditText"
    )
    BTN_SEND_OTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirimkan Kode OTP') or contains(@text, 'Kirimkan Kode OTP') or "
        "contains(@content-desc, 'Kirimkan') or contains(@text, 'Kirimkan')]"
    )
    BTN_RESEND_OTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim ulang') or contains(@text, 'Kirim ulang') or "
        "contains(@content-desc, 'Kirimkan Kode OTP')]"
    )
    # Tombol persis 'Lanjutkan' di layar OTP (driver_strings_id.json: button_next)
    BTN_LANJUTKAN_OTP = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']"
    )
    # Tombol persis 'Kirim ulang kode' (aktif setelah hitung mundur selesai)
    BTN_RESEND_EXACT = (
        AppiumBy.XPATH,
        "//*[@content-desc='Kirim ulang kode' or @text='Kirim ulang kode']"
    )
    # Pesan validasi resmi (driver_strings_id.json: form_validation_first_8)
    TEXT_VALIDATION_FIRST_8 = (
        AppiumBy.XPATH,
        "//*[@content-desc='Harus diawali dengan angka 8' or @text='Harus diawali dengan angka 8']"
    )
    TEXT_RESEND_COUNTDOWN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim ulang kode dalam') or contains(@text, 'Kirim ulang kode dalam')]"
    )
    BTN_BACK_OTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kembali') or contains(@text, 'Kembali') or contains(@class, 'ImageView')][1]"
    )

    # ==========================================================================
    # 3. POPUP & PESAN ERROR AUTENTIKASI
    # ==========================================================================
    ERROR_DRIVER_NOT_REGISTERED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Nomor driver belum terdaftar') or contains(@text, 'Nomor driver belum terdaftar')]"
    )
    ERROR_LOGGED_IN_OTHER_DEVICE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Anda sedang Login di perangkat lain') or contains(@text, 'Anda sedang Login di perangkat lain')]"
    )
    SNACKBAR_ERROR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'gagal') or contains(@text, 'gagal') or "
        "contains(@content-desc, 'salah') or contains(@text, 'salah') or "
        "contains(@content-desc, 'tidak valid') or contains(@text, 'tidak valid')]"
    )

    # ==========================================================================
    # 4. SYSTEM PERMISSIONS & POPUPS
    # ==========================================================================
    POPUP_LOCATION_PERMISSION = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'permission_message') or contains(@resource-id, 'grant_dialog') or "
        "contains(@text, 'Location') or contains(@text, 'Lokasi') or contains(@text, 'Izin')]"
    )
    BTN_ALLOW_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'permission_allow_foreground_only_button') or "
        "contains(@resource-id, 'permission_allow_one_time_button') or "
        "contains(@resource-id, 'android:id/button1') or "
        "contains(@text, 'While using the app') or contains(@text, 'Saat aplikasi digunakan') or "
        "contains(@text, 'Allow') or contains(@text, 'Izinkan')]"
    )
    BTN_ALLOW_NOTIFICATION = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'permission_allow_button') or contains(@text, 'Allow') or contains(@text, 'Izinkan')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    def is_login_screen_displayed(self) -> bool:
        """Memeriksa apakah layar login driver ditampilkan."""
        return self.is_displayed(self.TITLE_LOGIN, timeout=6) or self.is_displayed(self.BTN_JOIN_SEKARANG, timeout=4)

    def enter_phone_number(self, phone: str):
        """Memasukkan nomor handphone driver ke field input."""
        logger.info(f"Input nomor handphone driver: {phone}")
        self.type_text(self.FIELD_PHONE, phone, label="Field Nomor Telepon Driver")

    def click_join_sekarang(self):
        """Mengetuk tombol 'Join Sekarang'.

        Tidak menunggu tombol aktif: test negatif sengaja mengetuk tombol yang disabled
        (nomor kosong/tidak valid) lalu memeriksa bahwa aplikasi tidak lanjut ke OTP.
        """
        logger.info("Klik: Tombol Join Sekarang")
        self.find(self.BTN_JOIN_SEKARANG).click()

    def is_join_button_enabled(self) -> bool:
        """True bila tombol 'Join Sekarang' aktif."""
        return self.find(self.BTN_JOIN_SEKARANG).get_attribute("enabled") == "true"

    def is_validation_first_8_displayed(self, timeout: int = 5) -> bool:
        """True bila pesan 'Harus diawali dengan angka 8' tampil."""
        return self.is_displayed(self.TEXT_VALIDATION_FIRST_8, timeout=timeout)

    def is_otp_screen_displayed(self) -> bool:
        """Memeriksa apakah layar verifikasi kode OTP tampil."""
        return self.is_displayed(self.TITLE_OTP, timeout=6) or self.is_displayed(self.SUBTITLE_OTP, timeout=4)

    def enter_otp(self, otp: str = os.environ.get("EVMOTO_OTP_BYPASS", "")):
        """Memasukkan 4 digit kode OTP verifikasi bypass dev."""
        logger.info(f"Input kode OTP verifikasi driver: {otp}")
        self.type_text(self.FIELD_OTP, otp, label="Field Input 4 Kode OTP")
        # Kode tidak terkirim otomatis: layar OTP punya tombol 'Lanjutkan'
        if self.is_displayed(self.BTN_LANJUTKAN_OTP, timeout=3):
            self.find(self.BTN_LANJUTKAN_OTP).click()

    def click_resend_otp(self, max_wait_seconds: int = 75):
        """Menunggu hitung mundur selesai (tombol 'Kirim ulang kode' aktif), lalu mengetuknya."""
        deadline = time.time() + max_wait_seconds
        while time.time() < deadline:
            btns = self.driver.find_elements(*self.BTN_RESEND_EXACT)
            if btns and btns[0].get_attribute("enabled") == "true" and not self.is_displayed(self.TEXT_RESEND_COUNTDOWN, timeout=1):
                btns[0].click()
                return
            time.sleep(3)
        raise TimeoutError(f"Tombol 'Kirim ulang kode' tidak aktif setelah {max_wait_seconds} detik")

    def click_contact_cs(self):
        """Mengetuk tautan bantuan Hubungi CS WhatsApp."""
        self.click(self.LINK_CONTACT_CS, label="Tautan Hubungi CS Kami")

    def click_register_new_driver(self):
        """Mengetuk tautan pendaftaran 'Daftar sebagai Driver baru'."""
        self.click(self.LINK_REGISTER_NEW_DRIVER, label="Tautan Daftar sebagai Driver Baru")

    def is_driver_not_registered_displayed(self) -> bool:
        """Memeriksa apakah pesan error 'Nomor driver belum terdaftar' muncul."""
        return self.is_displayed(self.ERROR_DRIVER_NOT_REGISTERED, timeout=4)

    def is_logged_in_other_device_displayed(self) -> bool:
        """Memeriksa apakah modal peringatan 'Anda sedang Login di perangkat lain' muncul."""
        return self.is_displayed(self.ERROR_LOGGED_IN_OTHER_DEVICE, timeout=4)

    def is_snackbar_error_displayed(self) -> bool:
        """Memeriksa apakah muncul pesan snackbar error."""
        return self.is_displayed(self.SNACKBAR_ERROR, timeout=3)

    def handle_system_permissions(self):
        """Menangani popup izin lokasi dan notifikasi Android OS secara otomatis."""
        try:
            if self.is_displayed(self.BTN_ALLOW_LOCATION, timeout=2):
                logger.info("Mengizinkan akses lokasi perangkat (While using the app)")
                self.click(self.BTN_ALLOW_LOCATION, label="Izinkan Lokasi")
                time.sleep(0.5)
        except Exception:
            pass

        try:
            if self.is_displayed(self.BTN_ALLOW_NOTIFICATION, timeout=2):
                logger.info("Mengizinkan notifikasi aplikasi")
                self.click(self.BTN_ALLOW_NOTIFICATION, label="Izinkan Notifikasi")
                time.sleep(0.5)
        except Exception:
            pass

    def login_as_driver(self, phone: str = Config.DRIVER_ACTIVE_PHONE, otp: str = Config.DRIVER_ACTIVE_PIN):
        """
        Alur lengkap end-to-end login Driver ke aplikasi Dev Golang.
        Input nomor -> Join Sekarang -> Masukkan OTP <EVMOTO_OTP_BYPASS> -> Handle Izin Lokasi.
        """
        logger.info(f"Melakukan proses login driver dengan nomor: {phone}")
        self.handle_system_permissions()

        if self.is_login_screen_displayed():
            self.enter_phone_number(phone)
            self.click_join_sekarang()

        if self.is_otp_screen_displayed():
            self.enter_otp(otp)

        time.sleep(Config.HUMAN_PACING_MIN)
        self.handle_system_permissions()

    # ==========================================================================
    # 5. VERIFIKASI HASIL PENANGANAN IZIN SISTEM
    # ==========================================================================
    # Dialog izin bawaan Android (Permission Controller), bukan teks aplikasi.
    POPUP_SYSTEM_PERMISSION = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'com.android.permissioncontroller:id/') or "
        "contains(@resource-id, 'com.android.packageinstaller:id/permission')]"
    )

    def is_system_permission_dialog_displayed(self, timeout: int = 2) -> bool:
        """Memeriksa apakah dialog izin Android (lokasi/notifikasi) masih terbuka."""
        return self.is_displayed(self.POPUP_SYSTEM_PERMISSION, timeout=timeout)

    def get_app_permissions(self, jenis: str = "granted") -> list:
        """Daftar izin runtime aplikasi driver ('granted', 'denied', atau 'requested') lewat 'mobile: getPermissions'."""
        hasil = self.driver.execute_script("mobile: getPermissions", {
            "type": jenis,
            "appPackage": Config.DRIVER_PACKAGE,
        })
        return list(hasil or [])
