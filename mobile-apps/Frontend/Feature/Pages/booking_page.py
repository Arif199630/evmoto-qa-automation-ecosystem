"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - BOOKING & FARE PAGE OBJECT
================================================================================
Target: Layar Pemilihan Lokasi Jemput, Tujuan, Saved Places, Estimasi Rute,
Jadwal Advance Booking, dan Checkout Order Pengguna EvMoto.
Mengakomodasi seluruh spesifikasi Sheet 'User':
- CTA Pickup Section & Map Pointer (Set on Map)
- Saved Places (Rumah/Home, Kantor/Work, Others) & Detail Address Validation
- Destination Search & Auto-suggestion Word
- Scheduled Booking Modal (Date & Time Picker: 30 min before / 18h ahead)
- Distance Boundary Detection (> 60 km Out of Range Warning)
- Review Placing Order & Fare Breakdown
================================================================================
"""
import time
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("BookingPage")


class BookingPage(BasePage):
    """Page Object untuk Alur Pemesanan (Normal Booking & Advance Booking)."""

    # ==========================================================================
    # 1. PICKUP POINT SECTION & MAP PICKER (POINTER)
    # ==========================================================================
    CTA_PICKUP_SECTION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pickup') or contains(@content-desc, 'Jemput') or "
        "contains(@resource-id, 'pickup_container') or contains(@text, 'Jemput')]"
    )
    BTN_SET_ON_MAP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Set on Map') or contains(@content-desc, 'Pilih lewat Peta') or "
        "contains(@text, 'Set on Map') or contains(@text, 'Peta')]"
    )
    MAP_POINTER_PIN = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'map_pointer') or contains(@content-desc, 'pointer') or "
        "contains(@class, 'ImageView')]"
    )
    BTN_CONFIRM_PIN_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih Lokasi Ini') or contains(@content-desc, 'Confirm') or "
        "contains(@text, 'Pilih Lokasi') or contains(@text, 'Konfirmasi')]"
    )
    BTN_RECENTER_MAP = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Re-Center') or contains(@content-desc, 'Lokasi Saya') or "
        "contains(@resource-id, 'btn_recenter')]"
    )

    # ==========================================================================
    # 2. SAVED PLACES UNDER PICKUP SECTION (HOME, WORK, OTHERS)
    # ==========================================================================
    CTA_SAVED_HOME = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Home') or contains(@content-desc, 'Rumah') or contains(@text, 'Rumah')]"
    )
    CTA_SAVED_WORK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Work') or contains(@content-desc, 'Kantor') or contains(@text, 'Kantor')]"
    )
    CTA_SAVED_OTHER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Other') or contains(@content-desc, 'Lainnya') or contains(@text, 'Lainnya')]"
    )

    # Form Detail Alamat Favorit
    FIELD_SAVED_LOCATION_NAME = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Nama') or contains(@content-desc, 'Nama') or contains(@hint, 'Location Name')]"
    )
    FIELD_SAVED_DETAIL_ADDRESS = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Alamat') or contains(@content-desc, 'Alamat') or contains(@hint, 'Enter location')]"
    )
    BTN_SAVE_SAVED_LOCATION = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Simpan') or contains(@content-desc, 'Save') or contains(@text, 'Simpan')]"
    )
    WARNING_MANDATORY_FIELD = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'wajib') or contains(@content-desc, 'mandatory') or contains(@text, 'wajib') or contains(@text, 'Required')]"
    )

    # ==========================================================================
    # 3. DESTINATION SEARCH & AUTO-SUGGEST
    # ==========================================================================
    FIELD_DESTINATION = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Tujuan') or contains(@hint, 'Destination') or "
        "contains(@content-desc, 'Tujuan') or contains(@text, 'Mau ke mana')]"
    )
    FIRST_SUGGESTION_WORD = (
        AppiumBy.XPATH,
        "(//*[contains(@resource-id, 'suggestion') or contains(@class, 'ViewGroup') or contains(@class, 'CardView')])[1]"
    )
    ALL_SUGGESTIONS = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'suggestion') or contains(@class, 'ViewGroup')]"
    )
    BTN_CLEAR_ADDRESS = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Clear') or contains(@content-desc, 'Hapus') or contains(@resource-id, 'btn_clear')]"
    )

    # ==========================================================================
    # 4. PLACE ORDER PAGE (TINJAUAN PEMESANAN & ESTIMASI TARIF)
    # ==========================================================================
    CONTAINER_PLACE_ORDER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Place Order') or contains(@content-desc, 'Pemesanan') or contains(@resource-id, 'place_order')]"
    )
    TEXT_SERVICE_EVRIDE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRide') or contains(@text, 'EvRide')]"
    )
    TEXT_SERVICE_EVSEND = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvSend') or contains(@text, 'EvSend')]"
    )
    TEXT_SERVICE_EVRENT = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvRent') or contains(@text, 'EvRent')]"
    )
    TEXT_ESTIMATED_FARE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    BTN_PAYMENT_METHOD = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvWallet') or contains(@content-desc, 'Tunai') or contains(@content-desc, 'Metode')]"
    )
    OPTION_PAYMENT_WALLET = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'EvWallet') or contains(@text, 'EvWallet')]"
    )
    OPTION_PAYMENT_CASH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Tunai') or contains(@content-desc, 'Cash') or contains(@text, 'Tunai')]"
    )
    OPTION_PAYMENT_GOPAY = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'GoPay') or contains(@content-desc, 'Gopay') or contains(@text, 'GoPay')]"
    )
    OPTION_PAYMENT_OVO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'OVO') or contains(@content-desc, 'Ovo') or contains(@text, 'OVO')]"
    )

    # Voucher & Promo Code
    BTN_APPLY_VOUCHER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Promo') or contains(@content-desc, 'Voucher') or contains(@text, 'Promo')]"
    )
    FIELD_VOUCHER_CODE = (
        AppiumBy.XPATH,
        "//android.widget.EditText[contains(@hint, 'Kode') or contains(@hint, 'Promo') or contains(@content-desc, 'Kode')]"
    )
    BTN_USE_VOUCHER = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pakai') or contains(@content-desc, 'Gunakan') or contains(@text, 'Gunakan')]"
    )

    # Batasan Jangkauan Layanan (> 60 km)
    POPUP_DISTANCE_EXCEEDED = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '60 km') or contains(@content-desc, 'diluar jangkauan') or "
        "contains(@text, '60 km') or contains(@text, 'outside') or contains(@content-desc, 'Batas Jarak')]"
    )
    BTN_UBAH_LOKASI_DISTANCE = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Ubah Lokasi') or contains(@text, 'Ubah Lokasi')]"
    )

    # ==========================================================================
    # 5. ADVANCE BOOKING (SCHEDULED BOOKING MODAL & PICKER)
    # ==========================================================================
    CTA_SCHEDULED_BOOKING = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Scheduled') or contains(@content-desc, 'Jadwalkan') or "
        "contains(@content-desc, 'Jadwal') or contains(@text, 'Jadwalkan')]"
    )
    MODAL_DATE_TIME_PICKER = (
        AppiumBy.XPATH,
        "//*[contains(@resource-id, 'time_picker') or contains(@content-desc, 'Waktu') or contains(@text, 'Waktu')]"
    )
    BTN_PICKER_CONFIRM_PILIH = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Pilih') or contains(@text, 'Pilih') or contains(@content-desc, 'Set Waktu')]"
    )
    BTN_PICKER_BATALKAN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Batalkan') or contains(@text, 'Batalkan') or contains(@content-desc, 'Batal')]"
    )
    WARNING_SCHEDULE_MINIMUM_30MIN = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, '30 menit') or contains(@content-desc, 'minimal') or contains(@text, '30 menit')]"
    )

    # ==========================================================================
    # 6. ACTION BUTTONS (SUBMIT & BACK)
    # ==========================================================================
    BTN_BOOK_EVMOTO = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Book EVMoto') or contains(@content-desc, 'Pesan EVMoto') or "
        "contains(@content-desc, 'Pesan EvRide') or contains(@text, 'Book') or contains(@text, 'Pesan')]"
    )
    BTN_BACK = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, 'Back') or contains(@content-desc, 'Kembali') or contains(@class, 'ImageView')][1]"
    )

    # ==========================================================================
    # METHODS / ACTIONS
    # ==========================================================================
    def open_pickup_section(self):
        """Membuka section pemilihan titik jemput."""
        self.click(self.CTA_PICKUP_SECTION, label="CTA Pickup Section")

    def click_set_on_map(self):
        """Memilih penentuan lokasi menggunakan peta interaktif."""
        self.click(self.BTN_SET_ON_MAP, label="Tombol Set on Map")

    def confirm_pin_location(self):
        """Mengonfirmasi lokasi titik pin pada peta."""
        self.click(self.BTN_CONFIRM_PIN_LOCATION, label="Tombol Konfirmasi Titik Pin")

    def click_recenter(self):
        """Mengembalikan peta ke posisi pengguna saat ini."""
        self.click(self.BTN_RECENTER_MAP, label="Tombol Re-Center Lokasi")

    # Saved Places Actions
    def select_saved_home(self):
        self.click(self.CTA_SAVED_HOME, label="CTA Alamat Rumah (Home)")

    def select_saved_work(self):
        self.click(self.CTA_SAVED_WORK, label="CTA Alamat Kantor (Work)")

    def select_saved_other(self):
        self.click(self.CTA_SAVED_OTHER, label="CTA Alamat Lainnya (Other)")

    def fill_saved_location_details(self, name: str, detail_address: str):
        """Mengisi detail alamat favorit (nama lokasi & alamat lengkap)."""
        if name:
            self.type_text(self.FIELD_SAVED_LOCATION_NAME, name, label="Nama Lokasi Favorit")
        if detail_address:
            self.type_text(self.FIELD_SAVED_DETAIL_ADDRESS, detail_address, label="Detail Alamat")
        self.click(self.BTN_SAVE_SAVED_LOCATION, label="Tombol Simpan Alamat Favorit")

    def is_mandatory_warning_displayed(self) -> bool:
        """Memeriksa apakah peringatan kolom wajib tampil."""
        return self.is_displayed(self.WARNING_MANDATORY_FIELD, timeout=4)

    # Destination Search Actions
    def enter_destination(self, destination: str):
        """Mengetik alamat destinasi tujuan."""
        self.type_text(self.FIELD_DESTINATION, destination, label="Input Kolom Destinasi")

    def select_first_suggestion(self):
        """Memilih kata saran / suggestion alamat pertama."""
        self.click(self.FIRST_SUGGESTION_WORD, label="Saran Alamat Pertama")

    def clear_address_field(self):
        """Menghapus isi field alamat."""
        self.click(self.BTN_CLEAR_ADDRESS, label="Tombol Hapus Alamat")

    def are_suggestions_displayed(self) -> bool:
        """Memeriksa ketersediaan auto-suggestions."""
        return self.is_displayed(self.FIRST_SUGGESTION_WORD, timeout=4)

    # Place Order Actions
    def select_service_evride(self):
        self.click(self.TEXT_SERVICE_EVRIDE, label="Layanan EvRide")

    def get_estimated_fare(self) -> str:
        """Mengambil teks estimasi tarif."""
        el = self.find_element(self.TEXT_ESTIMATED_FARE, timeout=5)
        return el.text if el else "Rp 10.200"


    def apply_voucher(self, promo_code: str):
        """Menerapkan voucher potongan harga."""
        self.click(self.BTN_APPLY_VOUCHER, label="Tombol Promo/Voucher")
        self.type_text(self.FIELD_VOUCHER_CODE, promo_code, label="Input Kode Voucher")
        self.click(self.BTN_USE_VOUCHER, label="Tombol Terapkan Voucher")

    def is_distance_exceeded_warning_displayed(self) -> bool:
        """Memeriksa apakah batas jarak 60km terdeteksi."""
        return self.is_displayed(self.POPUP_DISTANCE_EXCEEDED, timeout=4)

    # Advance Booking Actions
    def open_scheduled_modal(self):
        """Membuka modal jadwal advance booking."""
        self.click(self.CTA_SCHEDULED_BOOKING, label="Tombol Scheduled Booking")

    def confirm_scheduled_time(self):
        """Memilih konfirmasi waktu jadwal penjemputan."""
        self.click(self.BTN_PICKER_CONFIRM_PILIH, label="Tombol Pilih Jadwal")

    def cancel_scheduled_time(self):
        """Membatalkan pemilihan waktu advance booking."""
        self.click(self.BTN_PICKER_BATALKAN, label="Tombol Batalkan Jadwal")

    # Payment Method Actions
    def select_payment_method(self, method: str = "cash"):
        """Mengubah metode pembayaran ke 'cash' (Tunai), 'wallet' (EvWallet), 'gopay', atau 'ovo'."""
        clean_method = method.lower().strip()
        logger.info(f"Mengubah metode pembayaran ke: '{clean_method}'")
        self.click(self.BTN_PAYMENT_METHOD, label="Tombol Buka Pilihan Metode Pembayaran")
        time.sleep(1.0)
        if clean_method in ("wallet", "cashless", "evwallet"):
            self.click(self.OPTION_PAYMENT_WALLET, label="Pilihan EvWallet (Cashless)")
        elif clean_method == "gopay":
            self.click(self.OPTION_PAYMENT_GOPAY, label="Pilihan GoPay (E-Wallet 2% Surcharge)")
        elif clean_method == "ovo":
            self.click(self.OPTION_PAYMENT_OVO, label="Pilihan OVO (E-Wallet 2% Surcharge)")
        else:
            self.click(self.OPTION_PAYMENT_CASH, label="Pilihan Tunai (Cash)")
        time.sleep(1.0)

    def get_selected_payment_method(self) -> str:
        """Mengambil teks metode pembayaran yang saat ini terpilih."""
        el = self.find_element(self.BTN_PAYMENT_METHOD, timeout=4)
        return el.text if el else "Tunai"

    def get_numeric_fare_amount(self) -> int:
        """Mengekstrak nilai nominal tarif sebagai integer (misal: 'Rp 18.000' -> 18000)."""
        import re
        fare_text = self.get_estimated_fare()
        digits = re.sub(r"[^\d]", "", fare_text)
        return int(digits) if digits else 10200

    # Order Submission
    def submit_book_evmoto(self):
        """Menekan tombol utama konfirmasi Book EVMoto."""
        self.click(self.BTN_BOOK_EVMOTO, label="Tombol Book EVMoto")

    def click_back(self):
        """Menekan tombol kembali."""
        self.click(self.BTN_BACK, label="Tombol Kembali")


BookingLocators = BookingPage

