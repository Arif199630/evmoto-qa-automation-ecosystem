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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("TrackingPage")

# Paket aplikasi telepon bawaan Android/Google/Samsung (tujuan tombol SOS darurat)
DIALER_PACKAGES = (
    "com.google.android.dialer",
    "com.android.dialer",
    "com.android.server.telecom",
    "com.samsung.android.dialer",
    "com.google.android.contacts",
)
# Paket WhatsApp (tujuan tombol Customer Service WhatsApp)
WHATSAPP_PACKAGES = ("com.whatsapp", "com.whatsapp.w4b")


def _xpath_literal(value: str) -> str:
    """Literal string XPath 1.0 yang aman untuk teks berisi tanda kutip (mis. payload XSS)."""
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ", \"'\", ".join(f"'{p}'" for p in parts) + ")"


class TrackingPage(BasePage):
    """Page Object untuk Siklus Hidup Perjalanan (Trip Lifecycle & In-Ride Tracking)."""

    # ==========================================================================
    # 1. SEARCHING DRIVER STATE & CANCEL SEARCH
    # ==========================================================================
    # Teks nyata aplikasi User v1.2.33: ev_motorcycle_driver_search & ev_motorcycle_waiting_driver_confirmation
    STATUS_SEARCHING_DRIVER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sedang mencari driver terdekat') or "
        "contains(@text, 'Sedang mencari driver terdekat') or "
        "contains(@content-desc, 'Sedang Menunggu Konfirmasi Driver') or "
        "contains(@content-desc, 'Mencari') or contains(@content-desc, 'Searching') or "
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
    # Teks nyata: driver_cancel_title 'Driver Membatalkan Perjalanan', driver_cancel_button 'Coba Lagi'
    POPUP_DRIVER_CANCELLED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Driver Membatalkan Perjalanan') or "
        "contains(@text, 'Driver Membatalkan Perjalanan') or "
        "contains(@content-desc, 'Driver has cancel') or contains(@content-desc, 'Driver membatalkan') or "
        "contains(@text, 'Driver has cancel') or contains(@text, 'dibatalkan oleh pengemudi')]"
    )
    BTN_TRY_AGAIN_SEARCH = (
        AppiumBy.XPATH,
        "//*[@content-desc='Coba Lagi' or @text='Coba Lagi' or "
        "contains(@content-desc, 'Try Again') or contains(@content-desc, 'Cari Lagi') or contains(@text, 'Try Again')]"
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
    # Teks nyata: successfully_rating_review 'Penilaian dan ulasan berhasil dikirim'
    SNACKBAR_RATING_SUCCESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Penilaian dan ulasan berhasil dikirim') or "
        "contains(@text, 'Penilaian dan ulasan berhasil dikirim') or "
        "contains(@content-desc, 'terima kasih') or contains(@content-desc, 'sukses') or "
        "contains(@text, 'success') or contains(@resource-id, 'snackbar_success')]"
    )

    # ==========================================================================
    # 8. LOCATOR VERIFIKASI HASIL (TEKS NYATA DARI user_lang_id.json APK v1.2.33)
    # ==========================================================================
    # Dialog konfirmasi batal saat mencari driver (cancel_order_title_dialog)
    DIALOG_CANCEL_ORDER_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Apakah Anda yakin ingin membatalkan pesanan') or "
        "contains(@text, 'Apakah Anda yakin ingin membatalkan pesanan')]"
    )
    # Driver sudah ditugaskan (driver_pick_up / driver_arrived_in / driver_arrive_the_pickup_point)
    TEXT_DRIVER_ASSIGNED_STATUS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Driver sedang menuju titik jemput') or "
        "contains(@text, 'Driver sedang menuju titik jemput') or "
        "contains(@content-desc, 'Driver telah tiba di titik penjemputan') or "
        "contains(@content-desc, 'Driver tiba di titik penjemputan')]"
    )
    # Tombol chat pada panel driver (chat_driver)
    BTN_CHAT_DRIVER_EXACT = (AppiumBy.XPATH, "//*[@content-desc='Chat Driver' or @text='Chat Driver']")
    # Dialog driver tidak tersedia setelah timeout (driver_not_available_title / _description)
    DIALOG_DRIVER_NOT_AVAILABLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Driver Tidak Ada yang Tersedia') or "
        "contains(@text, 'Driver Tidak Ada yang Tersedia') or "
        "contains(@content-desc, 'saat ini belum ada driver yang tersedia')]"
    )
    # Layar penilaian setelah trip selesai (how_travel_experience / submit_review)
    SCREEN_RATING_PROMPT = (
        AppiumBy.XPATH,
        "//*[@content-desc='Bagaimana pengalaman perjalanan Anda?' or "
        "@text='Bagaimana pengalaman perjalanan Anda?' or @content-desc='Kirim Penilaian' or "
        "@text='Kirim Penilaian']"
    )
    # Snackbar gagal membuka WhatsApp (unable_open_whatsapp)
    SNACKBAR_WHATSAPP_UNAVAILABLE = (
        AppiumBy.XPATH,
        "//*[@content-desc='Tidak dapat membuka WhatsApp' or @text='Tidak dapat membuka WhatsApp']"
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

    def _vertical_swipe_points(self):
        """Titik swipe relatif ukuran layar (koordinat tetap 1200px keluar layar emulator 320x640)."""
        size = self.driver.get_window_size()
        x = size["width"] // 2
        return x, int(size["height"] * 0.85), int(size["height"] * 0.40)

    def expand_driver_container(self):
        """Melakukan scroll up untuk memperluas kontainer informasi driver."""
        x, bawah, atas = self._vertical_swipe_points()
        self.swipe(start_x=x, start_y=bawah, end_x=x, end_y=atas, duration=400)

    def collapse_driver_container(self):
        """Melakukan scroll down untuk memperkecil kontainer informasi driver."""
        x, bawah, atas = self._vertical_swipe_points()
        self.swipe(start_x=x, start_y=atas, end_x=x, end_y=bawah, duration=400)

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

    # ==========================================================================
    # METHOD VERIFIKASI HASIL (dipakai assertion test booking)
    # ==========================================================================
    def wait_until_gone(self, locator, timeout: int = 10) -> bool:
        """True bila elemen hilang/tidak terlihat dalam batas waktu."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_until_searching_gone(self, timeout: int = 15) -> bool:
        """True bila status pencarian driver sudah hilang dari layar."""
        return self.wait_until_gone(self.STATUS_SEARCHING_DRIVER, timeout=timeout)

    def is_cancel_order_dialog_closed(self, timeout: int = 6) -> bool:
        """True bila dialog 'Apakah Anda yakin ingin membatalkan pesanan?' sudah tertutup."""
        return self.wait_until_gone(self.DIALOG_CANCEL_ORDER_CONFIRM, timeout=timeout)

    def is_driver_on_the_way_displayed(self, timeout: int = 10) -> bool:
        """Driver sudah ditugaskan: status 'Driver sedang menuju titik jemput' / tiba tampil."""
        return self.is_displayed(self.TEXT_DRIVER_ASSIGNED_STATUS, timeout=timeout)

    def is_chat_driver_button_displayed(self, timeout: int = 5) -> bool:
        """Tombol 'Chat Driver' pada panel informasi driver tampil."""
        return self.is_displayed(self.BTN_CHAT_DRIVER_EXACT, timeout=timeout)

    def get_chat_driver_button_y(self) -> int:
        """Posisi vertikal (piksel) tombol 'Chat Driver', untuk mengukur panel naik/turun."""
        return int(self.find(self.BTN_CHAT_DRIVER_EXACT, timeout=5).location["y"])

    def is_chat_message_displayed(self, message: str, timeout: int = 8) -> bool:
        """Gelembung chat yang diawali teks pesan yang dikirim tampil.

        Kolom input (EditText) dikecualikan: bila pesan gagal terkirim, teksnya masih
        tertinggal di kolom input dan tidak boleh terhitung sebagai terkirim.
        starts-with dipakai karena Flutter bisa menggabungkan jam kirim ke label gelembung.
        """
        literal = _xpath_literal(message)
        locator = (
            AppiumBy.XPATH,
            f"//*[not(self::android.widget.EditText) and "
            f"(starts-with(@content-desc, {literal}) or starts-with(@text, {literal}))]"
        )
        return self.is_displayed(locator, timeout=timeout)

    def is_driver_not_available_displayed(self, timeout: int = 5) -> bool:
        """Dialog 'Driver Tidak Ada yang Tersedia' tampil."""
        return self.is_displayed(self.DIALOG_DRIVER_NOT_AVAILABLE, timeout=timeout)

    def is_driver_cancelled_popup_displayed(self, timeout: int = 5) -> bool:
        """Popup 'Driver Membatalkan Perjalanan' tampil."""
        return self.is_displayed(self.POPUP_DRIVER_CANCELLED, timeout=timeout)

    def is_rating_screen_displayed(self, timeout: int = 5) -> bool:
        """Layar penilaian trip ('Bagaimana pengalaman perjalanan Anda?' / 'Kirim Penilaian') tampil."""
        return self.is_displayed(self.SCREEN_RATING_PROMPT, timeout=timeout)

    def is_whatsapp_unavailable_displayed(self, timeout: int = 3) -> bool:
        """Snackbar 'Tidak dapat membuka WhatsApp' tampil (WhatsApp tidak terpasang)."""
        return self.is_displayed(self.SNACKBAR_WHATSAPP_UNAVAILABLE, timeout=timeout)

    def get_current_package(self) -> str:
        """Nama paket aplikasi yang sedang di depan layar."""
        return self.driver.current_package or ""

    def is_phone_dialer_opened(self) -> bool:
        """True bila aplikasi telepon (dialer) sistem sedang tampil di depan."""
        return self.get_current_package() in DIALER_PACKAGES

    def is_whatsapp_opened(self) -> bool:
        """True bila aplikasi WhatsApp sedang tampil di depan."""
        return self.get_current_package() in WHATSAPP_PACKAGES


TrackingLocators = TrackingPage
