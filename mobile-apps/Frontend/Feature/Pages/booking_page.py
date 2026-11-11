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
import re
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from core.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("BookingPage")


def _exact(*labels: str) -> str:
    """XPath yang cocok PERSIS dengan salah satu label (content-desc atau text).

    Teks label diambil dari file bahasa aplikasi User (assets/jsons/user_lang_id.json
    di APK evmoto-user-1.2.33). Sengaja tidak memakai contains() agar kata pendek
    tidak ikut cocok dengan label lain.
    """
    kondisi = " or ".join(f"@content-desc='{label}' or @text='{label}'" for label in labels)
    return f"//*[{kondisi}]"


def _contains_phrase(*phrases: str) -> str:
    """XPath contains() khusus untuk KALIMAT panjang yang unik (bukan kata pendek).

    Dipakai untuk teks dialog/snackbar yang bisa tergabung dengan deskripsi di
    satu node semantics Flutter, sehingga pencocokan persis berisiko gagal.
    """
    kondisi = " or ".join(
        f"contains(@content-desc, '{phrase}') or contains(@text, '{phrase}')" for phrase in phrases
    )
    return f"//*[{kondisi}]"


# Pola jam (08:30 / 08.30) untuk membaca waktu jadwal yang tampil di layar Place Order.
_TIME_PATTERN = re.compile(r"(?<!\d)([01]?\d|2[0-3])[:.]([0-5]\d)(?!\d)")


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
        "//*[@content-desc='Pilih Lewat Peta' or @text='Pilih Lewat Peta' or "
        "contains(@content-desc, 'Set on Map') or contains(@content-desc, 'Pilih lewat Peta') or "
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
        "//android.widget.EditText[@text='Titik tujuan' or @text='Masukkan tujuan' or "
        "contains(@hint, 'Tujuan') or contains(@hint, 'Destination') or "
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
        "//*[@content-desc='Saldo EVMoto' or @text='Saldo EVMoto' or @content-desc='Dompet EVMoto' or "
        "@text='Dompet EVMoto' or contains(@content-desc, 'EvWallet') or contains(@text, 'EvWallet')]"
    )
    OPTION_PAYMENT_CASH = (
        AppiumBy.XPATH,
        "//*[@content-desc='Cash' or @text='Cash' or "
        "contains(@content-desc, 'Tunai') or contains(@content-desc, 'Cash') or contains(@text, 'Tunai')]"
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
    # 7. LOCATOR VERIFIKASI HASIL (TEKS NYATA DARI user_lang_id.json APK v1.2.33)
    # ==========================================================================
    # Ajakan pencarian tujuan di Beranda (home_ride_ready_to_go_hint / hello_where_today)
    TEXT_HOME_DESTINATION_PROMPT = (
        AppiumBy.XPATH,
        _exact("Hai, mau ke mana hari ini?", "Hello, mau kemana hari ini?", "Siap jalan? tentukan tujuanmu")
    )
    # Dialog izin lokasi (location_access_consent / enable_location)
    DIALOG_LOCATION_PERMISSION = (AppiumBy.XPATH, _exact("Izin lokasi", "Aktifkan lokasi"))
    # Snackbar simpan alamat favorit (successfully_saved_address / snackbar_address_edit_success)
    SNACKBAR_ADDRESS_SAVED = (AppiumBy.XPATH, _exact("Alamat berhasil disimpan"))
    # Tombol simpan pada form alamat favorit (save_address)
    BTN_SAVE_ADDRESS_EXACT = (AppiumBy.XPATH, _exact("Simpan alamat"))
    # Kolom input yang sudah terisi nilai (bukan placeholder). showing-hint='false' = berisi teks asli.
    FIELD_INPUT_PREFILLED = (
        AppiumBy.XPATH,
        "//android.widget.EditText[@showing-hint='false' and string-length(@text) > 0]"
    )
    # Layar pilih lokasi lewat peta (map_select_button / map_select_pickup / map_select_destination)
    BTN_MAP_SELECT_LOCATION = (AppiumBy.XPATH, _exact("Pilih Lokasi"))
    # Tombol utama layar Place Order (order_ev_moto)
    BTN_PESAN_EVMOTO_EXACT = (AppiumBy.XPATH, _exact("Pesan EVMoto"))
    # Tombol jadwal pada Place Order (advance_booking_button)
    BTN_JADWALKAN_EXACT = (AppiumBy.XPATH, _exact("Jadwalkan"))
    # Semua elemen yang mungkin memuat jam (pemisah ':' atau '.')
    ANY_TEXT_WITH_TIME_SEPARATOR = (
        AppiumBy.XPATH,
        "//*[contains(@content-desc, ':') or contains(@text, ':') or "
        "contains(@content-desc, '.') or contains(@text, '.')]"
    )
    # Dialog sukses pesanan terjadwal (advanced_booking_created_title / _button)
    DIALOG_SCHEDULED_CREATED = (AppiumBy.XPATH, _contains_phrase("Pesan Terjadwal Berhasil Dibuat"))
    BTN_SCHEDULED_CREATED_CONTINUE = (AppiumBy.XPATH, _exact("Lanjutkan"))
    # Status kartu pesanan terjadwal di Aktivitas (advanced_booking_status_order_scheduled)
    TEXT_SCHEDULED_ORDER_STATUS = (AppiumBy.XPATH, _exact("Pesanan Terjadwal"))
    # Judul detail pesanan terjadwal (advance_booking_detail_title)
    TEXT_SCHEDULED_DETAIL_TITLE = (AppiumBy.XPATH, _exact("Detail Jadwal Pemesanan"))
    # Snackbar pemilihan metode bayar (ride_checkout_select_payment_method_*_select_success)
    SNACKBAR_PAYMENT_CASH_SELECTED = (
        AppiumBy.XPATH,
        _contains_phrase("Pembayaran cash berhasil dipilih sebagai metode pembayaran")
    )
    SNACKBAR_PAYMENT_WALLET_SELECTED = (
        AppiumBy.XPATH,
        _contains_phrase("Dompet EVMoto berhasil dipilih sebagai metode pembayaran")
    )
    # Snackbar promo diterapkan (snackbar_coupon_select_success)
    SNACKBAR_PROMO_APPLIED = (AppiumBy.XPATH, _contains_phrase("Promo berhasil diterapkan ke pesanan Anda"))
    # Dialog saldo kurang (order_checkout_insufficient_balance_title / _button)
    DIALOG_INSUFFICIENT_BALANCE = (AppiumBy.XPATH, _exact("Saldo Anda Tidak Cukup"))
    BTN_OTHER_PAYMENT_METHOD = (AppiumBy.XPATH, _exact("Pilih Metode Pembayaran Lain"))
    # Label saldo di kartu dompet Beranda (home_ewallet_amount / my_balance)
    TEXT_HOME_BALANCE_AMOUNT = (
        AppiumBy.XPATH,
        "//*[@content-desc='Saldo Anda' or @text='Saldo Anda' or @content-desc='Saldo Kamu' or "
        "@text='Saldo Kamu']/following::*[contains(@content-desc, 'Rp') or contains(@text, 'Rp')][1]"
    )
    # Validasi titik jemput = tujuan (pickup_dropoff_same_location / same_location)
    WARNING_SAME_LOCATION_EXACT = (
        AppiumBy.XPATH,
        _exact("Titik penjemputan dan tujuan tidak boleh sama", "Titik jemput dan tujuan sama")
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
        """Mengambil teks estimasi tarif. String kosong bila tidak tampil (tidak ada angka cadangan).

        Flutter menaruh teks di atribut content-desc, jadi content-desc dibaca dulu lalu text.
        """
        el = self.find_element(self.TEXT_ESTIMATED_FARE, timeout=5)
        if not el:
            return ""
        return el.get_attribute("content-desc") or el.get_attribute("text") or ""


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
        """Mengambil teks metode pembayaran yang saat ini terpilih.

        Mengembalikan string kosong bila tombol metode bayar tidak terbaca
        (tanpa nilai cadangan palsu seperti 'Tunai'/'OVO').
        """
        try:
            el = self.find(self.BTN_PAYMENT_METHOD, timeout=4)
        except Exception:
            return ""
        return el.get_attribute("content-desc") or el.get_attribute("text") or ""

    def get_numeric_fare_amount(self) -> int:
        """Mengekstrak nilai nominal tarif sebagai integer (misal: 'Rp 18.000' -> 18000).

        Mengembalikan 0 bila tarif tidak terbaca (tanpa angka cadangan), supaya test
        yang memakainya bisa mendeteksi kegagalan membaca tarif dari layar.
        """
        fare_text = self.get_estimated_fare()
        digits = re.sub(r"[^\d]", "", fare_text)
        return int(digits) if digits else 0

    # Order Submission
    def submit_book_evmoto(self):
        """Menekan tombol utama konfirmasi Book EVMoto."""
        self.click(self.BTN_BOOK_EVMOTO, label="Tombol Book EVMoto")

    def click_back(self):
        """Menekan tombol kembali."""
        self.click(self.BTN_BACK, label="Tombol Kembali")

    # ==========================================================================
    # METHOD VERIFIKASI HASIL (dipakai assertion test booking)
    # ==========================================================================
    def wait_until_gone(self, locator, timeout: int = 8) -> bool:
        """True bila elemen hilang/tidak terlihat dalam batas waktu (untuk cek dialog tertutup)."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def is_home_destination_prompt_displayed(self, timeout: int = 10) -> bool:
        """Beranda aktif: ajakan 'Hai, mau ke mana hari ini?' tampil."""
        return self.is_displayed(self.TEXT_HOME_DESTINATION_PROMPT, timeout=timeout)

    def is_location_permission_dialog_displayed(self, timeout: int = 3) -> bool:
        """Dialog 'Izin lokasi' / 'Aktifkan lokasi' tampil (lokasi pengguna belum tersedia)."""
        return self.is_displayed(self.DIALOG_LOCATION_PERMISSION, timeout=timeout)

    def is_address_saved_snackbar_displayed(self, timeout: int = 8) -> bool:
        """Snackbar 'Alamat berhasil disimpan' tampil setelah menyimpan alamat favorit."""
        return self.is_displayed(self.SNACKBAR_ADDRESS_SAVED, timeout=timeout)

    def is_saved_location_form_displayed(self, timeout: int = 3) -> bool:
        """Form alamat favorit (kolom nama lokasi / tombol 'Simpan alamat') masih tampil."""
        return (
            self.is_displayed(self.BTN_SAVE_ADDRESS_EXACT, timeout=timeout)
            or self.is_displayed(self.FIELD_SAVED_LOCATION_NAME, timeout=1)
        )

    def is_destination_field_displayed(self, timeout: int = 8) -> bool:
        """Kolom input tujuan ('Titik tujuan' / 'Masukkan tujuan') tampil."""
        return self.is_displayed(self.FIELD_DESTINATION, timeout=timeout)

    def get_prefilled_input_texts(self, timeout: int = 8) -> list:
        """Isi semua kolom input yang sudah berisi nilai asli (bukan placeholder).

        Di form rute, kolom tujuan masih kosong, jadi nilai yang terbaca di sini
        adalah alamat titik jemput yang terisi otomatis.
        """
        elements = self.find_all(self.FIELD_INPUT_PREFILLED, timeout=timeout)
        texts = [(el.get_attribute("text") or "").strip() for el in elements]
        return [t for t in texts if t]

    def is_map_picker_displayed(self, timeout: int = 8) -> bool:
        """Layar pilih lokasi lewat peta tampil (tombol 'Pilih Lokasi')."""
        return self.is_displayed(self.BTN_MAP_SELECT_LOCATION, timeout=timeout)

    def is_place_order_displayed(self, timeout: int = 10) -> bool:
        """Layar Place Order tampil (tombol 'Pesan EVMoto')."""
        return self.is_displayed(self.BTN_PESAN_EVMOTO_EXACT, timeout=timeout)

    def is_schedule_button_displayed(self, timeout: int = 5) -> bool:
        """Tombol 'Jadwalkan' (mode reguler, belum ada jadwal) tampil di Place Order."""
        return self.is_displayed(self.BTN_JADWALKAN_EXACT, timeout=timeout)

    def get_visible_time_texts(self) -> set:
        """Kumpulan label di layar yang memuat jam (mis. '08:30' / '08.30').

        Label nominal rupiah dan jarak (km) diabaikan agar angka tarif tidak terbaca sebagai jam.
        """
        labels = set()
        for el in self.driver.find_elements(*self.ANY_TEXT_WITH_TIME_SEPARATOR):
            label = (el.get_attribute("content-desc") or el.get_attribute("text") or "").strip()
            if not label or "Rp" in label or "km" in label:
                continue
            if _TIME_PATTERN.search(label):
                labels.add(label)
        return labels

    def is_scheduled_created_dialog_displayed(self, timeout: int = 15) -> bool:
        """Dialog 'Pesan Terjadwal Berhasil Dibuat' tampil."""
        return self.is_displayed(self.DIALOG_SCHEDULED_CREATED, timeout=timeout)

    def close_scheduled_created_dialog(self):
        """Menutup dialog pesanan terjadwal dengan tombol 'Lanjutkan'."""
        self.click(self.BTN_SCHEDULED_CREATED_CONTINUE, label="Tombol Lanjutkan (Pesanan Terjadwal)")

    def is_scheduled_order_status_displayed(self, timeout: int = 8) -> bool:
        """Kartu berstatus 'Pesanan Terjadwal' tampil di Tab Booking Aktivitas."""
        return self.is_displayed(self.TEXT_SCHEDULED_ORDER_STATUS, timeout=timeout)

    def open_first_scheduled_order(self):
        """Membuka kartu pesanan terjadwal pertama (label 'Pesanan Terjadwal')."""
        self.click(self.TEXT_SCHEDULED_ORDER_STATUS, label="Kartu Pesanan Terjadwal")

    def is_scheduled_detail_displayed(self, timeout: int = 8) -> bool:
        """Halaman 'Detail Jadwal Pemesanan' tampil."""
        return self.is_displayed(self.TEXT_SCHEDULED_DETAIL_TITLE, timeout=timeout)

    def is_payment_selected_snackbar_displayed(self, method: str = "cash", timeout: int = 6) -> bool:
        """Snackbar konfirmasi metode bayar terpilih: 'cash' atau 'wallet' (Dompet EVMoto)."""
        locator = (
            self.SNACKBAR_PAYMENT_WALLET_SELECTED
            if method.lower().strip() in ("wallet", "cashless", "evwallet")
            else self.SNACKBAR_PAYMENT_CASH_SELECTED
        )
        return self.is_displayed(locator, timeout=timeout)

    def is_promo_applied_snackbar_displayed(self, timeout: int = 6) -> bool:
        """Snackbar 'Promo berhasil diterapkan ke pesanan Anda.' tampil."""
        return self.is_displayed(self.SNACKBAR_PROMO_APPLIED, timeout=timeout)

    def get_all_fare_amounts(self, timeout: int = 5) -> list:
        """Semua nominal rupiah (int) yang tampil di layar, mis. ['Rp 10.200'] -> [10200]."""
        amounts = []
        for el in self.find_all(self.TEXT_ESTIMATED_FARE, timeout=timeout):
            label = el.get_attribute("content-desc") or el.get_attribute("text") or ""
            for match in re.findall(r"Rp\s?([\d.]+)", label):
                digits = match.replace(".", "")
                if digits:
                    amounts.append(int(digits))
        return amounts

    def is_insufficient_balance_dialog_displayed(self, timeout: int = 8) -> bool:
        """Dialog 'Saldo Anda Tidak Cukup' beserta tombol 'Pilih Metode Pembayaran Lain' tampil."""
        return (
            self.is_displayed(self.DIALOG_INSUFFICIENT_BALANCE, timeout=timeout)
            and self.is_displayed(self.BTN_OTHER_PAYMENT_METHOD, timeout=3)
        )

    def get_home_wallet_balance_amount(self, timeout: int = 8):
        """Saldo dompet di Beranda sebagai int, atau None bila label saldo tidak terbaca."""
        try:
            el = self.find(self.TEXT_HOME_BALANCE_AMOUNT, timeout=timeout)
        except TimeoutException:
            return None
        label = el.get_attribute("content-desc") or el.get_attribute("text") or ""
        digits = re.sub(r"[^\d]", "", label)
        return int(digits) if digits else None

    def is_same_location_warning_displayed(self, timeout: int = 8) -> bool:
        """Validasi 'Titik penjemputan dan tujuan tidak boleh sama' tampil."""
        return self.is_displayed(self.WARNING_SAME_LOCATION_EXACT, timeout=timeout)


BookingLocators = BookingPage

