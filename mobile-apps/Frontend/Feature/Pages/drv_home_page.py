"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - HOME (BERANDA) PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Layar Utama / Beranda Mitra Driver, Status Online / Offline,
          Indikator Working Area, Kartu Saldo & Pendapatan, Metrik Performa,
          Pop-up Guarantee Income (GI), Refresh, dan Navigasi Menu.
Wording : Bersumber 100% dari strings resmi APK driver_lang_id.json
================================================================================
"""
import re
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger
from config.config import Config


logger = get_logger("DrvHomePage")


class DrvHomePage(BasePage):
    """Page Object untuk Layar Utama (Beranda) Driver EvMoto."""

    # ==========================================================================
    # 1. HEADER & STATUS KERJA (ONLINE / OFFLINE)
    # ==========================================================================
    # Penanda Beranda Driver (peta layar CI 11 Nov 2026): kartu statistik 'Pesanan Hari Ini'
    HEADER_BERANDA = (
        AppiumBy.XPATH,
        "//*[@content-desc='Pesanan Hari Ini' or @text='Pesanan Hari Ini']"
    )
    # Pop-up yang muncul saat Beranda dibuka dan menutupi layar
    POPUP_JAM_OPERASIONAL = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Pemberitahuan Jam Operasional')]"
    )
    BTN_LANJUTKAN_POPUP = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']"
    )
    SWITCH_ONLINE_OFFLINE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Online') or contains(@text, 'Online') or "
        "contains(@content-desc, 'Offline') or contains(@text, 'Offline') or "
        "contains(@class, 'Switch')]"
    )
    TEXT_STATUS_ONLINE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Online') or contains(@text, 'Online')]"
    )
    TEXT_STATUS_OFFLINE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Offline') or contains(@text, 'Offline')]"
    )

    # Indikator Batas Wilayah Kerja (Working Area Boundary)
    BANNER_OUTSIDE_WORKING_AREA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Working Area') or contains(@text, 'Working Area') or "
        "contains(@content-desc, 'diluar dari Working Area') or contains(@text, 'diluar dari Working Area')]"
    )
    SNACKBAR_AUTO_OFFLINE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Status Anda akan offline') or contains(@text, 'Status Anda akan offline')]"
    )

    # ==========================================================================
    # 2. FINANSIAL & SALDO DRIVER
    # ==========================================================================
    CARD_SALDO_KAMU = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Saldo Kamu') or starts-with(@text, 'Saldo Kamu')]"
    )
    VALUE_SALDO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    CARD_TOTAL_PENDAPATAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total Pendapatan') or contains(@text, 'Total Pendapatan')]"
    )

    # ==========================================================================
    # 3. METRIK PERFORMA & PESANAN (PRE-ORDER MONITORING)
    # ==========================================================================
    CARD_PESANAN_HARI_INI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesanan Hari Ini') or contains(@text, 'Pesanan Hari Ini')]"
    )
    CARD_PESANAN_BULAN_INI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesanan Bulan Ini') or contains(@text, 'Pesanan Bulan Ini')]"
    )
    CARD_RATING_SAYA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rating Saya') or contains(@text, 'Rating Saya')]"
    )

    # Overlay di Depan Layar
    BADGE_OVERLAY_ACTIVE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Order Dihalaman Depan Aktif') or contains(@text, 'Order Dihalaman Depan Aktif')]"
    )

    # Tombol Muat Ulang / Refresh Beranda
    BTN_REFRESH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Muat Ulang') or contains(@text, 'Muat Ulang') or contains(@class, 'RefreshIndicator')]"
    )

    # ==========================================================================
    # 4. TAB & SEKTOR PESANAN PRE-ORDER
    # ==========================================================================
    TAB_PESANAN_REGULER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesanan Reguler') or contains(@text, 'Pesanan Reguler')]"
    )
    TAB_PESANAN_TERJADWAL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesanan Terjadwal') or contains(@text, 'Pesanan Terjadwal')]"
    )
    LINK_LIHAT_AKTIVITAS_SAYA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lihat Aktivitas Saya') or contains(@text, 'Lihat Aktivitas Saya')]"
    )

    # ==========================================================================
    # 5. DIALOG / POPUP GUARANTEE INCOME (GI)
    # ==========================================================================
    DIALOG_GUARANTEE_INCOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Area Guarantee Income') or contains(@text, 'Area Guarantee Income') or "
        "contains(@content-desc, 'Jaminan Pendapatan') or contains(@text, 'Jaminan Pendapatan')]"
    )
    TEXT_GI_ONLINE_HOURS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Online di Jam Operasional') or contains(@text, 'Online di Jam Operasional')]"
    )
    TEXT_GI_NO_CANCEL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tidak Cancel/Reject Order') or contains(@text, 'Tidak Cancel/Reject Order')]"
    )
    BTN_GI_ARAHKAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Arahkan') or contains(@text, 'Arahkan')]"
    )
    BTN_GI_LIHAT_DETAIL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lihat Detail') or contains(@text, 'Lihat Detail')]"
    )
    BTN_CLOSE_DIALOG_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tutup') or contains(@text, 'Tutup') or contains(@class, 'Close')]"
    )

    # ==========================================================================
    # 5B. APP LIFECYCLE & DIALOG SISTEM (UPDATE & JAM OPERASIONAL)
    # ==========================================================================
    BTN_TOGGLE_HIDE_SALDO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'eye') or contains(@class, 'Visibility') or contains(@class, 'IconButton')]"
    )
    DIALOG_UPDATE_APP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Update Sekarang') or contains(@text, 'Update Sekarang') or "
        "contains(@content-desc, 'Versi Terbaru Telah Tersedia') or contains(@text, 'Versi Terbaru Telah Tersedia')]"
    )
    BTN_UPDATE_APP_NOW = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Perbarui sekarang') or contains(@text, 'Perbarui sekarang') or "
        "contains(@content-desc, 'Update Sekarang') or contains(@text, 'Update Sekarang')]"
    )
    DIALOG_OPERATING_HOURS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pemberitahuan Jam Operasional') or contains(@text, 'Pemberitahuan Jam Operasional')]"
    )
    BTN_NETWORK_SETTINGS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pengaturan Jaringan') or contains(@text, 'Pengaturan Jaringan')]"
    )

    # ==========================================================================
    # 6. BOTTOM NAVIGATION BAR
    # ==========================================================================
    # Navigasi bawah Driver hanya: Beranda | Offline/Online | Menu. 'Aktivitas Saya' adalah kartu di Beranda.
    BOTTOM_NAV_BERANDA = (
        AppiumBy.XPATH,
        "//*[@content-desc='Beranda' or @text='Beranda']"
    )
    BOTTOM_NAV_AKTIVITAS = (
        AppiumBy.XPATH,
        "//*[@content-desc='Aktivitas Saya' or @text='Aktivitas Saya']"
    )
    BOTTOM_NAV_MENU = (
        AppiumBy.XPATH,
        "//*[@content-desc='Menu' or @text='Menu']"
    )
    # Penanda layar tujuan navigasi: header 'Total Orderan' hanya ada di Menu (04_menu s.d. 07_menu_gulir_3),
    # tab 'Guarantee Income / Tab 1 dari 3' hanya ada di Aktivitas Saya (09_aktivitas_saya). Peta layar CI 12 Nov 2026.
    PENANDA_MENU = (
        AppiumBy.XPATH,
        "//*[@content-desc='Total Orderan' or @text='Total Orderan']"
    )
    PENANDA_AKTIVITAS = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Guarantee Income') and contains(@content-desc, 'Tab 1')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    def is_home_screen_displayed(self) -> bool:
        """Memeriksa apakah layar Beranda Driver tampil."""
        self.dismiss_operational_popup()
        return self.is_displayed(self.HEADER_BERANDA, timeout=6) or self.is_displayed(self.CARD_SALDO_KAMU, timeout=4)

    def dismiss_operational_popup(self):
        """Tutup pop-up 'Pemberitahuan Jam Operasional' (tombol 'Lanjutkan') bila sedang tampil."""
        if self.is_displayed(self.POPUP_JAM_OPERASIONAL, timeout=2):
            buttons = self.driver.find_elements(*self.BTN_LANJUTKAN_POPUP)
            if buttons:
                buttons[0].click()

    def open_wallet(self):
        """Buka layar eWallet lewat kartu 'Saldo Kamu' di Beranda."""
        self.dismiss_operational_popup()
        self.click(self.CARD_SALDO_KAMU, label="Kartu Saldo Kamu")

    def toggle_online_offline_status(self):
        """Mengetuk tombol sakelar status kerja Online / Offline."""
        logger.info("Mengetuk toggle status Online/Offline")
        self.click(self.SWITCH_ONLINE_OFFLINE, label="Toggle Status Online / Offline")
        time.sleep(1)

    def is_online_status_active(self) -> bool:
        """Memeriksa apakah driver berstatus Online."""
        return self.is_displayed(self.TEXT_STATUS_ONLINE, timeout=3)

    def is_offline_status_active(self) -> bool:
        """Memeriksa apakah driver berstatus Offline."""
        return self.is_displayed(self.TEXT_STATUS_OFFLINE, timeout=3)

    def is_saldo_card_displayed(self) -> bool:
        """Memeriksa apakah kartu 'Saldo Kamu' ditampilkan."""
        return self.is_displayed(self.CARD_SALDO_KAMU, timeout=4)

    def is_total_earnings_displayed(self) -> bool:
        """Memeriksa apakah kartu 'Total Pendapatan' ditampilkan."""
        return self.is_displayed(self.CARD_TOTAL_PENDAPATAN, timeout=4)

    def is_performance_metrics_displayed(self) -> bool:
        """Memeriksa metrik performa (Pesanan Hari Ini, Pesanan Bulan Ini, Rating Saya)."""
        c1 = self.is_displayed(self.CARD_PESANAN_HARI_INI, timeout=3)
        c2 = self.is_displayed(self.CARD_PESANAN_BULAN_INI, timeout=2)
        c3 = self.is_displayed(self.CARD_RATING_SAYA, timeout=2)
        return c1 or c2 or c3

    def is_outside_working_area_warning_displayed(self) -> bool:
        """Memeriksa apakah banner/snackbar peringatan di luar Working Area tampil."""
        return self.is_displayed(self.BANNER_OUTSIDE_WORKING_AREA, timeout=3) or self.is_displayed(self.SNACKBAR_AUTO_OFFLINE, timeout=2)

    def is_guarantee_income_dialog_displayed(self) -> bool:
        """Memeriksa apakah modal info Area Guarantee Income (GI) tampil."""
        return self.is_displayed(self.DIALOG_GUARANTEE_INCOME, timeout=4)

    def click_gi_arahkan(self):
        """Mengetuk tombol 'Arahkan' pada modal Guarantee Income."""
        self.click(self.BTN_GI_ARAHKAN, label="Tombol GI Arahkan")

    def click_gi_lihat_detail(self):
        """Mengetuk tombol 'Lihat Detail' pada modal Guarantee Income."""
        self.click(self.BTN_GI_LIHAT_DETAIL, label="Tombol GI Lihat Detail")

    def click_refresh_beranda(self):
        """Mengetuk tombol atau pemicu Muat Ulang Beranda."""
        self.click(self.BTN_REFRESH, label="Tombol Muat Ulang Beranda")

    def switch_to_regular_orders_tab(self):
        """Berpindah ke tab Pesanan Reguler."""
        self.click(self.TAB_PESANAN_REGULER, label="Tab Pesanan Reguler")

    def switch_to_scheduled_orders_tab(self):
        """Berpindah ke tab Pesanan Terjadwal."""
        self.click(self.TAB_PESANAN_TERJADWAL, label="Tab Pesanan Terjadwal")

    def _ketuk_dan_tunggu(self, tombol, penanda, label: str, percobaan: int = 2):
        """Ketuk tombol navigasi lalu tunggu layar tujuan (penanda) tampil; ulang sekali bila ketukan tertelan.

        Di CI ketukan pertama setelah login kadang tidak memindahkan layar (run 43134989584, MENU_PT_18:
        tombol Menu diketuk tetapi layar tetap Beranda). Bila layar tujuan tetap tidak tampil, langkah
        berikutnya di test yang gagal, jadi tidak ada kegagalan yang disembunyikan.
        """
        for _ in range(percobaan):
            self.dismiss_operational_popup()
            self.click(tombol, label=label)
            if self.is_displayed(penanda, timeout=6):
                return

    def navigate_to_menu(self):
        """Navigasi ke halaman Menu melalui Bottom Navigation Bar."""
        logger.info("Navigasi ke menu melalui Bottom Bar")
        self._ketuk_dan_tunggu(self.BOTTOM_NAV_MENU, self.PENANDA_MENU, "Tab Bottom Nav Menu")
        time.sleep(1)

    def navigate_to_activity(self):
        """Navigasi ke halaman Aktivitas Saya lewat kartu 'Aktivitas Saya' di Beranda."""
        logger.info("Navigasi ke Aktivitas Saya melalui kartu di Beranda")
        self._ketuk_dan_tunggu(self.BOTTOM_NAV_AKTIVITAS, self.PENANDA_AKTIVITAS, "Kartu Aktivitas Saya")
        time.sleep(1)

    def toggle_hide_balance(self):
        """Mengetuk ikon mata untuk sembunyikan/tampilkan nominal saldo."""
        logger.info("Mengetuk ikon mata untuk toggle hide/show saldo")
        self.click(self.BTN_TOGGLE_HIDE_SALDO, label="Tombol Toggle Sembunyikan Saldo")

    def is_update_dialog_displayed(self) -> bool:
        """Memeriksa apakah dialog pembaruan aplikasi (update) tampil."""
        return self.is_displayed(self.DIALOG_UPDATE_APP, timeout=3)

    def is_operating_hours_dialog_displayed(self) -> bool:
        """Memeriksa apakah modal pemberitahuan jam operasional tampil."""
        return self.is_displayed(self.DIALOG_OPERATING_HOURS, timeout=3)

    def click_network_settings(self):
        """Mengetuk tombol Pengaturan Jaringan."""
        self.click(self.BTN_NETWORK_SETTINGS, label="Tombol Pengaturan Jaringan")

    # ==========================================================================
    # 7. LOCATOR TAMBAHAN UNTUK VERIFIKASI HASIL (TEKS DARI driver_strings_id.json)
    # ==========================================================================
    # home_soft_update_title / home_update_now / update_later
    TEXT_SOFT_UPDATE_TITLE = (
        AppiumBy.XPATH,
        "//*[@content-desc='Versi Terbaru Telah Tersedia' or @text='Versi Terbaru Telah Tersedia']"
    )
    BTN_PERBARUI_SEKARANG = (
        AppiumBy.XPATH,
        "//*[@content-desc='Perbarui sekarang' or @text='Perbarui sekarang']"
    )
    BTN_PERBARUI_NANTI = (
        AppiumBy.XPATH,
        "//*[@content-desc='Perbarui nanti' or @text='Perbarui nanti']"
    )
    # home_force_update_title
    TEXT_FORCE_UPDATE_TITLE = (
        AppiumBy.XPATH,
        "//*[@content-desc='Update Sekarang' or @text='Update Sekarang']"
    )
    # home_operating_hours_description
    TEXT_OPERATING_HOURS_DESCRIPTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'layanan mengikuti jam operasional') or contains(@text, 'layanan mengikuti jam operasional')]"
    )
    # widgets_no_internet_title, snackbar_network_disconnected, dio_exception_connection_error, widgets_connection_error
    TEXT_NETWORK_ERROR = (
        AppiumBy.XPATH,
        "//*[@content-desc='Tidak Ada Koneksi Internet' or @text='Tidak Ada Koneksi Internet' or "
        "contains(@content-desc, 'Jaringan terputus, harap untuk periksa') or contains(@text, 'Jaringan terputus, harap untuk periksa') or "
        "contains(@content-desc, 'Tidak dapat terhubung ke server') or contains(@text, 'Tidak dapat terhubung ke server')]"
    )
    # critical_error_title (terlihat di dump layar emulator)
    TEXT_CRITICAL_ERROR = (
        AppiumBy.XPATH,
        "//*[@content-desc='Maaf terjadi kesalahan' or @text='Maaf terjadi kesalahan']"
    )
    # home_overlay_order_active (label persis)
    TEXT_OVERLAY_ORDER_ACTIVE = (
        AppiumBy.XPATH,
        "//*[@content-desc='Order Dihalaman Depan Aktif' or @text='Order Dihalaman Depan Aktif']"
    )

    def get_saldo_labels(self) -> list:
        """Mengambil semua label di layar yang memuat nominal 'Rp' atau karakter sensor (•, ●, *)."""
        labels = []
        for el in self.driver.find_elements(AppiumBy.XPATH, "//*[@content-desc!='' or @text!='']"):
            label = (el.get_attribute("content-desc") or el.get_attribute("text") or "").strip()
            if "Rp" in label or re.search(r"[•●*]{3,}", label):
                labels.append(label)
        return labels

    @staticmethod
    def has_masked_label(labels: list) -> bool:
        """True bila salah satu label berisi minimal tiga karakter sensor berturut-turut (mis. ••••••)."""
        return any(re.search(r"[•●*]{3,}", label) for label in labels)

    def is_soft_update_dialog_displayed(self) -> bool:
        """Memeriksa dialog 'Versi Terbaru Telah Tersedia'."""
        return self.is_displayed(self.TEXT_SOFT_UPDATE_TITLE, timeout=3)

    def is_perbarui_sekarang_displayed(self) -> bool:
        """Memeriksa tombol 'Perbarui sekarang'."""
        return self.is_displayed(self.BTN_PERBARUI_SEKARANG, timeout=3)

    def is_perbarui_nanti_displayed(self) -> bool:
        """Memeriksa tombol 'Perbarui nanti' (tombol tutup dialog update)."""
        return self.is_displayed(self.BTN_PERBARUI_NANTI, timeout=2)

    def is_force_update_dialog_displayed(self) -> bool:
        """Memeriksa dialog wajib 'Update Sekarang'."""
        return self.is_displayed(self.TEXT_FORCE_UPDATE_TITLE, timeout=3)

    def is_operating_hours_description_displayed(self) -> bool:
        """Memeriksa penjelasan 'Saat ini layanan mengikuti jam operasional yang berlaku...'."""
        return self.is_displayed(self.TEXT_OPERATING_HOURS_DESCRIPTION, timeout=3)

    def is_network_settings_button_displayed(self) -> bool:
        """Memeriksa tombol 'Pengaturan Jaringan' (muncul di widget tanpa koneksi)."""
        return self.is_displayed(self.BTN_NETWORK_SETTINGS, timeout=5)

    def is_network_error_displayed(self) -> bool:
        """Memeriksa pesan gangguan jaringan resmi aplikasi."""
        return self.is_displayed(self.TEXT_NETWORK_ERROR, timeout=6)

    def is_critical_error_displayed(self) -> bool:
        """Memeriksa layar 'Maaf terjadi kesalahan'."""
        return self.is_displayed(self.TEXT_CRITICAL_ERROR, timeout=2)

    def is_overlay_order_badge_displayed(self) -> bool:
        """Memeriksa badge 'Order Dihalaman Depan Aktif'."""
        return self.is_displayed(self.TEXT_OVERLAY_ORDER_ACTIVE, timeout=4)

    def get_current_package(self) -> str:
        """Nama package aplikasi yang sedang tampil di depan."""
        return self.driver.current_package or ""

    def is_driver_app_in_foreground(self) -> bool:
        """True bila aplikasi EvMoto Driver sedang tampil di depan."""
        return self.get_current_package() == Config.DRIVER_PACKAGE

    def return_to_driver_app(self):
        """Membawa aplikasi EvMoto Driver kembali ke depan."""
        self.driver.activate_app(Config.DRIVER_PACKAGE)
        time.sleep(1.5)

    def set_device_network(self, enabled: bool):
        """Menyalakan/mematikan Wi-Fi dan data seluler emulator lewat perintah Appium 'mobile: setConnectivity'."""
        self.driver.execute_script("mobile: setConnectivity", {"wifi": enabled, "data": enabled})
        time.sleep(2)

    def grant_overlay_permission(self):
        """Memberi izin tampil di atas aplikasi lain (SYSTEM_ALERT_WINDOW) lewat appops Appium."""
        self.driver.execute_script("mobile: changePermissions", {
            "permissions": ["SYSTEM_ALERT_WINDOW"],
            "appPackage": Config.DRIVER_PACKAGE,
            "action": "allow",
            "target": "appops",
        })

    def background_and_resume(self, seconds: int = 2):
        """Memindahkan aplikasi ke latar belakang lalu membukanya lagi (memicu cek ulang izin)."""
        self.driver.background_app(seconds)
        time.sleep(1.5)

    def pull_to_refresh(self):
        """Gestur tarik ke bawah (pull-to-refresh) dari area atas layar Beranda."""
        size = self.driver.get_window_size()
        x = int(size["width"] / 2)
        self.swipe(x, int(size["height"] * 0.3), x, int(size["height"] * 0.8), 600)
        time.sleep(2)

    def open_notification_shade(self):
        """Membuka panel notifikasi Android di atas aplikasi."""
        self.driver.open_notifications()
        time.sleep(1.5)

    def press_back(self):
        """Menekan tombol Back Android."""
        self.driver.back()
        time.sleep(1)
