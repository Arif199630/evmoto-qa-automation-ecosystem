"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - REGISTRATION PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Layar Registrasi Mitra Driver Baru, Formulir 3 Tahap (Data Personal,
          Kendaraan ECGO/Non-ECGO, Plat Nomor, Upload Dokumen SIM/STNK/SKCK/KTP,
          dan Kode Referral).
Wording : Bersumber 100% dari strings resmi APK driver_lang_id.json
================================================================================
"""
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("DrvRegisterPage")


class DrvRegisterPage(BasePage):
    """Page Object untuk Pendaftaran Mitra Pengemudi Baru EvMoto Driver."""

    # ==========================================================================
    # 1. TOMBOL AWAL & HEADER REGISTRASI
    # ==========================================================================
    CTA_REGISTER_NEW_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Daftar sebagai Driver baru') or contains(@text, 'Daftar sebagai Driver baru') or "
        "contains(@content-desc, 'Daftar') or contains(@text, 'Daftar')]"
    )
    TEXT_REGISTER_TITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Registrasi Driver Baru') or contains(@text, 'Registrasi Driver Baru') or "
        "contains(@content-desc, 'Data Informasi Personal') or contains(@text, 'Data Informasi Personal')]"
    )
    TEXT_REGISTER_SUBTITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lengkapi data Anda untuk melanjutkan') or contains(@text, 'Lengkapi data Anda')]"
    )

    # ==========================================================================
    # 2. PERTANYAAN DRIVER ECGO & PLAT KENDARAAN
    # ==========================================================================
    TEXT_ECGO_DRIVER_QUESTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Apakah Anda ECGO Driver?') or contains(@text, 'Apakah Anda ECGO Driver?')]"
    )
    RADIO_ECGO_YES = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ya') or contains(@text, 'Ya') or contains(@resource-id, 'radio_ecgo_yes')]"
    )
    RADIO_ECGO_NO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tidak') or contains(@text, 'Tidak') or contains(@resource-id, 'radio_ecgo_no')]"
    )
    FIELD_PLATE_NUMBER = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'B1234ABC') or contains(@content-desc, 'Plat') or "
        "contains(@hint, 'Nomor Plat') or contains(@content-desc, 'B1234')]"
    )
    FIELD_REFERRAL_CODE = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'referral') or contains(@content-desc, 'referral') or "
        "contains(@hint, 'kode referral')]"
    )

    # ==========================================================================
    # 3. UPLOAD DOKUMEN & FOTO PERSYARATAN
    # ==========================================================================
    BTN_UPLOAD_SELFIE_KTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Driver Selfie dengan KTP') or contains(@text, 'Driver Selfie dengan KTP') or "
        "contains(@content-desc, 'Selfie dengan KTP')]"
    )
    BTN_UPLOAD_STNK_FRONT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Foto STNK Depan') or contains(@text, 'Foto STNK Depan') or "
        "contains(@content-desc, 'STNK Depan')]"
    )
    BTN_UPLOAD_STNK_BACK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Foto STNK Belakang') or contains(@text, 'Foto STNK Belakang') or "
        "contains(@content-desc, 'STNK Belakang')]"
    )
    BTN_UPLOAD_SKCK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Foto SKCK') or contains(@text, 'Foto SKCK') or "
        "contains(@content-desc, 'SKCK')]"
    )

    # ==========================================================================
    # 4. ACTION BUTTONS & VALIDASI POPUP
    # ==========================================================================
    BTN_SUBMIT_REGISTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim') or contains(@text, 'Kirim') or "
        "contains(@content-desc, 'Lanjut') or contains(@text, 'Lanjut') or "
        "contains(@content-desc, 'Daftar') or contains(@text, 'Daftar')]"
    )
    BTN_BACK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kembali') or contains(@text, 'Kembali') or contains(@class, 'ImageView')][1]"
    )
    POPUP_SUCCESS_COMPLETE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'DATA  YANG DIKIRIM BERHASIL') or contains(@text, 'DATA  YANG DIKIRIM BERHASIL') or "
        "contains(@content-desc, 'Informasi Sudah Dilengkapi') or contains(@text, 'Informasi Sudah Dilengkapi')]"
    )
    TEXT_SUCCESS_NOTICE_2HOURS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '2 jam') or contains(@text, '2 jam') or "
        "contains(@content-desc, 'Tim kami akan menghubungi Anda')]"
    )
    WARNING_VALIDATION_MANDATORY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'wajib') or contains(@text, 'wajib') or "
        "contains(@content-desc, 'Harap isi') or contains(@text, 'tidak boleh kosong')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    def click_daftar_driver_baru(self):
        """Membuka form pendaftaran driver baru dari layar awal."""
        self.click(self.CTA_REGISTER_NEW_DRIVER, label="CTA Daftar sebagai Driver Baru")

    def is_register_screen_displayed(self) -> bool:
        """Memeriksa apakah layar pendaftaran terbuka."""
        return self.is_displayed(self.TEXT_REGISTER_TITLE, timeout=5)

    def select_ecgo_driver(self, is_ecgo: bool = True):
        """Memilih apakah driver menggunakan armada ECGO atau Non-ECGO."""
        if is_ecgo:
            self.click(self.RADIO_ECGO_YES, label="Opsi ECGO Driver: Ya")
        else:
            self.click(self.RADIO_ECGO_NO, label="Opsi ECGO Driver: Tidak")

    def enter_plate_number(self, plate: str):
        """Memasukkan nomor plat kendaraan motor driver."""
        self.type_text(self.FIELD_PLATE_NUMBER, plate, label="Field Plat Nomor Kendaraan")

    def enter_referral_code(self, code: str):
        """Memasukkan kode referral mitra pengemudi."""
        self.type_text(self.FIELD_REFERRAL_CODE, code, label="Field Kode Referral")

    def click_upload_selfie_ktp(self):
        """Mengetuk tombol upload selfie KTP."""
        self.click(self.BTN_UPLOAD_SELFIE_KTP, label="Upload Selfie KTP")

    def click_upload_stnk_front(self):
        """Mengetuk tombol upload STNK depan."""
        self.click(self.BTN_UPLOAD_STNK_FRONT, label="Upload STNK Depan")

    def click_upload_stnk_back(self):
        """Mengetuk tombol upload STNK belakang."""
        self.click(self.BTN_UPLOAD_STNK_BACK, label="Upload STNK Belakang")

    def click_upload_skck(self):
        """Mengetuk tombol upload SKCK."""
        self.click(self.BTN_UPLOAD_SKCK, label="Upload SKCK")

    def submit_registration_form(self):
        """Menekan tombol kirim / submit pendaftaran."""
        self.click(self.BTN_SUBMIT_REGISTER, label="Tombol Submit Pendaftaran")

    def is_registration_success_displayed(self) -> bool:
        """Memeriksa apakah pop-up sukses 'DATA YANG DIKIRIM BERHASIL' tampil."""
        return self.is_displayed(self.POPUP_SUCCESS_COMPLETE, timeout=5)

    def is_mandatory_warning_displayed(self) -> bool:
        """Memeriksa apakah validasi error kolom wajib tampil."""
        return self.is_displayed(self.WARNING_VALIDATION_MANDATORY, timeout=3)

    def click_back(self):
        """Mengetuk tombol kembali."""
        self.click(self.BTN_BACK, label="Tombol Kembali")
