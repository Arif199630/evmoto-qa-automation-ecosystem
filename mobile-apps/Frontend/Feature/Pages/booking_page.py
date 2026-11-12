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
from Frontend.Feature.Pages.home_page import HomePage
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
    # peta layar CI 12 Nov 2026: 01_beranda -> Beranda tidak punya kolom 'Jemput'; form rute (titik jemput + tujuan)
    # dibuka dari kolom tujuan ImageView 'Hello, mau kemana hari ini?'. Locator dipakai bersama dengan HomePage.
    CTA_PICKUP_SECTION = HomePage.SEARCH_DESTINATION
    # peta layar CI 12 Nov 2026: 03_panel_naik -> ImageView 'Pilih Lewat Peta' di kanan atas form rute.
    BTN_SET_ON_MAP = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Pilih Lewat Peta' or @text='Pilih Lewat Peta']"
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
    # peta layar CI 12 Nov 2026: 05_pilih_saran -> setelah saran tujuan dipilih muncul layar 'Lokasi Penjemputan'
    # (daftar titik jemput terdekat, 'Catatan tambahan (opsional)') dengan Button 'Pilih Lokasi' -> 06 Place Order.
    TEXT_PICKUP_CONFIRM_TITLE = (
        AppiumBy.XPATH,
        "//*[@content-desc='Lokasi Penjemputan' or @text='Lokasi Penjemputan']"
    )
    BTN_PICKUP_CONFIRM = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Pilih Lokasi' or @text='Pilih Lokasi']"
    )

    # ==========================================================================
    # 2. SAVED PLACES UNDER PICKUP SECTION (HOME, WORK, OTHERS)
    # ==========================================================================
    # peta layar CI 12 Nov 2026: 01_beranda -> chip ImageView 'Rumah' / 'Kantor' / 'Lainnya'. Dicocokkan persis dan
    # dibatasi ImageView: contains('Rumah') juga cocok dengan judul View 'Rumah' / 'Tambah Rumah' (11_alamat_rumah).
    CTA_SAVED_HOME = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Rumah' or @text='Rumah']"
    )
    CTA_SAVED_WORK = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Kantor' or @text='Kantor']"
    )
    CTA_SAVED_OTHER = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Lainnya' or @text='Lainnya']"
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
    # peta layar CI 12 Nov 2026: 03_panel_naik -> form rute berisi 2 EditText: titik jemput (terisi 'Menara Sentraya',
    # tanpa hint) dan tujuan (hint 'Masukkan tujuan'). Hint huruf kecil, jadi contains(@hint,'Tujuan') tidak cocok.
    FIELD_DESTINATION = (
        AppiumBy.XPATH,
        "//android.widget.EditText[@hint='Masukkan tujuan' or @text='Masukkan tujuan']"
    )
    # Kolom ketik alamat: tujuan di form rute (03_panel_naik) atau kolom alamat di form alamat favorit
    # (11_alamat_rumah: EditText hint 'Tambahkan alamat rumah kamu').
    FIELD_ADDRESS_SEARCH = (
        AppiumBy.XPATH,
        "//android.widget.EditText[@hint='Masukkan tujuan' or @text='Masukkan tujuan' or "
        "starts-with(@hint, 'Tambahkan alamat') or starts-with(@text, 'Tambahkan alamat')]"
    )
    # peta layar CI 12 Nov 2026: 04_saran_tujuan -> tiap saran = ImageView clickable dengan content-desc
    # '<jarak>km / <nama> / <alamat>' (mis. '2.1km', 'Mall Senayan City', 'Jl. Asia Afrika ...'). Saran dikenali dari
    # karakter pertama berupa angka; chip Rumah/Kantor/Lainnya, 'Lokasi Saat Ini' dan kartu 'ECGO 3' tidak diawali angka.
    FIRST_SUGGESTION_WORD = (
        AppiumBy.XPATH,
        "(//android.widget.ImageView[@clickable='true' and contains(@content-desc, 'km') and "
        "contains('0123456789', substring(@content-desc, 1, 1))])[1]"
    )
    ALL_SUGGESTIONS = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@clickable='true' and contains(@content-desc, 'km') and "
        "contains('0123456789', substring(@content-desc, 1, 1))]"
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
    # peta layar CI 12 Nov 2026: 06_konfirmasi_lokasi_1 -> tarif ada di kartu layanan ImageView
    # 'ECGO 3 / 1 / Kupon / Rp6.901 / Rp10.901' (harga setelah kupon + harga coret sebelum kupon). 'Diskon Rp 4.000' (View)
    # dan 'Rp0' saldo Beranda (View) sengaja tidak ikut: dibatasi ImageView.
    TEXT_ESTIMATED_FARE = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[contains(@content-desc, 'Rp') or contains(@text, 'Rp')]"
    )
    # peta layar CI 12 Nov 2026: 06_konfirmasi_lokasi_1 -> View 'Jarak 3.88 km . 15 menit'
    TEXT_TRIP_DISTANCE = (
        AppiumBy.XPATH,
        "//*[starts-with(@content-desc, 'Jarak ') or starts-with(@text, 'Jarak ')]"
    )
    # peta layar CI 12 Nov 2026: 06_konfirmasi_lokasi_1 -> chip metode bayar terpilih = ImageView 'Cash' (persis).
    # Label persis dipakai agar tidak cocok dengan pilihan di layar 'Metode Pembayaran' ('Cash / Pembayaran praktis...').
    BTN_PAYMENT_METHOD = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Cash' or @content-desc='Saldo EVMoto' or "
        "@content-desc='GoPay' or @content-desc='OVO']"
    )
    # peta layar CI 12 Nov 2026: 08_pilih_pembayaran -> judul View 'Metode Pembayaran'
    TITLE_PAYMENT_METHOD_SCREEN = (
        AppiumBy.XPATH,
        "//*[@content-desc='Metode Pembayaran' or @text='Metode Pembayaran']"
    )
    # peta layar CI 12 Nov 2026: 08_pilih_pembayaran -> ImageView 'Saldo EVMoto / Bayar mudah dengan Saldo EVMoto /
    # Saldo: Rp0' dan 'Cash / Pembayaran praktis dan cepat'. '!=' label persis mencegah tertukar dengan chip Place Order.
    OPTION_PAYMENT_WALLET = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[starts-with(@content-desc, 'Saldo EVMoto') and @content-desc!='Saldo EVMoto']"
    )
    OPTION_PAYMENT_CASH = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[starts-with(@content-desc, 'Cash') and @content-desc!='Cash']"
    )
    # peta layar CI 12 Nov 2026: 08_pilih_pembayaran -> GoPay & OVO belum aktif di akun uji: hanya teks di View
    # 'Pilih Metode Pembayaran / GoPay / Silahkan aktifkan layanan ini / OVO / Silahkan aktifkan layanan ini' + 2 Button
    # 'Aktifkan'. Bagian GoPay = teks antara 'GoPay' dan 'OVO'; bagian OVO = teks setelah 'OVO'.
    TEXT_GOPAY_NOT_ACTIVATED = (
        AppiumBy.XPATH,
        "//*[contains(substring-before(substring-after(@content-desc, 'GoPay'), 'OVO'), 'Silahkan aktifkan layanan ini')]"
    )
    TEXT_OVO_NOT_ACTIVATED = (
        AppiumBy.XPATH,
        "//*[contains(substring-after(@content-desc, 'OVO'), 'Silahkan aktifkan layanan ini')]"
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
    # peta layar CI 12 Nov 2026: 06_konfirmasi_lokasi_1 -> pemilih kupon = View clickable 'Diskon Rp 4.000' (ikon kupon
    # + '>'). Layar sesudah diketuk (kolom kode voucher, tombol pakai) belum ada di peta layar.
    BTN_APPLY_VOUCHER = (
        AppiumBy.XPATH,
        "//android.view.View[@clickable='true' and starts-with(@content-desc, 'Diskon')]"
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
    # peta layar CI 12 Nov 2026: 06_konfirmasi_lokasi_1 -> Button 'Jadwalkan' di kiri 'Pesan EVMoto'
    CTA_SCHEDULED_BOOKING = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Jadwalkan' or @text='Jadwalkan']"
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
    # peta layar CI 12 Nov 2026: 06_konfirmasi_lokasi_1 -> Button 'Pesan EVMoto'
    BTN_BOOK_EVMOTO = (
        AppiumBy.XPATH,
        "//android.widget.Button[@content-desc='Pesan EVMoto' or @text='Pesan EVMoto']"
    )
    # peta layar CI 12 Nov 2026: 03_panel_naik / 08_pilih_pembayaran / 11_alamat_rumah -> ImageView 'Back' kiri atas.
    # Locator lama (contains(@class,'ImageView')) cocok dengan ImageView apa pun (mis. kartu 'ECGO 3' / chip 'Cash').
    # Panah kembali di Place Order (screenshot 07_place_order_gulir_1) tidak berlabel; lihat click_back().
    BTN_BACK = (
        AppiumBy.XPATH,
        "//android.widget.ImageView[@content-desc='Back']"
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
    # peta layar CI 12 Nov 2026: 03_panel_naik -> kolom jemput text='Menara Sentraya'; kolom tujuan kosong (hanya hint).
    FIELD_INPUT_PREFILLED = (
        AppiumBy.XPATH,
        "//android.widget.EditText[string-length(@text) > 0 and not(@text = @hint)]"
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
        """Dari Beranda membuka form rute (titik jemput terisi otomatis + kolom 'Masukkan tujuan').

        Peta layar CI 12 Nov 2026: 01_beranda -> 03_panel_naik. Popup 'Pemberitahuan Jam Operasional' ditutup dulu, lalu
        kolom tujuan diketuk lewat HomePage.open_search_destination() (sudah mengetuk ulang sekali). Elemen kolom itu
        adalah wadah yang juga memuat chip Rumah/Kantor/Lainnya, jadi bila form belum terbuka, bagian atas wadah
        diketuk lewat koordinat (cara yang berhasil di CI, mapbook4: 06_form_tujuan_koordinat_1).
        """
        home = HomePage(self.driver)
        home.dismiss_welcome_popup_if_present()
        home.open_search_destination()
        if self.find_all(self.FIELD_DESTINATION, timeout=3):
            return
        wadah = self.driver.find_elements(*self.CTA_PICKUP_SECTION)
        if not wadah:
            return
        r = wadah[0].rect
        x, y = r["x"] + r["width"] // 2, r["y"] + 20
        logger.info(f"Form rute belum terbuka, mengetuk bagian atas kolom tujuan di ({x},{y})")
        self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        self.find_all(self.FIELD_DESTINATION, timeout=5)

    def confirm_pickup_location(self, timeout: int = 10) -> bool:
        """Layar 'Lokasi Penjemputan' (muncul setelah saran tujuan dipilih): tekan 'Pilih Lokasi'.

        Peta layar CI 12 Nov 2026: 05_pilih_saran -> 06_konfirmasi_lokasi_1 (Place Order). True bila layar itu tampil
        dan tombol ditekan; False bila layar tidak muncul (mis. aplikasi langsung menampilkan validasi/popup lain),
        sehingga assertion test sesudahnya yang menilai layar yang benar-benar tampil.
        """
        if not self.is_displayed(self.TEXT_PICKUP_CONFIRM_TITLE, timeout=timeout):
            logger.info("Layar 'Lokasi Penjemputan' tidak tampil setelah memilih saran tujuan")
            return False
        self.click(self.BTN_PICKUP_CONFIRM, label="Tombol 'Pilih Lokasi' (Lokasi Penjemputan)")
        return True

    # Kolom titik jemput di form rute: EditText pertama selain kolom tujuan (peta layar CI 12 Nov 2026: 03_panel_naik)
    FIELD_PICKUP = (AppiumBy.XPATH, "(//android.widget.EditText[not(@hint='Masukkan tujuan') and not(@text='Masukkan tujuan')])[1]")

    def set_pickup(self, pickup: str):
        """Ganti titik jemput di form rute dengan hasil pencarian alamat pertama (mis. 'Ecgo Evmoto Wijaya')."""
        field = self.find_element(self.FIELD_PICKUP, timeout=10)
        field.click()
        time.sleep(0.5)
        field.clear()
        field.send_keys(pickup)
        time.sleep(3)
        self.click(self.FIRST_SUGGESTION_WORD, label=f"Saran titik jemput '{pickup}'")
        time.sleep(3)
        # Bila aplikasi langsung meminta konfirmasi titik jemput, konfirmasi dulu sebelum mengisi tujuan
        if self.is_displayed(self.TEXT_PICKUP_CONFIRM_TITLE, timeout=3) and not self.driver.find_elements(*self.FIELD_DESTINATION):
            self.confirm_pickup_location(timeout=3)

    def open_place_order(self, destination: str, pickup: str = None):
        """Beranda -> form rute -> ketik tujuan -> saran pertama -> 'Pilih Lokasi' (peta layar CI 12 Nov 2026: 01 -> 06).

        Tidak menekan 'Pesan EVMoto'. Pemanggil wajib memastikan sendiri is_place_order_displayed().
        """
        self.open_pickup_section()
        if pickup:
            self.set_pickup(pickup)
            self.enter_destination(destination)
            self._select_suggestion_for(destination, exclude=pickup)
        else:
            self.enter_destination(destination)
            self.select_first_suggestion()
        self.confirm_pickup_location()

    def _select_suggestion_for(self, destination: str, exclude: str = None, timeout: int = 12):
        """Pilih saran alamat yang cocok dengan tujuan, bukan sisa daftar saran titik jemput.

        Run 43193268521: setelah titik jemput diisi, daftar saran jemput ('Ecgo Evmoto Wijaya 0.47km') masih tampil
        saat tujuan diketik; mengetuk saran pertama membuat tujuan = titik jemput ('Titik jemput dan tujuan sama').
        """
        kata = [w.lower() for w in re.findall(r"[A-Za-z0-9]{3,}", destination)]
        if exclude:  # kata yang juga ada di nama titik jemput (mis. 'wijaya') tidak bisa membedakan saran
            khas = [k for k in kata if k not in exclude.lower()]
            kata = khas or kata
        deadline = time.time() + timeout
        while time.time() < deadline:
            for el in self.driver.find_elements(AppiumBy.XPATH, self.FIRST_SUGGESTION_WORD[1][1:].rsplit(')[1]', 1)[0]):
                label = (el.get_attribute("content-desc") or el.get_attribute("text") or "").lower()
                if exclude and exclude.lower() in label and not any(k in label for k in kata):
                    continue
                if any(k in label for k in kata):
                    el.click()
                    time.sleep(2)
                    return
            time.sleep(1)
        raise AssertionError(f"Saran alamat untuk tujuan '{destination}' tidak muncul dalam {timeout} dtk")

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
        """Mengetik alamat tujuan (form rute) atau alamat favorit (form 'Tambah Rumah')."""
        self.type_text(self.FIELD_ADDRESS_SEARCH, destination, label="Input Kolom Destinasi")

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

    def _service_card_fares(self, timeout: int = 5) -> list:
        """Nominal 'RpN' di kartu layanan Place Order, mis. 'ECGO 3 / 1 / Kupon / Rp6.901 / Rp10.901' -> [6901, 10901].

        TimeoutException bila kartu tidak tampil; list kosong bila kartu tanpa nominal (tanpa angka cadangan).
        """
        el = self.find_element(self.TEXT_ESTIMATED_FARE, timeout=timeout)
        label = el.get_attribute("content-desc") or el.get_attribute("text") or ""
        return [int(m.replace(".", "")) for m in re.findall(r"Rp\s?([\d.]+)", label) if m.replace(".", "")]

    def get_estimated_fare(self) -> str:
        """Tarif yang dibayar pengguna di kartu layanan Place Order, mis. 'Rp6.901'. String kosong bila tanpa nominal.

        Peta layar CI 12 Nov 2026 (06_konfirmasi_lokasi_1): kartu memuat harga setelah kupon dan harga coret sebelum
        kupon; yang dibayar = nominal terkecil. Tanpa kupon hanya ada satu nominal.
        """
        fares = self._service_card_fares()
        return f"Rp{min(fares):,}".replace(",", ".") if fares else ""

    def get_fare_before_discount(self) -> str:
        """Tarif argo sebelum kupon (harga coret, mis. 'Rp10.901'); sama dengan get_estimated_fare() bila tanpa kupon."""
        fares = self._service_card_fares()
        return f"Rp{max(fares):,}".replace(",", ".") if fares else ""

    def get_trip_distance_km(self):
        """Jarak rute yang tampil di Place Order ('Jarak 3.88 km . 15 menit' -> 3.88), atau None bila tidak terbaca."""
        els = self.find_all(self.TEXT_TRIP_DISTANCE, timeout=5)
        if not els:
            return None
        label = els[0].get_attribute("content-desc") or els[0].get_attribute("text") or ""
        match = re.search(r"Jarak\s+([\d.,]+)\s*km", label)
        return float(match.group(1).replace(",", ".")) if match else None


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
        # peta layar CI 12 Nov 2026: 06_konfirmasi_lokasi_1 (chip 'Cash') -> 08_pilih_pembayaran ('Metode Pembayaran')
        self.click(self.BTN_PAYMENT_METHOD, label="Tombol Buka Pilihan Metode Pembayaran")
        self.find_all(self.TITLE_PAYMENT_METHOD_SCREEN, timeout=8)
        if clean_method in ("wallet", "cashless", "evwallet"):
            self.click(self.OPTION_PAYMENT_WALLET, label="Pilihan EvWallet (Cashless)")
        elif clean_method in ("gopay", "ovo"):
            nama = "GoPay" if clean_method == "gopay" else "OVO"
            belum_aktif = self.TEXT_GOPAY_NOT_ACTIVATED if clean_method == "gopay" else self.TEXT_OVO_NOT_ACTIVATED
            if self.driver.find_elements(*belum_aktif):
                raise AssertionError(
                    f"{nama} tidak bisa dipilih: layar 'Metode Pembayaran' menampilkan '{nama} - Silahkan aktifkan "
                    "layanan ini' dengan tombol 'Aktifkan' (e-wallet belum ditautkan ke akun uji)"
                )
            option = self.OPTION_PAYMENT_GOPAY if clean_method == "gopay" else self.OPTION_PAYMENT_OVO
            self.click(option, label=f"Pilihan {nama} (E-Wallet)")
        else:
            self.click(self.OPTION_PAYMENT_CASH, label="Pilihan Tunai (Cash)")
        time.sleep(1.0)
        # Bila daftar metode tidak menutup sendiri setelah dipilih, kembali ke Place Order lewat 'Back' (08_pilih_pembayaran).
        if not self.is_displayed(self.BTN_PESAN_EVMOTO_EXACT, timeout=3) and self.driver.find_elements(*self.TITLE_PAYMENT_METHOD_SCREEN):
            self.click(self.BTN_BACK, label="Tombol Back (Metode Pembayaran)")
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
        """Menekan tombol kembali: ImageView 'Back' bila berlabel, selain itu tombol Back Android.

        Peta layar CI 12 Nov 2026: form rute / Metode Pembayaran / alamat favorit punya ImageView 'Back'; panah kembali
        di Place Order tidak berlabel (07_place_order_gulir_1), dan Back Android mengembalikan layar
        (08_pilih_pembayaran -> 09_kembali_ke_place_order).
        """
        if self.driver.find_elements(*self.BTN_BACK):
            self.click(self.BTN_BACK, label="Tombol Kembali")
            return
        logger.info("ImageView 'Back' tidak ada di layar ini, menekan tombol Back Android")
        self.driver.back()
        time.sleep(1.0)

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

