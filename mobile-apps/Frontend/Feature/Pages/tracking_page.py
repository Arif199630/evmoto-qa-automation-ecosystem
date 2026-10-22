"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - TRACKING & RIDE LIFECYCLE PAGE OBJECT
================================================================================
Target: Layar Pencarian Driver, Pelacakan Real-time, Komunikasi Chat/Foto,
Pembatalan Pesanan, Dialog Pembatalan Driver, Emergency SOS, CS WhatsApp,
dan Penilaian Rating Driver.
Sesuai spesifikasi Sheet 'User' (TC40 s/d TC87).
================================================================================
"""
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("TrackingPage")


class TrackingPage(BasePage):
    """Page Object untuk Siklus Hidup Perjalanan (Trip Lifecycle & In-Ride Tracking)."""

    # ==========================================================================
    # 1. SEARCHING DRIVER STATE & CANCEL SEARCH
    # ==========================================================================
    STATUS_SEARCHING_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Mencari') or contains(@content-desc, 'Searching') or "
        "contains(@resource-id, 'searching_container') or contains(@text, 'Searching')]"
    )
    SNACKBAR_SEARCHING_ONGOING = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'snackbar_searching') or contains(@content-desc, 'on going') or "
        "contains(@content-desc, 'Mencari Driver')]"
    )
    BTN_CANCEL_SEARCHING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cancel') or contains(@content-desc, 'Batal') or "
        "contains(@text, 'Cancel') or contains(@text, 'Batal')]"
    )
    POPUP_CONFIRM_CANCEL = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'popup_cancel') or contains(@content-desc, 'Yakin') or "
        "contains(@text, 'Batalkan Pesanan') or contains(@content-desc, 'Batalkan')]"
    )
    BTN_CONFIRM_CANCEL_CLOSE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'close') or contains(@content-desc, 'Tutup') or "
        "contains(@text, 'close') or contains(@content-desc, 'x')]"
    )
    BTN_CONFIRM_CANCEL_SUBMIT = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'btn_confirm_cancel') or contains(@content-desc, 'Ya, Batalkan') or "
        "contains(@text, 'Cancel') or contains(@text, 'Batalkan')]"
    )

    # Driver Timeout / Not Available Snackbar
    SNACKBAR_DRIVER_NOT_AVAILABLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'not available') or contains(@content-desc, 'tidak ditemukan') or "
        "contains(@text, 'Driver not available') or contains(@text, 'tidak tersedia')]"
    )

    # ==========================================================================
    # 2. DRIVER ASSIGNED & DRIVER INFORMATION CONTAINER
    # ==========================================================================
    DRIVER_INFO_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'driver_info') or contains(@content-desc, 'Driver') or contains(@class, 'BottomSheet')]"
    )
    TEXT_DRIVER_NAME = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'driver_name') or contains(@content-desc, 'Budi') or contains(@content-desc, 'Driver')]"
    )
    TEXT_DRIVER_PLATE = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'driver_plate') or contains(@content-desc, 'B ') or contains(@text, 'B ')]"
    )
    TEXT_DISTANCE_ETA = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'min') or contains(@content-desc, 'km') or contains(@text, 'min')]"
    )

    # ==========================================================================
    # 3. CHAT WITH DRIVER (TEXT & PHOTO)
    # ==========================================================================
    BTN_CHAT_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Chat') or contains(@resource-id, 'btn_chat') or contains(@text, 'Chat')]"
    )
    FIELD_CHAT_INPUT = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Pesan') or contains(@hint, 'Chat') or contains(@content-desc, 'Pesan')]"
    )
    BTN_SEND_CHAT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Send') or contains(@content-desc, 'Kirim') or contains(@resource-id, 'btn_send')]"
    )
    BTN_UPLOAD_PHOTO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Photo') or contains(@content-desc, 'Kamera') or contains(@content-desc, 'Galeri')]"
    )
    TEXT_CHAT_MESSAGE_SENT = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'chat_bubble') or contains(@class, 'TextView')]"
    )

    # ==========================================================================
    # 4. EMERGENCY SOS & CUSTOMER SERVICE
    # ==========================================================================
    BTN_EMERGENCY_ICON = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Emergency') or contains(@content-desc, 'Darurat') or contains(@resource-id, 'btn_sos')]"
    )
    BTN_CUSTOMER_SERVICE_ICON = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Customer Service') or contains(@content-desc, 'CS') or contains(@resource-id, 'btn_cs')]"
    )

    # ==========================================================================
    # 5. USER CANCELLATION AFTER GETTING DRIVER
    # ==========================================================================
    BTN_CANCEL_TRIP_ACTIVE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cancel Trip') or contains(@content-desc, 'Batalkan Perjalanan') or contains(@text, 'Cancel')]"
    )
    MODAL_CANCEL_REASON = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'cancel_reasons') or contains(@content-desc, 'Alasan') or contains(@text, 'Alasan')]"
    )
    RADIO_CANCEL_REASON_ITEM = (
        AppiumBy.XPATH,
        "(//*[contains(@class, 'RadioButton') or contains(@content-desc, 'Alasan')])[1]"
    )
    BTN_SUBMIT_CANCEL_REASON = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Konfirmasi Batalkan') or contains(@content-desc, 'Submit') or contains(@text, 'Batalkan')]"
    )

    # ==========================================================================
    # 6. DRIVER CANCELLATION POPUP & TRY AGAIN
    # ==========================================================================
    POPUP_DRIVER_CANCELLED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Driver has cancel') or contains(@content-desc, 'Driver membatalkan') or "
        "contains(@text, 'Driver has cancel') or contains(@text, 'dibatalkan oleh pengemudi')]"
    )
    BTN_TRY_AGAIN_SEARCH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Try Again') or contains(@content-desc, 'Cari Lagi') or contains(@text, 'Try Again')]"
    )

    # ==========================================================================
    # 7. TRIP COMPLETED & DRIVER RATING / REVIEW
    # ==========================================================================
    SCREEN_ORDER_COMPLETE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sampai') or contains(@content-desc, 'Arrived') or contains(@text, 'Selesai')]"
    )
    TEXT_CASH_COLLECTED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cash Collected') or contains(@content-desc, 'Pembayaran Selesai')]"
    )
    STAR_RATING_5 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'star') or contains(@content-desc, 'Bintang') or contains(@class, 'RatingBar')])[5]"
    )
    STAR_RATING_1 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'star') or contains(@content-desc, 'Bintang') or contains(@class, 'RatingBar')])[1]"
    )
    FIELD_RATING_COMMENT = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Ulasan') or contains(@hint, 'Komentar') or contains(@content-desc, 'Ulasan')]"
    )
    BTN_SUBMIT_RATING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim') or contains(@content-desc, 'Submit') or contains(@text, 'Kirim')]"
    )
    SNACKBAR_RATING_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'terima kasih') or contains(@content-desc, 'sukses') or "
        "contains(@text, 'success') or contains(@resource-id, 'snackbar_success')]"
    )

    # ==========================================================================
    # METHODS / ACTIONS
    # ==========================================================================
    def is_searching_driver(self, timeout: int = 5) -> bool:
        """Memeriksa apakah layar berada dalam state pencarian driver."""
        return self.is_displayed(self.STATUS_SEARCHING_DRIVER, timeout=timeout)

    def cancel_searching_driver(self, confirm: bool = True):
        """Membatalkan proses pencarian driver."""
        self.click(self.BTN_CANCEL_SEARCHING, label="Tombol Batalkan Pencarian")
        if confirm:
            self.click(self.BTN_CONFIRM_CANCEL_SUBMIT, label="Konfirmasi Batalkan Pencarian")
        else:
            self.click(self.BTN_CONFIRM_CANCEL_CLOSE, label="Tutup Dialog Pembatalan (Tetap Mencari)")

    def is_driver_assigned(self, timeout: int = 15) -> bool:
        """Memeriksa apakah driver telah ditemukan dan ditugaskan."""
        return self.is_displayed(self.DRIVER_INFO_CONTAINER, timeout=timeout)

    def expand_driver_container(self):
        """Melakukan scroll up untuk memperluas kontainer informasi driver."""
        self.swipe(start_x=360, start_y=1200, end_x=360, end_y=600, duration=400)

    def collapse_driver_container(self):
        """Melakukan scroll down untuk memperkecil kontainer informasi driver."""
        self.swipe(start_x=360, start_y=600, end_x=360, end_y=1200, duration=400)

    def send_chat_message(self, message: str):
        """Mengirim pesan chat ke driver."""
        self.click(self.BTN_CHAT_DRIVER, label="Tombol Chat Driver")
        self.type_text(self.FIELD_CHAT_INPUT, message, label="Kolom Chat")
        self.click(self.BTN_SEND_CHAT, label="Tombol Kirim Chat")

    def cancel_trip_with_reason(self):
        """Membatalkan trip aktif setelah mendapat driver dengan memilih alasan."""
        self.click(self.BTN_CANCEL_TRIP_ACTIVE, label="Tombol Batalkan Perjalanan")
        self.click(self.RADIO_CANCEL_REASON_ITEM, label="Pilihan Alasan Pembatalan")
        self.click(self.BTN_SUBMIT_CANCEL_REASON, label="Submit Konfirmasi Batal")

    def click_try_again_after_driver_cancel(self):
        """Menekan Try Again saat driver membatalkan pesanan."""
        self.click(self.BTN_TRY_AGAIN_SEARCH, label="Tombol Try Again")

    def submit_driver_review(self, stars: int = 5, comment: str = "Driver ramah dan tepat waktu"):
        """Mengirimkan rating bintang dan ulasan pengemudi."""
        if stars == 5:
            self.click(self.STAR_RATING_5, label="Rating 5 Bintang")
        else:
            self.click(self.STAR_RATING_1, label="Rating 1 Bintang")
        if comment:
            self.type_text(self.FIELD_RATING_COMMENT, comment, label="Komentar Ulasan")
        self.click(self.BTN_SUBMIT_RATING, label="Tombol Kirim Penilaian")

    def is_rating_success_displayed(self) -> bool:
        """Memeriksa apakah snackbar sukses rating warna hijau tampil."""
        return self.is_displayed(self.SNACKBAR_RATING_SUCCESS, timeout=4)


TrackingLocators = TrackingPage
