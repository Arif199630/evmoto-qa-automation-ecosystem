"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - MY ACTIVITY & GUARANTEE INCOME PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Layar Aktivitas Saya, Tab Guarantee Income (GI), Perhitungan Akumulasi,
          Net Payment of Guarantee, Deductions, Timer Batas Waktu Wilayah GI,
          Geofencing Alerts, Riwayat Pendapatan, dan Riwayat Referral Income.
Wording : Bersumber 100% dari strings resmi APK driver_strings_id.json
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("DrvActivityPage")


class DrvActivityPage(BasePage):
    """Page Object untuk Layar Aktivitas Saya dan Dashboard Guarantee Income (GI)."""

    # ==========================================================================
    # 1. HEADER & TAB NAVIGASI AKTIVITAS
    # ==========================================================================
    HEADER_AKTIVITAS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Aktivitas Saya') or contains(@text, 'Aktivitas Saya')]"
    )
    TAB_PESANAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesanan') or contains(@text, 'Pesanan')]"
    )
    TAB_GUARANTEE_INCOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Guarantee Income') or contains(@text, 'Guarantee Income')]"
    )
    TAB_PENDAPATAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Revenue Summary') or contains(@text, 'Revenue Summary') or "
        "contains(@content-desc, 'Riwayat Pendapatan') or contains(@text, 'Riwayat Pendapatan')]"
    )
    TAB_REFERRAL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Referral Income') or contains(@text, 'Referral Income')]"
    )

    # 1.1 TAB PESANAN & INVOICE / DETAIL PESANAN DRIVER
    LIST_PESANAN_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'order_list') or contains(@class, 'RecyclerView') or contains(@class, 'ListView')]"
    )
    CARD_ORDER_ITEM = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'ORD-') or contains(@content-desc, 'Pesanan') or contains(@text, 'ORD-') or "
        "contains(@content-desc, 'Rp') or contains(@text, 'Rp')])[1]"
    )
    HEADER_ORDER_DETAIL_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Detail Pesanan') or contains(@text, 'Detail Pesanan') or "
        "contains(@content-desc, 'Rincian Pesanan') or contains(@text, 'Rincian Pesanan') or "
        "contains(@content-desc, 'Rincian Transaksi') or contains(@text, 'Rincian Transaksi')]"
    )
    TEXT_DETAIL_ORDER_ID = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'No. Pesanan') or contains(@text, 'No. Pesanan') or "
        "contains(@content-desc, 'ID Order') or contains(@text, 'ID Order') or "
        "contains(@content-desc, 'ORD-') or contains(@text, 'ORD-')]"
    )
    TEXT_DETAIL_TRIP_DATE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Waktu Selesai') or contains(@text, 'Waktu Selesai') or "
        "contains(@content-desc, 'Tanggal') or contains(@text, 'Tanggal')]"
    )
    TEXT_DETAIL_PICKUP_POINT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Titik Jemput') or contains(@text, 'Titik Jemput') or "
        "contains(@content-desc, 'Lokasi Penjemputan') or contains(@text, 'Lokasi Penjemputan')]"
    )
    TEXT_DETAIL_DROPOFF_POINT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Titik Antar') or contains(@text, 'Titik Antar') or "
        "contains(@content-desc, 'Tujuan') or contains(@text, 'Tujuan')]"
    )
    CONTAINER_RINCIAN_TARIF_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rincian Tarif') or contains(@text, 'Rincian Tarif') or "
        "contains(@content-desc, 'Rincian Pembayaran') or contains(@text, 'Rincian Pembayaran')]"
    )
    TEXT_RINCIAN_ARGO_JARAK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Biaya jarak tempuh') or contains(@text, 'Biaya jarak tempuh') or "
        "contains(@content-desc, 'Argo') or contains(@text, 'Argo')]"
    )
    TEXT_RINCIAN_FAR_FEE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Biaya jarak jauh') or contains(@text, 'Biaya jarak jauh') or "
        "contains(@content-desc, 'Far Distance') or contains(@text, 'Far Distance')]"
    )
    TEXT_RINCIAN_WAITING_FEE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Biaya menunggu') or contains(@text, 'Biaya menunggu') or "
        "contains(@content-desc, 'Waktu tunggu') or contains(@text, 'Waktu tunggu')]"
    )
    TEXT_RINCIAN_PLATFORM_FEE_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Biaya Platform (10%)') or contains(@text, 'Biaya Platform (10%)') or "
        "contains(@content-desc, 'Potongan 10%') or contains(@text, 'Potongan 10%')]"
    )
    TEXT_RINCIAN_SUBSIDI_KUPON = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Subsidi Kupon') or contains(@text, 'Subsidi Kupon') or "
        "contains(@content-desc, 'Diskon Kupon') or contains(@text, 'Diskon Kupon')]"
    )
    TEXT_TOTAL_DIBAYARKAN_PENUMPANG = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Yang dibayarkan penumpang') or contains(@text, 'Yang dibayarkan penumpang') or "
        "contains(@content-desc, 'Dibayarkan oleh penumpang') or contains(@text, 'Dibayarkan oleh penumpang')]"
    )
    TEXT_TOTAL_DITERIMA_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total yang diterima Driver') or contains(@text, 'Total yang diterima Driver') or "
        "contains(@content-desc, 'Yang didapatkan driver') or contains(@text, 'Yang didapatkan driver')]"
    )
    BADGE_METODE_PEMBAYARAN_DETAIL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cash') or contains(@text, 'Cash') or "
        "contains(@content-desc, 'Tunai') or contains(@text, 'Tunai') or "
        "contains(@content-desc, 'Pembayaran Online') or contains(@text, 'Pembayaran Online')]"
    )
    BADGE_STATUS_PESANAN_DETAIL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Selesai') or contains(@text, 'Selesai') or "
        "contains(@content-desc, 'Dibatalkan') or contains(@text, 'Dibatalkan')]"
    )
    BTN_KEMBALI_DETAIL_PESANAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kembali') or contains(@content-desc, 'Back') or "
        "contains(@content-desc, 'Navigate up') or contains(@class, 'ImageView')][1]"
    )
    EMPTY_STATE_PESANAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Ada Pesanan') or contains(@text, 'Belum Ada Pesanan') or "
        "contains(@content-desc, 'Tidak ada riwayat pesanan') or contains(@text, 'Tidak ada riwayat pesanan')]"
    )

    # ==========================================================================
    # 2. GUARANTEE INCOME (GI) METRICS & CARDS
    # ==========================================================================
    CARD_TOTAL_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'TOTAL GUARANTEE INCOME') or contains(@text, 'TOTAL GUARANTEE INCOME')]"
    )
    TEXT_GI_PER_HOUR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Guarantee Income/Hour') or contains(@text, 'Guarantee Income/Hour') or "
        "contains(@content-desc, 'Per jam') or contains(@text, 'Per jam')]"
    )
    CARD_AKUMULASI_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total Akumulasi Guarantee Income') or contains(@text, 'Total Akumulasi Guarantee Income')]"
    )
    CARD_NET_PAYMENT_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Net Payment of Guarantee') or contains(@text, 'Net Payment of Guarantee')]"
    )
    CARD_DEDUCTION_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Dipotong dari Guarantee Income') or contains(@text, 'Dipotong dari Guarantee Income')]"
    )
    TEXT_GI_PERIODE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Periode:') or contains(@text, 'Periode:')]"
    )

    # Timer & Batas Wilayah GI
    TIMER_REMAINING_TODAY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sisa waktu jaminan hari ini') or contains(@text, 'Sisa waktu jaminan hari ini')]"
    )
    TIMER_REMAINING_RETURN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sisa waktu kembali ke area') or contains(@text, 'Sisa waktu kembali ke area')]"
    )
    NOTICE_RETURN_BUFFER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batas waktu kembali dihitung') or contains(@text, 'Batas waktu kembali dihitung')]"
    )

    # Snackbar Geofencing GI
    SNACKBAR_ENTER_GI_AREA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'memasuki wilayah Gurantee Income') or contains(@text, 'memasuki wilayah Gurantee Income')]"
    )
    SNACKBAR_EXIT_GI_AREA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'keluar wilayah Gurantee Income') or contains(@text, 'keluar wilayah Gurantee Income')]"
    )
    SNACKBAR_BENEFIT_INVALID = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'tidak berlaku di luar area') or contains(@text, 'tidak berlaku di luar area')]"
    )

    # Riwayat GI
    SECTION_GI_HARI_INI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Guarantee Income Hari Ini') or contains(@text, 'Guarantee Income Hari Ini')]"
    )
    BTN_LIHAT_DETAIL_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lihat Detail') or contains(@text, 'Lihat Detail')]"
    )
    BADGE_STATUS_PAID = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sudah Dibayarkan') or contains(@text, 'Sudah Dibayarkan')]"
    )
    BADGE_STATUS_WAITING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Menunggu Konfirmasi') or contains(@text, 'Menunggu Konfirmasi')]"
    )
    EMPTY_STATE_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Tersedia Gurantee Income') or contains(@text, 'Belum Tersedia Gurantee Income') or "
        "contains(@content-desc, 'Tidak Ada Guarantee Income') or contains(@text, 'Tidak Ada Guarantee Income')]"
    )

    # ==========================================================================
    # 3. REVENUE SUMMARY & RIWAYAT PENDAPATAN
    # ==========================================================================
    HEADER_REVENUE_SUMMARY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Revenue Summary') or contains(@text, 'Revenue Summary') or "
        "contains(@content-desc, 'Riwayat Pendapatan') or contains(@text, 'Riwayat Pendapatan')]"
    )
    TEXT_DRIVER_EARNINGS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Yang didapatkan driver') or contains(@text, 'Yang didapatkan driver') or "
        "contains(@content-desc, 'Pendapatan driver') or contains(@text, 'Pendapatan driver')]"
    )
    TEXT_PLATFORM_FEE_NOTE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'total biaya jarak tempuh') or contains(@text, 'total biaya jarak tempuh') or "
        "contains(@content-desc, '10%') or contains(@text, '10%')]"
    )
    TEXT_PROMO_FEE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Biaya promo') or contains(@text, 'Biaya promo')]"
    )
    TEXT_BALANCE_BEFORE_AFTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo sebelum') or contains(@text, 'Saldo sebelum') or "
        "contains(@content-desc, 'Saldo sesudah') or contains(@text, 'Saldo sesudah')]"
    )
    EMPTY_STATE_REVENUE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Ada Riwayat') or contains(@text, 'Belum Ada Riwayat') or "
        "contains(@content-desc, 'Tidak ada riwayat') or contains(@text, 'Tidak ada riwayat')]"
    )

    # ==========================================================================
    # 4. REFERRAL INCOME
    # ==========================================================================
    HEADER_REFERRAL_INCOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Riwayat Referral Income') or contains(@text, 'Riwayat Referral Income')]"
    )
    TEXT_REFERRAL_PER_REGISTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Per Register') or contains(@text, 'Per Register')]"
    )
    TEXT_REFERRAL_TODAY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Referral Income Hari Ini') or contains(@text, 'Referral Income Hari Ini')]"
    )
    BTN_SHARE_REFERRAL_CODE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bagikan') or contains(@text, 'Bagikan') or "
        "contains(@content-desc, 'kode referral') or contains(@text, 'kode referral')]"
    )
    EMPTY_STATE_REFERRAL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Ada Riwayat Referral') or contains(@text, 'Belum Ada Riwayat Referral')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    def is_activity_screen_displayed(self) -> bool:
        """Memeriksa apakah layar Aktivitas Saya tampil."""
        return self.is_displayed(self.HEADER_AKTIVITAS, timeout=5) or self.is_displayed(self.CARD_TOTAL_GI, timeout=4)

    def switch_to_gi_tab(self):
        """Berpindah ke tab Guarantee Income."""
        logger.info("Berpindah ke Tab Guarantee Income")
        self.click(self.TAB_GUARANTEE_INCOME, label="Tab Guarantee Income")
        time.sleep(1)

    def is_gi_dashboard_displayed(self) -> bool:
        """Memeriksa apakah metrik dan kartu Guarantee Income tampil."""
        c1 = self.is_displayed(self.CARD_TOTAL_GI, timeout=4)
        c2 = self.is_displayed(self.TEXT_GI_PER_HOUR, timeout=3)
        c3 = self.is_displayed(self.CARD_NET_PAYMENT_GI, timeout=3)
        return c1 or c2 or c3

    def is_gi_timer_displayed(self) -> bool:
        """Memeriksa apakah indikator sisa waktu jaminan / sisa waktu kembali tampil."""
        return self.is_displayed(self.TIMER_REMAINING_TODAY, timeout=3) or self.is_displayed(self.TIMER_REMAINING_RETURN, timeout=3)

    def is_gi_geofence_snackbar_displayed(self) -> bool:
        """Memeriksa apakah snackbar notifikasi masuk/keluar wilayah GI tampil."""
        return (
            self.is_displayed(self.SNACKBAR_ENTER_GI_AREA, timeout=2) or
            self.is_displayed(self.SNACKBAR_EXIT_GI_AREA, timeout=2) or
            self.is_displayed(self.SNACKBAR_BENEFIT_INVALID, timeout=2)
        )

    def click_lihat_detail_gi(self):
        """Mengetuk tombol Lihat Detail pada riwayat GI."""
        self.click(self.BTN_LIHAT_DETAIL_GI, label="Tombol Lihat Detail GI")

    def switch_to_revenue_tab(self):
        """Berpindah ke tab Riwayat Pendapatan (Revenue Summary)."""
        logger.info("Berpindah ke Tab Revenue Summary")
        self.click(self.TAB_PENDAPATAN, label="Tab Revenue Summary")
        time.sleep(1)

    def is_revenue_summary_displayed(self) -> bool:
        """Memeriksa apakah kartu ringkasan pendapatan tampil."""
        return self.is_displayed(self.HEADER_REVENUE_SUMMARY, timeout=4) or self.is_displayed(self.TEXT_DRIVER_EARNINGS, timeout=3)

    def switch_to_referral_tab(self):
        """Berpindah ke tab Riwayat Referral Income."""
        logger.info("Berpindah ke Tab Referral Income")
        self.click(self.TAB_REFERRAL, label="Tab Referral Income")
        time.sleep(1)

    def is_referral_income_displayed(self) -> bool:
        """Memeriksa apakah tampilan referral income tampil."""
        return (
            self.is_displayed(self.HEADER_REFERRAL_INCOME, timeout=4) or
            self.is_displayed(self.TEXT_REFERRAL_PER_REGISTER, timeout=3) or
            self.is_displayed(self.EMPTY_STATE_REFERRAL, timeout=2)
        )

    # ==========================================================================
    # METHODS TAB PESANAN & INVOICE / DETAIL PESANAN DRIVER
    # ==========================================================================
    def switch_to_pesanan_tab(self):
        """Berpindah ke tab Pesanan (Riwayat Order Driver)."""
        logger.info("Berpindah ke Tab Pesanan Driver")
        self.click(self.TAB_PESANAN, label="Tab Pesanan Driver")
        time.sleep(1)

    def is_pesanan_tab_displayed(self) -> bool:
        """Memeriksa apakah tab Pesanan aktif."""
        return self.is_displayed(self.CARD_ORDER_ITEM, timeout=3) or self.is_displayed(self.EMPTY_STATE_PESANAN, timeout=3)

    def click_order_item_to_view_invoice(self):
        """Mengetuk kartu riwayat pesanan untuk membuka Invoice / Detail Pesanan Driver."""
        logger.info("Membuka detail pesanan / invoice driver...")
        self.click(self.CARD_ORDER_ITEM, label="Kartu Riwayat Pesanan Driver")
        time.sleep(1)

    def is_driver_order_invoice_displayed(self) -> bool:
        """Memeriksa apakah layar Detail Pesanan (Invoice Driver) tampil."""
        c1 = self.is_displayed(self.HEADER_ORDER_DETAIL_DRIVER, timeout=4)
        c2 = self.is_displayed(self.CONTAINER_RINCIAN_TARIF_DRIVER, timeout=3)
        c3 = self.is_displayed(self.TEXT_TOTAL_DITERIMA_DRIVER, timeout=3)
        return c1 or c2 or c3

    def close_order_detail_invoice(self):
        """Kembali dari layar Detail Pesanan / Invoice Driver ke Tab Pesanan."""
        self.click(self.BTN_KEMBALI_DETAIL_PESANAN, label="Tombol Kembali dari Detail Pesanan")
        time.sleep(1)
