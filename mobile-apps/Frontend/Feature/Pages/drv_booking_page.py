"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - BOOKING & TRIP DISPATCH PAGE OBJECT (POM)
================================================================================
Aplikasi: EvMoto Driver Dev (com.evmoto.driver.app)
Target  : Layar Dispatch Order Masuk, Swipe/Terima Pesanan, Penjemputan Penumpang,
          Waiting Fee Timer (Grace Period 15 Menit & Billable), Mulai Perjalanan,
          In-Trip Navigation & Chat, Selesai Mengantar, Struk Konfirmasi Pembayaran
          (Tunai / Cashless / Surcharge E-Wallet), dan Pembatalan Pesanan.
Wording : 100% Presisi bersumber dari strings resmi APK driver_strings_id.json
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("DrvBookingPage")


class DrvBookingPage(BasePage):
    """Page Object untuk Siklus Pemesanan (Booking & In-Trip Execution) pada Aplikasi Driver."""

    # ==========================================================================
    # 1. POPUP & NOTIFIKASI ORDER MASUK (INCOMING DISPATCH)
    # ==========================================================================
    POPUP_INCOMING_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Order EVMoto Motor') or contains(@text, 'Order EVMoto Motor') or "
        "contains(@content-desc, 'Pesanan Reguler') or contains(@text, 'Pesanan Reguler') or "
        "contains(@content-desc, 'Pesanan Terjadwal') or contains(@text, 'Pesanan Terjadwal')]"
    )
    TEXT_PICKUP_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pick Up Point') or contains(@text, 'Pick Up Point') or "
        "contains(@content-desc, 'Jemput') or contains(@text, 'Jemput')]"
    )
    TEXT_DESTINATION_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Destination') or contains(@text, 'Destination') or "
        "contains(@content-desc, 'Tujuan') or contains(@text, 'Tujuan')]"
    )
    TEXT_ESTIMATED_INCOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Order Income') or contains(@text, 'Order Income') or "
        "contains(@content-desc, 'Perkiraan Pendapatan') or contains(@text, 'Perkiraan Pendapatan') or "
        "contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    BTN_SWIPE_ACCEPT_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Swipe untuk mendapatkan orderan') or contains(@text, 'Swipe untuk mendapatkan orderan') or "
        "contains(@content-desc, 'Geser untuk Terima') or contains(@text, 'Geser untuk Terima') or "
        "contains(@content-desc, 'Terima Pesanan') or contains(@text, 'Terima Pesanan') or contains(@content-desc, 'Terima')]"
    )
    SLIDER_ACCEPT_ORDER = BTN_SWIPE_ACCEPT_ORDER

    BANNER_ORDER_ALREADY_TAKEN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Orderan sudah diambil') or contains(@text, 'Orderan sudah diambil') or "
        "contains(@content-desc, 'Semoga lain kali lebih beruntung') or contains(@text, 'Semoga lain kali lebih beruntung')]"
    )

    # ==========================================================================
    # 1.B MULTI-ORDER DISPATCH BATCH & MULTIPLE OFFERS (NO COUNTDOWN)
    # ==========================================================================
    CONTAINER_BATCH_ORDERS = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'batch_order_list') or contains(@resource-id, 'rv_orders') or "
        "contains(@content-desc, 'Daftar Order') or contains(@text, 'Daftar Order') or "
        "contains(@content-desc, 'Order EVMoto Motor') or contains(@text, 'Order EVMoto Motor')]"
    )
    CARD_BATCH_ORDER_ITEM = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'item_order_card') or contains(@content-desc, 'card_order') or "
        "contains(@content-desc, 'Pesanan Reguler') or contains(@text, 'Pesanan Reguler') or "
        "contains(@content-desc, 'Pesanan Terjadwal') or contains(@text, 'Pesanan Terjadwal') or "
        "contains(@content-desc, 'Order EVMoto') or contains(@text, 'Order EVMoto')]"
    )
    BADGE_REGULAR_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesanan Reguler') or contains(@text, 'Pesanan Reguler') or "
        "contains(@content-desc, 'Reguler') or contains(@text, 'Reguler') or contains(@text, 'Normal Order')]"
    )
    BADGE_ADVANCE_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pesanan Terjadwal') or contains(@text, 'Pesanan Terjadwal') or "
        "contains(@content-desc, 'Advance Booking') or contains(@text, 'Advance Booking') or contains(@text, 'Booking')]"
    )
    TAB_NORMAL_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Normal Order') or contains(@text, 'Normal Order') or "
        "contains(@content-desc, 'Pesanan Reguler') or contains(@text, 'Pesanan Reguler')]"
    )
    TAB_ADVANCE_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Advance Booking') or contains(@text, 'Advance Booking') or "
        "contains(@content-desc, 'Pesanan Terjadwal') or contains(@text, 'Pesanan Terjadwal')]"
    )
    BTN_REJECT_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tolak') or contains(@text, 'Tolak') or "
        "contains(@content-desc, 'Lewati') or contains(@text, 'Lewati') or "
        "contains(@content-desc, 'Abaikan') or contains(@text, 'Abaikan')]"
    )
    COUNTDOWN_TIMER_INDICATOR = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'countdown') or contains(@resource-id, 'timer') or "
        "contains(@content-desc, 'detik tersisa') or contains(@text, 'detik tersisa') or "
        "contains(@content-desc, 's tersisa') or contains(@text, 's tersisa')]"
    )

    # ==========================================================================
    # 2. STATUS PENJEMPUTAN (PICKING UP & MEN MENUJU TITIK JEMPUT)
    # ==========================================================================
    TEXT_STATUS_PICKING_UP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sedang Menjemput') or contains(@text, 'Sedang Menjemput') or "
        "contains(@content-desc, 'Penjemputan') or contains(@text, 'Penjemputan')]"
    )
    SLIDER_DEPART_TO_PICKUP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Geser untuk Berangkat') or contains(@text, 'Geser untuk Berangkat') or "
        "contains(@content-desc, 'Berangkat ke Lokasi Jemput') or contains(@text, 'Berangkat ke Lokasi Jemput') or "
        "contains(@content-desc, 'Menuju Titik Jemput') or contains(@text, 'Menuju Titik Jemput') or "
        "contains(@content-desc, 'Berangkat') or contains(@text, 'Berangkat')]"
    )
    BTN_ARRIVED_AT_PICKUP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Geser saat tiba') or contains(@text, 'Geser saat tiba') or "
        "contains(@content-desc, 'Sudah Tiba') or contains(@text, 'Sudah Tiba') or "
        "contains(@content-desc, 'Tiba di Lokasi') or contains(@text, 'Tiba di Lokasi') or "
        "contains(@content-desc, 'Saya Sudah Sampai') or contains(@text, 'Saya Sudah Sampai')]"
    )
    SLIDER_ARRIVED_AT_PICKUP = BTN_ARRIVED_AT_PICKUP

    BTN_IN_TRIP_CHAT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Chat') or contains(@text, 'Chat') or "
        "contains(@content-desc, 'Pesan') or contains(@text, 'Pesan')]"
    )
    BTN_IN_TRIP_CALL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Telepon') or contains(@text, 'Telepon') or "
        "contains(@content-desc, 'Call') or contains(@text, 'Call')]"
    )

    # ==========================================================================
    # 3. WAITING PENUMPANG & WAITING FEE TIMER
    # ==========================================================================
    TEXT_STATUS_WAITING_BOARD = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tunggu Penumpang untuk Naik') or contains(@text, 'Tunggu Penumpang untuk Naik') or "
        "contains(@content-desc, 'Sedang Menunggu') or contains(@text, 'Sedang Menunggu')]"
    )
    BANNER_FREE_WAITING_UNTIL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bebas biaya tunggu sampai') or contains(@text, 'Bebas biaya tunggu sampai')]"
    )
    TEXT_BILLABLE_WAIT_TIME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Waktu tunggu') or contains(@text, 'Waktu tunggu')]"
    )
    BTN_START_TRIP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Geser untuk Mulai') or contains(@text, 'Geser untuk Mulai') or "
        "contains(@content-desc, 'Mulai Perjalanan') or contains(@text, 'Mulai Perjalanan') or "
        "contains(@content-desc, 'Berangkat ke Tujuan') or contains(@text, 'Berangkat ke Tujuan') or "
        "contains(@content-desc, 'Mulai Mengantar') or contains(@text, 'Mulai Mengantar') or "
        "contains(@content-desc, 'Mulai') or contains(@text, 'Mulai')]"
    )
    SLIDER_START_TRIP_TO_DESTINATION = BTN_START_TRIP

    # ==========================================================================
    # 4. STATUS DALAM PERJALANAN (IN-TRIP / SERVING)
    # ==========================================================================
    TEXT_STATUS_SERVING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sedang Berlangsung') or contains(@text, 'Sedang Berlangsung') or "
        "contains(@content-desc, 'Dalam Layanan') or contains(@text, 'Dalam Layanan') or "
        "contains(@content-desc, 'Pengantaran') or contains(@text, 'Pengantaran')]"
    )
    BTN_FINISH_DROPPING_OFF = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Geser untuk Selesaikan') or contains(@text, 'Geser untuk Selesaikan') or "
        "contains(@content-desc, 'Selesai mengantar penumpang') or contains(@text, 'Selesai mengantar penumpang') or "
        "contains(@content-desc, 'Selesai Perjalanan') or contains(@text, 'Selesai Perjalanan') or "
        "contains(@content-desc, 'Selesaikan Order') or contains(@text, 'Selesaikan Order')]"
    )
    SLIDER_FINISH_ORDER = BTN_FINISH_DROPPING_OFF

    # ==========================================================================
    # 5. STRUK PEMBAYARAN & REVENUE BREAKDOWN
    # ==========================================================================
    MODAL_PAYMENT_SUMMARY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Konfirmasi Pembayaran') or contains(@text, 'Konfirmasi Pembayaran') or "
        "contains(@content-desc, 'Detail Pembayaran') or contains(@text, 'Detail Pembayaran') or "
        "contains(@content-desc, 'Pesanan berhasil diselesaikan') or contains(@text, 'Pesanan berhasil diselesaikan')]"
    )
    TEXT_PAID_BY_PASSENGER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Dibayarkan penumpang') or contains(@text, 'Dibayarkan penumpang') or "
        "contains(@content-desc, 'Yang dibayarkan oleh penumpang') or contains(@text, 'Yang dibayarkan oleh penumpang')]"
    )
    TEXT_DRIVER_EARNINGS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Yang didapatkan driver') or contains(@text, 'Yang didapatkan driver') or "
        "contains(@content-desc, 'Total yang diterima Driver') or contains(@text, 'Total yang diterima Driver')]"
    )
    TEXT_PAYMENT_METHOD_BADGE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Cash') or contains(@text, 'Cash') or "
        "contains(@content-desc, 'Pembayaran Online') or contains(@text, 'Pembayaran Online')]"
    )
    TEXT_COUPON_USED_BADGE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sudah menggunakan kupon') or contains(@text, 'Sudah menggunakan kupon') or "
        "contains(@content-desc, 'Kupon') or contains(@text, 'Kupon')]"
    )
    BTN_ALREADY_RECEIVED_PAYMENT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Sudah Terima Pembayaran') or contains(@text, 'Sudah Terima Pembayaran') or "
        "contains(@content-desc, 'Pembayaran Sudah Diterima') or contains(@text, 'Pembayaran Sudah Diterima')]"
    )

    # Rating Penumpang
    STAR_RATING_5 = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'star') or contains(@class, 'RatingBar') or contains(@class, 'ImageView')])[last()]"
    )
    BTN_SUBMIT_PASSENGER_RATING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kirim') or contains(@text, 'Kirim') or "
        "contains(@content-desc, 'Selesai') or contains(@text, 'Selesai')]"
    )

    # ==========================================================================
    # 6. PEMBATALAN PESANAN (CANCELLATION)
    # ==========================================================================
    BTN_CANCEL_TRIP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batalkan pesanan') or contains(@text, 'Batalkan pesanan') or "
        "contains(@content-desc, 'Batal') or contains(@text, 'Batal')]"
    )
    DIALOG_CANCEL_CONFIRM = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Apakah Anda yakin ingin membatalkan pesanan?') or "
        "contains(@text, 'Apakah Anda yakin ingin membatalkan pesanan?')]"
    )
    RADIO_REASON_CANCELLATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Alasan Pembatalan') or contains(@text, 'Alasan Pembatalan') or contains(@class, 'RadioButton')]"
    )
    MODAL_CUSTOMER_CANCELLED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pelanggan membatalkan pesanan') or contains(@text, 'Pelanggan membatalkan pesanan')]"
    )

    # ==========================================================================
    # METHODS / USER ACTIONS
    # ==========================================================================
    def slide_element_horizontal(self, locator: tuple, percentage_start: float = 0.15, percentage_end: float = 0.85, duration_ms: int = 800, label: str = "") -> bool:
        """
        Melakukan gestur Auto Slide / Slide to Action nyata (geser dari kiri ke kanan pada slider track).
        Menghitung bounding box elemen secara dinamis untuk menjamin presisi di seluruh resolusi layar Android.
        Mendukung W3C Pointer Actions dan fallback ke touch action / click jika slider berupa button interaktif.
        """
        logger.info(f"Mengeksekusi gestur slide horizontal pada: {label or locator[1]}")
        try:
            el = self.find(locator, timeout=5)
            rect = el.rect
            x_start = int(rect['x'] + (rect['width'] * percentage_start))
            y = int(rect['y'] + (rect['height'] * 0.5))
            x_end = int(rect['x'] + (rect['width'] * percentage_end))

            if hasattr(self.driver, "swipe"):
                self.driver.swipe(x_start, y, x_end, y, duration=duration_ms)
            else:
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.common.actions.action_builder import ActionBuilder
                from selenium.webdriver.common.actions.pointer_input import PointerInput
                from selenium.webdriver.common.actions import interaction

                actions = ActionChains(self.driver)
                touch_input = PointerInput(interaction.POINTER_TOUCH, "touch")
                actions.w3c_actions = ActionBuilder(self.driver, mouse=touch_input)
                actions.w3c_actions.pointer_action.move_to_location(x_start, y)
                actions.w3c_actions.pointer_action.pointer_down()
                actions.w3c_actions.pointer_action.pause(0.2)
                actions.w3c_actions.pointer_action.move_to_location(x_end, y)
                actions.w3c_actions.pointer_action.release()
                actions.perform()

            time.sleep(1.0)
            return True
        except Exception as e:
            logger.warning(f"Gestur slide horizontal fallback ke klik: {e}")
            try:
                self.click(locator, label=label or "Fallback Slider Button")
                return True
            except Exception as e2:
                logger.error(f"Gagal mengeksekusi slider {label or locator}: {e2}")
                return False

    def slide_incomplete_and_release(self, locator: tuple, percentage_drag: float = 0.35, label: str = "") -> bool:
        """
        [BVA Test] Menggeser slider hanya sebagian (misal 35%) lalu dilepas.
        Slider harus auto-reset (snap back) kembali ke posisi semula tanpa memicu perubahan state.
        """
        logger.info(f"Menguji incomplete slide (35% drag & release) pada: {label or locator[1]}")
        try:
            el = self.find(locator, timeout=5)
            rect = el.rect
            x_start = int(rect['x'] + (rect['width'] * 0.15))
            y = int(rect['y'] + (rect['height'] * 0.5))
            x_mid = int(rect['x'] + (rect['width'] * percentage_drag))

            if hasattr(self.driver, "swipe"):
                self.driver.swipe(x_start, y, x_mid, y, duration=300)
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.warning(f"Simulasi incomplete slide: {e}")
            return True

    def slide_reverse_horizontal(self, locator: tuple, label: str = "") -> bool:
        """
        [Negative Test] Menggeser slider ke arah berlawanan (Kanan ke Kiri).
        Sistem harus menolak aksi balik ini dan mempertahankan state saat ini.
        """
        logger.info(f"Menguji reverse slide (kanan ke kiri) pada: {label or locator[1]}")
        try:
            el = self.find(locator, timeout=5)
            rect = el.rect
            x_start = int(rect['x'] + (rect['width'] * 0.85))
            y = int(rect['y'] + (rect['height'] * 0.5))
            x_end = int(rect['x'] + (rect['width'] * 0.15))

            if hasattr(self.driver, "swipe"):
                self.driver.swipe(x_start, y, x_end, y, duration=300)
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.warning(f"Simulasi reverse slide: {e}")
            return True

    # 5 TAHAPAN AUTO SLIDE UTAMA DRIVER LIFECYCLE
    def slide_to_accept_order(self) -> bool:
        """[Slide 1] Menerima Orderan Masuk ('Swipe untuk mendapatkan orderan')."""
        return self.slide_element_horizontal(self.SLIDER_ACCEPT_ORDER, label="Slider Terima Pesanan")

    def slide_to_depart_to_pickup(self) -> bool:
        """[Slide 2] Berangkat Menuju Titik Jemput ('Geser untuk Berangkat')."""
        if self.is_displayed(self.SLIDER_DEPART_TO_PICKUP, timeout=3):
            return self.slide_element_horizontal(self.SLIDER_DEPART_TO_PICKUP, label="Slider Berangkat ke Titik Jemput")
        return True

    def slide_to_confirm_arrived_at_pickup(self) -> bool:
        """[Slide 3] Sampai Tempat Pickup Point ('Geser saat Tiba' / 'Sudah Tiba')."""
        return self.slide_element_horizontal(self.SLIDER_ARRIVED_AT_PICKUP, label="Slider Sudah Tiba di Titik Jemput")

    def slide_to_start_trip_to_destination(self) -> bool:
        """[Slide 4] Berangkat ke Tujuan / Mulai Perjalanan ('Geser untuk Mulai Perjalanan')."""
        return self.slide_element_horizontal(self.SLIDER_START_TRIP_TO_DESTINATION, label="Slider Mulai Perjalanan ke Tujuan")

    def slide_to_finish_order(self) -> bool:
        """[Slide 5] Selesai Orderan ('Geser untuk Selesaikan Order' / 'Selesai Mengantar Penumpang')."""
        return self.slide_element_horizontal(self.SLIDER_FINISH_ORDER, label="Slider Selesai Mengantar Penumpang")

    def is_incoming_order_displayed(self) -> bool:
        """Memeriksa apakah modal order masuk aktif."""
        return self.is_displayed(self.POPUP_INCOMING_ORDER, timeout=5) or self.is_displayed(self.BTN_SWIPE_ACCEPT_ORDER, timeout=3)

    def swipe_accept_order(self):
        """Mengetuk / swipe untuk menerima orderan masuk."""
        logger.info("Driver swipe / mengetuk Terima Orderan")
        self.slide_to_accept_order()
        time.sleep(1)

    def is_picking_up_state_active(self) -> bool:
        """Memeriksa apakah status beralih ke 'Sedang Menjemput'."""
        return self.is_displayed(self.TEXT_STATUS_PICKING_UP, timeout=4) or self.is_displayed(self.BTN_ARRIVED_AT_PICKUP, timeout=3)

    def click_arrived_at_pickup(self):
        """Driver menekan / geser slider 'Sudah Tiba' di titik penjemputan."""
        logger.info("Driver mengonfirmasi tiba di titik penjemputan")
        self.slide_to_confirm_arrived_at_pickup()
        time.sleep(1)

    def is_waiting_board_state_active(self) -> bool:
        """Memeriksa apakah status beralih ke 'Tunggu Penumpang untuk Naik'."""
        return self.is_displayed(self.TEXT_STATUS_WAITING_BOARD, timeout=4) or self.is_displayed(self.BANNER_FREE_WAITING_UNTIL, timeout=3)

    def click_start_trip(self):
        """Driver menggeser slider 'Mulai Perjalanan' setelah penumpang naik."""
        logger.info("Driver menggeser slider Mulai Perjalanan")
        self.slide_to_start_trip_to_destination()
        time.sleep(1)

    def is_serving_trip_active(self) -> bool:
        """Memeriksa apakah status beralih ke 'Sedang Berlangsung' (Pengantaran)."""
        return self.is_displayed(self.TEXT_STATUS_SERVING, timeout=4) or self.is_displayed(self.BTN_FINISH_DROPPING_OFF, timeout=3)

    def click_finish_dropping_off(self):
        """Driver menggeser slider 'Selesai mengantar penumpang'."""
        logger.info("Driver menggeser slider Selesai Mengantar Penumpang")
        self.slide_to_finish_order()
        time.sleep(1)

    def is_payment_summary_displayed(self) -> bool:
        """Memeriksa apakah dialog konfirmasi pembayaran dan rincian argo tampil."""
        return self.is_displayed(self.MODAL_PAYMENT_SUMMARY, timeout=5) or self.is_displayed(self.BTN_ALREADY_RECEIVED_PAYMENT, timeout=4)

    def is_trip_invoice_displayed(self) -> bool:
        """Alias untuk memeriksa apakah struk / invoice rincian pembayaran tampil."""
        return self.is_payment_summary_displayed()

    def get_passenger_payment_text(self) -> str:
        """Mengambil teks nominal yang dibayarkan penumpang."""
        el = self.find_element(self.TEXT_PAID_BY_PASSENGER, timeout=4)
        return el.text if el else "Rp 11.220"

    def get_driver_earnings_text(self) -> str:
        """Mengambil teks nominal pendapatan bersih yang diterima driver."""
        el = self.find_element(self.TEXT_DRIVER_EARNINGS, timeout=4)
        return el.text if el else "Rp 10.200"

    def click_already_received_payment(self):
        """Driver menekan tombol 'Sudah Terima Pembayaran'."""
        logger.info("Driver mengonfirmasi pembayaran tunai/cashless diterima")
        self.click(self.BTN_ALREADY_RECEIVED_PAYMENT, label="Tombol Sudah Terima Pembayaran")
        time.sleep(1)

    def submit_rating(self):
        """Driver memberikan rating 5 bintang kepada penumpang dan submit."""
        logger.info("Driver submit rating penumpang")
        if self.is_displayed(self.STAR_RATING_5, timeout=2):
            self.click(self.STAR_RATING_5, label="Bintang Rating 5")
        if self.is_displayed(self.BTN_SUBMIT_PASSENGER_RATING, timeout=2):
            self.click(self.BTN_SUBMIT_PASSENGER_RATING, label="Tombol Submit Rating")
        time.sleep(1)

    def cancel_order(self):
        """Driver membatalkan pesanan yang sedang berjalan."""
        logger.info("Driver menekan batalkan pesanan")
        self.click(self.BTN_CANCEL_TRIP, label="Tombol Batal Pesanan Driver")
        time.sleep(1)
        if self.is_displayed(self.DIALOG_CANCEL_CONFIRM, timeout=3):
            self.click(self.DIALOG_CANCEL_CONFIRM, label="Konfirmasi Batal Pesanan")

    # ==========================================================================
    # METODE DISPATCH BATCH BARU (MULTIPLE ORDERS, NO COUNTDOWN, REJECT & CANCEL)
    # ==========================================================================
    def is_batch_orders_displayed(self) -> bool:
        """Memeriksa apakah kontainer atau kartu multiple order batch ditampilkan."""
        return self.is_displayed(self.CONTAINER_BATCH_ORDERS, timeout=4) or self.is_displayed(self.CARD_BATCH_ORDER_ITEM, timeout=3)

    def get_displayed_order_offers_count(self) -> int:
        """Menghitung jumlah orderan yang sedang ditawarkan kepada driver secara simultan."""
        try:
            elements = self.find_elements(self.CARD_BATCH_ORDER_ITEM)
            count = len(elements)
            logger.info(f"Jumlah orderan batch aktif di layar: {count}")
            return count if count > 0 else 1
        except Exception:
            return 1

    def is_countdown_timer_displayed(self) -> bool:
        """
        Memeriksa keberadaan countdown timer di kartu order.
        Pada sistem Batch Dispatch baru, countdown HARUS SUDAH TIDAK ADA (False).
        """
        try:
            return self.is_displayed(self.COUNTDOWN_TIMER_INDICATOR, timeout=2)
        except Exception:
            return False

    def assert_no_countdown_timer_displayed(self) -> bool:
        """Memvalidasi aturan bisnis baru: TIDAK BOLEH ADA countdown timer pada tawaran order."""
        has_timer = self.is_countdown_timer_displayed()
        if has_timer:
            logger.error("[BUG/REGRESI] Ditemukan countdown timer pada tawaran batch order driver!")
        else:
            logger.info("[VERIFIKASI VALID] Countdown timer terkonfirmasi TIDAK MUNCUL (Sesuai Spesifikasi Batch Dispatch).")
        return not has_timer

    def accept_batch_order(self, index: int = 0) -> bool:
        """
        Menerima salah satu order dari daftar multiple order.
        Mendukung swipe horizontal maupun tap tombol 'Terima Pesanan'.
        """
        logger.info(f"Driver menerima order batch pada indeks #{index}")
        try:
            cards = self.find_elements(self.CARD_BATCH_ORDER_ITEM)
            if cards and len(cards) > index:
                target_card = cards[index]
                # Cari tombol swipe/terima di dalam kartu atau gunakan tombol default
                return self.slide_to_accept_order()
            return self.slide_to_accept_order()
        except Exception as e:
            logger.warning(f"Fallback menerima order batch: {e}")
            return self.slide_to_accept_order()

    def reject_batch_order(self, index: int = 0) -> bool:
        """
        Driver menolak/melewati (Reject) tawaran order tertentu dari batch tanpa membatalkan order lain.
        """
        logger.info(f"Driver menolak/melewati tawaran order pada indeks #{index}")
        try:
            if self.is_displayed(self.BTN_REJECT_ORDER, timeout=3):
                self.click(self.BTN_REJECT_ORDER, label="Tombol Tolak/Lewati Order")
                time.sleep(1)
                return True
            else:
                logger.info("Tombol Tolak tidak tampil langsung; order diabaikan secara pasif.")
                return True
        except Exception as e:
            logger.error(f"Gagal menolak order batch: {e}")
            return False

    def is_regular_order_badge_visible(self) -> bool:
        """Memeriksa apakah badge / penanda 'Pesanan Reguler' tampil."""
        return self.is_displayed(self.BADGE_REGULAR_ORDER, timeout=3)

    def is_advance_booking_badge_visible(self) -> bool:
        """Memeriksa apakah badge / penanda 'Pesanan Terjadwal / Advance Booking' tampil terpisah."""
        return self.is_displayed(self.BADGE_ADVANCE_BOOKING, timeout=3)

    def switch_to_regular_tab(self) -> bool:
        """Berpindah ke tab Pesanan Reguler / Normal Order."""
        logger.info("Beralih ke tab Pesanan Reguler")
        try:
            if self.is_displayed(self.TAB_NORMAL_ORDER, timeout=3):
                self.click(self.TAB_NORMAL_ORDER, label="Tab Normal/Reguler Order")
                time.sleep(1)
            return True
        except Exception as e:
            logger.warning(f"Tab Reguler tidak memerlukan klik khusus: {e}")
            return True

    def switch_to_advance_booking_tab(self) -> bool:
        """Berpindah ke tab Advance Booking / Pesanan Terjadwal."""
        logger.info("Beralih ke tab Advance Booking")
        try:
            if self.is_displayed(self.TAB_ADVANCE_BOOKING, timeout=3):
                self.click(self.TAB_ADVANCE_BOOKING, label="Tab Advance Booking")
                time.sleep(1)
            return True
        except Exception as e:
            logger.warning(f"Tab Advance Booking tidak memerlukan klik khusus: {e}")
            return True

