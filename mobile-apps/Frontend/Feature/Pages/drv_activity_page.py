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
import re
import time
from typing import Optional
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from Pages.drv_home_page import DrvHomePage
from utils.logger import get_logger

logger = get_logger("DrvActivityPage")

DRIVER_PACKAGE = "com.evmoto.driver.app"
_POLA_RUPIAH = re.compile(r"([+\-−]?)\s*Rp\s?(\d[\d.]*(?:,\d+)?)", re.I)
_POLA_JAM = re.compile(r"\d{1,2}[:.]\d{2}")


def parse_rupiah(teks: str) -> Optional[float]:
    """Nominal Rupiah pertama di teks UI: 'Rp 10.200' -> 10200.0, '-Rp 1.020' -> -1020.0, tanpa 'Rp' -> None."""
    if not teks:
        return None
    m = _POLA_RUPIAH.search(teks)
    if not m:
        return None
    angka = float(m.group(2).rstrip(".").replace(".", "").replace(",", "."))
    return -angka if m.group(1) in ("-", "−") else angka


def label_elemen(el) -> str:
    """content-desc (Flutter) atau text (native) sebuah elemen."""
    return (el.get_attribute("content-desc") or el.get_attribute("text") or "").strip()


def baca_teks_sekitar(page: BasePage, locator) -> list:
    """Teks label, saudara berikutnya, dan induknya.

    Flutter kadang merender nilai di node terpisah dari labelnya, jadi nilai dicari di tiga tempat itu.
    Mengembalikan list kosong bila label tidak ditemukan.
    """
    try:
        el = page.find(locator, timeout=5)
    except Exception:
        return []
    hasil = [label_elemen(el)]
    for xpath_relatif in ("following-sibling::*[1]", ".."):
        try:
            hasil.append(label_elemen(el.find_element(AppiumBy.XPATH, xpath_relatif)))
        except Exception:
            pass
    return [t for t in hasil if t]


def baca_nominal_dekat_label(page: BasePage, locator) -> Optional[float]:
    """Nominal Rupiah milik sebuah label (di label itu sendiri, saudara berikutnya, atau induknya)."""
    for teks in baca_teks_sekitar(page, locator):
        nominal = parse_rupiah(teks)
        if nominal is not None:
            return nominal
    return None


class DrvActivityPage(BasePage):
    """Page Object untuk Layar Aktivitas Saya dan Dashboard Guarantee Income (GI)."""

    # ==========================================================================
    # 1. HEADER & TAB NAVIGASI AKTIVITAS
    # ==========================================================================
    # Layar Aktivitas Saya punya tab 'Guarantee Income / Tab 1 dari 3' (kartu 'Aktivitas Saya' di Beranda
    # memakai teks yang sama, jadi penandanya tab, bukan judul)
    HEADER_AKTIVITAS = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Guarantee Income') or starts-with(@content-desc, 'Coupon Income')]"
    )
    # Layar Aktivitas Saya tidak punya tab Pesanan. Riwayat order driver ada di layar terpisah 'Order Saya'
    # yang dibuka dari kartu 'Order Saya' di Beranda (peta layar CI 12 Nov 2026: 01_beranda -> 13_order_saya).
    # contains('Pesanan') lama hanya cocok dengan 'Pesanan Hari Ini' / 'Pesanan Berjalan' di Beranda.
    TAB_PESANAN = (
        AppiumBy.XPATH,
        "//*[@content-desc='Order Saya' or @text='Order Saya']"
    )
    # Tab pertama layar Order Saya: 'Semua\nTab 1 dari 3' (13_order_saya); penanda layar Order Saya
    # (label 'Order Saya' saja juga dipakai kartu di Beranda)
    TAB_ORDER_SAYA_SEMUA = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Semua') and contains(@content-desc, 'Tab 1')]"
    )
    # Tombol kembali di kiri atas tiap sub-layar (09_aktivitas_saya, 13_order_saya, 17_kirim_masukan)
    BTN_KEMBALI = (
        AppiumBy.XPATH,
        "//*[@content-desc='Kembali' or @text='Kembali']"
    )
    # Tab Flutter berlabel 'Guarantee Income\nTab 1 dari 3' (09_aktivitas_saya)
    TAB_GUARANTEE_INCOME = (
        AppiumBy.XPATH,
        "//*[(starts-with(@content-desc, 'Guarantee Income') and contains(@content-desc, 'Tab 1')) or "
        "@text='Guarantee Income']"
    )
    # Tab 'Riwayat Pendapatan / Revenue Summary' di aplikasi = tab 'Coupon Income\nTab 2 dari 3', berisi rincian
    # Jenis Pendapatan (Order Income, Cash Income, E-wallet, OVO, GoPay, Penalti). Key APK label Order Income juga
    # my_activity_coupon_order_income. Peta layar CI 12 Nov 2026: 10_tab_coupon_income.
    TAB_PENDAPATAN = (
        AppiumBy.XPATH,
        "//*[(starts-with(@content-desc, 'Coupon Income') and contains(@content-desc, 'Tab 2')) or "
        "contains(@content-desc, 'Revenue Summary') or contains(@text, 'Revenue Summary') or "
        "contains(@content-desc, 'Riwayat Pendapatan') or contains(@text, 'Riwayat Pendapatan')]"
    )
    # Label tab resmi APK: my_activity_tab_referral = 'Referral Program'. Flutter menambah akhiran
    # '\nTab 3 dari 3', jadi dicocokkan dengan starts-with (10_tab_coupon_income, 12_tab_ketiga).
    # 'Referral Income' dipertahankan dari locator lama.
    TAB_REFERRAL = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Referral Program') or @text='Referral Program' or "
        "contains(@content-desc, 'Referral Income') or contains(@text, 'Referral Income')]"
    )

    # 1.1 TAB PESANAN & INVOICE / DETAIL PESANAN DRIVER
    LIST_PESANAN_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'order_list') or contains(@class, 'RecyclerView') or contains(@class, 'ListView')]"
    )
    # Kartu riwayat di layar Order Saya berlabel 'Reguler\nSelesai\nLokasi Tujuan\n<alamat>' (13_order_saya).
    # contains('Pesanan') / contains('Rp') lama juga cocok dengan Beranda ('Pesanan Hari Ini', 'Saldo Kamu Rp...').
    CARD_ORDER_ITEM = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Lokasi Tujuan') or contains(@text, 'Lokasi Tujuan') or "
        "contains(@content-desc, 'ORD-') or contains(@text, 'ORD-')])[1]"
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
    # Sub-layar aplikasi Driver memakai ImageView content-desc 'Kembali' di kiri atas (09, 13, 17, 19 peta layar
    # CI 12 Nov 2026). contains(@class,'ImageView') lama cocok dengan ikon apa saja.
    BTN_KEMBALI_DETAIL_PESANAN = (
        AppiumBy.XPATH,
        "//*[@content-desc='Kembali' or @text='Kembali' or @content-desc='Navigate up']"
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
    # Isi tab Coupon Income: tabel 'Jenis Pendapatan | Pendapatan' (10_tab_coupon_income)
    HEADER_REVENUE_SUMMARY = (
        AppiumBy.XPATH,
        "//*[@content-desc='Jenis Pendapatan' or @text='Jenis Pendapatan' or "
        "contains(@content-desc, 'Revenue Summary') or contains(@text, 'Revenue Summary') or "
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
    # Isi tab 'Referral Program' (tab 3): 'Estimasi Total Pendapatan', kode DRV-..., 'Lihat QR Code',
    # 'Unduh QR Code' (peta layar CI 12 Nov 2026: 12_tab_ketiga). Label ini tidak ada di tab 1 dan 2.
    HEADER_REFERRAL_PROGRAM = (
        AppiumBy.XPATH,
        "//*[@content-desc='Estimasi Total Pendapatan' or @text='Estimasi Total Pendapatan' or "
        "@content-desc='Lihat QR Code' or @text='Lihat QR Code']"
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
        """Berpindah ke tab Referral Program (tab ke-3).

        Saat Aktivitas Saya baru dibuka, baris tab hanya menampilkan Guarantee Income dan Coupon Income;
        tab ke-3 baru ikut tampil setelah tab Coupon Income dipilih (peta layar CI 12 Nov 2026:
        09_aktivitas_saya -> 10_tab_coupon_income).
        """
        logger.info("Berpindah ke Tab Referral Program")
        if not self.is_displayed(self.TAB_REFERRAL, timeout=2):
            self.click(self.TAB_PENDAPATAN, label="Tab Coupon Income (memunculkan tab ke-3)")
            time.sleep(1)
        self.click(self.TAB_REFERRAL, label="Tab Referral Program")
        time.sleep(1)

    def is_referral_income_displayed(self) -> bool:
        """Memeriksa apakah tampilan referral (tab Referral Program) tampil."""
        return (
            self.is_displayed(self.HEADER_REFERRAL_PROGRAM, timeout=4) or
            self.is_displayed(self.HEADER_REFERRAL_INCOME, timeout=2) or
            self.is_displayed(self.TEXT_REFERRAL_PER_REGISTER, timeout=3) or
            self.is_displayed(self.EMPTY_STATE_REFERRAL, timeout=2)
        )

    # ==========================================================================
    # METHODS TAB PESANAN & INVOICE / DETAIL PESANAN DRIVER
    # ==========================================================================
    def switch_to_pesanan_tab(self):
        """Membuka riwayat order driver: layar 'Order Saya' dari Beranda (bukan tab di Aktivitas Saya).

        Dari layar Aktivitas Saya kembali dulu ke Beranda lewat tombol 'Kembali', lalu ketuk kartu 'Order Saya'
        (peta layar CI 12 Nov 2026: 09_aktivitas_saya, 01_beranda, 13_order_saya).
        """
        logger.info("Membuka layar Order Saya (riwayat order driver)")
        if self.is_displayed(self.TAB_ORDER_SAYA_SEMUA, timeout=2):
            return
        if self.is_displayed(self.HEADER_AKTIVITAS, timeout=2):
            self.click(self.BTN_KEMBALI, label="Tombol Kembali dari Aktivitas Saya")
            time.sleep(1)
        # Pop-up 'Pemberitahuan Jam Operasional' bisa menutupi Beranda (bukti CI: HOME_PT_16_FAILED.xml)
        DrvHomePage(self.driver).dismiss_operational_popup()
        self.click(self.TAB_PESANAN, label="Kartu Order Saya di Beranda")
        self.is_displayed(self.TAB_ORDER_SAYA_SEMUA, timeout=6)
        time.sleep(1)

    def is_pesanan_tab_displayed(self) -> bool:
        """Memeriksa layar Order Saya aktif dan memuat kartu riwayat atau empty state."""
        if not self.is_displayed(self.TAB_ORDER_SAYA_SEMUA, timeout=4):
            return False
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

    # ==========================================================================
    # 5. LOCATOR VERIFIKASI HASIL (teks dari driver_strings_id.json, nama key di komentar)
    # ==========================================================================
    # guarantee_income_history_per_hour = '*Per jam {{amount}}'
    TEXT_GI_RATE_PER_JAM = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, '*Per jam') or starts-with(@text, '*Per jam')]"
    )
    # my_activity_guarantee_not_available = 'Belum Tersedia Gurantee Income' (ejaan sesuai APK)
    EMPTY_STATE_GI_NOT_AVAILABLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Tersedia Gurantee Income') or contains(@text, 'Belum Tersedia Gurantee Income')]"
    )
    # guarantee_income_history_empty_today / guarantee_income_history_empty_title
    EMPTY_STATE_GI_TODAY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Anda belum memiliki pendapatan Guarantee Income pada hari ini') or "
        "contains(@text, 'Anda belum memiliki pendapatan Guarantee Income pada hari ini') or "
        "contains(@content-desc, 'Tidak Ada Guarantee Income') or contains(@text, 'Tidak Ada Guarantee Income')]"
    )
    # guarantee_income_area_out_title = 'Anda Berada Di Luar Area Jaminan Pendapatan.'
    TEXT_GI_OUTSIDE_AREA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Anda Berada Di Luar Area Jaminan Pendapatan') or "
        "contains(@text, 'Anda Berada Di Luar Area Jaminan Pendapatan')]"
    )
    # my_activity_total_guarantee_payment_zero = 'Total Guarantee Payment tetap Rp0'
    TEXT_GI_TOTAL_PAYMENT_ZERO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total Guarantee Payment tetap Rp0') or contains(@text, 'Total Guarantee Payment tetap Rp0')]"
    )
    # guarantee_income_history_title / guarantee_income_history_total_net_label (ejaan sesuai APK)
    HEADER_RIWAYAT_GI = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Riwayat Guarantee Income') or contains(@text, 'Riwayat Guarantee Income')]"
    )
    TEXT_GI_TOTAL_NET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total Net Gurantee') or contains(@text, 'Total Net Gurantee')]"
    )
    # my_activity_coupon_order_amount / my_activity_coupon_order_income
    TEXT_ORDER_AMOUNT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Order Amount') or contains(@text, 'Order Amount')]"
    )
    TEXT_ORDER_INCOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Order Income') or contains(@text, 'Order Income')]"
    )
    # ewallet_history_revenue_balance_before / _change / _after
    TEXT_SALDO_SEBELUM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo sebelum') or contains(@text, 'Saldo sebelum')]"
    )
    TEXT_PERUBAHAN_SALDO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Perubahan saldo') or contains(@text, 'Perubahan saldo')]"
    )
    TEXT_SALDO_SESUDAH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo sesudah') or contains(@text, 'Saldo sesudah')]"
    )
    # ewallet_activity_empty_title / no_activity_yet
    EMPTY_STATE_AKTIVITAS_APK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Tersedia Aktivitas') or contains(@text, 'Belum Tersedia Aktivitas') or "
        "contains(@content-desc, 'Belum Ada Aktivitas') or contains(@text, 'Belum Ada Aktivitas')]"
    )
    # my_activity_referral_total / my_activity_view_qr_code / my_activity_share_qr_code
    TEXT_TOTAL_REFERRAL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total Referral') or contains(@text, 'Total Referral')]"
    )
    BTN_LIHAT_QR_CODE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lihat QR Code') or contains(@text, 'Lihat QR Code')]"
    )
    BTN_BAGIKAN_QR_CODE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bagikan QR Code') or contains(@text, 'Bagikan QR Code')]"
    )
    # Share sheet Android (bukan bagian APK): resource-id chooser/resolver milik sistem
    ANDROID_SHARE_SHEET = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'android:id/chooser') or contains(@resource-id, 'android:id/resolver') or "
        "contains(@resource-id, 'com.android.intentresolver')]"
    )
    # widgets_no_internet_title, snackbar_network_disconnected, requirements_internet_disconnected,
    # dio_exception_connection_error, home_refresh, critical_error_button
    INDIKATOR_OFFLINE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tidak Ada Koneksi Internet') or contains(@text, 'Tidak Ada Koneksi Internet') or "
        "contains(@content-desc, 'Jaringan terputus') or contains(@text, 'Jaringan terputus') or "
        "contains(@content-desc, 'Koneksi tidak terhubung') or contains(@text, 'Koneksi tidak terhubung') or "
        "contains(@content-desc, 'Tidak dapat terhubung ke server') or contains(@text, 'Tidak dapat terhubung ke server') or "
        "@content-desc='Muat Ulang' or @text='Muat Ulang' or @content-desc='Coba Lagi' or @text='Coba Lagi']"
    )
    # Layar error sistem yang terlihat di dump nyata aplikasi Driver
    LAYAR_ERROR_SISTEM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Maaf terjadi kesalahan') or contains(@text, 'Maaf terjadi kesalahan') or "
        "contains(@content-desc, 'Kesalahan sistem, silakan coba lagi nanti') or "
        "contains(@text, 'Kesalahan sistem, silakan coba lagi nanti')]"
    )
    # Bukti ada riwayat pesanan: status persis order_state_completed / order_state_cancelled, atau nomor order
    # Di Order Saya status menyatu dengan label kartu: 'Reguler\nSelesai\nLokasi Tujuan\n...' (13_order_saya)
    BUKTI_RIWAYAT_PESANAN = (
        AppiumBy.XPATH,
        "//*[@content-desc='Selesai' or @text='Selesai' or @content-desc='Dibatalkan' or @text='Dibatalkan' or "
        "contains(@content-desc, 'Lokasi Tujuan') or "
        "contains(@content-desc, 'ORD-') or contains(@text, 'ORD-') or "
        "contains(@content-desc, 'Order #') or contains(@text, 'Order #')]"
    )

    # ==========================================================================
    # 6. METHOD VERIFIKASI HASIL
    # ==========================================================================
    def scroll_until_visible(self, locator, max_swipes: int = 4) -> bool:
        """Geser layar ke atas sampai elemen tampil (maks max_swipes kali). True bila akhirnya tampil."""
        if self.is_displayed(locator, timeout=3):
            return True
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        for _ in range(max_swipes):
            self.swipe(x, int(size["height"] * 0.75), x, int(size["height"] * 0.35), duration=500)
            time.sleep(0.8)
            if self.is_displayed(locator, timeout=2):
                return True
        return False

    def read_amount_near(self, locator) -> Optional[float]:
        """Nominal Rupiah milik label (digeser ke layar dulu). None bila label/nominal tidak terbaca."""
        if not self.scroll_until_visible(locator):
            return None
        return baca_nominal_dekat_label(self, locator)

    def read_texts_near(self, locator) -> list:
        """Teks label beserta saudara dan induknya (digeser ke layar dulu)."""
        if not self.scroll_until_visible(locator):
            return []
        return baca_teks_sekitar(self, locator)

    def read_time_near(self, locator) -> Optional[str]:
        """Teks waktu (format HH:MM / MM:SS) milik label timer, None bila tidak terbaca."""
        for teks in self.read_texts_near(locator):
            m = _POLA_JAM.search(teks)
            if m:
                return m.group(0)
        return None

    def is_gi_program_not_available(self) -> bool:
        """True bila tab GI menampilkan 'Belum Tersedia Gurantee Income' (akun tanpa program GI)."""
        return self.is_displayed(self.EMPTY_STATE_GI_NOT_AVAILABLE, timeout=3)

    def is_gi_outside_area(self) -> bool:
        """True bila aplikasi menyatakan driver berada di luar area jaminan pendapatan."""
        return self.is_displayed(self.TEXT_GI_OUTSIDE_AREA, timeout=3)

    def is_gi_today_empty(self) -> bool:
        """True bila riwayat GI hari ini kosong (teks empty state resmi APK)."""
        return self.scroll_until_visible(self.EMPTY_STATE_GI_TODAY, max_swipes=3)

    def has_gi_history_status_badge(self) -> bool:
        """True bila minimal satu riwayat GI menampilkan badge status (Sudah Dibayarkan / Menunggu Konfirmasi)."""
        return (self.scroll_until_visible(self.BADGE_STATUS_PAID, max_swipes=3) or
                self.is_displayed(self.BADGE_STATUS_WAITING, timeout=2))

    def is_gi_detail_displayed(self) -> bool:
        """True bila halaman/modal rincian GI terbuka (judul riwayat GI atau label 'Total Net Gurantee')."""
        return self.is_displayed(self.HEADER_RIWAYAT_GI, timeout=5) or self.is_displayed(self.TEXT_GI_TOTAL_NET, timeout=3)

    def is_revenue_empty_state_displayed(self) -> bool:
        """True bila layar pendapatan menampilkan empty state."""
        return self.is_displayed(self.EMPTY_STATE_REVENUE, timeout=3) or self.is_displayed(self.EMPTY_STATE_AKTIVITAS_APK, timeout=2)

    def has_revenue_ledger(self) -> bool:
        """True bila minimal satu baris mutasi pendapatan ('Saldo sebelum') tampil."""
        return self.scroll_until_visible(self.TEXT_SALDO_SEBELUM, max_swipes=2)

    def read_referral_total(self) -> Optional[int]:
        """Angka 'Total Referral' (jumlah downline). None bila tidak terbaca."""
        for teks in self.read_texts_near(self.TEXT_TOTAL_REFERRAL):
            sisa = teks.replace("Total Referral", "")
            m = re.search(r"\d+", sisa)
            if m:
                return int(m.group(0))
        return None

    def open_share_referral(self):
        """Mengetuk 'Bagikan QR Code' (membuka 'Lihat QR Code' dulu bila tombol bagikan belum tampil)."""
        if not self.is_displayed(self.BTN_BAGIKAN_QR_CODE, timeout=3) and self.scroll_until_visible(self.BTN_LIHAT_QR_CODE, max_swipes=2):
            self.click(self.BTN_LIHAT_QR_CODE, label="Tombol Lihat QR Code")
            time.sleep(1)
        self.scroll_until_visible(self.BTN_BAGIKAN_QR_CODE, max_swipes=2)
        self.click(self.BTN_BAGIKAN_QR_CODE, label="Tombol Bagikan QR Code")
        time.sleep(2)

    def is_android_share_sheet_displayed(self) -> bool:
        """True bila dialog berbagi bawaan Android (chooser) sedang tampil."""
        try:
            if self.driver.current_package in ("android", "com.android.intentresolver"):
                return True
        except Exception:
            pass
        return self.is_displayed(self.ANDROID_SHARE_SHEET, timeout=3)

    def close_share_sheet(self):
        """Menutup dialog berbagi Android dengan tombol Back."""
        self.driver.press_keycode(4)
        time.sleep(1)

    def is_app_in_foreground(self) -> bool:
        """True bila aplikasi Driver masih berjalan di foreground (tidak force close)."""
        try:
            return self.driver.query_app_state(DRIVER_PACKAGE) == 4
        except Exception:
            return False

    def is_error_screen_displayed(self) -> bool:
        """True bila layar error sistem ('Maaf terjadi kesalahan') tampil."""
        return self.is_displayed(self.LAYAR_ERROR_SISTEM, timeout=2)

    def set_network_enabled(self, enabled: bool) -> bool:
        """Menyalakan/mematikan Wi-Fi dan data seluler via UiAutomator2. False bila perangkat menolak."""
        try:
            self.driver.execute_script("mobile: setConnectivity", {"wifi": enabled, "data": enabled})
            time.sleep(2)
            return True
        except Exception as e:
            logger.warning(f"Kontrol jaringan tidak didukung perangkat: {e}")
            return False

    def is_offline_indicator_displayed(self) -> bool:
        """True bila aplikasi menampilkan pesan jaringan terputus atau tombol muat ulang / coba lagi."""
        return self.is_displayed(self.INDIKATOR_OFFLINE, timeout=8)

    def has_order_history(self) -> bool:
        """True bila tab Pesanan memuat minimal satu riwayat order (status atau nomor order)."""
        return self.is_displayed(self.BUKTI_RIWAYAT_PESANAN, timeout=3)

    def is_pesanan_empty_state_displayed(self) -> bool:
        """True bila tab Pesanan menampilkan empty state 'Belum Ada Pesanan'."""
        return self.is_displayed(self.EMPTY_STATE_PESANAN, timeout=3)
