"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - HOME PAGE (BERANDA)
================================================================================
Target: Layar Utama / Beranda Pengguna EVMoto (Flutter App)
Struktur UI Beranda Lengkap (Diurutkan dari Atas ke Bawah):
1. Header & Identitas:
   - Greeting ('Hi, where are you going today?' / 'Halo, mau ke mana hari ini?')
   - Lokasi Penjemputan Terkini (Current Location Pin & Address Bar)
   - Ikon Notifikasi / Bell (Pusat Notifikasi & Promo)
   - Avatar / Shortcut Profil Header
2. Kartu Saldo & Shortcut Dompet (EvWallet Card):
   - Informasi Saldo (Rp XX.XXX)
   - Tombol 'Top Up' / 'Isi Saldo'
   - Tombol 'Pay' / 'Bayar' (QRIS Shortcut)
   - Tombol 'History' / 'Riwayat Transaksi'
3. Bilah Pencarian Destinasi (Search Destination Bar):
   - Input 'where are you going' / 'Mau ke mana'
   - Quick Destination Chips: 'Tempat ngopi', 'Kantor', 'Rumah', '+ Tambah Lokasi'
4. Grid Layanan Utama EVMoto:
   - 'EvRide' (Ojek Motor Listrik Hijau)
   - 'EvSend' (Pengiriman Paket / Logistik)
   - 'EvRent' / 'Battery Swap' (Sewa Motor / Stasiun Penukaran Baterai)
   - 'Lainnya / More Services'
5. Carousel / Slider Promo & Berita Edukasi Hijau:
   - Banner Promo Diskon Pengguna Baru / Cashback
   - Navigasi Geser Banner (Swipe Right / Left)
   - Tombol / Link 'Lihat Semua Promo'
6. Widget Aktivitas Terkini & Live Order Tracking:
   - Status Pesanan Aktif / Trip Terbaru
   - Tombol Pesan Ulang / Riwayat Cepat
7. Bilah Navigasi Bawah (Bottom Navigation Bar):
   - Tab 'Home / Beranda'
   - Tab 'Activity / Aktivitas'
   - Tab 'Me / Profil'
8. Dialog, Popup, & Refresh States:
   - Welcome Modal ('Continue' / 'Lanjut')
   - Peringatan GPS / Lokasi Mati di Beranda
   - Pull to Refresh Data Beranda
   - Dialog Konfirmasi Keluar saat tekan Back di Beranda
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("HomePage")


class HomePage(BasePage):
    """Page Object untuk Beranda Utama Pengguna Aplikasi EvMoto."""

    # ==========================================================================
    # 1. HEADER, GREETING, LOKASI PENJEMPUTAN & NOTIFIKASI
    # ==========================================================================
    TEXT_GREETING_TITLE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'where are you going') or contains(@content-desc, 'Mau ke mana') or "
        "contains(@content-desc, 'Hi,') or contains(@content-desc, 'Halo,') or "
        "contains(@text, 'where are you going') or contains(@text, 'Mau ke mana')]"
    )
    USER_AVATAR_HEADER = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[contains(@content-desc, 'avatar') or contains(@content-desc, 'profile')] | "
        "(//android.widget.ImageView)[1]"
    )
    LOCATION_CURRENT_PIN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lokasi') or contains(@content-desc, 'Location') or "
        "contains(@content-desc, 'Jl.') or contains(@text, 'Jl.')]"
    )
    BTN_NOTIFICATION_BELL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Notification') or contains(@content-desc, 'Notifikasi') or "
        "contains(@resource-id, 'bell') or contains(@content-desc, 'bell')]"
    )
    BADGE_NOTIFICATION_UNREAD = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'badge') or contains(@content-desc, 'unread')]"
    )
    CONTAINER_NOTIFICATION_LIST = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pemberitahuan') or contains(@content-desc, 'Notifikasi') or "
        "contains(@text, 'Notifikasi')]"
    )

    # ==========================================================================
    # 2. KARTU SALDO & SHORTCUT DOMPET (EVWALLET CARD)
    # ==========================================================================
    CARD_WALLET_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Saldo') or contains(@content-desc, 'Balance') or "
        "contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    TEXT_HOME_WALLET_BALANCE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    BTN_WALLET_TOP_UP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Top Up') or contains(@content-desc, 'Isi Saldo') or "
        "contains(@text, 'Top Up') or contains(@text, 'Isi Saldo')]"
    )
    BTN_WALLET_PAY_QR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Bayar') or contains(@content-desc, 'Pay') or "
        "contains(@content-desc, 'QRIS') or contains(@text, 'Bayar')]"
    )
    BTN_WALLET_HISTORY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Riwayat') or contains(@content-desc, 'History') or "
        "contains(@text, 'Riwayat')]"
    )
    MODAL_TOP_UP_CHOICE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Nominal') or contains(@content-desc, 'Pilih Nominal') or "
        "contains(@content-desc, 'Top Up')]"
    )
    BTN_CLOSE_MODAL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Close') or contains(@content-desc, 'Tutup') or "
        "contains(@content-desc, 'Batal') or contains(@text, 'Batal')]"
    )

    # ==========================================================================
    # 3. BILAH PENCARIAN DESTINASI & QUICK DESTINATION CHIPS
    # ==========================================================================
    SEARCH_DESTINATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'where are you going') or contains(@content-desc, 'Mau ke mana') or "
        "contains(@content-desc, 'Cari tujuan') or contains(@text, 'where are you going')]"
    )
    INPUT_SEARCH_FIELD = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'tujuan') or contains(@hint, 'going') or "
        "contains(@hint, 'Cari') or @class='android.widget.EditText']"
    )
    DESTINATION_COFFEE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tempat ngopi') or contains(@content-desc, 'Coffee') or "
        "contains(@text, 'Tempat ngopi')]"
    )
    DESTINATION_OFFICE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Kantor') or contains(@content-desc, 'Office') or "
        "contains(@text, 'Kantor')]"
    )
    DESTINATION_HOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rumah') or contains(@content-desc, 'Home') or "
        "contains(@text, 'Rumah')]"
    )
    BTN_ADD_FAVORITE_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tambah') or contains(@content-desc, 'Add')]"
    )
    SEARCH_RESULT_ITEM_FIRST = (
        AppiumBy.XPATH,
        "(//*[contains(@resource-id, 'list_item') or contains(@class, 'ViewGroup') or "
        "contains(@content-desc, 'Jl.') or contains(@text, 'Jl.')])[1]"
    )
    SEARCH_RESULT_EMPTY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'tidak ditemukan') or contains(@content-desc, 'Not found') or "
        "contains(@content-desc, 'Tidak ada hasil')]"
    )

    # ==========================================================================
    # 4. GRID LAYANAN UTAMA EVMOTO (SERVICE GRID)
    # ==========================================================================
    SERVICE_EVRIDE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRide') or contains(@content-desc, 'Ride') or "
        "contains(@text, 'EvRide')]"
    )
    SERVICE_EVSEND = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvSend') or contains(@content-desc, 'Send') or "
        "contains(@content-desc, 'Paket') or contains(@text, 'EvSend')]"
    )
    SERVICE_EVRENT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRent') or contains(@content-desc, 'Rent') or "
        "contains(@content-desc, 'Sewa') or contains(@content-desc, 'Battery') or "
        "contains(@text, 'EvRent')]"
    )
    SERVICE_MORE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lainnya') or contains(@content-desc, 'More') or "
        "contains(@text, 'Lainnya')]"
    )
    SCREEN_BOOKING_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRide') or contains(@content-desc, 'Pesan') or "
        "contains(@content-desc, 'Tarif') or contains(@content-desc, 'Pilih Tujuan')]"
    )
    SCREEN_REVIEW_PLACING_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Review') or contains(@content-desc, 'Ringkasan') or "
        "contains(@content-desc, 'Estimasi') or contains(@content-desc, 'Detail Pemesanan') or "
        "contains(@content-desc, 'Pesan EvRide') or contains(@text, 'Pesan EvRide')]"
    )
    TEXT_ESTIMATED_FARE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    TEXT_PICKUP_SUMMARY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Jemput') or contains(@hint, 'Jemput') or contains(@content-desc, 'Pickup')]"
    )
    TEXT_DESTINATION_SUMMARY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tujuan') or contains(@hint, 'Tujuan') or contains(@content-desc, 'Destination')]"
    )
    BTN_PAYMENT_OPTION_SUMMARY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tunai') or contains(@content-desc, 'Cash') or "
        "contains(@content-desc, 'Dompet') or contains(@content-desc, 'Metode')]"
    )

    # ==========================================================================
    # 5. CAROUSEL / SLIDER PROMO & BANNER EDUKASI HIJAU
    # ==========================================================================
    BANNER_PROMO_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'banner') or contains(@resource-id, 'promo') or "
        "contains(@content-desc, 'Promo') or contains(@content-desc, 'Diskon') or "
        "contains(@content-desc, 'Cashback') or contains(@content-desc, 'Green')]"
    )
    BANNER_PROMO_FIRST = (
        AppiumBy.XPATH,
        "(//*[contains(@content-desc, 'Promo') or contains(@content-desc, 'Diskon') or "
        "contains(@content-desc, 'Cashback') or contains(@content-desc, 'EvMoto')])[1]"
    )
    BTN_VIEW_ALL_PROMOS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Lihat Semua') or contains(@content-desc, 'View All') or "
        "contains(@content-desc, 'Semua Promo')]"
    )
    MODAL_PROMO_DETAIL = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Syarat & Ketentuan Promo') or contains(@content-desc, 'Detail Promo') or "
        "contains(@content-desc, 'Gunakan Promo')]"
    )

    # ==========================================================================
    # 6. WIDGET AKTIVITAS TERKINI / LIVE TRIP STATUS
    # ==========================================================================
    WIDGET_RECENT_ACTIVITY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Aktivitas Terkini') or contains(@content-desc, 'Pesanan Aktif') or "
        "contains(@content-desc, 'Perjalanan Terakhir') or contains(@content-desc, 'Sedang Berlangsung')]"
    )
    TEXT_NO_ACTIVE_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Belum ada pesanan') or contains(@content-desc, 'No active order') or "
        "contains(@content-desc, 'Siap bepergian')]"
    )

    # ==========================================================================
    # 7. BILAH NAVIGASI BAWAH (BOTTOM NAVIGATION BAR)
    # ==========================================================================
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
    NAV_ME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Me') or contains(@content-desc, 'Akun') or "
        "contains(@content-desc, 'Profil') or contains(@text, 'Me') or contains(@text, 'Akun')]"
    )

    # ==========================================================================
    # 8. DIALOG, POPUP SAMBUTAN & EXIT CONFIRMATION
    # ==========================================================================
    BTN_CONTINUE_POPUP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Continue') or contains(@content-desc, 'Lanjut') or "
        "contains(@text, 'Continue') or contains(@text, 'Lanjut')]"
    )
    POPUP_LOCATION_DISABLED_WARNING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Aktifkan Lokasi') or contains(@content-desc, 'Enable Location') or "
        "contains(@content-desc, 'Izin lokasi')]"
    )
    DIALOG_EXIT_APP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Keluar dari aplikasi') or contains(@content-desc, 'Exit app') or "
        "contains(@content-desc, 'Apakah Anda yakin ingin keluar?')]"
    )
    BTN_CANCEL_EXIT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batal') or contains(@content-desc, 'Cancel') or "
        "contains(@text, 'Batal')]"
    )
    SNACKBAR_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'snackbar') or contains(@class, 'SnackBar') or "
        "contains(@content-desc, 'berhasil') or contains(@text, 'berhasil')]"
    )
    SCREEN_QRIS_SCANNER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'scanner') or contains(@resource-id, 'camera') or "
        "contains(@content-desc, 'Scan QRIS') or contains(@content-desc, 'Pindai') or "
        "contains(@content-desc, 'Bayar') or contains(@text, 'Scan QRIS')]"
    )
    BTN_CLOSE_SCANNER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tutup') or contains(@content-desc, 'Close') or "
        "contains(@content-desc, 'Back') or contains(@content-desc, 'Kembali')]"
    )
    SCREEN_WALLET_HISTORY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Riwayat Transaksi') or contains(@content-desc, 'Mutasi') or "
        "contains(@content-desc, 'Riwayat') or contains(@text, 'Riwayat Transaksi')]"
    )
    SCREEN_EVSEND_CONTAINER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvSend') or contains(@content-desc, 'Kirim Paket') or "
        "contains(@content-desc, 'Pengiriman') or contains(@content-desc, 'Detail Pengirim')]"
    )
    SCREEN_EVRENT_SWAP_STATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRent') or contains(@content-desc, 'Stasiun Baterai') or "
        "contains(@content-desc, 'Swap Station') or contains(@content-desc, 'Baterai')]"
    )
    LIST_RECENT_SEARCHES = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pencarian Terakhir') or contains(@content-desc, 'Riwayat Pencarian') or "
        "contains(@resource-id, 'recent_item') or contains(@class, 'recent')]"
    )
    BANNER_PEAK_HOUR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Jam Sibuk') or contains(@content-desc, 'Peak Hour') or "
        "contains(@content-desc, 'Lonjakan Tarif') or contains(@content-desc, 'Tarif disesuaikan')]"
    )
    WARNING_SAME_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'tidak boleh sama') or contains(@content-desc, 'cannot be the same') or "
        "contains(@content-desc, 'Pilih lokasi berbeda')]"
    )
    SNACKBAR_OFFLINE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'koneksi') or contains(@content-desc, 'internet') or "
        "contains(@text, 'koneksi') or contains(@content-desc, 'Coba Lagi')]"
    )
    BTN_RETRY_NETWORK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Coba Lagi') or contains(@text, 'Coba Lagi') or "
        "contains(@content-desc, 'Retry')]"
    )

    # ==========================================================================
    # ACTION METHODS
    # ==========================================================================

    def dismiss_welcome_popup_if_present(self):
        """Menutup dialog sambutan / modal 'Continue' jika ada."""
        try:
            buttons = self.find_all(self.BTN_CONTINUE_POPUP, timeout=3)
            if buttons:
                logger.info("Mendeteksi popup sambutan 'Continue', menutup popup...")
                buttons[0].click()
                time.sleep(1)
        except Exception:
            pass

    def is_home_screen_displayed(self, timeout: int = 15) -> bool:
        """Memeriksa apakah layar Beranda aktif dan elemen utama termuat."""
        self.dismiss_welcome_popup_if_present()
        return (
            self.is_displayed(self.SEARCH_DESTINATION, timeout=timeout) or
            self.is_displayed(self.NAV_HOME, timeout=timeout) or
            self.is_displayed(self.TEXT_GREETING_TITLE, timeout=timeout)
        )

    # 1. Header & Greeting
    def get_user_greeting_text(self) -> str:
        """Mengambil teks sapaan pengguna di header."""
        try:
            return self.get_text(self.TEXT_GREETING_TITLE)
        except Exception:
            return ""

    def get_current_pickup_location_text(self) -> str:
        """Mengambil teks alamat penjemputan saat ini."""
        try:
            return self.get_text(self.LOCATION_CURRENT_PIN)
        except Exception:
            return ""

    def is_notification_bell_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah ikon lonceng notifikasi tampil di header."""
        return self.is_displayed(self.BTN_NOTIFICATION_BELL, timeout=timeout)

    def open_notification_center(self):
        """Mengetuk ikon lonceng notifikasi untuk membuka pusat notifikasi."""
        self.click(self.BTN_NOTIFICATION_BELL, label="Ikon 'Notifikasi'")

    def is_notification_center_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah halaman atau daftar notifikasi terbuka."""
        return self.is_displayed(self.CONTAINER_NOTIFICATION_LIST, timeout=timeout)

    # 2. Saldo & Dompet
    def get_wallet_balance_text(self) -> str:
        """Mengambil teks saldo dompet pada kartu Beranda."""
        try:
            return self.get_text(self.TEXT_HOME_WALLET_BALANCE)
        except Exception:
            return ""

    def open_top_up_from_home(self):
        """Menekan tombol 'Top Up' dari kartu saldo beranda."""
        self.click(self.BTN_WALLET_TOP_UP, label="Tombol 'Top Up'")

    def is_top_up_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah modal pilihan isi saldo terbuka."""
        return self.is_displayed(self.MODAL_TOP_UP_CHOICE, timeout=timeout)

    def cancel_top_up_modal(self):
        """Menutup modal top up."""
        if self.is_displayed(self.BTN_CLOSE_MODAL, timeout=3):
            self.click(self.BTN_CLOSE_MODAL, label="Tombol 'Batal / Tutup Modal'")
        else:
            self.press_back_key()

    def open_wallet_pay_qr(self):
        """Menekan tombol Bayar / QRIS pada kartu saldo."""
        self.click(self.BTN_WALLET_PAY_QR, label="Tombol 'Bayar / QRIS'")

    def open_wallet_history(self):
        """Menekan tombol Riwayat Transaksi pada kartu saldo."""
        self.click(self.BTN_WALLET_HISTORY, label="Tombol 'Riwayat'")

    # 3. Pencarian Tujuan & Shortcut Destinasi
    def open_search_destination(self):
        """Mengetuk bar pencarian destinasi untuk membuka form input alamat."""
        self.click(self.SEARCH_DESTINATION, label="Bilah Pencarian 'where are you going'")

    def input_destination_search(self, destination: str):
        """Menginput kata kunci lokasi tujuan pada kolom pencarian."""
        try:
            self.type_text(self.INPUT_SEARCH_FIELD, destination, label=f"Cari Tujuan ({destination})")
        except Exception:
            try:
                self.driver.switch_to.active_element.send_keys(destination)
            except Exception:
                pass

    def select_quick_destination(self, chip_type: str = "coffee"):
        """Menekan salah satu shortcut chip destinasi ('coffee', 'office', 'home')."""
        if chip_type.lower() in ("coffee", "ngopi"):
            self.click(self.DESTINATION_COFFEE, label="Shortcut 'Tempat ngopi'")
        elif chip_type.lower() in ("office", "kantor"):
            self.click(self.DESTINATION_OFFICE, label="Shortcut 'Kantor'")
        else:
            self.click(self.DESTINATION_HOME, label="Shortcut 'Rumah'")

    def is_search_result_empty(self, timeout: int = 5) -> bool:
        """Memeriksa apakah pencarian menampilkan indikator 'tidak ditemukan'."""
        return self.is_displayed(self.SEARCH_RESULT_EMPTY, timeout=timeout)

    # 4. Layanan Utama EVMoto
    def click_service_evride(self):
        """Menekan tombol layanan 'EvRide'."""
        self.click(self.SERVICE_EVRIDE, label="Layanan 'EvRide'")

    def click_service_evsend(self):
        """Menekan tombol layanan 'EvSend'."""
        self.click(self.SERVICE_EVSEND, label="Layanan 'EvSend'")

    def click_service_evrent(self):
        """Menekan tombol layanan 'EvRent'."""
        self.click(self.SERVICE_EVRENT, label="Layanan 'EvRent'")

    def is_booking_screen_displayed(self, timeout: int = 10) -> bool:
        """Memeriksa apakah navigasi berhasil masuk ke layar booking/pemesanan rute."""
        return self.is_displayed(self.SCREEN_BOOKING_CONTAINER, timeout=timeout)

    def is_review_placing_order_displayed(self, timeout: int = 8) -> bool:
        """
        Memverifikasi bahwa layar peninjauan pesanan (Review Placing Order) termuat.
        Menampilkan estimasi tarif, rute penjemputan & tujuan, serta metode pembayaran.
        PENTING: Tahap ini HANYA meninjau rincian pemesanan dan TIDAK mengeksekusi placing order.
        """
        return (
            self.is_displayed(self.SCREEN_REVIEW_PLACING_ORDER, timeout=timeout) or
            self.is_displayed(self.TEXT_ESTIMATED_FARE, timeout=timeout) or
            self.is_displayed(self.SCREEN_BOOKING_CONTAINER, timeout=timeout)
        )

    def cancel_review_placing_order(self):
        """
        Membatalkan alur pemesanan dari layar Review Placing Order dan kembali ke Beranda utama.
        Menjamin pesanan TIDAK dieksekusi (Exclude Placing Order).
        """
        logger.info("[EXCLUDE PLACING ORDER] Membatalkan layar review pemesanan, kembali ke Beranda...")
        self.press_back_key()
        time.sleep(1)

    # 5. Promo Carousel
    def is_promo_banner_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah carousel promo tampil di layar beranda."""
        return self.is_displayed(self.BANNER_PROMO_CONTAINER, timeout=timeout) or self.is_displayed(self.BANNER_PROMO_FIRST, timeout=timeout)

    def swipe_promo_banner_next(self):
        """Melakukan gestur swipe horizontal untuk menggeser banner promo berikutnya."""
        try:
            size = self.driver.get_window_size()
            start_x = int(size['width'] * 0.85)
            end_x = int(size['width'] * 0.15)
            y = int(size['height'] * 0.65)
            self.driver.swipe(start_x, y, end_x, y, 600)
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Gagal melakukan swipe banner promo: {e}")

    def click_first_promo_banner(self):
        """Menekan banner promo pertama untuk membuka detail promosi."""
        self.click(self.BANNER_PROMO_FIRST, label="Banner Promo Pertama")

    def is_promo_modal_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah dialog detail promo muncul."""
        return self.is_displayed(self.MODAL_PROMO_DETAIL, timeout=timeout)

    def close_promo_modal(self):
        """Menutup dialog detail promo."""
        if self.is_displayed(self.BTN_CLOSE_MODAL, timeout=3):
            self.click(self.BTN_CLOSE_MODAL, label="Tutup Detail Promo")
        else:
            self.press_back_key()

    # 6. Widget Aktivitas Terkini
    def is_recent_activity_widget_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah widget aktivitas terkini / pesanan aktif tampil."""
        return self.is_displayed(self.WIDGET_RECENT_ACTIVITY, timeout=timeout) or self.is_displayed(self.TEXT_NO_ACTIVE_ORDER, timeout=timeout)

    # 7. Bottom Navigation Bar
    def navigate_to_home(self):
        """Menekan tab navigasi 'Home' / 'Beranda'."""
        self.click(self.NAV_HOME, label="Tab Navigasi 'Home'")

    def navigate_to_activity(self):
        """Menekan tab navigasi 'Activity' / 'Aktivitas'."""
        self.dismiss_welcome_popup_if_present()
        self.click(self.NAV_ACTIVITY, label="Tab Navigasi 'Activity'")

    def navigate_to_profile(self):
        """Menekan tab navigasi 'Me' / 'Akun' untuk membuka Halaman Profil."""
        self.dismiss_welcome_popup_if_present()
        self.click(self.NAV_ME, label="Tab Navigasi 'Me / Profil'")

    # 8. Gestur & Ketahanan (Resilience)
    def pull_to_refresh_home(self):
        """Melakukan gestur pull-to-refresh (tarik ke bawah) untuk memuat ulang data beranda."""
        logger.info("Menjalankan gestur pull-to-refresh pada Beranda...")
        try:
            size = self.driver.get_window_size()
            center_x = int(size['width'] * 0.5)
            start_y = int(size['height'] * 0.25)
            end_y = int(size['height'] * 0.70)
            self.driver.swipe(center_x, start_y, center_x, end_y, 800)
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Gagal melakukan pull-to-refresh: {e}")

    def press_back_key(self):
        """Menekan tombol Android Hardware Back Key (Keycode 4)."""
        logger.info("Menekan Android Hardware Back Key (Keycode 4)")
        try:
            self.driver.press_keycode(4)
        except Exception as e:
            logger.warning(f"Gagal menekan hardware back key: {e}")
        time.sleep(1)

    def is_exit_confirmation_dialog_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah dialog konfirmasi keluar aplikasi muncul."""
        return self.is_displayed(self.DIALOG_EXIT_APP, timeout=timeout)

    def cancel_exit_confirmation(self):
        """Membatalkan keluar aplikasi."""
        if self.is_displayed(self.BTN_CANCEL_EXIT, timeout=3):
            self.click(self.BTN_CANCEL_EXIT, label="Tombol 'Batal Keluar'")
        else:
            self.press_back_key()

    # 9. Extended Action Methods (QRIS, EvSend, EvRent, Recent Searches, Network Resilience)
    def is_qris_scanner_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah layar pemindai QRIS bayar terbuka."""
        return self.is_displayed(self.SCREEN_QRIS_SCANNER, timeout=timeout)

    def close_qris_scanner(self):
        """Menutup layar scanner QRIS dan kembali ke Beranda."""
        if self.is_displayed(self.BTN_CLOSE_SCANNER, timeout=3):
            self.click(self.BTN_CLOSE_SCANNER, label="Tombol 'Tutup Scanner'")
        else:
            self.press_back_key()

    def is_wallet_history_screen_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah layar riwayat transaksi dompet termuat."""
        return self.is_displayed(self.SCREEN_WALLET_HISTORY, timeout=timeout)

    def is_evsend_screen_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah layar layanan EvSend terbuka."""
        return self.is_displayed(self.SCREEN_EVSEND_CONTAINER, timeout=timeout)

    def is_evrent_swap_station_screen_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah layar layanan EvRent / Stasiun Baterai terbuka."""
        return self.is_displayed(self.SCREEN_EVRENT_SWAP_STATION, timeout=timeout)

    def is_recent_search_history_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah daftar riwayat pencarian terkini muncul."""
        return self.is_displayed(self.LIST_RECENT_SEARCHES, timeout=timeout)

    def is_peak_hour_banner_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah informasi lonjakan tarif jam sibuk tertera."""
        return self.is_displayed(self.BANNER_PEAK_HOUR, timeout=timeout)

    def is_same_location_warning_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa validasi error saat titik jemput dan titik tujuan sama."""
        return self.is_displayed(self.WARNING_SAME_LOCATION, timeout=timeout)

    def is_offline_snackbar_displayed(self, timeout: int = 5) -> bool:
        """Memeriksa apakah snackbar ketiadaan koneksi internet muncul."""
        return self.is_displayed(self.SNACKBAR_OFFLINE, timeout=timeout)

    def click_retry_network(self):
        """Mengetuk tombol Coba Lagi pada snackbar offline."""
        if self.is_displayed(self.BTN_RETRY_NETWORK, timeout=3):
            self.click(self.BTN_RETRY_NETWORK, label="Tombol 'Coba Lagi'")

    def background_and_resume_app(self, seconds: int = 3):
        """Memindahkan aplikasi ke background selama N detik lalu me-resume ke foreground."""
        logger.info(f"Memindahkan aplikasi ke background selama {seconds} detik...")
        try:
            self.driver.background_app(seconds)
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Fallback background_app: {e}")


# Backward compatibility alias
HomeLocators = HomePage



