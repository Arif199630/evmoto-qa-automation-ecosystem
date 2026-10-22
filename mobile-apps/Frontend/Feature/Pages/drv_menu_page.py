"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - MENU & ACCOUNT PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Layar Menu Mitra Driver, Hubungkan eWallet ECGO, Penarikan Dana &
          Rekening Tersimpan, Izin Order Layar Utama, Bersihkan Cache,
          Ganti Bahasa (i18n), FAQ / Panduan Penggunaan, Hapus Akun, dan Logout.
Wording : Bersumber 100% dari strings resmi APK driver_lang_id.json
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("DrvMenuPage")


class DrvMenuPage(BasePage):
    """Page Object untuk Layar Menu, eWallet, & Pengaturan Akun Driver EvMoto."""

    # ==========================================================================
    # 1. HEADER & IDENTITAS DRIVER
    # ==========================================================================
    TITLE_MENU = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Menu') or contains(@text, 'Menu')]"
    )
    PROFILE_DRIVER_NAME = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'driver_name') or contains(@content-desc, 'Driver') or "
        "contains(@content-desc, 'Mitra') or contains(@class, 'TextView')][1]"
    )

    # ==========================================================================
    # 2. EWALLET ECGO & KARTU SALDO
    # ==========================================================================
    CARD_SALDO_EVMOTO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo EVMoto') or contains(@text, 'Saldo EVMoto')]"
    )
    CARD_SALDO_ECGO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo ECGO') or contains(@text, 'Saldo ECGO')]"
    )
    BTN_HUBUNGKAN_EWALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hubungkan') or contains(@text, 'Hubungkan')]"
    )
    BTN_PUTUSKAN_EWALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Putuskan eWallet') or contains(@text, 'Putuskan eWallet')]"
    )
    DIALOG_PUTUSKAN_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ya, Putuskan') or contains(@text, 'Ya, Putuskan')]"
    )

    # ==========================================================================
    # 3. REKENING BANK & PENARIKAN DANA (WITHDRAW)
    # ==========================================================================
    MENU_TARIK_DANA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tarik Dana') or contains(@text, 'Tarik Dana')]"
    )
    MENU_REKENING_TERSIMPAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Nomor Rekening Tersimpan') or contains(@text, 'Nomor Rekening Tersimpan')]"
    )
    BTN_TAMBAH_REKENING_BARU = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tambahhkan Nomor Rekening Baru') or contains(@text, 'Tambahhkan Nomor Rekening Baru') or "
        "contains(@content-desc, 'Tambah Rekening') or contains(@text, 'Tambah Rekening')]"
    )
    FIELD_SELECT_BANK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih Bank') or contains(@text, 'Pilih Bank') or "
        "contains(@content-desc, 'Pilih nama bank') or contains(@text, 'Pilih nama bank')]"
    )
    FIELD_ACCOUNT_NUMBER = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'nomor rekening') or contains(@hint, 'Nomor Rekening')]"
    )
    FIELD_OWNER_NAME = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'nama pemilik') or contains(@hint, 'Nama Pemilik')]"
    )
    BTN_SIMPAN_REKENING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Simpan') or contains(@text, 'Simpan') or "
        "contains(@content-desc, 'Tambah') or contains(@text, 'Tambah')]"
    )
    SNACKBAR_REKENING_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil menambah rekening') or contains(@text, 'Berhasil menambah rekening')]"
    )

    # ==========================================================================
    # 4. PENGATURAN APLIKASI & KELOLA AKUN
    # ==========================================================================
    MENU_KELOLA_AKUN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kelola Akun') or contains(@text, 'Kelola Akun')]"
    )
    MENU_OVERLAY_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Izinkan Order di Layar Utama') or contains(@text, 'Izinkan Order di Layar Utama') or "
        "contains(@content-desc, 'Akfitkan Order Dilayar Utama') or contains(@text, 'Akfitkan Order Dilayar Utama')]"
    )
    MENU_BERSIHKAN_CACHE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bersihkan cache') or contains(@text, 'Bersihkan cache') or "
        "contains(@content-desc, 'Clear Cache') or contains(@text, 'Clear Cache')]"
    )
    SNACKBAR_CACHE_CLEARED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil membersihkan cache') or contains(@text, 'Berhasil membersihkan cache')]"
    )

    # Pengaturan Bahasa (i18n)
    MENU_GANTI_BAHASA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ganti Bahasa') or contains(@text, 'Ganti Bahasa') or "
        "contains(@content-desc, 'Bahasa') or contains(@text, 'Bahasa')]"
    )
    OPTION_LANG_INDONESIAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bahasa Indonesia') or contains(@text, 'Bahasa Indonesia')]"
    )
    OPTION_LANG_ENGLISH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'English') or contains(@text, 'English')]"
    )
    OPTION_LANG_CHINESE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '當代中文') or contains(@text, '當代中文')]"
    )
    SNACKBAR_LANG_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil mengganti bahasa') or contains(@text, 'Berhasil mengganti bahasa')]"
    )

    # Panduan & FAQ Penggunaan
    MENU_CARA_PENGGUNAAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cara Penggunaan Aplikasi') or contains(@text, 'Cara Penggunaan Aplikasi')]"
    )
    TEXT_TIPS_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tips untuk Driver') or contains(@text, 'Tips untuk Driver')]"
    )

    # ==========================================================================
    # 5. HAPUS AKUN & LOGOUT (AUTHENTICATION LIFECYCLE)
    # ==========================================================================
    MENU_HAPUS_AKUN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hapus Akun') or contains(@text, 'Hapus Akun')]"
    )
    DIALOG_HAPUS_AKUN_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Yakin Ingin Mengajukan Penghapusan Akun?') or "
        "contains(@text, 'Yakin Ingin Mengajukan Penghapusan Akun?')]"
    )
    BTN_CONFIRM_HAPUS_AKUN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hapus Sekarang') or contains(@text, 'Hapus Sekarang')]"
    )

    MENU_LOGOUT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Keluar dari Akun') or contains(@text, 'Keluar dari Akun')]"
    )
    DIALOG_LOGOUT_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Yakin Ingin Keluar Dari Akun?') or contains(@text, 'Yakin Ingin Keluar Dari Akun?')]"
    )
    BTN_CONFIRM_LOGOUT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Keluar Sekarang') or contains(@text, 'Keluar Sekarang')]"
    )
    BTN_CANCEL_LOGOUT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@text, 'Batal')]"
    )
    SNACKBAR_LOGOUT_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Berhasil keluar akun') or contains(@text, 'Berhasil keluar akun')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    def is_menu_screen_displayed(self) -> bool:
        """Memeriksa apakah layar Menu Driver aktif."""
        return self.is_displayed(self.TITLE_MENU, timeout=5) or self.is_displayed(self.MENU_KELOLA_AKUN, timeout=4)

    def is_ewallet_ecgo_displayed(self) -> bool:
        """Memeriksa apakah modul eWallet ECGO ditampilkan."""
        return self.is_displayed(self.CARD_SALDO_EVMOTO, timeout=3) or self.is_displayed(self.CARD_SALDO_ECGO, timeout=3)

    def click_hubungkan_ewallet(self):
        """Mengetuk tombol Hubungkan eWallet ECGO."""
        self.click(self.BTN_HUBUNGKAN_EWALLET, label="Tombol Hubungkan eWallet ECGO")

    def click_putuskan_ewallet(self):
        """Mengetuk tombol Putuskan eWallet ECGO."""
        self.click(self.BTN_PUTUSKAN_EWALLET, label="Tombol Putuskan eWallet ECGO")

    def open_rekening_tersimpan(self):
        """Membuka menu Nomor Rekening Tersimpan."""
        self.scroll_down()
        self.click(self.MENU_REKENING_TERSIMPAN, label="Menu Nomor Rekening Tersimpan")

    def click_tambah_rekening_baru(self):
        """Mengetuk tombol Tambahkan Nomor Rekening Baru."""
        self.click(self.BTN_TAMBAH_REKENING_BARU, label="Tombol Tambah Nomor Rekening Baru")

    def input_data_rekening(self, nomor_rekening: str, nama_pemilik: str):
        """Mengisi data formulir rekening penarikan dana."""
        self.type_text(self.FIELD_ACCOUNT_NUMBER, nomor_rekening, label="Field Nomor Rekening")
        self.type_text(self.FIELD_OWNER_NAME, nama_pemilik, label="Field Nama Pemilik")

    def click_simpan_rekening(self):
        """Mengetuk tombol Simpan Rekening."""
        self.click(self.BTN_SIMPAN_REKENING, label="Tombol Simpan Rekening")

    def open_kelola_akun(self):
        """Membuka sub-menu Kelola Akun."""
        self.click(self.MENU_KELOLA_AKUN, label="Menu Kelola Akun")

    def toggle_overlay_order_permission(self):
        """Mengetuk opsi izin overlay 'Izinkan Order di Layar Utama'."""
        self.click(self.MENU_OVERLAY_ORDER, label="Toggle Izinkan Order di Layar Utama")

    def click_bersihkan_cache(self):
        """Mengetuk opsi bersihkan cache aplikasi."""
        self.click(self.MENU_BERSIHKAN_CACHE, label="Tombol Bersihkan Cache")

    def is_cache_cleared_success_displayed(self) -> bool:
        """Memeriksa apakah snackbar 'Berhasil membersihkan cache' tampil."""
        return self.is_displayed(self.SNACKBAR_CACHE_CLEARED, timeout=3)

    def open_ganti_bahasa(self):
        """Membuka modal / opsi Ganti Bahasa."""
        self.click(self.MENU_GANTI_BAHASA, label="Menu Ganti Bahasa")

    def select_language(self, lang_code: str = "id"):
        """Memilih bahasa aplikasi: 'id' (Indonesia), 'en' (English), 'cn' (Chinese)."""
        if lang_code == "en":
            self.click(self.OPTION_LANG_ENGLISH, label="Pilihan Bahasa: English")
        elif lang_code == "cn":
            self.click(self.OPTION_LANG_CHINESE, label="Pilihan Bahasa: 當代中文")
        else:
            self.click(self.OPTION_LANG_INDONESIAN, label="Pilihan Bahasa: Bahasa Indonesia")

    def is_language_change_success_displayed(self) -> bool:
        """Memeriksa snackbar 'Berhasil mengganti bahasa'."""
        return self.is_displayed(self.SNACKBAR_LANG_SUCCESS, timeout=3)

    def open_cara_penggunaan(self):
        """Membuka layar Cara Penggunaan Aplikasi & Tips Driver."""
        self.click(self.MENU_CARA_PENGGUNAAN, label="Menu Cara Penggunaan Aplikasi")

    def is_tips_driver_displayed(self) -> bool:
        """Memeriksa apakah konten Tips untuk Driver tampil."""
        return self.is_displayed(self.TEXT_TIPS_DRIVER, timeout=4)

    def click_logout_menu(self):
        """Mengetuk menu Keluar dari Akun."""
        self.scroll_down()
        self.click(self.MENU_LOGOUT, label="Menu Keluar dari Akun")

    def is_logout_confirmation_displayed(self) -> bool:
        """Memeriksa apakah pop-up konfirmasi logout tampil."""
        return self.is_displayed(self.DIALOG_LOGOUT_CONFIRM, timeout=4)

    def confirm_logout(self):
        """Mengetuk tombol konfirmasi 'Keluar Sekarang'."""
        self.click(self.BTN_CONFIRM_LOGOUT, label="Tombol Konfirmasi Keluar Sekarang")

    def cancel_logout(self):
        """Mengetuk tombol Batal pada pop-up konfirmasi logout."""
        self.click(self.BTN_CANCEL_LOGOUT, label="Tombol Batal Logout")

    def click_delete_account_menu(self):
        """Mengetuk menu Hapus Akun."""
        self.scroll_down()
        self.click(self.MENU_HAPUS_AKUN, label="Menu Hapus Akun")

    def is_delete_account_confirmation_displayed(self) -> bool:
        """Memeriksa apakah pop-up konfirmasi hapus akun tampil."""
        return self.is_displayed(self.DIALOG_HAPUS_AKUN_CONFIRM, timeout=4)

    # ==========================================================================
    # 6. FEEDBACK / MASUKAN DRIVER & TENTANG KAMI
    # ==========================================================================
    MENU_FEEDBACK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Masukan') or contains(@text, 'Masukan') or contains(@content-desc, 'Feedback')]"
    )
    FIELD_FEEDBACK_TEXT = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Masukan') or contains(@hint, 'masukan') or contains(@hint, 'Saran')]"
    )
    BTN_SUBMIT_FEEDBACK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim') or contains(@text, 'Kirim')]"
    )
    SNACKBAR_FEEDBACK_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Masukan anda berhasil terkirim') or contains(@text, 'Masukan anda berhasil terkirim')]"
    )

    MENU_TENTANG_KAMI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tentang Kami') or contains(@text, 'Tentang Kami')]"
    )
    TEXT_APP_VERSION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'v1.9') or contains(@text, 'v1.9') or contains(@content-desc, 'Versi') or contains(@text, 'Versi')]"
    )

    # Detail FAQ & Video Tutorial
    FAQ_STEP_DOWNLOAD = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Unduh dan Daftar') or contains(@text, 'Unduh dan Daftar')]"
    )
    FAQ_STEP_OPEN_HOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Buka Halaman Utama') or contains(@text, 'Buka Halaman Utama')]"
    )
    FAQ_STEP_ACTIVATE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cara mengaktifkan aplikasi') or contains(@text, 'Cara mengaktifkan aplikasi')]"
    )
    VIDEO_LOAD_FAILED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Video gagal dimuat') or contains(@text, 'Video gagal dimuat')]"
    )

    # OTP Hapus Akun
    FIELD_DELETE_ACCOUNT_OTP = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'OTP') or contains(@hint, 'Kode')]"
    )
    BTN_CONFIRM_DELETE_OTP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Konfirmasi OTP') or contains(@text, 'Konfirmasi OTP')]"
    )

    def open_feedback_form(self):
        """Membuka form Kirim Masukan / Feedback."""
        self.click(self.MENU_FEEDBACK, label="Menu Masukan / Feedback")

    def submit_feedback(self, pesan: str):
        """Mengisi dan mengirim masukan driver."""
        self.type_text(self.FIELD_FEEDBACK_TEXT, pesan, label="Field Pesan Masukan")
        self.click(self.BTN_SUBMIT_FEEDBACK, label="Tombol Kirim Masukan")

    def is_feedback_success_displayed(self) -> bool:
        """Memeriksa apakah snackbar 'Masukan anda berhasil terkirim' tampil."""
        return self.is_displayed(self.SNACKBAR_FEEDBACK_SUCCESS, timeout=3)

    def open_tentang_kami(self):
        """Membuka halaman Tentang Kami."""
        self.click(self.MENU_TENTANG_KAMI, label="Menu Tentang Kami")

    def is_app_version_displayed(self) -> bool:
        """Memeriksa apakah versi aplikasi tertera."""
        return self.is_displayed(self.TEXT_APP_VERSION, timeout=3)

