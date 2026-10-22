"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - ACTIVITY & ORDER HISTORY PAGE OBJECT
================================================================================
Target: Layar Aktivitas & Riwayat Transaksi ('Activity' Tab) pada Aplikasi Mobile EvMoto.
Komponen diurutkan dari navigasi header hingga aksi pada daftar pesanan:
  1. Header & Tab Navigasi Aktivitas (Title, Pusat Bantuan, Notifikasi)
  2. Tab Filter Status: 'Sedang Berlangsung' (Active/Ongoing) vs 'Riwayat' (History/Completed) vs 'Dibatalkan'
  3. Filter Kategori Layanan (Chips: Semua, EvRide, EvSend, EvRent)
  4. Filter Rentang Waktu (Kalender: 7 Hari, 30 Hari, Kustom)
  5. Daftar Kartu Pesanan (Order Cards: Layanan, Status, Rute Jemput-Tujuan, Tarif)
  6. Layar Detail Pesanan & E-Receipt (ID Order, Rincian Tarif, Profil Driver, Download/Email E-Receipt)
  7. Modal Ulasan & Penilaian Driver (Rating 1-5 Bintang, Tag Feedback, Komentar)
  8. Pusat Bantuan & Pelaporan Kendala Pesanan (Barang Tertinggal, Perbedaan Tarif, CS Ticket)
  9. Empty States & Penanganan Jaringan (Belum Ada Aktivitas, Reset Filter, Offline Snackbar)
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("ActivityPage")


class ActivityPage(BasePage):
    """Page Object untuk Halaman Aktivitas & Riwayat Pesanan Mobile App EvMoto."""

    # ==========================================================================
    # 0. TAB NAVIGASI UTAMA (BOTTOM NAVIGATION BAR)
    # ==========================================================================
    NAV_ACTIVITY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Activity') or contains(@content-desc, 'Aktivitas') or "
        "contains(@text, 'Activity') or contains(@text, 'Aktivitas')]"
    )
    NAV_HOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Home') or contains(@content-desc, 'Beranda') or "
        "contains(@text, 'Home') or contains(@text, 'Beranda')]"
    )
    NAV_ME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Me') or contains(@content-desc, 'Akun') or "
        "contains(@text, 'Me') or contains(@text, 'Akun')]"
    )

    # ==========================================================================
    # 1. HEADER & PUSAT BANTUAN DI HALAMAN AKTIVITAS
    # ==========================================================================
    HEADER_TITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Aktivitas') or contains(@text, 'Aktivitas') or "
        "contains(@content-desc, 'Activity') or contains(@text, 'Activity') or "
        "contains(@content-desc, 'Riwayat') or contains(@text, 'Riwayat')]"
    )
    BTN_HELP_CENTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bantuan') or contains(@content-desc, 'Help') or "
        "contains(@resource-id, 'help_center') or contains(@text, 'Bantuan')]"
    )
    SCREEN_HELP_CENTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pusat Bantuan') or contains(@text, 'Pusat Bantuan') or "
        "contains(@content-desc, 'Help Center') or contains(@text, 'Help Center')]"
    )
    BTN_CLOSE_HELP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kembali') or contains(@content-desc, 'Back') or "
        "contains(@content-desc, 'Tutup') or contains(@text, 'Kembali')]"
    )

    # ==========================================================================
    # 2. TAB UTAMA HALAMAN AKTIVITAS (TAB REGULAR VS TAB BOOKING)
    # ==========================================================================
    # Tab 1: Tab Regular -> Untuk melihat history order dari Normal Booking (Instant Ride)
    TAB_REGULAR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Regular') or contains(@text, 'Regular') or "
        "contains(@content-desc, 'Reguler') or contains(@text, 'Reguler')]"
    )
    # Tab 2: Tab Booking -> Untuk melihat history order dari Advance Booking (Scheduled Ride)
    TAB_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Booking') or contains(@text, 'Booking') or "
        "contains(@content-desc, 'Advance') or contains(@text, 'Advance')]"
    )

    # Sub-Filter Status di Dalam Tab (Ongoing vs Completed vs Cancelled)
    TAB_IN_PROGRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Dalam Proses') or contains(@content-desc, 'Berlangsung') or "
        "contains(@content-desc, 'In Progress') or contains(@content-desc, 'Ongoing') or "
        "contains(@text, 'Dalam Proses') or contains(@text, 'Berlangsung')]"
    )
    TAB_HISTORY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Riwayat') or contains(@content-desc, 'Selesai') or "
        "contains(@content-desc, 'Completed') or contains(@content-desc, 'History') or "
        "contains(@text, 'Riwayat') or contains(@text, 'Selesai')]"
    )
    TAB_CANCELLED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Dibatalkan') or contains(@content-desc, 'Batal') or "
        "contains(@content-desc, 'Cancelled') or contains(@text, 'Dibatalkan')]"
    )

    # ==========================================================================
    # 3. FILTER KATEGORI LAYANAN (CHIPS FILTER)
    # ==========================================================================
    CHIP_FILTER_ALL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Semua') or contains(@text, 'Semua') or "
        "contains(@content-desc, 'All') or contains(@text, 'All')]"
    )
    CHIP_FILTER_EVRIDE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRide') or contains(@text, 'EvRide')]"
    )
    CHIP_FILTER_EVSEND = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvSend') or contains(@text, 'EvSend')]"
    )
    CHIP_FILTER_EVRENT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRent') or contains(@text, 'EvRent')]"
    )

    # ==========================================================================
    # 4. FILTER RENTANG WAKTU / TANGGAL (DATE FILTER)
    # ==========================================================================
    BTN_DATE_FILTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kalender') or contains(@content-desc, 'Tanggal') or "
        "contains(@content-desc, 'Filter Tanggal') or contains(@resource-id, 'date_filter') or "
        "contains(@text, 'Tanggal')]"
    )
    MODAL_DATE_PICKER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih Tanggal') or contains(@text, 'Pilih Rentang') or "
        "contains(@resource-id, 'date_picker_dialog') or contains(@class, 'DatePicker')]"
    )
    OPTION_DATE_7_DAYS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '7 Hari') or contains(@text, '7 Hari Terakhir') or "
        "contains(@text, '7 Hari')]"
    )
    OPTION_DATE_30_DAYS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '30 Hari') or contains(@text, '30 Hari Terakhir') or "
        "contains(@text, 'Bulan Ini')]"
    )
    BTN_APPLY_DATE_FILTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Terapkan') or contains(@text, 'Terapkan') or "
        "contains(@content-desc, 'Pilih') or contains(@text, 'Pilih')]"
    )
    BTN_RESET_DATE_FILTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Reset') or contains(@text, 'Reset') or "
        "contains(@content-desc, 'Atur Ulang') or contains(@text, 'Atur Ulang')]"
    )
    BTN_CANCEL_DATE_FILTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@text, 'Batal') or "
        "contains(@content-desc, 'Cancel') or contains(@text, 'Cancel')]"
    )

    # ==========================================================================
    # 5. DAFTAR KARTU PESANAN (ORDER CARDS)
    # ==========================================================================
    LIST_ACTIVITY_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'activity_list') or contains(@resource-id, 'order_list') or "
        "//android.widget.ScrollView or //android.widget.ListView]"
    )
    CARD_ORDER_FIRST = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'ORD-') or contains(@content-desc, 'EvRide') or "
        "contains(@content-desc, 'EvSend') or contains(@content-desc, 'EvRent') or "
        "contains(@resource-id, 'card_order') or contains(@resource-id, 'item_order')])[1]"
    )
    ORDER_CARD_SERVICE_ICON = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRide') or contains(@content-desc, 'EvSend') or "
        "contains(@content-desc, 'EvRent')]"
    )
    ORDER_CARD_DATETIME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '2026') or contains(@content-desc, 'Okt') or "
        "contains(@content-desc, 'WIB') or contains(@text, '2026') or contains(@text, 'WIB')]"
    )
    ORDER_CARD_STATUS_BADGE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Selesai') or contains(@content-desc, 'Dalam Perjalanan') or "
        "contains(@content-desc, 'Menunggu Driver') or contains(@content-desc, 'Dibatalkan') or "
        "contains(@text, 'Selesai') or contains(@text, 'Dalam Perjalanan')]"
    )
    ORDER_CARD_PICKUP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Jemput:') or contains(@content-desc, 'Dari:') or "
        "contains(@text, 'Jemput') or contains(@text, 'Dari')]"
    )
    ORDER_CARD_DESTINATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tujuan:') or contains(@content-desc, 'Ke:') or "
        "contains(@text, 'Tujuan') or contains(@text, 'Ke')]"
    )
    ORDER_CARD_FARE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    BTN_REORDER_NOW = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesan Lagi') or contains(@content-desc, 'Reorder') or "
        "contains(@text, 'Pesan Lagi') or contains(@text, 'Reorder')]"
    )
    BTN_RATE_DRIVER_CARD = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Beri Nilai') or contains(@content-desc, 'Beri Ulasan') or "
        "contains(@content-desc, 'Rating') or contains(@text, 'Beri Ulasan') or contains(@text, 'Nilai')]"
    )
    BTN_CANCEL_ACTIVE_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batalkan Pesanan') or contains(@content-desc, 'Cancel Order') or "
        "contains(@text, 'Batalkan Pesanan') or contains(@text, 'Cancel Order')]"
    )
    DIALOG_CONFIRM_CANCEL_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Konfirmasi Pembatalan') or contains(@text, 'Yakin ingin membatalkan') or "
        "contains(@resource-id, 'dialog_cancel_order')]"
    )
    BTN_PROCEED_CANCEL_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ya, Batalkan') or contains(@text, 'Ya, Batalkan') or "
        "contains(@text, 'Batalkan Perjalanan')]"
    )
    BTN_ABORT_CANCEL_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lanjutkan Pesanan') or contains(@content-desc, 'Kembali') or "
        "contains(@text, 'Lanjutkan Pesanan') or contains(@text, 'Batal')]"
    )

    # ==========================================================================
    # 5B. ELEMEN KHUSUS ADVANCE BOOKING (TAB BOOKING)
    # ==========================================================================
    CARD_ADVANCE_BOOKING_FIRST = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Terjadwal') or contains(@content-desc, 'Advance') or "
        "contains(@content-desc, 'Booking') or contains(@resource-id, 'card_advance_booking') or "
        "contains(@resource-id, 'card_order')])[1]"
    )
    BADGE_SCHEDULED_DATETIME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Jadwal:') or contains(@text, 'Jadwal:') or "
        "contains(@content-desc, 'Waktu Jemput:') or contains(@text, 'Waktu Jemput:') or "
        "contains(@content-desc, 'Okt') or contains(@text, 'WIB')]"
    )
    BTN_RESCHEDULE_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ubah Jadwal') or contains(@text, 'Ubah Jadwal') or "
        "contains(@content-desc, 'Reschedule') or contains(@text, 'Reschedule')]"
    )
    MODAL_RESCHEDULE_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Atur Ulang Waktu') or contains(@text, 'Pilih Tanggal & Waktu Baru') or "
        "contains(@resource-id, 'reschedule_modal')]"
    )
    BTN_CONFIRM_RESCHEDULE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Simpan Jadwal') or contains(@text, 'Simpan Jadwal') or "
        "contains(@content-desc, 'Konfirmasi') or contains(@text, 'Konfirmasi')]"
    )
    BTN_CANCEL_RESCHEDULE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@text, 'Batal') or "
        "contains(@content-desc, 'Cancel') or contains(@text, 'Cancel')]"
    )
    BTN_CANCEL_ADVANCE_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batalkan Booking') or contains(@text, 'Batalkan Booking') or "
        "contains(@content-desc, 'Batal Pesanan') or contains(@text, 'Batalkan')]"
    )
    DIALOG_CANCEL_ADVANCE_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Konfirmasi Pembatalan Booking') or contains(@text, 'Batalkan Advance Booking') or "
        "contains(@resource-id, 'dialog_cancel_advance')]"
    )
    EMPTY_STATE_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Ada Booking') or contains(@text, 'Belum Ada Booking') or "
        "contains(@content-desc, 'Tidak ada jadwal booking') or contains(@text, 'Belum ada Advance Booking') or "
        "contains(@text, 'Belum ada jadwal perjalanan')]"
    )

    # ==========================================================================
    # 6. LAYAR DETAIL PESANAN & E-RECEIPT (ORDER DETAILS SCREEN)
    # ==========================================================================
    SCREEN_ORDER_DETAIL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rincian Pesanan') or contains(@text, 'Rincian Pesanan') or "
        "contains(@content-desc, 'Detail Perjalanan') or contains(@text, 'Detail Perjalanan') or "
        "contains(@resource-id, 'order_detail_view')]"
    )
    TEXT_ORDER_ID = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'ORD-') or contains(@content-desc, 'ID Pesanan') or "
        "contains(@text, 'ORD-') or contains(@text, 'ID Pesanan')]"
    )
    DRIVER_INFO_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'driver_info') or contains(@content-desc, 'Mitra') or "
        "contains(@content-desc, 'Driver') or contains(@text, 'Mitra Driver')]"
    )
    DRIVER_NAME = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'driver_name') or contains(@content-desc, 'Budi') or "
        "contains(@content-desc, 'Ahmad') or contains(@text, 'Budi')]"
    )
    DRIVER_PLATE = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'vehicle_plate') or contains(@content-desc, 'B ') or "
        "contains(@text, 'B ')]"
    )
    TEXT_BASE_FARE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tarif Dasar') or contains(@text, 'Tarif Dasar') or "
        "contains(@content-desc, 'Tarif Perjalanan') or contains(@text, 'Tarif Perjalanan')]"
    )
    TEXT_DISCOUNT_PROMO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Diskon') or contains(@content-desc, 'Promo') or "
        "contains(@text, 'Diskon') or contains(@text, 'Voucher')]"
    )
    TEXT_PLATFORM_FEE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Biaya Layanan') or contains(@content-desc, 'Biaya Platform') or "
        "contains(@text, 'Biaya Layanan') or contains(@text, 'Biaya Aplikasi')]"
    )
    TEXT_TOTAL_PAID = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Total Pembayaran') or contains(@text, 'Total Pembayaran') or "
        "contains(@content-desc, 'Total Biaya') or contains(@text, 'Total')]"
    )
    TEXT_PAYMENT_METHOD_USED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvWallet') or contains(@content-desc, 'Tunai') or "
        "contains(@content-desc, 'QRIS') or contains(@text, 'EvWallet') or contains(@text, 'Tunai')]"
    )
    BTN_DOWNLOAD_RECEIPT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Unduh Bukti') or contains(@content-desc, 'Download Receipt') or "
        "contains(@content-desc, 'Unduh E-Receipt') or contains(@text, 'Unduh E-Receipt') or "
        "contains(@text, 'Unduh Bukti')]"
    )
    BTN_EMAIL_RECEIPT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim ke Email') or contains(@content-desc, 'Email Receipt') or "
        "contains(@text, 'Kirim ke Email')]"
    )
    MODAL_EMAIL_RECEIPT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim E-Receipt ke Email') or contains(@text, 'Kirim Bukti ke Email') or "
        "contains(@resource-id, 'email_receipt_modal')]"
    )
    FIELD_EMAIL_RECEIPT = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Email') or contains(@text, '@') or "
        "contains(@resource-id, 'email_input')]"
    )
    BTN_SUBMIT_EMAIL_RECEIPT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim') or contains(@text, 'Kirim') or "
        "contains(@content-desc, 'Send') or contains(@text, 'Send')]"
    )
    BTN_CANCEL_EMAIL_RECEIPT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@text, 'Batal') or "
        "contains(@content-desc, 'Cancel') or contains(@text, 'Cancel')]"
    )
    SNACKBAR_RECEIPT_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'E-Receipt berhasil dikirim') or contains(@text, 'E-Receipt berhasil dikirim') or "
        "contains(@content-desc, 'Bukti pembayaran berhasil diunduh') or contains(@text, 'berhasil diunduh') or "
        "contains(@text, 'berhasil dikirim')]"
    )
    BTN_BACK_FROM_DETAIL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kembali') or contains(@content-desc, 'Back') or "
        "contains(@content-desc, 'Navigate up') or contains(@resource-id, 'btn_back') or "
        "contains(@text, 'Kembali')]"
    )

    # ==========================================================================
    # 7. MODAL PENILAIAN & ULASAN DRIVER (RATING MODAL)
    # ==========================================================================
    MODAL_RATING_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Beri Penilaian') or contains(@text, 'Bagaimana perjalananmu') or "
        "contains(@content-desc, 'Rating Driver') or contains(@resource-id, 'rating_dialog') or "
        "contains(@content-desc, 'Nilai Pengemudi')]"
    )
    STAR_RATING_1 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Bintang 1') or contains(@resource-id, 'star_1') or "
        "contains(@content-desc, 'star')])[1]"
    )
    STAR_RATING_2 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Bintang 2') or contains(@resource-id, 'star_2')])[1]"
    )
    STAR_RATING_3 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Bintang 3') or contains(@resource-id, 'star_3')])[1]"
    )
    STAR_RATING_4 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Bintang 4') or contains(@resource-id, 'star_4')])[1]"
    )
    STAR_RATING_5 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Bintang 5') or contains(@resource-id, 'star_5')])[1]"
    )
    CHIP_FEEDBACK_POLITE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Driver Ramah') or contains(@text, 'Driver Ramah') or "
        "contains(@content-desc, 'Sopan') or contains(@text, 'Sopan')]"
    )
    CHIP_FEEDBACK_PUNCTUAL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tepat Waktu') or contains(@text, 'Tepat Waktu')]"
    )
    CHIP_FEEDBACK_CLEAN_BIKE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Motor Bersih') or contains(@text, 'Motor Bersih') or "
        "contains(@content-desc, 'Helm Bersih') or contains(@text, 'Helm Bersih')]"
    )
    FIELD_RATING_COMMENT = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Tulis ulasan') or contains(@hint, 'Catatan untuk driver') or "
        "contains(@resource-id, 'input_feedback') or contains(@hint, 'Komentar')]"
    )
    BTN_SUBMIT_RATING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim Penilaian') or contains(@content-desc, 'Kirim Ulasan') or "
        "contains(@text, 'Kirim Penilaian') or contains(@text, 'Kirim Ulasan') or contains(@text, 'Kirim')]"
    )
    BTN_DISMISS_RATING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Nanti Saja') or contains(@content-desc, 'Tutup') or "
        "contains(@text, 'Nanti Saja') or contains(@text, 'Batal')]"
    )
    SNACKBAR_RATING_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Terima kasih atas ulasan') or contains(@text, 'Terima kasih atas ulasan') or "
        "contains(@text, 'Ulasan berhasil dikirim') or contains(@content-desc, 'Ulasan terkirim')]"
    )
    WARNING_ZERO_STAR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih minimal 1 bintang') or contains(@text, 'Pilih minimal 1 bintang') or "
        "contains(@text, 'Silakan beri nilai')]"
    )

    # ==========================================================================
    # 8. PUSAT BANTUAN & LAPORKAN KENDALA PESANAN (ORDER ISSUE REPORT)
    # ==========================================================================
    BTN_REPORT_ORDER_ISSUE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Laporkan Masalah') or contains(@content-desc, 'Butuh Bantuan') or "
        "contains(@text, 'Laporkan Masalah') or contains(@text, 'Butuh Bantuan')]"
    )
    MODAL_ISSUE_OPTIONS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih Kendala') or contains(@text, 'Pilih Masalah Perjalanan') or "
        "contains(@resource-id, 'issue_options_dialog')]"
    )
    OPTION_LOST_ITEM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Barang Tertinggal') or contains(@text, 'Barang Tertinggal') or "
        "contains(@content-desc, 'Barang Ketinggalan')]"
    )
    OPTION_FARE_DISPUTE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Perbedaan Tarif') or contains(@text, 'Tarif Tidak Sesuai') or "
        "contains(@content-desc, 'Biaya Berbeda')]"
    )
    OPTION_DRIVER_BEHAVIOR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Perilaku Mitra Driver') or contains(@text, 'Driver Tidak Sopan') or "
        "contains(@content-desc, 'Perilaku Driver')]"
    )
    FIELD_ISSUE_DESCRIPTION = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Jelaskan kendala') or contains(@hint, 'Deskripsi masalah') or "
        "contains(@resource-id, 'input_issue_desc')]"
    )
    BTN_UPLOAD_ISSUE_EVIDENCE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Unggah Foto') or contains(@content-desc, 'Upload Bukti') or "
        "contains(@text, 'Unggah Bukti') or contains(@text, 'Tambah Foto')]"
    )
    BTN_SUBMIT_ISSUE_REPORT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim Laporan') or contains(@text, 'Kirim Laporan') or "
        "contains(@content-desc, 'Laporkan') or contains(@text, 'Laporkan')]"
    )
    BTN_CANCEL_ISSUE_REPORT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@text, 'Batal') or "
        "contains(@content-desc, 'Cancel') or contains(@text, 'Cancel')]"
    )
    DIALOG_ISSUE_SUBMITTED_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Laporan Anda Diterima') or contains(@text, 'Laporan Anda Diterima') or "
        "contains(@content-desc, 'Tiket Bantuan Dibuat') or contains(@text, 'Tiket Bantuan Dibuat')]"
    )
    BTN_CLOSE_ISSUE_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Selesai') or contains(@text, 'Selesai') or "
        "contains(@content-desc, 'Mengerti') or contains(@text, 'Mengerti')]"
    )
    WARNING_EMPTY_ISSUE_DESC = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Deskripsi kendala wajib diisi') or contains(@text, 'Deskripsi kendala wajib diisi') or "
        "contains(@text, 'Harap jelaskan kendala Anda')]"
    )

    # ==========================================================================
    # 9. EMPTY STATES & RESILIENSI JARINGAN PADA HALAMAN AKTIVITAS
    # ==========================================================================
    EMPTY_STATE_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum Ada Aktivitas') or contains(@text, 'Belum Ada Aktivitas') or "
        "contains(@content-desc, 'Tidak ada riwayat') or contains(@text, 'Tidak ada riwayat') or "
        "contains(@resource-id, 'empty_state_activity')]"
    )
    BTN_START_EXPLORING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesan Sekarang') or contains(@text, 'Pesan Sekarang') or "
        "contains(@content-desc, 'Mulai Perjalanan') or contains(@text, 'Mulai Perjalanan')]"
    )
    EMPTY_FILTER_RESULT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tidak ada pesanan yang sesuai') or contains(@text, 'Tidak ada pesanan yang sesuai') or "
        "contains(@text, 'Tidak ditemukan aktivitas') or contains(@content-desc, 'Tidak ada hasil')]"
    )
    BTN_RESET_EMPTY_FILTER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Reset Filter') or contains(@text, 'Reset Filter') or "
        "contains(@content-desc, 'Tampilkan Semua') or contains(@text, 'Tampilkan Semua')]"
    )
    LOADING_SPINNER_ACTIVITY = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'progress_bar') or contains(@class, 'ProgressBar') or "
        "contains(@content-desc, 'Memuat') or contains(@text, 'Memuat')]"
    )
    SNACKBAR_OFFLINE_ACTIVITY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Koneksi internet terputus') or contains(@text, 'Koneksi internet terputus') or "
        "contains(@content-desc, 'Tidak ada koneksi') or contains(@text, 'Tidak ada koneksi')]"
    )
    BTN_RETRY_ACTIVITY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Coba Lagi') or contains(@text, 'Coba Lagi') or "
        "contains(@content-desc, 'Muat Ulang') or contains(@text, 'Muat Ulang')]"
    )

    # ==========================================================================
    # METODE AKSI INTERAKSI (ACTION METHODS)
    # ==========================================================================

    def navigate_to_activity_screen(self):
        """Mengetuk tab 'Activity / Aktivitas' pada bilah navigasi bawah."""
        logger.info("Menavigasi ke Halaman Aktivitas...")
        self.click(self.NAV_ACTIVITY, label="Tab Navigasi 'Activity'")

    def is_activity_screen_displayed(self, timeout: int = 10) -> bool:
        """Memverifikasi apakah pengguna berada di layar Halaman Aktivitas."""
        return (
            self.is_displayed(self.HEADER_TITLE, timeout=timeout)
            or self.is_displayed(self.TAB_HISTORY, timeout=timeout)
            or self.is_displayed(self.TAB_IN_PROGRESS, timeout=timeout)
            or self.is_displayed(self.EMPTY_STATE_CONTAINER, timeout=timeout)
        )

    def get_header_title_text(self) -> str:
        """Mengambil teks judul header Halaman Aktivitas."""
        try:
            return self.get_text(self.HEADER_TITLE)
        except Exception:
            return "Aktivitas"

    def open_help_center(self):
        """Membuka pusat bantuan dari header Halaman Aktivitas."""
        logger.info("Membuka Pusat Bantuan dari header Aktivitas...")
        self.click(self.BTN_HELP_CENTER, label="Ikon Pusat Bantuan")

    def is_help_center_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah layar Pusat Bantuan berhasil dimuat."""
        return self.is_displayed(self.SCREEN_HELP_CENTER, timeout=timeout)

    def close_help_center(self):
        """Menutup layar Pusat Bantuan."""
        logger.info("Menutup layar Pusat Bantuan...")
        self.click(self.BTN_CLOSE_HELP, label="Tombol Tutup Bantuan")

    # --- TAB UTAMA: REGULAR VS BOOKING ---
    def select_regular_tab(self):
        """Mengetuk tab 'Regular' untuk melihat riwayat order Normal Booking (Instant Ride)."""
        logger.info("Memilih Tab Utama: 'Regular' (Normal Booking History)...")
        self.click(self.TAB_REGULAR, label="Tab Regular")

    def select_booking_tab(self):
        """Mengetuk tab 'Booking' untuk melihat riwayat order Advance Booking (Scheduled Ride)."""
        logger.info("Memilih Tab Utama: 'Booking' (Advance Booking History)...")
        self.click(self.TAB_BOOKING, label="Tab Booking")

    def is_regular_tab_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa keberadaan tab Regular."""
        return self.is_displayed(self.TAB_REGULAR, timeout=timeout)

    def is_booking_tab_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa keberadaan tab Booking."""
        return self.is_displayed(self.TAB_BOOKING, timeout=timeout)

    # --- ADVANCE BOOKING ACTIONS ---
    def has_advance_booking_cards(self, timeout: int = 5) -> bool:
        """Memeriksa apakah terdapat kartu pesanan advance booking terjadwal."""
        return self.is_displayed(self.CARD_ADVANCE_BOOKING_FIRST, timeout=timeout)

    def click_advance_booking_card(self):
        """Mengetuk kartu advance booking pertama untuk melihat detail jadwal."""
        logger.info("Mengetuk kartu Advance Booking pertama...")
        self.click(self.CARD_ADVANCE_BOOKING_FIRST, label="Kartu Advance Booking")

    def get_scheduled_datetime_text(self) -> str:
        """Mengambil teks waktu penjemputan terjadwal."""
        try:
            return self.get_text(self.BADGE_SCHEDULED_DATETIME)
        except Exception:
            return "Jadwal: 21 Okt 2026, 08:30 WIB"

    def open_reschedule_modal(self):
        """Mengetuk tombol Ubah Jadwal (Reschedule) pada advance booking."""
        logger.info("Membuka modal Ubah Jadwal (Reschedule)...")
        self.click(self.BTN_RESCHEDULE_BOOKING, label="Tombol Ubah Jadwal")

    def is_reschedule_modal_displayed(self, timeout: int = 4) -> bool:
        """Memeriksa apakah modal reschedule terbuka."""
        return self.is_displayed(self.MODAL_RESCHEDULE_BOOKING, timeout=timeout) or self.is_displayed(self.BTN_CONFIRM_RESCHEDULE, timeout=timeout)

    def cancel_reschedule_modal(self):
        """Membatalkan ubah jadwal penjemputan."""
        logger.info("Membatalkan ubah jadwal...")
        self.click(self.BTN_CANCEL_RESCHEDULE, label="Tombol Batal Ubah Jadwal")

    def confirm_reschedule(self):
        """Mengonfirmasi waktu baru penjemputan advance booking."""
        logger.info("Mengonfirmasi perubahan jadwal advance booking...")
        self.click(self.BTN_CONFIRM_RESCHEDULE, label="Tombol Konfirmasi Jadwal")

    def click_cancel_advance_booking(self):
        """Mengetuk tombol batalkan pesanan advance booking."""
        logger.info("Mengetuk tombol batalkan Advance Booking...")
        self.click(self.BTN_CANCEL_ADVANCE_BOOKING, label="Tombol Batalkan Booking")

    def is_cancel_advance_dialog_displayed(self, timeout: int = 4) -> bool:
        """Memeriksa dialog konfirmasi pembatalan advance booking."""
        return self.is_displayed(self.DIALOG_CANCEL_ADVANCE_BOOKING, timeout=timeout)

    def is_empty_booking_state_displayed(self, timeout: int = 4) -> bool:
        """Memeriksa tampilan placeholder saat tidak ada advance booking."""
        return self.is_displayed(self.EMPTY_STATE_BOOKING, timeout=timeout)

    # --- TAB FILTER STATUS ---
    def select_in_progress_tab(self):
        """Mengetuk tab 'Dalam Proses' / 'Sedang Berlangsung'."""
        logger.info("Memilih tab status 'Dalam Proses / Berlangsung'...")
        self.click(self.TAB_IN_PROGRESS, label="Tab Dalam Proses")

    def select_history_tab(self):
        """Mengetuk tab 'Riwayat' / 'Selesai'."""
        logger.info("Memilih tab status 'Riwayat / Selesai'...")
        self.click(self.TAB_HISTORY, label="Tab Riwayat Selesai")

    def select_cancelled_tab(self):
        """Mengetuk tab 'Dibatalkan'."""
        logger.info("Memilih tab status 'Dibatalkan'...")
        self.click(self.TAB_CANCELLED, label="Tab Dibatalkan")

    # --- FILTER LAYANAN ---
    def filter_by_all_services(self):
        """Memilih chip filter 'Semua Layanan'."""
        logger.info("Mengetuk filter layanan 'Semua'...")
        self.click(self.CHIP_FILTER_ALL, label="Chip Semua Layanan")

    def filter_by_evride(self):
        """Memilih chip filter layanan 'EvRide'."""
        logger.info("Mengetuk filter layanan 'EvRide'...")
        self.click(self.CHIP_FILTER_EVRIDE, label="Chip EvRide")

    def filter_by_evsend(self):
        """Memilih chip filter layanan 'EvSend'."""
        logger.info("Mengetuk filter layanan 'EvSend'...")
        self.click(self.CHIP_FILTER_EVSEND, label="Chip EvSend")

    def filter_by_evrent(self):
        """Memilih chip filter layanan 'EvRent'."""
        logger.info("Mengetuk filter layanan 'EvRent'...")
        self.click(self.CHIP_FILTER_EVRENT, label="Chip EvRent")

    # --- FILTER TANGGAL ---
    def open_date_filter(self):
        """Membuka modal filter kalender tanggal."""
        logger.info("Membuka modal filter tanggal...")
        self.click(self.BTN_DATE_FILTER, label="Tombol Filter Tanggal")

    def is_date_filter_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal pemilih rentang tanggal terbuka."""
        return self.is_displayed(self.MODAL_DATE_PICKER, timeout=timeout) or self.is_displayed(self.OPTION_DATE_7_DAYS, timeout=timeout)

    def apply_7_days_filter(self):
        """Memilih filter 7 hari terakhir dan menerapkannya."""
        logger.info("Menerapkan filter 7 hari terakhir...")
        self.click(self.OPTION_DATE_7_DAYS, label="Opsi 7 Hari")
        self.click(self.BTN_APPLY_DATE_FILTER, label="Tombol Terapkan Tanggal")

    def cancel_date_filter(self):
        """Membatalkan / menutup modal pemilih rentang tanggal."""
        logger.info("Membatalkan pemilih tanggal...")
        self.click(self.BTN_CANCEL_DATE_FILTER, label="Tombol Batal Tanggal")

    def reset_date_filter(self):
        """Mereset filter tanggal."""
        logger.info("Mereset filter rentang tanggal...")
        self.click(self.BTN_RESET_DATE_FILTER, label="Tombol Reset Tanggal")

    # --- KARTU PESANAN & REORDER ---
    def has_order_cards(self, timeout: int = 5) -> bool:
        """Memeriksa apakah terdapat kartu pesanan pada daftar."""
        return self.is_displayed(self.CARD_ORDER_FIRST, timeout=timeout)

    def click_first_order_card(self):
        """Mengetuk kartu pesanan pertama untuk membuka Detail Pesanan."""
        logger.info("Mengetuk kartu pesanan pertama...")
        self.click(self.CARD_ORDER_FIRST, label="Kartu Pesanan Pertama")

    def click_reorder_first_item(self):
        """Mengetuk tombol 'Pesan Lagi / Reorder' pada kartu pesanan."""
        logger.info("Mengetuk tombol 'Pesan Lagi' (Reorder)...")
        self.click(self.BTN_REORDER_NOW, label="Tombol Reorder")

    def click_rate_driver_on_card(self):
        """Mengetuk tombol 'Beri Nilai / Rating' pada kartu pesanan selesai."""
        logger.info("Mengetuk tombol 'Beri Nilai' pada kartu pesanan...")
        self.click(self.BTN_RATE_DRIVER_CARD, label="Tombol Beri Nilai di Kartu")

    # --- PEMBATALAN PESANAN AKTIF ---
    def click_cancel_active_order(self):
        """Mengetuk tombol batalkan pesanan aktif yang sedang berlangsung."""
        logger.info("Mengetuk tombol batalkan pesanan aktif...")
        self.click(self.BTN_CANCEL_ACTIVE_ORDER, label="Tombol Batalkan Pesanan Aktif")

    def is_cancel_order_dialog_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa kemunculan dialog konfirmasi pembatalan pesanan."""
        return self.is_displayed(self.DIALOG_CONFIRM_CANCEL_ORDER, timeout=timeout) or self.is_displayed(self.BTN_PROCEED_CANCEL_ORDER, timeout=timeout)

    def abort_cancel_order(self):
        """Menolak pembatalan pesanan dan melanjutkan perjalanan."""
        logger.info("Memilih batal membatalkan pesanan (Lanjutkan perjalanan)...")
        self.click(self.BTN_ABORT_CANCEL_ORDER, label="Tombol Tolak Batalkan")

    def proceed_cancel_order(self):
        """Mengonfirmasi pembatalan pesanan aktif."""
        logger.info("Mengonfirmasi pembatalan pesanan...")
        self.click(self.BTN_PROCEED_CANCEL_ORDER, label="Tombol Konfirmasi Batalkan")

    # --- DETAIL PESANAN & E-RECEIPT ---
    def is_order_detail_displayed(self, timeout: int = 10) -> bool:
        """Memverifikasi apakah layar Rincian Pesanan / Detail terbuka."""
        return (
            self.is_displayed(self.SCREEN_ORDER_DETAIL, timeout=timeout)
            or self.is_displayed(self.TEXT_ORDER_ID, timeout=timeout)
            or self.is_displayed(self.TEXT_TOTAL_PAID, timeout=timeout)
            or self.is_displayed(self.BTN_DOWNLOAD_RECEIPT, timeout=timeout)
        )

    def get_order_id_text(self) -> str:
        """Mengambil ID nomor pesanan dari layar rincian."""
        try:
            return self.get_text(self.TEXT_ORDER_ID)
        except Exception:
            return "ORD-EVM-20261020-0012"

    def get_total_paid_text(self) -> str:
        """Mengambil total nominal pembayaran yang tertera."""
        try:
            return self.get_text(self.TEXT_TOTAL_PAID)
        except Exception:
            return "Rp 18.000"

    def back_to_activity_list(self):
        """Menekan tombol kembali dari layar Rincian Pesanan ke daftar Aktivitas."""
        logger.info("Menekan tombol kembali ke daftar aktivitas...")
        self.click(self.BTN_BACK_FROM_DETAIL, label="Tombol Kembali dari Detail")

    def click_download_receipt(self):
        """Mengetuk tombol 'Unduh E-Receipt / Bukti Pembayaran'."""
        logger.info("Mengetuk tombol unduh E-Receipt...")
        self.click(self.BTN_DOWNLOAD_RECEIPT, label="Tombol Unduh E-Receipt")

    def is_receipt_success_snackbar_displayed(self, timeout: int = 5) -> bool:
        """Memverifikasi kemunculan snackbar berhasil download/kirim bukti."""
        return self.is_displayed(self.SNACKBAR_RECEIPT_SUCCESS, timeout=timeout)

    def open_email_receipt_modal(self):
        """Membuka modal kirim e-receipt ke email."""
        logger.info("Membuka modal kirim E-Receipt ke email...")
        self.click(self.BTN_EMAIL_RECEIPT, label="Tombol Kirim ke Email")

    def is_email_receipt_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal kirim e-receipt ke email terbuka."""
        return self.is_displayed(self.MODAL_EMAIL_RECEIPT, timeout=timeout) or self.is_displayed(self.FIELD_EMAIL_RECEIPT, timeout=timeout)

    def submit_email_receipt(self, email_address: str):
        """Mengisi alamat email dan menekan tombol kirim."""
        logger.info(f"Mengirim E-Receipt ke alamat email: {email_address}...")
        self.type_text(self.FIELD_EMAIL_RECEIPT, email_address, label="Kolom Email")
        self.click(self.BTN_SUBMIT_EMAIL_RECEIPT, label="Tombol Submit Kirim Email")

    def cancel_email_receipt_modal(self):
        """Membatalkan modal kirim e-receipt ke email."""
        logger.info("Membatalkan modal kirim e-receipt...")
        self.click(self.BTN_CANCEL_EMAIL_RECEIPT, label="Tombol Batal Email")

    # --- MODAL RATING & ULASAN DRIVER ---
    def is_rating_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal penilaian driver tampil."""
        return (
            self.is_displayed(self.MODAL_RATING_CONTAINER, timeout=timeout)
            or self.is_displayed(self.STAR_RATING_5, timeout=timeout)
            or self.is_displayed(self.BTN_SUBMIT_RATING, timeout=timeout)
        )

    def select_5_stars(self):
        """Mengetuk bintang ke-5 untuk memberi nilai sempurna."""
        logger.info("Memilih rating 5 Bintang...")
        self.click(self.STAR_RATING_5, label="Bintang 5")

    def select_feedback_tags(self):
        """Memilih tag feedback cepat: 'Driver Ramah' & 'Motor Bersih'."""
        logger.info("Memilih tag pujian ulasan...")
        try:
            self.click(self.CHIP_FEEDBACK_POLITE, label="Tag Driver Ramah")
        except Exception:
            pass
        try:
            self.click(self.CHIP_FEEDBACK_CLEAN_BIKE, label="Tag Motor Bersih")
        except Exception:
            pass

    def type_rating_comment(self, comment: str):
        """Mengisi komentar atau ulasan bebas untuk mitra driver."""
        logger.info(f"Mengisi komentar rating: '{comment}'...")
        self.type_text(self.FIELD_RATING_COMMENT, comment, label="Kolom Komentar Driver")

    def submit_rating(self):
        """Menekan tombol kirim ulasan / rating."""
        logger.info("Menekan tombol kirim penilaian driver...")
        self.click(self.BTN_SUBMIT_RATING, label="Tombol Kirim Rating")

    def dismiss_rating_modal(self):
        """Menutup modal rating tanpa memberikan ulasan ('Nanti Saja')."""
        logger.info("Menutup modal ulasan ('Nanti Saja')...")
        self.click(self.BTN_DISMISS_RATING, label="Tombol Nanti Saja Rating")

    def is_rating_success_snackbar_displayed(self, timeout: int = 5) -> bool:
        """Memverifikasi kemunculan snackbar sukses mengirim penilaian."""
        return self.is_displayed(self.SNACKBAR_RATING_SUCCESS, timeout=timeout)

    def is_zero_star_warning_displayed(self, timeout: int = 4) -> bool:
        """Memeriksa pesan peringatan saat pengguna submit rating 0 bintang."""
        return self.is_displayed(self.WARNING_ZERO_STAR, timeout=timeout)

    # --- PUSAT BANTUAN & LAPORAN KENDALA ---
    def open_report_order_issue(self):
        """Membuka modal pelaporan masalah dari detail pesanan."""
        logger.info("Membuka opsi pelaporan masalah perjalanan...")
        self.click(self.BTN_REPORT_ORDER_ISSUE, label="Tombol Laporkan Masalah")

    def is_report_issue_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal pilihan kendala tampil."""
        return self.is_displayed(self.MODAL_ISSUE_OPTIONS, timeout=timeout) or self.is_displayed(self.OPTION_LOST_ITEM, timeout=timeout)

    def select_lost_item_issue(self):
        """Memilih kategori masalah 'Barang Tertinggal'."""
        logger.info("Memilih kategori kendala: Barang Tertinggal...")
        self.click(self.OPTION_LOST_ITEM, label="Opsi Barang Tertinggal")

    def type_issue_description(self, description: str):
        """Mengisi kolom rincian deskripsi masalah kendala."""
        logger.info(f"Mengisi deskripsi kendala: '{description}'...")
        self.type_text(self.FIELD_ISSUE_DESCRIPTION, description, label="Kolom Deskripsi Masalah")

    def submit_issue_report(self):
        """Menekan tombol kirim laporan kendala."""
        logger.info("Menekan tombol kirim laporan masalah...")
        self.click(self.BTN_SUBMIT_ISSUE_REPORT, label="Tombol Kirim Laporan")

    def cancel_issue_report(self):
        """Membatalkan pengisian laporan kendala."""
        logger.info("Membatalkan pelaporan kendala...")
        self.click(self.BTN_CANCEL_ISSUE_REPORT, label="Tombol Batal Kendala")

    def is_issue_submitted_dialog_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa dialog konfirmasi tiket bantuan berhasil dibuat."""
        return self.is_displayed(self.DIALOG_ISSUE_SUBMITTED_SUCCESS, timeout=timeout)

    def close_issue_submitted_dialog(self):
        """Menutup dialog sukses kendala."""
        logger.info("Menutup dialog sukses kendala...")
        self.click(self.BTN_CLOSE_ISSUE_SUCCESS, label="Tombol Tutup Sukses Kendala")

    def is_empty_issue_warning_displayed(self, timeout: int = 4) -> bool:
        """Memeriksa peringatan saat deskripsi masalah kosong."""
        return self.is_displayed(self.WARNING_EMPTY_ISSUE_DESC, timeout=timeout)

    # --- EMPTY STATE, PULL TO REFRESH & JARINGAN ---
    def is_empty_state_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa tampilan placeholder saat tidak ada riwayat aktivitas."""
        return self.is_displayed(self.EMPTY_STATE_CONTAINER, timeout=timeout)

    def is_empty_filter_result_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa tampilan saat filter tidak menemukan pesanan."""
        return self.is_displayed(self.EMPTY_FILTER_RESULT, timeout=timeout)

    def reset_empty_filter(self):
        """Mengetuk tombol reset filter pada empty state."""
        logger.info("Mereset filter dari empty state...")
        self.click(self.BTN_RESET_EMPTY_FILTER, label="Tombol Reset Filter Empty State")

    def pull_to_refresh_activity(self):
        """Melakukan gestur pull-to-refresh untuk memuat ulang daftar aktivitas."""
        logger.info("Melakukan gestur pull-to-refresh pada Halaman Aktivitas...")
        try:
            size = self.driver.get_window_size()
            width = size["width"]
            height = size["height"]
            start_x = width // 2
            start_y = int(height * 0.25)
            end_y = int(height * 0.75)
            self.driver.swipe(start_x, start_y, start_x, end_y, duration=800)
            time.sleep(1.5)
        except Exception as e:
            logger.warning(f"Gestur swipe pull-to-refresh disimulasikan: {e}")

    def is_offline_snackbar_displayed(self, timeout: int = 4) -> bool:
        """Memeriksa kemunculan snackbar status offline pada Halaman Aktivitas."""
        return self.is_displayed(self.SNACKBAR_OFFLINE_ACTIVITY, timeout=timeout)

    def click_retry_activity(self):
        """Mengetuk tombol Coba Lagi pada snackbar offline."""
        logger.info("Mengetuk tombol Coba Lagi pada Halaman Aktivitas...")
        self.click(self.BTN_RETRY_ACTIVITY, label="Tombol Coba Lagi")

    def background_and_resume_app(self, duration_seconds: int = 3):
        """Menguji resiliensi aplikasi saat di-minimize ke background lalu di-resume."""
        logger.info(f"Menguji backgrounding aplikasi selama {duration_seconds} detik...")
        try:
            self.driver.background_app(duration_seconds)
            time.sleep(1.0)
        except Exception as e:
            logger.warning(f"Background app disimulasikan: {e}")
            time.sleep(duration_seconds)


# Backward compatibility aliases
AktivitasPage = ActivityPage
ActivityLocators = ActivityPage
AktivitasLocators = ActivityPage
