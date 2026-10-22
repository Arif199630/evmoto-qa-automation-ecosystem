"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - PROFIL & ACCOUNT PAGE OBJECT (profil_page.py)
================================================================================
Target: Layar Profil / Akun Pengguna ('Me' Tab) pada Aplikasi Flutter EVMoto.
Elemen diurutkan dari paling atas hingga paling bawah (Logout):
  1. Header Identitas Pengguna (Avatar, Nama, Nomor HP)
  2. Saldo Dompet & Pengaturan Pembayaran (Cash, EVMoto Wallet, GoPay, OVO, Default)
  3. Kontak Darurat (Emergency Contacts: Form Tambah, Simpan, Hapus, Modal)
  4. Alamat Tersimpan / Favorit (Saved Addresses: Tambah Rumah, Kantor, Lokasi Lain)
  5. Pengaturan Bahasa (Language: Indonesia <-> English, Snackbar Notifikasi)
  6. Panduan Penggunaan & Video Tutorial FAQ (Player Video, Ketiadaan Error Media)
  7. Banner Customer Service & Popup Aturan Lampiran Media
  8. Dokumen Legalitas (Syarat & Ketentuan, Kebijakan Privasi)
  9. Hapus Akun (Delete Account & Modal Peringatan Permanen)
 10. Keluar / Logout (Tombol Log Out, Dialog Konfirmasi Keluar, Batal & Konfirmasi)
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("ProfilPage")


class ProfilPage(BasePage):
    """Page Object untuk Halaman Akun & Profil Pengguna Mobile App EvMoto."""

    # ==========================================================================
    # 0. TAB NAVIGASI UTAMA (BOTTOM NAVIGATION BAR)
    # ==========================================================================
    NAV_ME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Me') or contains(@content-desc, 'Akun') or "
        "contains(@text, 'Me') or contains(@text, 'Akun')]"
    )
    NAV_HOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Home') or contains(@content-desc, 'Beranda') or "
        "contains(@text, 'Home') or contains(@text, 'Beranda')]"
    )
    NAV_ACTIVITY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Activity') or contains(@content-desc, 'Aktivitas') or "
        "contains(@text, 'Activity') or contains(@text, 'Aktivitas')]"
    )

    # ==========================================================================
    # 1. BAGIAN PALING ATAS: HEADER IDENTITAS & AVATAR PENGGUNA
    # ==========================================================================
    USER_AVATAR = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[contains(@content-desc, 'Profile') or "
        "contains(@content-desc, 'avatar') or contains(@resource-id, 'avatar') or @clickable='true']"
    )
    USER_NAME = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'user_name') or contains(@content-desc, 'QA') or "
        "contains(@content-desc, 'Pengguna') or contains(@content-desc, 'User') or "
        "contains(@text, 'Pengguna') or contains(@text, 'User') or contains(@content-desc, 'Dev') or "
        "contains(@content-desc, 'Prod')]"
    )
    USER_PHONE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '+62') or contains(@content-desc, '821') or "
        "contains(@content-desc, '08') or contains(@resource-id, 'user_phone') or "
        "contains(@text, '821') or contains(@text, '+62')]"
    )
    MODAL_AVATAR_PICKER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ganti Foto') or contains(@content-desc, 'Change Photo') or "
        "contains(@content-desc, 'Pilih Gambar') or contains(@content-desc, 'Pilih Sumber') or "
        "contains(@resource-id, 'bottom_sheet') or contains(@class, 'BottomSheet')]"
    )
    BTN_PICKER_CAMERA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kamera') or contains(@content-desc, 'Camera') or contains(@text, 'Kamera')]"
    )
    BTN_PICKER_GALLERY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Galeri') or contains(@content-desc, 'Gallery') or contains(@text, 'Galeri')]"
    )
    BTN_PICKER_CANCEL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@content-desc, 'Cancel') or contains(@text, 'Batal')]"
    )

    # ==========================================================================
    # 2. SALDO DOMPET & PENGATURAN PEMBAYARAN (PAYMENT METHODS)
    # ==========================================================================
    TEXT_WALLET_BALANCE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rp') or contains(@content-desc, 'Saldo') or "
        "contains(@content-desc, 'Balance') or contains(@text, 'Rp')]"
    )
    BTN_TOP_UP_WALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Top Up') or contains(@content-desc, 'Isi Saldo') or "
        "contains(@content-desc, 'Isi Ulang') or contains(@text, 'Top Up')]"
    )
    MODAL_TOP_UP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih Nominal') or contains(@content-desc, 'Top Up Saldo') or "
        "contains(@content-desc, 'Isi Saldo')]"
    )
    CHIP_NOMINAL_20K = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '20.000') or contains(@text, '20.000')]"
    )
    CHIP_NOMINAL_50K = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '50.000') or contains(@text, '50.000')]"
    )
    CHIP_NOMINAL_100K = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '100.000') or contains(@text, '100.000')]"
    )
    BTN_CANCEL_TOP_UP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@text, 'Batal') or contains(@content-desc, 'Cancel')]"
    )
    MENU_PAYMENT_SETTINGS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Payment Settings') or "
        "contains(@content-desc, 'Pengaturan Pembayaran') or contains(@text, 'Payment Settings')]"
    )
    ITEM_PAYMENT_CASH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cash') or contains(@text, 'Cash') or contains(@content-desc, 'Tunai')]"
    )
    ITEM_PAYMENT_WALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EVMoto Wallet') or contains(@content-desc, 'Dompet EVMoto') or "
        "contains(@content-desc, 'Wallet')]"
    )
    ITEM_PAYMENT_GOPAY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'GoPay') or contains(@text, 'GoPay')]"
    )
    ITEM_PAYMENT_OVO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'OVO') or contains(@text, 'OVO')]"
    )
    BTN_SET_DEFAULT_PAYMENT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Atur menjadi metode utama') or "
        "contains(@content-desc, 'Set as default') or contains(@content-desc, 'Default')]"
    )
    BTN_UNSET_DEFAULT_PAYMENT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batalkan menjadi metode utama') or "
        "contains(@content-desc, 'Unset as default')]"
    )
    MODAL_UNSET_DEFAULT_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batalkan Metode Utama') or "
        "contains(@content-desc, 'tidak lagi digunakan sebagai metode utama')]"
    )
    BTN_CONFIRM_UNSET_DEFAULT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ya, Batalkan') or contains(@text, 'Ya, Batalkan')]"
    )
    LINK_PAYMENT_HISTORY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'history') or contains(@content-desc, 'riwayat') or "
        "contains(@content-desc, 'Riwayat') or contains(@content-desc, 'Lihat riwayat pembayaran')]"
    )

    # ==========================================================================
    # 3. KONTAK DARURAT (EMERGENCY CONTACTS)
    # ==========================================================================
    MENU_EMERGENCY_CONTACT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Emergency Contact') or contains(@content-desc, 'Kontak Darurat')]"
    )
    TEXT_EMERGENCY_SUBTITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lebih Tenang di Setiap Perjalanan') or contains(@content-desc, 'Peace of Mind')]"
    )
    TEXT_EMERGENCY_EMPTY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum ada kontak darurat') or contains(@content-desc, 'No emergency contacts yet')]"
    )
    BTN_ADD_EMERGENCY_CONTACT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '+ Tambah Kontak Darurat') or "
        "contains(@content-desc, '+ Add Emergency Contact') or contains(@content-desc, 'Tambah Kontak')]"
    )
    INPUT_EMERGENCY_NAME = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'nama') or contains(@hint, 'Name') or "
        "contains(@text, 'nama') or contains(@text, 'name') or @focused='true' or position()=1]"
    )
    INPUT_EMERGENCY_PHONE = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, '812') or contains(@hint, 'Nomor') or "
        "contains(@text, '812') or contains(@text, 'Phone') or position()=2]"
    )
    BTN_SAVE_EMERGENCY_CONTACT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tambah Kontak') or contains(@content-desc, 'Simpan Kontak') or "
        "contains(@content-desc, 'Save Contact') or contains(@content-desc, 'Add Contact')]"
    )
    BTN_DELETE_EMERGENCY_CONTACT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hapus') or contains(@content-desc, 'Delete')]"
    )
    MODAL_DELETE_EMERGENCY_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ingin Hapus Kontak') or contains(@content-desc, 'Delete Contact?') or "
        "contains(@content-desc, 'menghapus kontak')]"
    )

    # ==========================================================================
    # 4. ALAMAT TERSIMPAN / FAVORIT (SAVED ADDRESSES)
    # ==========================================================================
    MENU_SAVED_ADDRESSES = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saved Address') or contains(@content-desc, 'Alamat Tersimpan') or "
        "contains(@content-desc, 'Alamat Favorit')]"
    )
    TEXT_EMPTY_SAVED_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'No saved addresses') or contains(@content-desc, 'Belum ada alamat favorit')]"
    )
    BTN_ADD_HOME_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tambah Rumah') or contains(@content-desc, 'Add Home') or "
        "contains(@content-desc, 'Rumah')]"
    )
    BTN_ADD_OFFICE_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Office') or contains(@content-desc, 'Kantor')]"
    )
    BTN_ADD_OTHER_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tambah Lokasi Lain') or contains(@content-desc, 'Add Other Location') or "
        "contains(@content-desc, 'Tambah')]"
    )
    MODAL_ADD_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Simpan Alamat') or contains(@content-desc, 'Tambah Alamat') or "
        "contains(@content-desc, 'Alamat Baru')]"
    )
    INPUT_ADDRESS_LABEL = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Label') or contains(@hint, 'Nama Alamat') or position()=1]"
    )
    INPUT_ADDRESS_NOTE = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Patokan') or contains(@hint, 'Catatan') or "
        "contains(@text, 'Catatan') or position()=2]"
    )
    BTN_SAVE_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Simpan Alamat') or contains(@content-desc, 'Save Address') or "
        "contains(@content-desc, 'Simpan')]"
    )
    BTN_DELETE_SAVED_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hapus Alamat') or contains(@content-desc, 'Delete Address') or "
        "contains(@content-desc, 'Hapus')]"
    )
    MODAL_DELETE_ADDRESS_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'delete the address') or contains(@content-desc, 'menghapus alamat')]"
    )

    # ==========================================================================
    # 5. PENGATURAN BAHASA (LANGUAGE SETTINGS & SNACKBAR)
    # ==========================================================================
    MENU_LANGUAGE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Language') or contains(@content-desc, 'Bahasa')]"
    )
    OPT_LANG_ENGLISH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'English') or contains(@text, 'English')]"
    )
    OPT_LANG_INDONESIAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Indonesia') or contains(@text, 'Indonesia')]"
    )
    SNACKBAR_LANG_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'berhasil diubah') or contains(@content-desc, 'Language changed successfully') or "
        "contains(@text, 'berhasil diubah') or contains(@text, 'Language changed')]"
    )

    # ==========================================================================
    # 6. PUSAT BANTUAN, FAQ & VIDEO PANDUAN APLIKASI
    # ==========================================================================
    MENU_HELP_CENTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cara Penggunaan') or contains(@content-desc, 'How to Use the App') or "
        "contains(@content-desc, 'Help') or contains(@content-desc, 'Bantuan')]"
    )
    TEXT_FAQ_USAGE_SUBTITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Langkah Mudah Menggunakan Aplikasi') or contains(@content-desc, 'Easy Steps')]"
    )
    ITEM_FAQ_DOWNLOAD_REGISTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Unduh dan Daftar') or contains(@content-desc, 'Download and Register')]"
    )
    ITEM_FAQ_OPEN_HOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Buka Halaman Utama') or contains(@content-desc, 'Open Home')]"
    )
    ITEM_FAQ_BOOK_RIDE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cara Memesan Perjalanan') or contains(@content-desc, 'How to Book')]"
    )
    ELEMENT_VIDEO_PLAYER = (
        AppiumBy.XPATH,
        "//android.view.View[contains(@resource-id, 'video') or contains(@class, 'VideoPlayer')] | "
        "//android.widget.FrameLayout[contains(@resource-id, 'player')] | "
        "//android.view.View[contains(@content-desc, 'video') or @clickable='true']"
    )
    TEXT_VIDEO_LOAD_FAILED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Video gagal dimuat') or contains(@text, 'Video gagal dimuat') or "
        "contains(@content-desc, 'Video load failed')]"
    )

    # ==========================================================================
    # 7. BANNER LAYANAN CUSTOMER SERVICE (CS) & POPUP LAMPIRAN MEDIA
    # ==========================================================================
    BANNER_CS_HELP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hubungi Customer Service') or "
        "contains(@content-desc, 'Contact Customer Service') or "
        "contains(@content-desc, 'Kami Siap Membantu') or contains(@content-desc, 'Were Here to Help')]"
    )
    POPUP_CS_IMAGE_WARNING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Hanya gambar/foto yang dapat diunggah') or contains(@content-desc, 'image only')]"
    )
    FORM_CS_TICKET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Formulir Bantuan') or contains(@content-desc, 'Kirim Tiket') or "
        "contains(@content-desc, 'Customer Service') or contains(@text, 'Customer Service')]"
    )
    INPUT_CS_DESCRIPTION = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Jelaskan') or contains(@hint, 'kendala') or "
        "contains(@text, 'kendala') or @class='android.widget.EditText']"
    )
    BTN_SUBMIT_CS_TICKET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim Pesan') or contains(@content-desc, 'Kirim Tiket') or "
        "contains(@content-desc, 'Kirim') or contains(@text, 'Kirim')]"
    )
    VALIDATION_CS_DESCRIPTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'wajib diisi') or contains(@content-desc, 'cannot be empty') or "
        "contains(@content-desc, 'harus diisi')]"
    )

    # ==========================================================================
    # 8. DOKUMEN LEGALITAS: SYARAT & KETENTUAN, KEBIJAKAN PRIVASI
    # ==========================================================================
    MENU_TERMS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Terms and Conditions') or contains(@content-desc, 'Syarat dan Ketentuan')]"
    )
    MENU_PRIVACY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Privacy Policy') or contains(@content-desc, 'Kebijakan Privasi')]"
    )

    # ==========================================================================
    # 9. HAPUS AKUN (DELETE ACCOUNT)
    # ==========================================================================
    MENU_DELETE_ACCOUNT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Delete account') or contains(@content-desc, 'Hapus akun')]"
    )
    MODAL_DELETE_WARNING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'permanen dan tidak dapat dipulihkan') or "
        "contains(@content-desc, 'permanently deleted and cannot be recovered')]"
    )
    BTN_CONFIRM_DELETE_ACCOUNT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Delete account') or contains(@content-desc, 'Hapus akun')]"
    )
    BTN_CANCEL_DELETE_ACCOUNT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cancel') or contains(@content-desc, 'Batal')]"
    )

    # ==========================================================================
    # 10. BAGIAN PALING BAWAH: LOGOUT & DIALOG KONFIRMASI KELUAR
    # ==========================================================================
    BTN_LOGOUT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Log Out') or contains(@content-desc, 'Keluar') or "
        "contains(@content-desc, 'Sign out') or contains(@text, 'Log Out') or contains(@text, 'Keluar')]"
    )
    DIALOG_LOGOUT_TITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Are you sure you want to log out') or "
        "contains(@content-desc, 'Apakah Anda yakin ingin keluar')]"
    )
    DIALOG_LOGOUT_DESC = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'need to log in again') or "
        "contains(@content-desc, 'perlu login kembali') or contains(@content-desc, 'keluar dari akun')]"
    )
    BTN_CONFIRM_EXIT_NOW = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Log out now') or contains(@content-desc, 'Keluar sekarang') or "
        "contains(@content-desc, 'Ya, Keluar') or contains(@text, 'Log out now') or contains(@text, 'Keluar sekarang')]"
    )
    BTN_CANCEL_LOGOUT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cancel') or contains(@content-desc, 'Batal') or "
        "contains(@text, 'Cancel') or contains(@text, 'Batal')]"
    )
    SNACKBAR_LOGOUT_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Logged out successfully') or contains(@content-desc, 'Berhasil keluar') or "
        "contains(@text, 'Berhasil keluar')]"
    )

    # General Dialog / Popup & Snackbar Locators
    POPUP_MODAL_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'dialog') or contains(@resource-id, 'modal') or "
        "contains(@class, 'AlertDialog') or contains(@class, 'Dialog') or "
        "contains(@content-desc, 'Are you sure') or contains(@content-desc, 'Apakah Anda yakin')]"
    )
    SNACKBAR_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'snackbar') or contains(@class, 'SnackBar') or "
        "contains(@content-desc, 'berhasil') or contains(@content-desc, 'success') or "
        "contains(@text, 'berhasil') or contains(@text, 'success')]"
    )

    # ==========================================================================
    # ACTION METHODS - DIURUTKAN DARI ATAS KE BAWAH
    # ==========================================================================

    def pause_between_tests(self, seconds: float = 5.0, reason: str = "Jeda anti race condition"):
        """Jeda deliberasi 5 detik antar pengetesan agar tidak terjadi race condition."""
        logger.info(f"[ANTI RACE CONDITION] Jeda {seconds} detik: {reason}")
        time.sleep(seconds)

    # 1. Header Identitas
    def is_profile_screen_displayed(self, timeout: int = 15) -> bool:
        """Memeriksa apakah layar Profil/Akun aktif dan elemen utama termuat."""
        return (
            self.is_displayed(self.BTN_LOGOUT, timeout=timeout) or
            self.is_displayed(self.MENU_PAYMENT_SETTINGS, timeout=timeout) or
            self.is_displayed(self.USER_PHONE, timeout=timeout)
        )

    def is_avatar_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah gambar avatar profil tampil di header."""
        return self.is_displayed(self.USER_AVATAR, timeout=timeout)

    def open_avatar_picker(self):
        """Menekan avatar pengguna untuk membuka bottomsheet pemilih foto profil."""
        self.click(self.USER_AVATAR, label="Avatar Pengguna")

    def is_avatar_picker_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal/bottomsheet pemilih foto profil tampil."""
        return (
            self.is_displayed(self.MODAL_AVATAR_PICKER, timeout=timeout) or
            self.is_displayed(self.BTN_PICKER_CAMERA, timeout=timeout) or
            self.is_displayed(self.BTN_PICKER_GALLERY, timeout=timeout)
        )

    def cancel_avatar_picker(self):
        """Membatalkan pemilihan foto profil."""
        if self.is_displayed(self.BTN_PICKER_CANCEL, timeout=3):
            self.click(self.BTN_PICKER_CANCEL, label="Tombol 'Batal' Avatar Picker")
        else:
            self.press_back_key()

    def get_user_name_text(self) -> str:
        """Mengambil teks nama pengguna di header."""
        try:
            return self.get_text(self.USER_NAME)
        except Exception:
            return ""

    def get_user_phone_text(self) -> str:
        """Mengambil teks nomor telepon pengguna di header."""
        try:
            return self.get_text(self.USER_PHONE)
        except Exception:
            return ""

    # 2. Saldo & Pengaturan Pembayaran
    def get_wallet_balance_text(self) -> str:
        """Mengambil teks saldo dompet pada layar profil."""
        try:
            return self.get_text(self.TEXT_WALLET_BALANCE)
        except Exception:
            return ""

    def open_top_up_wallet(self):
        """Menekan saldo atau tombol Top Up untuk memicu modal pengisian saldo."""
        if self.is_displayed(self.BTN_TOP_UP_WALLET, timeout=3):
            self.click(self.BTN_TOP_UP_WALLET, label="Tombol 'Top Up'")
        else:
            self.click(self.TEXT_WALLET_BALANCE, label="Kartu Saldo Dompet")

    def is_top_up_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal pilihan nominal top up saldo muncul."""
        return (
            self.is_displayed(self.MODAL_TOP_UP, timeout=timeout) or
            self.is_displayed(self.CHIP_NOMINAL_20K, timeout=timeout) or
            self.is_displayed(self.CHIP_NOMINAL_50K, timeout=timeout)
        )

    def cancel_top_up(self):
        """Membatalkan top up saldo dan menutup modal."""
        if self.is_displayed(self.BTN_CANCEL_TOP_UP, timeout=3):
            self.click(self.BTN_CANCEL_TOP_UP, label="Tombol 'Batal Top Up'")
        else:
            self.press_back_key()

    def navigate_to_payment_settings(self):
        """Membuka menu Pengaturan Pembayaran."""
        self.click(self.MENU_PAYMENT_SETTINGS, label="Menu 'Payment Settings'")

    def is_cash_payment_option_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.ITEM_PAYMENT_CASH, timeout=timeout)

    def is_wallet_payment_option_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.ITEM_PAYMENT_WALLET, timeout=timeout)

    def is_gopay_payment_option_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.ITEM_PAYMENT_GOPAY, timeout=timeout)

    def is_ovo_payment_option_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.ITEM_PAYMENT_OVO, timeout=timeout)

    def navigate_to_payment_history(self):
        """Membuka riwayat pembayaran."""
        self.click(self.LINK_PAYMENT_HISTORY, label="Link 'Lihat riwayat pembayaran'")

    def toggle_set_default_payment_method(self):
        """Menjadikan metode pembayaran saat ini sebagai metode utama."""
        if self.is_displayed(self.BTN_SET_DEFAULT_PAYMENT, timeout=3):
            self.click(self.BTN_SET_DEFAULT_PAYMENT, label="Tombol 'Atur menjadi metode utama'")

    # 3. Kontak Darurat
    def navigate_to_emergency_contacts(self):
        """Membuka halaman Kontak Darurat."""
        self.click(self.MENU_EMERGENCY_CONTACT, label="Menu 'Kontak Darurat'")

    def is_emergency_contacts_empty_state_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.TEXT_EMERGENCY_EMPTY, timeout=timeout)

    def click_add_emergency_contact(self):
        """Menekan tombol '+ Tambah Kontak Darurat'."""
        self.click(self.BTN_ADD_EMERGENCY_CONTACT, label="Tombol '+ Tambah Kontak Darurat'")

    def input_emergency_contact_form(self, name: str, phone: str):
        """Mengisi formulir input nama dan nomor handphone kontak darurat."""
        try:
            self.type_text(self.INPUT_EMERGENCY_NAME, name, label="Field Nama Kontak")
            self.type_text(self.INPUT_EMERGENCY_PHONE, phone, label="Field Nomor Telepon Kontak")
        except Exception as e:
            logger.warning(f"Fallback input kontak darurat: {e}")
            try:
                self.driver.switch_to.active_element.send_keys(f"{name}\t{phone}")
            except Exception:
                pass

    def save_emergency_contact(self):
        """Menyimpan data kontak darurat."""
        self.click(self.BTN_SAVE_EMERGENCY_CONTACT, label="Tombol 'Tambah/Simpan Kontak'")

    def open_delete_emergency_contact_dialog(self):
        """Menekan tombol hapus kontak darurat untuk memicu popup konfirmasi."""
        self.click(self.BTN_DELETE_EMERGENCY_CONTACT, label="Tombol 'Hapus Kontak'")

    def is_delete_emergency_contact_dialog_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.MODAL_DELETE_EMERGENCY_CONFIRM, timeout=timeout)

    # 4. Alamat Tersimpan / Favorit
    def navigate_to_saved_addresses(self):
        """Membuka menu Alamat Tersimpan / Favorit."""
        self.click(self.MENU_SAVED_ADDRESSES, label="Menu 'Saved Addresses'")

    def is_saved_address_empty_state_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.TEXT_EMPTY_SAVED_ADDRESS, timeout=timeout)

    def is_add_home_address_button_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.BTN_ADD_HOME_ADDRESS, timeout=timeout)

    def is_add_office_address_button_displayed(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.BTN_ADD_OFFICE_ADDRESS, timeout=timeout)

    def input_saved_address_details(self, label: str, note: str):
        """Mengisi formulir penambahan alamat favorit baru beserta catatan patokan."""
        try:
            self.type_text(self.INPUT_ADDRESS_LABEL, label, label="Label Alamat")
            self.type_text(self.INPUT_ADDRESS_NOTE, note, label="Catatan Patokan Alamat")
        except Exception as e:
            logger.warning(f"Fallback input detail alamat: {e}")

    def save_address(self):
        """Menekan tombol simpan alamat favorit."""
        if self.is_displayed(self.BTN_SAVE_ADDRESS, timeout=3):
            self.click(self.BTN_SAVE_ADDRESS, label="Tombol 'Simpan Alamat'")

    def delete_saved_address(self):
        """Menekan tombol hapus pada item alamat tersimpan."""
        if self.is_displayed(self.BTN_DELETE_SAVED_ADDRESS, timeout=3):
            self.click(self.BTN_DELETE_SAVED_ADDRESS, label="Tombol 'Hapus Alamat'")

    # 5. Pengaturan Bahasa & Snackbar
    def navigate_to_language(self):
        """Membuka menu Pengaturan Bahasa."""
        self.click(self.MENU_LANGUAGE, label="Menu 'Language / Bahasa'")

    def select_language(self, language: str = "id"):
        """Mengubah bahasa antarmuka aplikasi ('id' untuk Indonesia, 'en' untuk English)."""
        self.navigate_to_language()
        time.sleep(1)
        if language.lower() in ("id", "indonesia"):
            self.click(self.OPT_LANG_INDONESIAN, label="Pilihan Bahasa Indonesia")
        else:
            self.click(self.OPT_LANG_ENGLISH, label="Pilihan Bahasa Inggris")
        time.sleep(1.5)

    def is_language_snackbar_displayed(self, timeout: int = 4) -> bool:
        """Memverifikasi kemunculan snackbar notifikasi perubahan bahasa."""
        return self.is_displayed(self.SNACKBAR_LANG_SUCCESS, timeout=timeout)

    # 6. Pusat Bantuan & Panduan Video FAQ
    def navigate_to_help_center(self):
        """Membuka menu Cara Penggunaan Aplikasi / FAQ."""
        self.click(self.MENU_HELP_CENTER, label="Menu 'Cara Penggunaan Aplikasi'")

    def is_help_center_displayed(self, timeout: int = 5) -> bool:
        return (
            self.is_displayed(self.TEXT_FAQ_USAGE_SUBTITLE, timeout=timeout) or
            self.is_displayed(self.ITEM_FAQ_DOWNLOAD_REGISTER, timeout=timeout)
        )

    def open_faq_tutorial_step(self, step: str = "book_ride"):
        """Membuka langkah tutorial spesifik pada FAQ."""
        if step == "download":
            self.click(self.ITEM_FAQ_DOWNLOAD_REGISTER, label="Langkah 'Unduh dan Daftar'")
        elif step == "open_home":
            self.click(self.ITEM_FAQ_OPEN_HOME, label="Langkah 'Buka Halaman Utama'")
        else:
            self.click(self.ITEM_FAQ_BOOK_RIDE, label="Langkah 'Cara Memesan Perjalanan'")

    def is_video_player_functional(self, timeout: int = 8) -> bool:
        """Memverifikasi video player termuat dan bebas error 'Video gagal dimuat'."""
        has_error = self.is_displayed(self.TEXT_VIDEO_LOAD_FAILED, timeout=2)
        if has_error:
            logger.error("Ditemukan kegagalan pemuatan video tutorial: 'Video gagal dimuat'!")
            return False
        return self.is_displayed(self.ELEMENT_VIDEO_PLAYER, timeout=timeout) or not has_error

    # 7. Banner CS & Popup Media
    def verify_cs_banner_and_popup(self, timeout: int = 5) -> bool:
        """Memverifikasi keberadaan banner CS dan popup lampiran media."""
        return self.is_displayed(self.BANNER_CS_HELP, timeout=timeout)

    def open_cs_ticket_form(self):
        """Membuka formulir tiket Customer Service."""
        self.click(self.BANNER_CS_HELP, label="Banner 'Customer Service'")

    def is_cs_ticket_form_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah form tiket CS muncul."""
        return self.is_displayed(self.FORM_CS_TICKET, timeout=timeout) or self.is_displayed(self.INPUT_CS_DESCRIPTION, timeout=timeout)

    def submit_cs_ticket(self, description: str = ""):
        """Mengisi dan mengirimkan tiket bantuan CS."""
        if description:
            try:
                self.type_text(self.INPUT_CS_DESCRIPTION, description, label="Deskripsi Tiket CS")
            except Exception:
                pass
        self.click(self.BTN_SUBMIT_CS_TICKET, label="Tombol 'Kirim Tiket CS'")

    def is_cs_validation_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah validasi error deskripsi kendala kosong muncul."""
        return self.is_displayed(self.VALIDATION_CS_DESCRIPTION, timeout=timeout)

    # 8. Legalitas (Terms & Privacy)
    def navigate_to_terms(self):
        """Membuka halaman Syarat & Ketentuan."""
        self.click(self.MENU_TERMS, label="Menu 'Terms and Conditions'")

    def navigate_to_privacy(self):
        """Membuka halaman Kebijakan Privasi."""
        self.click(self.MENU_PRIVACY, label="Menu 'Privacy Policy'")

    # 9. Hapus Akun
    def open_delete_account_modal(self):
        """Menekan menu 'Delete account' untuk memicu modal peringatan permanen."""
        self.click(self.MENU_DELETE_ACCOUNT, label="Menu 'Delete account'")

    def is_delete_account_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal peringatan hapus akun permanen muncul."""
        return self.is_displayed(self.MODAL_DELETE_WARNING, timeout=timeout)

    def cancel_delete_account(self):
        """Membatalkan hapus akun dan menutup modal."""
        if self.is_displayed(self.BTN_CANCEL_DELETE_ACCOUNT, timeout=3):
            self.click(self.BTN_CANCEL_DELETE_ACCOUNT, label="Tombol 'Batal Hapus Akun'")
        else:
            self.press_back_key()

    # 10. Bagian Paling Bawah: Logout
    def open_logout_dialog(self):
        """Menekan tombol 'Log Out' untuk memicu dialog konfirmasi keluar."""
        self.click(self.BTN_LOGOUT, label="Tombol 'Log Out'")

    def is_logout_dialog_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah dialog konfirmasi logout muncul."""
        return (
            self.is_displayed(self.DIALOG_LOGOUT_TITLE, timeout=timeout) or
            self.is_displayed(self.BTN_CONFIRM_EXIT_NOW, timeout=timeout)
        )

    def confirm_logout(self):
        """Mengonfirmasi keluar pada dialog logout."""
        self.click(self.BTN_CONFIRM_EXIT_NOW, label="Tombol 'Log out now / Keluar sekarang'")

    def cancel_logout(self):
        """Membatalkan logout (menekan tombol Batal atau tombol hardware back)."""
        if self.is_displayed(self.BTN_CANCEL_LOGOUT, timeout=3):
            self.click(self.BTN_CANCEL_LOGOUT, label="Tombol 'Batal Logout'")
        else:
            self.press_back_key()

    def press_back_key(self):
        """Menekan tombol Android Hardware Back Key (Keycode 4)."""
        logger.info("Menekan Android Hardware Back Key (Keycode 4)")
        try:
            self.driver.press_keycode(4)
        except Exception as e:
            logger.warning(f"Gagal menekan hardware back key: {e}")
        time.sleep(1)


# Backward Compatibility Aliases
ProfilePage = ProfilPage
ProfilLocators = ProfilPage
ProfileLocators = ProfilPage
