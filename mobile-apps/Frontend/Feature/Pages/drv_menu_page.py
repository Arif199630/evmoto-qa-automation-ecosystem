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
import re
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
    # Halaman Menu tidak punya judul 'Menu'. Penandanya label header 'Total Orderan' yang tetap tampil saat
    # daftar menu digulir (peta layar CI 12 Nov 2026: 04_menu s.d. 07_menu_gulir_3). 'Cara Penggunaan Aplikasi'
    # tidak dipakai lagi: hilang saat digulir (05/06) dan juga judul layar panduan (19_cara_penggunaan_5dtk).
    TITLE_MENU = (
        AppiumBy.XPATH,
        "//*[@content-desc='Total Orderan' or @text='Total Orderan']"
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
    # Label persis 'Kelola Akun' di bagian bawah Menu (peta layar CI 12 Nov 2026: 06_menu_gulir_2).
    # Alternatif lama 'Evaluasi Saya' dibuang: itu menu lain (18_evaluasi_saya), bukan Kelola Akun.
    MENU_KELOLA_AKUN = (
        AppiumBy.XPATH,
        "//*[@content-desc='Kelola Akun' or @text='Kelola Akun']"
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
    # Subjudul layar panduan, tampil setelah konten selesai dimuat (peta layar CI 12 Nov 2026: 19_cara_penggunaan_5dtk)
    TITLE_LANGKAH_MUDAH = (
        AppiumBy.XPATH,
        "//*[@content-desc='Langkah Mudah Menggunakan Aplikasi' or @text='Langkah Mudah Menggunakan Aplikasi']"
    )
    # 'Tips untuk Driver' ada di bagian bawah layar Cara Penggunaan Aplikasi (21_cara_penggunaan_gulir_2), bukan di Menu
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
        """Membuka sub-menu Kelola Akun (item paling bawah Menu, perlu digulir: 06_menu_gulir_2)."""
        self.is_displayed_after_scroll(self.MENU_KELOLA_AKUN)
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
        """Membuka layar Cara Penggunaan Aplikasi & Tips Driver, lalu menunggu daftar langkah selesai dimuat."""
        self.click(self.MENU_CARA_PENGGUNAAN, label="Menu Cara Penggunaan Aplikasi")
        # Konten panduan baru muncul beberapa detik setelah layar terbuka (peta layar CI: dump 19 diambil 5 detik)
        self.is_displayed(self.TITLE_LANGKAH_MUDAH, timeout=10)

    def is_tips_driver_displayed(self) -> bool:
        """Memeriksa apakah konten Tips untuk Driver tampil (boleh menggeser layar panduan)."""
        return self.is_displayed_after_scroll(self.TEXT_TIPS_DRIVER)

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
    # Item Menu 'Kirim Masukan' (peta layar CI 12 Nov 2026: 04_menu); dicocokkan persis
    MENU_FEEDBACK = (
        AppiumBy.XPATH,
        "//*[@content-desc='Kirim Masukan' or @text='Kirim Masukan' or contains(@content-desc, 'Feedback')]"
    )
    # Hint resmi kolom masukan (hint_feedback) diawali 'Kemajuan kami tidak terlepas...', bukan 'Masukan'.
    # Form masukan hanya punya satu kolom input, jadi EditText pertama sudah cukup spesifik.
    FIELD_FEEDBACK_TEXT = (
        AppiumBy.XPATH,
        "(//android.widget.EditText)[1]"
    )
    # Hanya elemen Button dengan label persis. contains('Kirim') juga cocok dengan judul/menu 'Kirim Masukan'.
    BTN_SUBMIT_FEEDBACK = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Kirim' or @text='Kirim' or "
        "@content-desc='Kirim Masukan' or @text='Kirim Masukan']"
    )
    SNACKBAR_FEEDBACK_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Masukan anda berhasil terkirim') or contains(@text, 'Masukan anda berhasil terkirim')]"
    )

    MENU_TENTANG_KAMI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tentang Kami') or contains(@text, 'Tentang Kami')]"
    )
    # Label versi di bagian bawah Menu: 'App Versi v.1.9.27+97' (peta layar CI 12 Nov 2026: 06_menu_gulir_2)
    TEXT_APP_VERSION = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'App Versi') or starts-with(@text, 'App Versi') or "
        "contains(@content-desc, 'v1.9') or contains(@text, 'v1.9') or contains(@content-desc, 'Versi') or contains(@text, 'Versi')]"
    )

    # Detail FAQ & Video Tutorial
    # Langkah 1 di aplikasi berjudul 'Unduh Aplikasi' dengan isi '...dan daftar akun...'
    # (peta layar CI 12 Nov 2026: 19_cara_penggunaan_5dtk); label lama 'Unduh dan Daftar' dipertahankan
    FAQ_STEP_DOWNLOAD = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Unduh Aplikasi') or starts-with(@text, 'Unduh Aplikasi') or "
        "contains(@content-desc, 'Unduh dan Daftar') or contains(@text, 'Unduh dan Daftar')]"
    )
    FAQ_STEP_OPEN_HOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Buka Halaman Utama') or contains(@text, 'Buka Halaman Utama')]"
    )
    # Langkah 'Aktifkan Aplikasi' (peta layar CI 12 Nov 2026: 19_cara_penggunaan_5dtk, 21_cara_penggunaan_gulir_2);
    # label lama 'Cara mengaktifkan aplikasi' dipertahankan
    FAQ_STEP_ACTIVATE = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Aktifkan Aplikasi') or starts-with(@text, 'Aktifkan Aplikasi') or "
        "contains(@content-desc, 'Cara mengaktifkan aplikasi') or contains(@text, 'Cara mengaktifkan aplikasi')]"
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

    # ==========================================================================
    # 7. LOCATOR TAMBAHAN UNTUK VERIFIKASI HASIL (TEKS DARI driver_strings_id.json)
    # ==========================================================================
    # account_faq_tips_description
    TEXT_TIPS_DESCRIPTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pastikan koneksi internet stabil') or contains(@text, 'Pastikan koneksi internet stabil')]"
    )
    # critical_error_title (terlihat di dump layar emulator: View content-desc='Maaf terjadi kesalahan')
    TEXT_CRITICAL_ERROR = (
        AppiumBy.XPATH,
        "//*[@content-desc='Maaf terjadi kesalahan' or @text='Maaf terjadi kesalahan' or "
        "@content-desc='Kesalahan server' or @text='Kesalahan server']"
    )
    # Bocoran pesan error basis data ke layar (tidak boleh muncul)
    TEXT_DATABASE_ERROR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'SQL') or contains(@text, 'SQL') or "
        "contains(@content-desc, 'syntax error') or contains(@text, 'syntax error')]"
    )
    # account_delete_otp_title
    TITLE_DELETE_ACCOUNT_OTP = (
        AppiumBy.XPATH,
        "//*[@content-desc='Masukkan Kode OTP' or @text='Masukkan Kode OTP']"
    )
    # ewallet_resend_code_in: 'Kirim ulang kode dalam ' + sisa detik
    TEXT_RESEND_OTP_COUNTDOWN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim ulang kode dalam') or contains(@text, 'Kirim ulang kode dalam')]"
    )
    # account_delete_success_title (tidak boleh muncul saat OTP salah)
    TEXT_DELETE_ACCOUNT_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Akun Anda telah berhasil dihapus') or contains(@text, 'Akun Anda telah berhasil dihapus')]"
    )

    def scroll_down(self, ratio: float = 0.4):
        """Menggeser layar ke bawah (jari dari 70% ke 30% tinggi layar) memakai swipe dari BasePage."""
        size = self.driver.get_window_size()
        x = int(size["width"] / 2)
        start_y = int(size["height"] * 0.7)
        end_y = int(size["height"] * (0.7 - ratio))
        self.swipe(x, start_y, x, end_y, 500)
        time.sleep(0.5)

    def is_displayed_after_scroll(self, locator, max_swipes: int = 3, timeout: int = 3) -> bool:
        """Mencari elemen; bila belum terlihat, geser layar ke bawah lalu cek ulang (maksimal max_swipes kali)."""
        if self.is_displayed(locator, timeout=timeout):
            return True
        for _ in range(max_swipes):
            self.scroll_down()
            if self.is_displayed(locator, timeout=2):
                return True
        return False

    def is_faq_step_download_displayed(self) -> bool:
        """Memeriksa langkah panduan 'Unduh dan Daftar' (boleh menggeser layar)."""
        return self.is_displayed_after_scroll(self.FAQ_STEP_DOWNLOAD)

    def is_faq_step_open_home_displayed(self) -> bool:
        """Memeriksa langkah panduan 'Buka Halaman Utama' (boleh menggeser layar)."""
        return self.is_displayed_after_scroll(self.FAQ_STEP_OPEN_HOME)

    def is_faq_step_activate_displayed(self) -> bool:
        """Memeriksa langkah panduan 'Cara mengaktifkan aplikasi' (boleh menggeser layar)."""
        return self.is_displayed_after_scroll(self.FAQ_STEP_ACTIVATE)

    def is_tips_description_displayed(self) -> bool:
        """Memeriksa teks 'Pastikan koneksi internet stabil, Applikasi selalu aktif di latar belakang.'"""
        return self.is_displayed_after_scroll(self.TEXT_TIPS_DESCRIPTION)

    def is_app_version_number_displayed(self) -> bool:
        """Memeriksa ada label berisi nomor versi berformat angka.angka.angka (mis. 1.9.29) di layar."""
        source = self.driver.page_source
        return re.search(r'(?:content-desc|text)="[^"]*\bv?\d+\.\d+\.\d+', source) is not None

    def is_feedback_form_displayed(self) -> bool:
        """Memeriksa form masukan terbuka: kolom input dan tombol Kirim sama-sama tampil."""
        return self.is_displayed(self.FIELD_FEEDBACK_TEXT, timeout=5) and self.is_displayed(self.BTN_SUBMIT_FEEDBACK, timeout=3)

    def click_submit_feedback(self):
        """Mengetuk tombol Kirim pada form masukan (tanpa mengisi teks)."""
        self.click(self.BTN_SUBMIT_FEEDBACK, label="Tombol Kirim Masukan")

    def is_critical_error_displayed(self) -> bool:
        """Memeriksa layar/pesan 'Maaf terjadi kesalahan' atau 'Kesalahan server'."""
        return self.is_displayed(self.TEXT_CRITICAL_ERROR, timeout=2)

    def is_database_error_exposed(self) -> bool:
        """Memeriksa apakah pesan error basis data (SQL / syntax error) bocor ke layar."""
        return self.is_displayed(self.TEXT_DATABASE_ERROR, timeout=2)

    def confirm_hapus_akun(self):
        """Mengetuk tombol 'Hapus Sekarang' pada dialog pengajuan hapus akun."""
        self.click(self.BTN_CONFIRM_HAPUS_AKUN, label="Tombol Hapus Sekarang")

    def is_delete_account_otp_screen_displayed(self) -> bool:
        """Memeriksa layar OTP hapus akun ('Masukkan Kode OTP' dan tombol 'Konfirmasi OTP')."""
        return self.is_displayed(self.TITLE_DELETE_ACCOUNT_OTP, timeout=6) and self.is_displayed(self.BTN_CONFIRM_DELETE_OTP, timeout=3)

    def is_resend_otp_countdown_displayed(self) -> bool:
        """Memeriksa hitung mundur 'Kirim ulang kode dalam ...'."""
        return self.is_displayed(self.TEXT_RESEND_OTP_COUNTDOWN, timeout=3)

    def enter_delete_account_otp(self, kode: str):
        """Mengisi kode OTP pada layar verifikasi hapus akun."""
        self.type_text(self.FIELD_DELETE_ACCOUNT_OTP, kode, label="Field OTP Hapus Akun")

    def click_confirm_delete_otp(self):
        """Mengetuk tombol 'Konfirmasi OTP' hapus akun."""
        self.click(self.BTN_CONFIRM_DELETE_OTP, label="Tombol Konfirmasi OTP Hapus Akun")

    def is_delete_account_success_displayed(self) -> bool:
        """Memeriksa pesan 'Akun Anda telah berhasil dihapus.'"""
        return self.is_displayed(self.TEXT_DELETE_ACCOUNT_SUCCESS, timeout=3)
