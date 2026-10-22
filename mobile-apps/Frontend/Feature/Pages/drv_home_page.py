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
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("DrvHomePage")


class DrvHomePage(BasePage):
    """Page Object untuk Layar Utama (Beranda) Driver EvMoto."""

    # ==========================================================================
    # 1. HEADER & STATUS KERJA (ONLINE / OFFLINE)
    # ==========================================================================
    HEADER_BERANDA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Beranda') or contains(@text, 'Beranda')]"
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
        "//*[contains(@content-desc, 'Saldo Kamu') or contains(@text, 'Saldo Kamu')]"
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
    BOTTOM_NAV_BERANDA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Beranda') or contains(@text, 'Beranda')][last()]"
    )
    BOTTOM_NAV_AKTIVITAS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Aktivitas Saya') or contains(@text, 'Aktivitas Saya') or "
        "contains(@content-desc, 'Order Saya') or contains(@text, 'Order Saya')]"
    )
    BOTTOM_NAV_MENU = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Menu') or contains(@text, 'Menu')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    def is_home_screen_displayed(self) -> bool:
        """Memeriksa apakah layar Beranda Driver tampil."""
        return self.is_displayed(self.HEADER_BERANDA, timeout=6) or self.is_displayed(self.CARD_SALDO_KAMU, timeout=4)

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

    def navigate_to_menu(self):
        """Navigasi ke halaman Menu melalui Bottom Navigation Bar."""
        logger.info("Navigasi ke menu melalui Bottom Bar")
        self.click(self.BOTTOM_NAV_MENU, label="Tab Bottom Nav Menu")
        time.sleep(1)

    def navigate_to_activity(self):
        """Navigasi ke halaman Aktivitas Saya melalui Bottom Navigation Bar."""
        logger.info("Navigasi ke Aktivitas Saya melalui Bottom Bar")
        self.click(self.BOTTOM_NAV_AKTIVITAS, label="Tab Bottom Nav Aktivitas Saya")
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

