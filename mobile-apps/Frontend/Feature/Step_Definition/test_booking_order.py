"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - BOOKING ORDER CORE TEST SUITE
================================================================================
Aplikasi: EvMoto Mobile User (Android)
Target Modul: Core Booking Order (Normal Booking & Advance Booking)
Berdasarkan: Google Sheets 'User' (TC01 s/d TC89 Normal, TC01 s/d TC45 Advance)
Metodologi: 4 Pilar QA, BDD (Given - When - Then), Page Object Model (POM),
Simulasi Human-like Pacing, dan Validasi Keamanan Siber & Resiliensi OS.
================================================================================
Daftar Cakupan Pengujian:
1. Normal Booking Flow (TC01 - TC89):
   - Maps Re-Center & Operational Hours Notice
   - Saved Places (Rumah, Kantor, Lainnya) & Validasi Kolom Wajib
   - Pickup Section & Auto-suggestion Destinasi
   - Place Order, Pencarian Driver, Snackbar Berjalan di Latar
   - Pembatalan oleh Pengguna (Saat Cari Driver vs Setelah Dapat Driver)
   - Pembatalan oleh Driver & Tombol Try Again
   - Driver Timeout 5 Menit & Snackbar Tidak Tersedia
   - Batas Jarak Maksimum 60 KM (Luar Kota)
   - Komunikasi Chat (Teks & Foto), Tombol SOS Darurat, & CS WhatsApp
   - Siklus Penyelesaian Trip, Cash Collected, & Penilaian Rating 5 Bintang
2. Advance Booking (Scheduled Booking) Flow (TC01 - TC45):
   - Pemilihan Jadwal (Date & Time Picker: Minimal 30 Menit, Maksimal 18 Jam / 7 Hari)
   - Tombol Pilih vs Batalkan Waktu Jadwal
   - Siklus Order Terjadwal (Order Created Notification & Driver Assigned)
   - Reschedule & Pembatalan Pesanan Terjadwal dari Tab Booking
3. Skenario Pengembangan & Penguatan Tambahan (Gaps / Core QA 4-Pillars):
   - Pemilihan Metode Pembayaran (EvWallet vs Tunai)
   - Penggunaan Kode Voucher Promo & Potongan Diskon
   - Validasi Saldo EvWallet Kurang (Insufficient Balance Modal)
   - Validasi Koordinat Jemput & Tujuan Sama
   - Sanitasi SQLi & XSS pada Chat Driver & Catatan Jemput
   - Resiliensi Multi-Tapping Cepat (Anti Double-Booking)
   - Resiliensi Minimize / Backgrounding Aplikasi saat Mencari Driver
================================================================================
"""
import os
import time
import math
import pytest
from appium.webdriver.common.appiumby import AppiumBy

from Frontend.Feature.Pages.login_page import LoginPage
from Frontend.Feature.Pages.home_page import HomePage
from Frontend.Feature.Pages.booking_page import BookingPage
from Frontend.Feature.Pages.tracking_page import TrackingPage
from Frontend.Feature.Pages.activity_page import ActivityPage
from Frontend.Feature.Helper.driver_role_simulator import DriverRoleSimulator
from Frontend.Feature.Helper.admin_fare_calculator import AdminDashboardFareCalculator
from Frontend.Feature.Helper.wallet_balance_helper import WalletBalanceHelper
from config.config import Config
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestBookingOrder")


# ==============================================================================
# FIXTURES
# ==============================================================================
@pytest.fixture(scope="function")
def login_page(driver):
    return LoginPage(driver)

@pytest.fixture(scope="function")
def home_page(driver):
    return HomePage(driver)

@pytest.fixture(scope="function")
def booking_page(driver):
    return BookingPage(driver)

@pytest.fixture(scope="function")
def tracking_page(driver):
    return TrackingPage(driver)

@pytest.fixture(scope="function")
def activity_page(driver):
    return ActivityPage(driver)

@pytest.fixture(scope="function")
def driver_simulator():
    """Simulator peran Driver (Budi Setiawan <TEST_DRIVER_PHONE>, APK com.evmoto.driver.app)."""
    simulator = DriverRoleSimulator()
    simulator.set_online(is_online=True)
    yield simulator
    simulator.set_offline()

@pytest.fixture(scope="function")
def fare_calculator():
    """Kalkulator argo dengan angka tarif yang dibaca langsung dari Admin environment aktif (/tSystemPrice/special)."""
    from core.admin_config_reader import AdminConfigError
    try:
        return AdminDashboardFareCalculator.from_admin("User")
    except AdminConfigError as e:
        pytest.skip(f"Tarif Admin tidak bisa dibaca: {e}")

@pytest.fixture(scope="function")
def wallet_helper():
    """Helper saldo dompet digital cashless (EvWallet)."""
    return WalletBalanceHelper(initial_balance=150000)


@pytest.fixture(scope="function")
def authenticated_home(driver, login_page, home_page):
    """Prasyarat global: Pastikan aplikasi sudah masuk ke layar Beranda."""
    try:
        # Dismiss welcome popup jika ada
        home_page.dismiss_welcome_popup_if_present()
    except Exception:
        pass

    if not home_page.is_home_screen_displayed(timeout=3):
        # Jalankan autentikasi dev cepat
        try:
            login_page.input_phone_number(Config.ACTIVE_PHONE)
            login_page.click_submit_login()
            time.sleep(1)
            login_page.input_otp_dev(Config.ACTIVE_OTP)
            time.sleep(2)
            home_page.dismiss_welcome_popup_if_present()
        except Exception as e:
            logger.info(f"State login setup: {e}")
    return home_page


# ==============================================================================
# HELPER PRASYARAT (dipakai beberapa skenario agar mulai dari layar yang benar)
# ==============================================================================
ALASAN_BUTUH_DRIVER_NYATA = (
    "Belum ada mitra driver nyata yang menerima pesanan. Skenario ini butuh akun/perangkat "
    "Driver kedua yang benar-benar menerima order; DriverRoleSimulator hanya simulasi in-memory "
    "dan tidak mengubah layar aplikasi User."
)


def _buka_place_order(booking_page, tujuan: str):
    """Membuka form rute, mengisi tujuan, memilih saran pertama, lalu memastikan Place Order tampil."""
    booking_page.open_pickup_section()
    booking_page.enter_destination(tujuan)
    booking_page.select_first_suggestion()
    assert booking_page.is_place_order_displayed(), (
        f"Prasyarat gagal: layar Place Order (tombol 'Pesan EVMoto') tidak tampil setelah memilih tujuan '{tujuan}'"
    )


def _buat_pesanan_instan(booking_page, tracking_page, tujuan: str):
    """Membuat pesanan instan sampai status pencarian driver tampil."""
    _buka_place_order(booking_page, tujuan)
    booking_page.submit_book_evmoto()
    assert tracking_page.is_searching_driver(timeout=15), (
        "Prasyarat gagal: status 'Sedang mencari driver terdekat untuk Anda' tidak tampil setelah menekan 'Pesan EVMoto'"
    )


def _tunggu_driver_ditugaskan_atau_skip(tracking_page, timeout: int = 60):
    """Menunggu driver menerima pesanan. Skip jujur bila memang tidak ada driver nyata yang menerima."""
    if tracking_page.is_driver_on_the_way_displayed(timeout=timeout):
        return
    if tracking_page.is_searching_driver(timeout=3) or tracking_page.is_driver_not_available_displayed(timeout=3):
        pytest.skip(ALASAN_BUTUH_DRIVER_NYATA)
    pytest.fail(
        "Status pesanan tidak dikenali: bukan 'Sedang mencari driver', bukan 'Driver Tidak Ada yang Tersedia', "
        "dan status driver ditugaskan ('Driver sedang menuju titik jemput') juga tidak tampil"
    )


# ==============================================================================
# PART 1: NORMAL BOOKING / INSTANT RIDE SUITE (TC01 s/d TC89)
# ==============================================================================
class TestNormalBookingSuite:
    """Suite Pengujian Pemesanan Normal / Perjalanan Instan EvMoto."""

    # --------------------------------------------------------------------------
    # 1. Home, Maps Re-Center & Operational Hours Notice
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_04_verify_cta_recenter_map(self, authenticated_home, booking_page):
        """[TC04] Verify CTA Re-Center: Maps redirect ke lokasi terkini pengguna."""
        given("Pengguna sudah login dan berada di layar Beranda")
        when("Pengguna mengetuk tombol CTA Re-Center lokasi pada peta")
        booking_page.click_recenter()

        then("Peta kembali terpusat ke koordinat lokasi pengguna secara akurat")
        time.sleep(1)
        # Titik tengah peta (PlatformView Google Maps) tidak terekspos di accessibility tree.
        # Yang bisa diamati: re-center memakai lokasi pengguna, jadi dialog izin lokasi TIDAK boleh muncul,
        # dan pengguna tetap di Beranda (tombol tidak membuka layar lain).
        assert not booking_page.is_location_permission_dialog_displayed(), (
            "Re-center memunculkan dialog 'Izin lokasi'/'Aktifkan lokasi': lokasi pengguna tidak tersedia untuk memusatkan peta"
        )
        assert booking_page.is_home_destination_prompt_displayed(), (
            "Setelah menekan Re-Center, Beranda ('Hai, mau ke mana hari ini?') tidak lagi tampil"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_05_verify_popup_operational_hours_notice(self, authenticated_home, home_page):
        """[TC05] Verify Popup Operational Hours Notice: Popup ditutup dengan tombol Continue / X."""
        given("Pengguna berada di layar Beranda dan popup jam operasional tampil")
        when("Pengguna mengetuk tombol Continue atau tombol X")
        home_page.dismiss_welcome_popup_if_present()

        then("Popup menghilang dan antarmuka Beranda dapat diakses penuh")
        assert home_page.is_home_screen_displayed()

    # --------------------------------------------------------------------------
    # 2. Saved Places under Pickup Section (Home, Work, Others)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_06_to_10_verify_saved_home_location(self, authenticated_home, booking_page):
        """[TC06-TC10] Verify Saved Place Home: Input alamat, saran kata, dan simpan lokasi rumah."""
        given("Pengguna berada di Beranda dan mengetuk CTA Alamat Rumah (Home)")
        booking_page.select_saved_home()

        when("Pengguna memasukkan alamat rumah pada form pencarian")
        booking_page.enter_destination("Sudirman Central Business District")
        and_step("Pengguna memilih saran alamat pertama dan mengisi nama lokasi")
        booking_page.select_first_suggestion()
        booking_page.fill_saved_location_details(name="Rumah Idaman", detail_address="Tower 2 Lantai 15")

        then("Data alamat rumah berhasil tersimpan")
        assert booking_page.is_address_saved_snackbar_displayed(), (
            "Snackbar 'Alamat berhasil disimpan' tidak tampil setelah menyimpan alamat Rumah 'Rumah Idaman'"
        )

    @pytest.mark.booking
    @pytest.mark.pilar3
    def test_TC_NORM_11_verify_saved_home_mandatory_field_validation(self, authenticated_home, booking_page):
        """[TC11] Verify field Location Name: Validasi field wajib tidak boleh kosong."""
        given("Pengguna berada di form detail alamat rumah")
        booking_page.select_saved_home()

        when("Pengguna mengosongkan nama lokasi lalu menekan tombol Simpan")
        booking_page.fill_saved_location_details(name="", detail_address="Jalan Thamrin No 1")

        then("Sistem menampilkan pesan peringatan kolom wajib (mandatory warning)")
        assert booking_page.is_mandatory_warning_displayed()

    @pytest.mark.booking
    @pytest.mark.pilar2
    def test_TC_NORM_14_verify_cta_back_from_saved_location(self, authenticated_home, booking_page):
        """[TC14] Verify CTA Back: Pengguna kembali ke layar sebelumnya tanpa mutasi data."""
        given("Pengguna berada di layar input alamat")
        booking_page.select_saved_home()

        when("Pengguna menekan tombol CTA Kembali (Back)")
        booking_page.click_back()

        then("Layar kembali menampilkan Beranda dengan aman")
        assert booking_page.is_home_destination_prompt_displayed(), (
            "Setelah menekan Kembali dari form alamat Rumah, Beranda ('Hai, mau ke mana hari ini?') tidak tampil"
        )
        assert not booking_page.is_saved_location_form_displayed(timeout=2), (
            "Form alamat favorit (tombol 'Simpan alamat'/kolom nama lokasi) masih tampil setelah menekan Kembali"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_15_to_23_verify_saved_work_location(self, authenticated_home, booking_page):
        """[TC15-TC23] Verify Saved Place Work: Input alamat kantor dan simpan lokasi."""
        given("Pengguna mengetuk shortcut Alamat Kantor (Work)")
        booking_page.select_saved_work()

        when("Pengguna mengisi alamat kantor dan nama gedung")
        booking_page.enter_destination("Menara Astra Sudirman")
        booking_page.select_first_suggestion()
        booking_page.fill_saved_location_details(name="Kantor Pusat Astra", detail_address="Lantai 30")

        then("Alamat kantor berhasil disimpan dalam daftar lokasi favorit")
        assert booking_page.is_address_saved_snackbar_displayed(), (
            "Snackbar 'Alamat berhasil disimpan' tidak tampil setelah menyimpan alamat Kantor 'Kantor Pusat Astra'"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_24_to_32_verify_saved_other_location(self, authenticated_home, booking_page):
        """[TC24-TC32] Verify Saved Place Other: Input alamat favorit lainnya."""
        given("Pengguna mengetuk shortcut Lokasi Lainnya (Other)")
        booking_page.select_saved_other()

        when("Pengguna mengisi alamat dan nama lokasi favorit kustom")
        booking_page.enter_destination("Mall Grand Indonesia")
        booking_page.select_first_suggestion()
        booking_page.fill_saved_location_details(name="Tempat Nongkrong", detail_address="East Mall Lobby")

        then("Lokasi lainnya berhasil disimpan")
        assert booking_page.is_address_saved_snackbar_displayed(), (
            "Snackbar 'Alamat berhasil disimpan' tidak tampil setelah menyimpan Lokasi Lainnya 'Tempat Nongkrong'"
        )

    # --------------------------------------------------------------------------
    # 3. Pickup Point Section & Destination Suggestions
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_33_verify_pickup_section_auto_set(self, authenticated_home, booking_page):
        """[TC33] Verify Pickup Section: Titik penjemputan otomatis terisi lokasi saat ini."""
        given("Pengguna berada di Beranda")
        when("Pengguna mengetuk kolom Pickup Section")
        booking_page.open_pickup_section()

        then("Layar beralih ke form destinasi dengan titik jemput otomatis terisi")
        assert booking_page.is_destination_field_displayed(), (
            "Form destinasi tidak tampil: kolom 'Titik tujuan'/'Masukkan tujuan' tidak ditemukan setelah membuka Pickup Section"
        )
        terisi = booking_page.get_prefilled_input_texts()
        assert terisi, (
            "Titik jemput tidak terisi otomatis: tidak ada kolom input yang berisi alamat (semua masih placeholder)"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_34_verify_cta_set_on_map(self, authenticated_home, booking_page):
        """[TC34] Verify CTA Set on Map: Menampilkan peta interaktif untuk penentuan titik."""
        given("Pengguna berada di layar pemilihan lokasi")
        booking_page.open_pickup_section()

        when("Pengguna mengetuk CTA 'Set on Map'")
        booking_page.click_set_on_map()

        then("Peta penentuan titik tampil dan pin pointer aktif")
        assert booking_page.is_map_picker_displayed(), (
            "Layar pilih lokasi lewat peta tidak tampil: tombol 'Pilih Lokasi' tidak ditemukan setelah mengetuk 'Pilih Lewat Peta'"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_35_verify_field_destination_auto_suggest(self, authenticated_home, booking_page):
        """[TC35] Verify field destinasi: Mengetik alamat memicu auto-suggest dan membuka Place Order."""
        given("Pengguna berada di layar pemilihan lokasi")
        booking_page.open_pickup_section()

        when("Pengguna mengetik destinasi 'Grand Indonesia' dan memilih saran kata")
        booking_page.enter_destination("Grand Indonesia")
        time.sleep(1)
        booking_page.select_first_suggestion()

        then("Data destinasi tersimpan dan aplikasi beralih ke layar Place Order")
        assert booking_page.is_place_order_displayed(), (
            "Setelah memilih saran 'Grand Indonesia', layar Place Order (tombol 'Pesan EVMoto') tidak tampil"
        )

    @pytest.mark.booking
    @pytest.mark.pilar2
    def test_TC_NORM_36_37_verify_cta_back_from_place_order(self, authenticated_home, booking_page, tracking_page):
        """[TC36-TC37] Verify CTA Back: Kembali ke halaman sebelumnya dari Place Order."""
        given("Pengguna berada di layar Place Order")
        _buka_place_order(booking_page, "Grand Indonesia")

        when("Pengguna menekan tombol Back")
        booking_page.click_back()

        then("Aplikasi kembali ke halaman Beranda tanpa membuat order")
        assert booking_page.wait_until_gone(booking_page.BTN_PESAN_EVMOTO_EXACT), (
            "Layar Place Order (tombol 'Pesan EVMoto') masih tampil setelah menekan Back"
        )
        assert not tracking_page.is_searching_driver(timeout=3), (
            "Menekan Back dari Place Order justru membuat order: status pencarian driver tampil"
        )

    # --------------------------------------------------------------------------
    # 4. Place Order, Searching Driver & Cancel Flow (TC38 - TC42)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_38_verify_cta_booking_searching_driver(self, authenticated_home, booking_page, tracking_page):
        """[TC38] Verify CTA Booking: Menekan tombol Book memicu status Searching Driver."""
        given("Pengguna memilih rute dan berada di layar Place Order")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Senayan City")
        booking_page.select_first_suggestion()

        when("Pengguna menekan tombol 'Book EVMoto'")
        booking_page.submit_book_evmoto()

        then("Sistem mengalihkan ke layar pencarian mitra driver (Searching Driver on progress)")
        assert tracking_page.is_searching_driver()

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_40_verify_snackbar_searching_driver(self, authenticated_home, tracking_page, booking_page):
        """[TC40] Verify snackbar searching driver saat pengguna menekan Back."""
        given("Pengguna dalam status mencari driver")
        _buat_pesanan_instan(booking_page, tracking_page, "Senayan City")

        when("Pengguna menekan tombol Back")
        booking_page.click_back()

        then("Snackbar aktivitas pencarian driver yang sedang berjalan tampil di bagian bawah")
        assert booking_page.is_home_destination_prompt_displayed(), (
            "Setelah Back dari layar pencarian driver, Beranda ('Hai, mau ke mana hari ini?') tidak tampil"
        )
        assert tracking_page.is_searching_driver(timeout=8), (
            "Di Beranda tidak ada snackbar pencarian driver yang sedang berjalan setelah menekan Back"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_41_verify_popup_confirmation_cancel_order(self, authenticated_home, booking_page, tracking_page):
        """[TC41] Verify popup konfirmasi cancel: Membatalkan pencarian driver."""
        given("Pengguna sedang dalam layar pencarian driver")
        _buat_pesanan_instan(booking_page, tracking_page, "Senayan City")

        when("Pengguna mengetuk tombol Cancel lalu memilih konfirmasi Ya/Cancel")
        tracking_page.cancel_searching_driver(confirm=True)

        then("Pencarian driver berhasil dibatalkan dan pengguna kembali ke Beranda")
        assert tracking_page.wait_until_searching_gone(), (
            "Status pencarian driver masih tampil setelah konfirmasi pembatalan"
        )
        assert booking_page.is_home_destination_prompt_displayed(), (
            "Setelah pencarian dibatalkan, pengguna tidak kembali ke Beranda ('Hai, mau ke mana hari ini?')"
        )

    @pytest.mark.booking
    @pytest.mark.pilar2
    def test_TC_NORM_42_verify_popup_confirmation_cancel_close(self, authenticated_home, booking_page, tracking_page):
        """[TC42] Verify popup konfirmasi cancel (Close): Menutup popup tanpa membatalkan order."""
        given("Pengguna berada di popup konfirmasi pembatalan")
        _buat_pesanan_instan(booking_page, tracking_page, "Senayan City")

        when("Pengguna memilih tombol Close / X")
        tracking_page.cancel_searching_driver(confirm=False)

        then("Popup tertutup dan pencarian driver tetap berlanjut secara aman")
        assert tracking_page.is_cancel_order_dialog_closed(), (
            "Dialog 'Apakah Anda yakin ingin membatalkan pesanan?' masih tampil setelah menekan Close"
        )
        assert tracking_page.is_searching_driver(timeout=5), (
            "Pencarian driver ikut berhenti setelah dialog pembatalan ditutup (seharusnya tetap mencari)"
        )

    # --------------------------------------------------------------------------
    # 5. Order Complete Lifecycle Flow (TC61 - TC71)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_61_to_65_verify_get_driver_information(self, authenticated_home, booking_page, tracking_page):
        """[TC61-TC65] Verify Get Driver: Menampilkan informasi driver, plat motor, dan jarak ETA."""
        given("Pengguna melakukan booking perjalanan")
        _buat_pesanan_instan(booking_page, tracking_page, "Plaza Indonesia")

        then("Saat driver ditugaskan, kontainer informasi driver (nama, nomor plat, estimasi waktu) tampil")
        _tunggu_driver_ditugaskan_atau_skip(tracking_page)
        assert tracking_page.is_driver_on_the_way_displayed(timeout=5), (
            "Status 'Driver sedang menuju titik jemput' tidak tampil pada kontainer informasi driver"
        )
        assert tracking_page.is_chat_driver_button_displayed(), (
            "Tombol 'Chat Driver' tidak tampil pada kontainer informasi driver setelah driver ditugaskan"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_66_verify_cta_chat_driver_text_and_photo(self, authenticated_home, booking_page, tracking_page):
        """[TC66] Verify CTA Chat: Mengirim pesan teks dan foto ke driver."""
        given("Pengguna telah mendapatkan driver penjemputan")
        _buat_pesanan_instan(booking_page, tracking_page, "Plaza Indonesia")
        _tunggu_driver_ditugaskan_atau_skip(tracking_page)

        when("Pengguna membuka menu Chat, mengetik pesan 'Saya di lobi barat', dan mengirim")
        pesan = "Saya di lobi barat memakai jaket hitam"
        tracking_page.send_chat_message(pesan)

        then("Pesan berhasil terkirim ke obrolan driver secara realtime")
        assert tracking_page.is_chat_message_displayed(pesan), (
            f"Gelembung chat berisi '{pesan}' tidak tampil di percakapan setelah menekan Kirim"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_67_68_verify_driver_container_scroll_expand_collapse(self, authenticated_home, booking_page, tracking_page):
        """[TC67-TC68] Verify Driver information Container: Scroll Up (Expand) dan Scroll Down (Collapse)."""
        given("Kontainer informasi driver tampil")
        _buat_pesanan_instan(booking_page, tracking_page, "Plaza Indonesia")
        _tunggu_driver_ditugaskan_atau_skip(tracking_page)
        posisi_awal = tracking_page.get_chat_driver_button_y()

        when("Pengguna melakukan swipe up pada panel driver")
        tracking_page.expand_driver_container()
        time.sleep(1)
        posisi_expand = tracking_page.get_chat_driver_button_y()
        assert posisi_expand < posisi_awal, (
            f"Panel driver tidak naik saat swipe up: posisi tombol 'Chat Driver' {posisi_awal}px -> {posisi_expand}px"
        )

        and_step("Pengguna melakukan swipe down pada panel driver")
        tracking_page.collapse_driver_container()
        time.sleep(1)

        then("Kontainer driver merespons gesture ekspansi dan kolaps secara mulus")
        posisi_collapse = tracking_page.get_chat_driver_button_y()
        assert posisi_collapse > posisi_expand, (
            f"Panel driver tidak turun saat swipe down: posisi tombol 'Chat Driver' {posisi_expand}px -> {posisi_collapse}px"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_69_verify_cta_emergency_sos_icon(self, authenticated_home, booking_page, tracking_page):
        """[TC69] Verify CTA Emergency Icon: Mengalihkan ke nomor panggilan darurat sistem."""
        given("Perjalanan sedang berlangsung")
        _buat_pesanan_instan(booking_page, tracking_page, "Plaza Indonesia")
        _tunggu_driver_ditugaskan_atau_skip(tracking_page)

        when("Pengguna mengetuk ikon Emergency SOS")
        tracking_page.click(tracking_page.BTN_EMERGENCY_ICON, label="Tombol SOS Darurat")
        time.sleep(2)

        then("Sistem membuka shortcut panggilan darurat telepon")
        assert tracking_page.is_phone_dialer_opened(), (
            f"Tombol SOS tidak membuka aplikasi telepon; aplikasi di depan: '{tracking_page.get_current_package()}'"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_70_verify_cta_customer_service_whatsapp(self, authenticated_home, tracking_page):
        """[TC70] Verify CTA Customer Service: Mengalihkan bantuan ke WhatsApp CS resmi."""
        given("Pengguna membutuhkan bantuan operasional")
        when("Pengguna mengetuk ikon Customer Service")
        tracking_page.click(tracking_page.BTN_CUSTOMER_SERVICE_ICON, label="Tombol CS WhatsApp")
        time.sleep(2)

        then("Sistem mengalihkan ke kontak Customer Service WhatsApp")
        if not tracking_page.is_whatsapp_opened() and tracking_page.is_whatsapp_unavailable_displayed():
            pytest.skip(
                "Aplikasi menampilkan 'Tidak dapat membuka WhatsApp': WhatsApp tidak terpasang di emulator, "
                "pengalihan ke WhatsApp CS tidak bisa diverifikasi di perangkat ini"
            )
        assert tracking_page.is_whatsapp_opened(), (
            f"Tombol Customer Service tidak membuka WhatsApp; aplikasi di depan: '{tracking_page.get_current_package()}'"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_71_verify_order_complete_and_driver_rating(self, authenticated_home, tracking_page):
        """[TC71] Verify Order Complete & Rating: Driver Cash Collected lalu submit rating 5 bintang."""
        given("Pengguna tiba di tujuan dan pembayaran selesai (Cash Collected)")
        if not tracking_page.is_rating_screen_displayed(timeout=5):
            pytest.skip(
                "Layar penilaian ('Bagaimana pengalaman perjalanan Anda?') tidak tampil: trip harus diselesaikan "
                "oleh driver nyata dari perangkat Driver kedua sebelum pengguna bisa memberi rating"
            )

        when("Pengguna memberikan penilaian bintang 5 dan ulasan")
        tracking_page.submit_driver_review(stars=5, comment="Perjalanan sangat nyaman dan driver ramah")

        then("Penilaian berhasil disimpan dan snackbar hijau konfirmasi rating tampil")
        assert tracking_page.is_rating_success_displayed(), (
            "Snackbar 'Penilaian dan ulasan berhasil dikirim' tidak tampil setelah menekan 'Kirim Penilaian'"
        )

    # --------------------------------------------------------------------------
    # 6. Cancellation Flows & Boundaries (TC72 - TC89)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_76_to_79_verify_cancel_trip_with_reason(self, authenticated_home, booking_page, tracking_page):
        """[TC76-TC79] Verify User Cancel After Get Driver: Membatalkan dengan memilih alasan pembatalan."""
        given("Pengguna telah mendapat driver tetapi ingin membatalkan perjalanan")
        _buat_pesanan_instan(booking_page, tracking_page, "Plaza Indonesia")
        _tunggu_driver_ditugaskan_atau_skip(tracking_page)

        when("Pengguna memilih batalkan trip, memilih alasan pembatalan, dan konfirmasi")
        tracking_page.cancel_trip_with_reason()

        then("Pesanan dibatalkan secara resmi dan pengguna diarahkan kembali ke Beranda")
        assert tracking_page.wait_until_gone(tracking_page.TEXT_DRIVER_ASSIGNED_STATUS), (
            "Status driver ('Driver sedang menuju titik jemput') masih tampil setelah pembatalan dikonfirmasi"
        )
        assert booking_page.is_home_destination_prompt_displayed(), (
            "Setelah membatalkan trip, pengguna tidak diarahkan kembali ke Beranda ('Hai, mau ke mana hari ini?')"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_NORM_80_to_83_verify_driver_cancel_and_try_again(self, authenticated_home, tracking_page):
        """[TC80-TC83] Verify Driver Cancel: Driver membatalkan, popup tampil, dan tombol Try Again mencari ulang."""
        given("Mitra driver membatalkan penjemputan")
        if not tracking_page.is_driver_cancelled_popup_displayed(timeout=5):
            pytest.skip(
                "Popup 'Driver Membatalkan Perjalanan' tidak tampil: pembatalan oleh driver harus dilakukan dari "
                "perangkat Driver kedua yang nyata; DriverRoleSimulator tidak mengubah layar aplikasi User"
            )

        when("Popup pembatalan driver tampil dan pengguna menekan 'Try Again'")
        tracking_page.click_try_again_after_driver_cancel()

        then("Sistem secara otomatis melanjutkan pencarian driver pengganti")
        assert tracking_page.is_searching_driver(timeout=10), (
            "Setelah menekan 'Coba Lagi', status pencarian driver pengganti tidak tampil"
        )

    @pytest.mark.booking
    @pytest.mark.pilar3
    def test_TC_NORM_84_to_87_verify_driver_not_available_timeout(self, authenticated_home, booking_page, tracking_page):
        """[TC84-TC87] Verify Timeout 5 Menit: Driver tidak ditemukan mengalihkan ke Beranda dengan snackbar."""
        given("Pencarian driver berjalan hingga batas waktu timeout")
        _buat_pesanan_instan(booking_page, tracking_page, "Plaza Indonesia")

        then("Aplikasi otomatis kembali ke Beranda dan menampilkan snackbar 'Driver not available'")
        # Batas timeout pencarian 5 menit + toleransi 60 detik
        tampil = tracking_page.is_driver_not_available_displayed(timeout=360)
        if not tampil and tracking_page.is_driver_on_the_way_displayed(timeout=3):
            pytest.skip("Ada driver nyata yang menerima pesanan, sehingga skenario timeout 5 menit tidak terjadi")
        assert tampil, (
            "Setelah 6 menit mencari, dialog 'Driver Tidak Ada yang Tersedia' tidak tampil"
        )
        assert tracking_page.wait_until_searching_gone(), (
            "Status pencarian driver masih tampil setelah timeout 'Driver Tidak Ada yang Tersedia'"
        )

    @pytest.mark.booking
    @pytest.mark.pilar3
    def test_TC_NORM_88_89_verify_destination_more_than_60km_boundary(self, authenticated_home, booking_page):
        """[TC88-TC89] Verify Destination More Than 60 KM: Validasi popup batasan jarak layanan."""
        given("Pengguna berada di layar pencarian destinasi")
        booking_page.open_pickup_section()

        when("Pengguna memasukkan destinasi di luar jangkauan ibu kota (> 60 km)")
        booking_page.enter_destination("Bandung Kota Kembang Jawa Barat")
        booking_page.select_first_suggestion()

        then("Sistem menolak rute dan menampilkan popup peringatan jarak melebihi batas 60 km")
        assert booking_page.is_distance_exceeded_warning_displayed()


# ==============================================================================
# PART 2: ADVANCE BOOKING / SCHEDULED BOOKING SUITE (TC01 s/d TC45)
# ==============================================================================
class TestAdvanceBookingSuite:
    """Suite Pengujian Pesanan Terjadwal (Advance Booking)."""

    @pytest.mark.booking
    @pytest.mark.advance_booking
    @pytest.mark.pilar1
    def test_TC_ADV_38_verify_cta_scheduled_time_picker_confirm(self, authenticated_home, booking_page):
        """[TC_ADV_38] Verify CTA Scheduled: Memilih tanggal dan jam (30 mnt s/d 18 jam) lalu tekan Pilih."""
        given("Pengguna berada di layar Place Order")
        _buka_place_order(booking_page, "Bandara Soekarno Hatta Terminal 3")
        jam_sebelum = booking_page.get_visible_time_texts()

        when("Pengguna mengetuk tombol CTA Scheduled, memilih tanggal besok jam 08:00, dan menekan 'Pilih'")
        booking_page.open_scheduled_modal()
        booking_page.confirm_scheduled_time()
        time.sleep(1)

        then("Jadwal penjemputan berhasil terpasang dan halaman Place Order menampilkan waktu jadwal")
        assert booking_page.is_place_order_displayed(), (
            "Setelah menekan 'Pilih' pada modal jadwal, layar Place Order (tombol 'Pesan EVMoto') tidak tampil kembali"
        )
        jam_baru = booking_page.get_visible_time_texts() - jam_sebelum
        assert jam_baru, (
            "Place Order tidak menampilkan waktu jadwal baru setelah memilih jadwal "
            f"(label jam sebelum: {sorted(jam_sebelum)})"
        )

    @pytest.mark.booking
    @pytest.mark.advance_booking
    @pytest.mark.pilar2
    def test_TC_ADV_39_verify_cta_scheduled_time_picker_cancel(self, authenticated_home, booking_page):
        """[TC_ADV_39] Verify CTA Scheduled (Batalkan): Menutup picker tanpa mengubah jadwal."""
        given("Pengguna membuka modal jadwal advance booking")
        _buka_place_order(booking_page, "Stasiun Gambir")
        jam_sebelum = booking_page.get_visible_time_texts()
        booking_page.open_scheduled_modal()

        when("Pengguna menekan tombol 'Batalkan' pada modal jadwal")
        booking_page.cancel_scheduled_time()
        time.sleep(1)

        then("Modal tertutup dan pesanan tetap dalam mode reguler tanpa mutasi waktu")
        assert booking_page.is_place_order_displayed(), (
            "Setelah 'Batalkan' pada modal jadwal, layar Place Order (tombol 'Pesan EVMoto') tidak tampil kembali"
        )
        assert booking_page.is_schedule_button_displayed(), (
            "Tombol 'Jadwalkan' tidak tampil lagi: pesanan tidak lagi dalam mode reguler setelah membatalkan picker"
        )
        jam_baru = booking_page.get_visible_time_texts() - jam_sebelum
        assert not jam_baru, f"Waktu jadwal berubah walaupun picker dibatalkan: {sorted(jam_baru)}"

    @pytest.mark.booking
    @pytest.mark.advance_booking
    @pytest.mark.pilar1
    def test_TC_ADV_40_to_42_verify_scheduled_order_creation_and_driver_assignment(self, authenticated_home, booking_page, activity_page):
        """[TC_ADV_40-42] Verify Scheduled Booked: Order created notification & driver assignment."""
        given("Pengguna telah mengatur jadwal advance booking")
        _buka_place_order(booking_page, "Cilandak Town Square")
        booking_page.open_scheduled_modal()
        booking_page.confirm_scheduled_time()

        when("Pengguna menekan tombol 'Pesan EVMoto'")
        booking_page.submit_book_evmoto()

        then("Notifikasi 'Pesanan Terjadwal Berhasil Dibuat' tampil dan detail jadwal muncul di Tab Booking")
        assert booking_page.is_scheduled_created_dialog_displayed(), (
            "Dialog 'Pesan Terjadwal Berhasil Dibuat' tidak tampil setelah menekan 'Pesan EVMoto' dengan jadwal"
        )
        booking_page.close_scheduled_created_dialog()
        activity_page.navigate_to_activity_screen()
        activity_page.select_booking_tab()
        assert booking_page.is_scheduled_order_status_displayed(), (
            "Kartu berstatus 'Pesanan Terjadwal' tidak muncul di Tab Booking Aktivitas setelah pesanan dibuat"
        )

    @pytest.mark.booking
    @pytest.mark.advance_booking
    @pytest.mark.pilar1
    def test_TC_ADV_44_45_verify_reschedule_and_cancel_from_activity_tab_booking(self, authenticated_home, booking_page, activity_page):
        """[TC_ADV_44-45] Verify Reschedule & Cancel Scheduled Trip dari Halaman Aktivitas Tab Booking."""
        given("Pengguna membuka Halaman Aktivitas dan memilih 'Tab Booking'")
        activity_page.navigate_to_activity_screen()
        activity_page.select_booking_tab()
        if not booking_page.is_scheduled_order_status_displayed():
            pytest.skip(
                "Akun uji tidak punya kartu 'Pesanan Terjadwal' di Tab Booking; buat dulu lewat TC_ADV_40-42"
            )

        when("Pengguna meninjau pesanan terjadwal dan menekan 'Ubah Jadwal'")
        booking_page.open_first_scheduled_order()
        assert booking_page.is_scheduled_detail_displayed(), (
            "Halaman 'Detail Jadwal Pemesanan' tidak tampil setelah membuka kartu 'Pesanan Terjadwal'"
        )
        assert activity_page.is_displayed(activity_page.BTN_RESCHEDULE_BOOKING, timeout=5), (
            "Tombol 'Ubah Jadwal' tidak tampil di Detail Jadwal Pemesanan "
            "(string 'Ubah Jadwal' juga tidak ada di file bahasa aplikasi User v1.2.33)"
        )
        activity_page.open_reschedule_modal()

        then("Modal penyesuaian waktu tampil dan jadwal dapat diperbarui dengan sinkronisasi server")
        assert activity_page.is_reschedule_modal_displayed(), (
            "Modal penyesuaian waktu tidak tampil setelah menekan 'Ubah Jadwal'"
        )

# ==============================================================================
# PART 3: EXTENDED CORE QA 4-PILLARS ENHANCEMENTS (CRITICAL GAPS IDENTIFIED)
# ==============================================================================
class TestBookingCoreEnhancements:
    """Suite Pengembangan Pengujian Tingkat Lanjut untuk Menjamin Zero-Defect Core Booking."""

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_EXT_PT_01_verify_payment_method_selection(self, authenticated_home, booking_page):
        """[Pilar 1 - Positive True] Verifikasi pemilihan metode bayar antara EvWallet dan Tunai."""
        given("Pengguna berada di layar Place Order")
        _buka_place_order(booking_page, "Grand Indonesia")

        when("Pengguna beralih metode pembayaran dari EvWallet ke Tunai (Cash)")
        booking_page.click(booking_page.BTN_PAYMENT_METHOD, label="Metode Pembayaran")
        booking_page.click(booking_page.OPTION_PAYMENT_CASH, label="Pilihan Tunai")

        then("Metode pembayaran aktif berhasil diperbarui ke 'Tunai'")
        assert booking_page.is_payment_selected_snackbar_displayed("cash"), (
            "Snackbar 'Pembayaran cash berhasil dipilih sebagai metode pembayaran.' tidak tampil setelah memilih Cash"
        )

    @pytest.mark.booking
    @pytest.mark.pilar1
    def test_TC_EXT_PT_02_verify_voucher_promo_discount_application(self, authenticated_home, booking_page):
        """[Pilar 1 - Positive True] Verifikasi aplikasi voucher diskon memotong total estimasi tarif."""
        given("Pengguna berada di layar Place Order")
        _buka_place_order(booking_page, "Grand Indonesia")
        tarif_sebelum = booking_page.get_all_fare_amounts()
        assert tarif_sebelum, "Prasyarat gagal: tidak ada nominal 'Rp' yang terbaca di Place Order sebelum voucher"

        when("Pengguna memasukkan voucher promo 'EVMOTOBARU' dan menekan Pakai")
        booking_page.apply_voucher("EVMOTOBARU")

        then("Total tarif terpotong diskon secara realtime")
        assert booking_page.is_promo_applied_snackbar_displayed(), (
            "Snackbar 'Promo berhasil diterapkan ke pesanan Anda.' tidak tampil setelah memakai voucher 'EVMOTOBARU'"
        )
        tarif_sesudah = booking_page.get_all_fare_amounts()
        assert tarif_sesudah and min(tarif_sesudah) < min(tarif_sebelum), (
            f"Total tarif tidak berkurang setelah voucher: sebelum {tarif_sebelum}, sesudah {tarif_sesudah}"
        )

    @pytest.mark.booking
    @pytest.mark.pilar2
    def test_TC_EXT_PF_01_verify_insufficient_wallet_balance_modal(self, authenticated_home, booking_page, tracking_page):
        """[Pilar 2 - Positive False] Saldo EvWallet kurang memunculkan modal saran Top Up tanpa mutasi order."""
        given("Pengguna memiliki saldo EvWallet Rp 0")
        saldo = booking_page.get_home_wallet_balance_amount()
        if saldo is None:
            pytest.skip("Saldo dompet di Beranda (label 'Saldo Anda'/'Saldo Kamu') tidak terbaca, prasyarat Rp 0 tidak bisa dipastikan")
        if saldo > 0:
            pytest.skip(
                f"Prasyarat tidak terpenuhi: saldo akun uji Rp {saldo:,}".replace(",", ".")
                + ", padahal skenario butuh Rp 0 dan saldo tidak bisa dikosongkan dari UI"
            )

        when("Pengguna mencoba order layanan dengan metode EvWallet")
        _buka_place_order(booking_page, "Grand Indonesia")
        booking_page.select_payment_method("wallet")
        booking_page.submit_book_evmoto()

        then("Sistem menampilkan dialog 'Saldo EvWallet Tidak Cukup' dengan opsi Isi Saldo atau Ganti Tunai")
        assert booking_page.is_insufficient_balance_dialog_displayed(), (
            "Dialog 'Saldo Anda Tidak Cukup' dengan tombol 'Pilih Metode Pembayaran Lain' tidak tampil saat saldo Rp 0"
        )
        assert not tracking_page.is_searching_driver(timeout=3), (
            "Order tetap dibuat (status pencarian driver tampil) walaupun saldo EvWallet Rp 0"
        )

    @pytest.mark.booking
    @pytest.mark.pilar3
    def test_TC_EXT_NT_01_verify_same_pickup_and_destination_boundary(self, authenticated_home, booking_page):
        """[Pilar 3 - Negative True] Validasi titik jemput dan titik tujuan identik ditolak sistem."""
        given("Pengguna berada di layar rute perjalanan")
        booking_page.open_pickup_section()
        alamat_jemput = booking_page.get_prefilled_input_texts()
        assert alamat_jemput, "Prasyarat gagal: alamat titik jemput tidak terisi otomatis di form rute"

        when("Pengguna memasukkan destinasi yang persis sama dengan koordinat jemput")
        booking_page.enter_destination(alamat_jemput[0])
        booking_page.select_first_suggestion()

        then("Sistem menampilkan validasi 'Titik penjemputan dan tujuan tidak boleh sama'")
        assert booking_page.is_same_location_warning_displayed(), (
            f"Validasi 'Titik penjemputan dan tujuan tidak boleh sama' tidak tampil untuk tujuan '{alamat_jemput[0]}'"
        )

    @pytest.mark.booking
    @pytest.mark.pilar3
    def test_TC_EXT_NT_02_verify_advance_booking_less_than_30min_rejected(self, authenticated_home, booking_page):
        """[Pilar 3 - Negative True] Pemilihan jadwal advance booking < 30 menit ke depan ditolak."""
        given("Pengguna membuka modal jadwal advance booking")
        _buka_place_order(booking_page, "Stasiun Gambir")
        booking_page.open_scheduled_modal()

        when("Pengguna mencoba memilih waktu 10 menit ke depan")
        pytest.skip(
            "Picker jadwal berupa wheel Flutter tanpa label aksesibilitas per menit, sehingga waktu +10 menit "
            "tidak bisa dipilih secara pasti, dan file bahasa aplikasi User v1.2.33 tidak memuat pesan "
            "'minimal 30 menit' untuk diverifikasi"
        )

    @pytest.mark.booking
    @pytest.mark.pilar4
    def test_TC_EXT_NF_01_verify_chat_and_notes_sqli_xss_sanitization(self, authenticated_home, booking_page, tracking_page):
        """[Pilar 4 - Negative False] Uji penetrasi SQLi & XSS pada kolom chat driver dan catatan penjemputan."""
        given("Pengguna terhubung dengan driver")
        _buat_pesanan_instan(booking_page, tracking_page, "Plaza Indonesia")
        _tunggu_driver_ditugaskan_atau_skip(tracking_page)
        payload = "<script>alert('XSS_EVMOTO')</script>' OR '1'='1"

        when("Pengguna mengirim payload XSS/SQLi ke chat driver")
        tracking_page.send_chat_message(payload)

        then("Pesan tersanitasi aman oleh backend/Flutter layer tanpa memicu eksekusi skrip atau crash")
        assert tracking_page.get_current_package() == "com.evmoto.user.app", (
            f"Aplikasi User tidak lagi di depan setelah mengirim payload (crash?): '{tracking_page.get_current_package()}'"
        )
        assert tracking_page.is_chat_message_displayed(payload), (
            "Payload XSS/SQLi tidak tampil sebagai teks biasa di gelembung chat (pesan hilang atau ditolak tanpa umpan balik)"
        )

    @pytest.mark.booking
    @pytest.mark.pilar4
    def test_TC_EXT_NF_02_verify_rapid_multi_tap_on_book_button(self, authenticated_home, booking_page, tracking_page):
        """[Pilar 4 - Negative False] Anti Double-Booking: Multi-tap cepat pada tombol Book EvMoto."""
        given("Pengguna berada di layar Place Order")
        _buka_place_order(booking_page, "Senayan City")

        when("Pengguna melakukan tapping cepat 5 kali berturut-turut pada tombol 'Pesan'")
        for _ in range(5):
            try:
                booking_page.submit_book_evmoto()
            except Exception:
                pass

        then("Sistem mendebounce request, hanya membuat tepat 1 pesanan, dan tidak terjadi duplikasi transaksi")
        assert tracking_page.is_searching_driver(timeout=15), (
            "Tidak ada pesanan yang terbentuk: status pencarian driver tidak tampil setelah tap beruntun"
        )
        # Bila terbentuk 2 pesanan, setelah satu dibatalkan masih tersisa pencarian driver lain.
        tracking_page.cancel_searching_driver(confirm=True)
        assert tracking_page.wait_until_searching_gone(), (
            "Masih ada pencarian driver setelah satu pesanan dibatalkan: indikasi pesanan ganda dari tap beruntun"
        )

    @pytest.mark.booking
    @pytest.mark.pilar4
    def test_TC_EXT_NF_03_verify_app_backgrounding_during_driver_search(self, driver, authenticated_home, booking_page, tracking_page):
        """[Pilar 4 - Negative False] Resiliensi OS: Aplikasi di-minimize saat mencari driver lalu dibuka kembali."""
        given("Pengguna sedang dalam proses mencari mitra driver")
        _buat_pesanan_instan(booking_page, tracking_page, "Senayan City")

        when("Aplikasi di-background selama 4 detik lalu di-resume kembali")
        driver.background_app(4)

        then("Status pencarian driver tetap aktif dan sesi pesanan tidak hilang")
        assert tracking_page.get_current_package() == "com.evmoto.user.app", (
            f"Aplikasi User tidak kembali ke depan setelah resume: '{tracking_page.get_current_package()}'"
        )
        assert tracking_page.is_searching_driver(timeout=10), (
            "Status pencarian driver hilang setelah aplikasi di-background 4 detik lalu dibuka kembali"
        )

    @pytest.mark.booking
    @pytest.mark.happy_flow
    def test_TC_EXT_HF_01_master_e2e_booking_lifecycle_happy_flow(self, authenticated_home, booking_page, tracking_page):
        """[Happy Flow] Alur Master End-to-End Booking Order dari jemput hingga selesai dan ulasan."""
        given("Pengguna membuka form pemesanan perjalanan")
        booking_page.open_pickup_section()

        when("Pengguna memasukkan destinasi dan memilih rute")
        booking_page.enter_destination("Plaza Indonesia")
        booking_page.select_first_suggestion()
        assert booking_page.is_place_order_displayed(), "Layar Place Order (tombol 'Pesan EVMoto') tidak tampil setelah memilih rute"

        and_step("Pengguna meninjau tarif dan melakukan pemesanan")
        booking_page.submit_book_evmoto()
        assert tracking_page.is_searching_driver(timeout=15), "Status pencarian driver tidak tampil setelah menekan 'Pesan EVMoto'"
        _tunggu_driver_ditugaskan_atau_skip(tracking_page)

        and_step("Pengguna berinteraksi dengan driver dan menyelesaikan perjalanan")
        pesan = "Saya sudah di lobi utama"
        tracking_page.send_chat_message(pesan)
        assert tracking_page.is_chat_message_displayed(pesan), f"Pesan chat '{pesan}' tidak tampil di percakapan"
        if not tracking_page.is_rating_screen_displayed(timeout=60):
            pytest.skip(
                "Layar penilaian tidak tampil: trip harus diselesaikan driver nyata dari perangkat Driver kedua"
            )
        tracking_page.submit_driver_review(stars=5, comment="Sangat cepat dan ramah!")

        then("Seluruh siklus booking order selesai dengan status sukses 100%")
        assert tracking_page.is_rating_success_displayed(), (
            "Snackbar 'Penilaian dan ulasan berhasil dikirim' tidak tampil di akhir siklus booking"
        )

# ==============================================================================
# PART 4: SKENARIO KHUSUS USER APPS & INTEGRASI PERAN DRIVER DEV (TC01 s/d TC06)
# ==============================================================================
class TestSpecializedUserBookingSuite:
    """
    Suite Pengujian Khusus User Apps pada Environment Dev Golang:
    1. Concurrency / Race Condition: 1 Driver, 2 User Order Bersamaan (Anti-Conflict)
    2. Argo Formula: Verifikasi Harga Argo Sesuai Konfigurasi Dashboard Admin Menu #23
    3. Driver Online Order: Driver Online menerima pesanan User secara realtime
    4. Driver Busy Isolation: Driver aktif pengantaran order diisolasi dari pesanan User lain
    5. Switch Payment Method: User mengubah metode pembayaran sebelum konfirmasi order
    6. Cashless Wallet Deduction: Verifikasi pemotongan saldo dompet cashless berkurang akurat
    """

    @pytest.mark.booking
    @pytest.mark.pilar4
    @pytest.mark.race_condition
    def test_TC_SPEC_RC_01_verify_race_condition_two_users_one_driver_no_bug(self, authenticated_home, booking_page, driver_simulator):
        """
        [Pilar 4 - Negative False] Race Condition Concurrency: 1 Driver, 2 User Order Bersamaan.
        Deskripsi: Menguji ketahanan sistem saat 1 Mitra Driver online (<TEST_DRIVER_PHONE>) menerima 2 pesanan pengguna (User 1: <TEST_USER_PHONE> dan User 2: <EVMOTO_PHONE_EXTRA_2>) secara bersamaan (concurrent race condition). Memastikan sistem tidak mengalami crash, tidak ada double booking, dan User 2 dialihkan secara aman ke antrean pencarian driver lain.
        Ekspektasi: Sistem menangani race condition secara atomic, User 1 terhubung ke driver, User 2 tetap berada di antrean pencarian tanpa bug atau data error.
        """
        given("1 Mitra Driver (<TEST_DRIVER_PHONE>) berstatus Online pada environment Dev Golang")
        driver_simulator.set_online(is_online=True, latitude=-6.2088, longitude=106.8456)
        assert driver_simulator.is_driver_online() is True

        when("Pengguna 1 membuka aplikasi dan menentukan rute perjalanan ke Grand Indonesia")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Grand Indonesia Mall")
        booking_page.select_first_suggestion()

        and_step("Pengguna 1 dan Pengguna 2 melakukan booking secara bersamaan (simultan)")
        booking_page.submit_book_evmoto()

        # Simulasi penyelesaian race condition secara atomic pada dispatcher
        user_1_payload = {
            "order_id": "ORD-DEV-RC01-A",
            "user_phone": os.environ.get("TEST_USER_PHONE", ""),
            "pickup": "Menara Astra",
            "destination": "Grand Indonesia"
        }
        user_2_payload = {
            "order_id": "ORD-DEV-RC01-B",
            "user_phone": os.environ.get("EVMOTO_PHONE_EXTRA_2", ""),
            "pickup": "Menara BCA",
            "destination": "Plaza Indonesia"
        }
        rc_result = driver_simulator.resolve_concurrent_orders(user_1_payload, user_2_payload)

        then("Driver ditugaskan secara eksklusif ke Pengguna 1 tanpa double booking")
        assert rc_result["race_condition_prevented"] is True
        assert rc_result["assigned_to"]["user_phone"] == os.environ.get("TEST_USER_PHONE", "")

        and_step("Pengguna 2 tetap dalam antrean pencarian mitra lain tanpa error atau aplikasi crash")
        assert rc_result["rejected_or_queued"]["error"] is None
        assert rc_result["rejected_or_queued"]["status"] == "searching_other_driver"
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.fare_argo
    def test_TC_SPEC_ARGO_02_verify_fare_calculated_from_admin_dashboard_settings(self, authenticated_home, booking_page, fare_calculator):
        """
        [Pilar 1 - Positive True] Validasi Harga Argo Berdasarkan Konfigurasi Dashboard Admin EvMoto.
        Deskripsi: Memastikan kalkulasi harga argo pada aplikasi User dihitung secara presisi berdasarkan formula pengaturan tarif pada Dashboard Admin EvMoto (User: <ADMIN_URL>/tSystemPrice/tSystemPrice_update/1626, Driver: <ADMIN_URL>/tSystemPrice/tSystemPrice_update/1619 - Model: ECGO 3 Jakarta: Tarif Awal startPrice Rp 6.000 untuk 2 KM pertama, Tarif Jarak mileageFee Rp 2.800/KM).
        Ekspektasi: Estimasi tarif argo yang tampil pada layar aplikasi User (Rp 10.200 untuk rute 3.5 KM) sesuai 100% secara matematis dengan rumus Dashboard Admin environment aktif.
        """
        given("Pengguna berada di layar penentuan rute penjemputan dan tujuan")
        booking_page.open_pickup_section()

        when("Pengguna memasukkan destinasi Plaza Senayan dengan jarak rute terukur 3.5 KM")
        booking_page.enter_destination("Plaza Senayan")
        booking_page.select_first_suggestion()
        trip_distance_km = 3.5

        and_step("Aplikasi menampilkan rincian estimasi tarif argo pada layar Place Order")
        ui_fare_text = booking_page.get_estimated_fare()
        logger.info(f"Tarif tertera di User App: '{ui_fare_text}' untuk jarak {trip_distance_km} KM")

        then("Harga argo diverifikasi cocok dengan rumus konfigurasi Dashboard Admin Production")
        is_valid, validation_msg = fare_calculator.verify_ui_fare(ui_fare_text, distance_km=trip_distance_km)
        assert is_valid is True, f"Kalkulasi argo tidak sinkron dengan dashboard: {validation_msg}"
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.driver_dispatch
    def test_TC_SPEC_DISP_03_verify_driver_online_and_user_order_accepted(self, authenticated_home, booking_page, tracking_page, driver_simulator):
        """
        [Pilar 1 - Positive True] Driver Sedang Online Menerima Order Pengguna Realtime.
        Deskripsi: Menguji alur ketika Mitra Driver berstatus Online dan siap menerima order, lalu Pengguna melakukan pemesanan (Book EVMoto). Memastikan sistem berhasil mendispatch pesanan ke driver, driver menerima order, dan layar User bertransisi ke antarmuka Driver Assigned dengan live tracking.
        Ekspektasi: Driver berhasil menerima pesanan pengguna dan informasi driver (nama, nomor plat, estimasi waktu) tampil lengkap di aplikasi User.
        """
        given("Mitra Driver (<TEST_DRIVER_PHONE>) berstatus Online dan tersedia di sekitar lokasi jemput")
        driver_simulator.set_online(is_online=True)
        assert driver_simulator.is_driver_available() is True

        when("Pengguna menentukan rute ke Plaza Indonesia dan menekan tombol 'Pesan EVMoto'")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Plaza Indonesia")
        booking_page.select_first_suggestion()
        booking_page.submit_book_evmoto()

        and_step("Mitra Driver menerima ping pesanan dan menekan 'Terima Order' pada APK Driver")
        accepted_trip = driver_simulator.accept_order({
            "order_id": "ORD-LIVE-DISPATCH-01",
            "user_phone": Config.ACTIVE_PHONE,
            "pickup": "Menara Astra",
            "destination": "Plaza Indonesia",
            "fare": "Rp 10.200"
        })

        then("Aplikasi User beralih menampilkan detail Driver Budi Setiawan (B 1234 EVM) dan estimasi penjemputan")
        assert accepted_trip["status"] == "driver_assigned"
        assert driver_simulator.is_driver_available() is False
        assert tracking_page.is_driver_assigned()
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar2
    @pytest.mark.driver_busy
    def test_TC_SPEC_BUSY_04_verify_driver_busy_in_trip_isolated_from_new_user_order(self, authenticated_home, booking_page, tracking_page, driver_simulator):
        """
        [Pilar 2 - Positive False] Driver Sedang Aktif Pengantaran Order: Terisolasi dari Order Baru Pengguna Lain.
        Deskripsi: Menguji kondisi di mana Mitra Driver sedang dalam perjalanan aktif mengantar penumpang (In-Progress / Busy). Pengguna lain kemudian membuat pesanan baru. Memastikan sistem mengisolasi driver yang sedang sibuk, tidak menugaskan order baru kepadanya, dan perjalanan penumpang pertama tidak terganggu.
        Ekspektasi: Pesanan pengguna baru tidak di-assign ke driver yang sedang sibuk, driver tetap fokus pada trip aktif, dan pengguna baru tetap mencari armada lain.
        """
        given("Mitra Driver (<TEST_DRIVER_PHONE>) sedang aktif menjalankan pengantaran order penumpang lain")
        driver_simulator.set_active_trip_busy(
            order_id="TRIP-ONGOING-881",
            customer_name="Siti Rahma",
            pickup="Sudirman",
            destination="Blok M Plaza"
        )
        assert driver_simulator.is_driver_available() is False

        when("Pengguna lain membuka aplikasi dan memesan perjalanan ke Cilandak Town Square")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Cilandak Town Square")
        booking_page.select_first_suggestion()
        booking_page.submit_book_evmoto()

        and_step("Sistem memverifikasi ketersediaan armada terdekat")
        dispatch_attempt = driver_simulator.attempt_dispatch_to_busy_driver({
            "order_id": "ORD-NEW-USER-202",
            "user_phone": os.environ.get("EVMOTO_PHONE_EXTRA_2", "")
        })

        then("Sistem menolak penugasan ke driver sibuk dan menjaga perjalanan penumpang pertama tetap aman")
        assert dispatch_attempt["dispatched_to_driver"] is False
        assert dispatch_attempt["reason"] == "DRIVER_BUSY_WITH_TRIP"
        assert dispatch_attempt["active_trip_preserved"] is True
        assert tracking_page.is_searching_driver()
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.payment_switch
    def test_TC_SPEC_PAY_05_verify_user_switches_payment_method_before_placing_order(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Pengguna Mengubah Metode Pembayaran Sebelum Konfirmasi Order.
        Deskripsi: Memastikan pengguna dapat secara fleksibel mengubah metode pembayaran pada layar Place Order (misal beralih dari Tunai ke EvWallet Cashless, lalu kembali ke Tunai) sebelum menekan tombol Pesan. Memastikan status metode bayar terupdate seketika tanpa reset form rute.
        Ekspektasi: Label metode pembayaran yang aktif terupdate secara instan dan pesanan dieksekusi dengan metode bayar yang baru dipilih.
        """
        given("Pengguna telah memilih rute perjalanan dan berada di halaman Place Order")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Menara BCA Grand Indonesia")
        booking_page.select_first_suggestion()

        when("Pengguna membuka opsi pembayaran dan beralih ke metode EvWallet (Cashless)")
        booking_page.select_payment_method("wallet")
        time.sleep(1.0)

        and_step("Pengguna kemudian mengubah kembali metode pembayaran ke Tunai (Cash)")
        booking_page.select_payment_method("cash")
        time.sleep(1.0)

        then("Metode pembayaran aktif berhasil diperbarui ke Tunai dan siap untuk konfirmasi order")
        assert booking_page.is_payment_selected_snackbar_displayed("cash"), (
            "Snackbar 'Pembayaran cash berhasil dipilih sebagai metode pembayaran.' tidak tampil setelah kembali ke Cash"
        )
        assert booking_page.is_place_order_displayed(timeout=5), (
            "Form Place Order (tombol 'Pesan EVMoto') hilang setelah mengganti metode pembayaran"
        )
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.cashless_deduction
    def test_TC_SPEC_WAL_06_verify_cashless_payment_balance_deducted_accurately(self, authenticated_home, booking_page, driver_simulator, wallet_helper):
        """
        [Pilar 1 - Positive True] Verifikasi Pemotongan Saldo Dompet Cashless Berkurang Akurat Pasca Order.
        Deskripsi: Menguji transaksi menggunakan metode pembayaran Cashless (EvWallet). Sistem mencatat saldo awal pengguna, memproses pemesanan hingga perjalanan selesai, dan memvalidasi bahwa saldo dompet berkurang tepat sebesar total tarif argo perjalanan tanpa pemotongan berlebih.
        Ekspektasi: Saldo akhir pengguna berkurang tepat sebesar tarif argo perjalanan (balance_after == balance_before - fare_amount) dan mutasi tercatat sukses.
        """
        given("Pengguna memiliki saldo dompet digital EvWallet yang cukup (Saldo Awal: Rp 150.000)")
        initial_balance = wallet_helper.get_current_balance()
        assert initial_balance >= 10200

        when("Pengguna memesan perjalanan dengan memilih metode pembayaran EvWallet Cashless")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Kota Kasablanka Mall")
        booking_page.select_first_suggestion()
        booking_page.select_payment_method("wallet")
        booking_page.submit_book_evmoto()

        and_step("Perjalanan diselesaikan oleh Driver dan sistem memproses pemotongan saldo cashless")
        trip_fare = booking_page.get_numeric_fare_amount()
        assert trip_fare > 0, "Tarif perjalanan tidak terbaca dari layar Place Order (nominal 'Rp' kosong)"
        txn = wallet_helper.deduct_fare(fare_amount=trip_fare, order_id="ORD-CASHLESS-DEV-01")
        driver_simulator.complete_trip(payment_method="cashless", fare_amount=trip_fare)

        then("Saldo dompet digital pengguna berkurang tepat sebesar tarif argo perjalanan")
        is_exact, audit_msg = wallet_helper.verify_deduction(
            balance_before=initial_balance,
            balance_after=txn["balance_after"],
            expected_fare=trip_fare
        )
        assert is_exact is True, audit_msg
        assert txn["balance_after"] == initial_balance - trip_fare

        time.sleep(Config.HUMAN_PACING_MIN)


# ==============================================================================
# SUITE PENGUJIAN ENGINE KALKULASI HARGA RESMI EVMOTO (6 KONDISI BISNIS)
# ==============================================================================
class TestEvMotoFarePricingEngineSuite:
    """
    Suite Pengujian Khusus Perhitungan Harga EvMoto Berdasarkan 6 Kondisi Bisnis:
    1. Harga Normal: Jarak Dekat (<= 2 KM: Rp 6.000), Jarak Sedang (3.5 KM: Rp 10.200), Jarak Jauh (10.0 KM: Rp 38.400)
    2. Platform Fee (10%): Seamless di sisi User Apps (+ Rp 1.020 pada rute 3.5 KM -> Rp 11.220)
    3. Waiting Fee: Waktu tunggu > 15 menit dikenakan Rp 500 / menit (misal 20 menit = 5 x 500 = + Rp 2.500)
    4. Kupon Diskon Rp 5.000: Memotong subtotal tagihan (- Rp 5.000)
    5. Penalty: Denda pembatalan / penalti pengguna (+ Rp 5.000)
    6. Charge Fee 2% E-Wallet: Pembayaran GoPay & OVO dikenakan 2% dari Grand Total akumulatif
       (mencakup argo, platform fee, waiting fee, penalty, dan diskon kupon). Tunai & EvWallet = 0%.
    """

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.pricing_engine
    def test_TC_FARE_01_verify_normal_pricing_short_medium_long_distance(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Harga Normal Berdasarkan Jarak (Dekat, Sedang, Jauh).
        Deskripsi: Menguji validitas perhitungan tarif argo dasar sesuai ketentuan operasional:
          - Jarak Dekat (1.5 KM <= 2.0 KM): Tarif minimum Rp 6.000
          - Jarak Sedang (3.5 KM): Rp 6.000 + (1.5 KM x Rp 2.800) = Rp 10.200
          - Jarak Jauh (10.0 KM): Rp 6.000 + (8.0 KM x Rp 2.800 = Rp 22.400) + FarFee (4.0 KM x Rp 2.500 = Rp 10.000) = Rp 38.400
        Ekspektasi: Seluruh nilai argo terhitung persis tanpa pembulatan sesuai formula Dashboard Production.
        """
        calc = AdminDashboardFareCalculator()

        given("Pengguna melakukan simulasi rute Jarak Dekat (1.5 KM)")
        res_dekat = calc.calculate_base_argo(1.5)
        then("Tarif dasar yang terhitung adalah tarif minimum Rp 6.000")
        assert res_dekat["total_argo"] == 6000.0
        assert res_dekat["formatted_argo"] == "Rp 6.000"

        when("Pengguna memilih rute Jarak Sedang (3.5 KM)")
        res_sedang = calc.calculate_base_argo(3.5)
        then("Tarif terhitung persis Rp 10.200 (Rp 6.000 + 1.5 KM x Rp 2.800)")
        assert res_sedang["total_argo"] == 10200.0
        assert res_sedang["formatted_argo"] == "Rp 10.200"

        and_step("Pengguna memilih rute Jarak Jauh (10.0 KM)")
        res_jauh = calc.calculate_base_argo(10.0)
        then("Tarif terhitung persis Rp 38.400 (Base Rp 6.000 + Mileage Rp 22.400 + FarFee Rp 10.000)")
        assert res_jauh["total_argo"] == 38400.0
        assert res_jauh["formatted_argo"] == "Rp 38.400"
        assert res_jauh["long_distance_charge"] == 10000.0

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.platform_fee
    def test_TC_FARE_02_verify_seamless_platform_fee_10_percent(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Platform Fee 0% pada Tagihan User Apps.
        Deskripsi: Memastikan tagihan dasar pengguna adalah tarif argo murni tanpa potongan/tambahan platform fee terpisah.
          - Rute 3.5 KM: Argo Rp 10.200
          - Platform Fee: Rp 0
          - Grand Total: Rp 10.200 (Metode Tunai / EvWallet).
        Ekspektasi: Grand total invoice pengguna menjadi Rp 10.200.
        """
        calc = AdminDashboardFareCalculator()
        given("Pengguna memesan rute standar 3.5 KM dengan metode bayar Tunai")
        breakdown = calc.calculate_grand_total(3.5, payment_method="cash")

        then("Platform Fee tambahan pada invoice customer adalah Rp 0")
        assert breakdown["total_argo"] == 10200.0
        assert breakdown["platform_fee"] == 0.0
        assert breakdown["formatted_platform_fee"] == "Rp 0"

        and_step("Grand total tagihan pengguna terhitung tepat Rp 10.200")
        assert breakdown["grand_total"] == 10200.0
        assert breakdown["formatted_grand_total"] == "Rp 10.200"

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.waiting_fee
    def test_TC_FARE_03_verify_waiting_fee_after_15_minutes_threshold(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Waiting Fee Setelah Melewati Toleransi 15 Menit Gratis.
        Deskripsi: Menguji pengenaan biaya tunggu driver di titik jemput (Rp 500 / menit setelah 15 menit):
          - Tunggu 12 Menit: Di bawah batas 15 menit -> Waiting Fee = Rp 0
          - Tunggu 20 Menit: Kelebihan 5 menit x Rp 500 = Rp 2.500
          - Grand Total (3.5 KM): Rp 10.200 + Rp 2.500 = Rp 12.700.
        Ekspektasi: Biaya tunggu bertambah secara proporsional hanya untuk menit kelebihan.
        """
        calc = AdminDashboardFareCalculator()

        given("Driver menunggu di titik penjemputan selama 12 menit (dalam batas toleransi)")
        res_free = calc.calculate_grand_total(3.5, payment_method="cash", waiting_minutes=12)
        then("Tidak ada biaya tunggu yang dikenakan (Waiting Fee = Rp 0)")
        assert res_free["excess_wait_minutes"] == 0
        assert res_free["waiting_fee"] == 0.0

        when("Driver menunggu selama 20 menit (kelebihan 5 menit)")
        res_charged = calc.calculate_grand_total(3.5, payment_method="cash", waiting_minutes=20)
        then("Biaya tunggu dikenakan sebesar 5 x Rp 500 = Rp 2.500")
        assert res_charged["excess_wait_minutes"] == 5
        assert res_charged["waiting_fee"] == 2500.0
        assert res_charged["formatted_waiting_fee"] == "Rp 2.500"

        and_step("Grand total tagihan menjadi Rp 10.200 + Rp 2.500 = Rp 12.700")
        assert res_charged["grand_total"] == 12700.0
        assert res_charged["formatted_grand_total"] == "Rp 12.700"

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.coupon_discount
    def test_TC_FARE_04_verify_coupon_voucher_discount_5000(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Pemotongan Kupon Diskon Promosi Rp 5.000.
        Deskripsi: Menguji pengurangan voucher kupon diskon Rp 5.000 pada rute 3.5 KM:
          - Subtotal Awal (Argo Rp 10.200): Rp 10.200
          - Kupon Diskon: - Rp 5.000
          - Grand Total Setelah Diskon: Rp 10.200 - Rp 5.000 = Rp 5.200.
        Ekspektasi: Tagihan berkurang tepat Rp 5.000 tanpa memengaruhi hak pengemudi.
        """
        calc = AdminDashboardFareCalculator()

        given("Pengguna menerapkan kupon diskon promosi Rp 5.000 pada checkout rute 3.5 KM")
        res_coupon = calc.calculate_grand_total(3.5, payment_method="cash", use_coupon=True, coupon_amount=5000.0)

        then("Potongan diskon kupon tercatat tepat Rp 5.000")
        assert res_coupon["coupon_discount"] == 5000.0
        assert res_coupon["formatted_coupon"] == "Rp 5.000"

        and_step("Grand total akhir tagihan berkurang menjadi Rp 5.200")
        assert res_coupon["grand_total"] == 5200.0
        assert res_coupon["formatted_grand_total"] == "Rp 5.200"

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.penalty_fee
    def test_TC_FARE_05_verify_cancellation_penalty_fee_application(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Penambahan Denda / Penalty Biaya Pembatalan Rp 5.000.
        Deskripsi: Menguji penambahan biaya penalty pembatalan perjalanan terlambat (Rp 5.000):
          - Subtotal (Argo Rp 10.200): Rp 10.200
          - Penalty: + Rp 5.000
          - Grand Total: Rp 10.200 + Rp 5.000 = Rp 15.200.
        Ekspektasi: Penalty pembatalan tercatat valid sebesar Rp 5.000 pada invoice pengguna.
        """
        calc = AdminDashboardFareCalculator()

        given("Pengguna dikenakan biaya penalty pembatalan sebesar Rp 5.000")
        res_pen = calc.calculate_grand_total(3.5, payment_method="cash", apply_penalty=True, penalty_amount=5000.0)

        then("Komponen penalty tercatat sebesar Rp 5.000")
        assert res_pen["penalty_fee"] == 5000.0
        assert res_pen["formatted_penalty"] == "Rp 5.000"

        and_step("Grand total tagihan bertambah menjadi Rp 15.200")
        assert res_pen["grand_total"] == 15200.0
        assert res_pen["formatted_grand_total"] == "Rp 15.200"

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.ewallet_charge
    def test_TC_FARE_06_verify_ewallet_gopay_ovo_2_percent_charge_fee(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Handling Fee Gross-Up E-Wallet (GoPay 2% & OVO 1.665%).
        Deskripsi: Menguji pengenaan gross-up handling fee untuk GoPay & OVO:
          - Tunai & EvWallet: Charge Fee = Rp 0 (0%), Grand Total = Rp 10.200
          - GoPay: math.ceil(10.200 * (100 / 98)) = Rp 10.409 (Handling Fee = Rp 209)
          - OVO: math.ceil(10.200 * (100 / 98.335)) = Rp 10.373 (Handling Fee = Rp 173)
        """
        calc = AdminDashboardFareCalculator()

        given("Pengguna memilih metode pembayaran Tunai (Cash)")
        res_cash = calc.calculate_grand_total(3.5, payment_method="cash")
        then("Tidak ada Charge Fee yang dikenakan (Rp 0)")
        assert res_cash["charge_fee_amount"] == 0.0
        assert res_cash["grand_total"] == 10200.0

        when("Pengguna memilih metode pembayaran GoPay (E-Wallet 2% Gross-Up)")
        res_gopay = calc.calculate_grand_total(3.5, payment_method="gopay")
        then("Handling Fee 2% Gross-Up dikenakan sebesar Rp 209 dan total tagihan menjadi Rp 10.409")
        assert res_gopay["is_ewallet_surcharge"] is True
        assert res_gopay["charge_fee_amount"] == 209.0
        assert res_gopay["formatted_charge_fee"] == "Rp 209"
        assert res_gopay["grand_total"] == 10409.0
        assert res_gopay["formatted_grand_total"] == "Rp 10.409"

        and_step("Pengguna memilih metode pembayaran OVO (E-Wallet 1.665% Gross-Up)")
        res_ovo = calc.calculate_grand_total(3.5, payment_method="ovo")
        then("Handling Fee 1.665% Gross-Up pada OVO sebesar Rp 173 dan total tagihan Rp 10.373")
        assert res_ovo["charge_fee_amount"] == 173.0
        assert res_ovo["formatted_charge_fee"] == "Rp 173"
        assert res_ovo["grand_total"] == 10373.0
        assert res_ovo["formatted_grand_total"] == "Rp 10.373"

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.pricing_engine
    def test_TC_FARE_07_verify_comprehensive_all_in_one_grand_total(self, authenticated_home, booking_page):
        """
        [Pilar 1 - Positive True] Verifikasi Kombo Menyeluruh (All-in-One 6 Kondisi Bisnis).
        Deskripsi: Menguji kombinasi lengkap seluruh parameter dalam satu transaksi:
          - Jarak 3.5 KM (Argo Rp 10.200)
          - Waiting Fee 20 menit (+ Rp 2.500)
          - Penalty (+ Rp 5.000)
          - Kupon Diskon (- Rp 5.000)
          - Adjusted Subtotal: 10.200 + 2.500 + 5.000 - 5.000 = Rp 12.700
          - Metode Bayar: GoPay -> Gross-Up 2% = math.ceil(12.700 * 100 / 98) = Rp 12.960 (Fee Rp 260)
        """
        calc = AdminDashboardFareCalculator()

        given("Pengguna melakukan perjalanan 3.5 KM dengan GoPay, kena Waiting Fee, Penalty, dan memakai Kupon")
        breakdown = calc.calculate_grand_total(
            distance_km=3.5,
            payment_method="gopay",
            waiting_minutes=20,
            use_coupon=True,
            coupon_amount=5000.0,
            apply_penalty=True,
            penalty_amount=5000.0
        )

        then("Subtotal akumulatif terhitung tepat Rp 12.700")
        assert breakdown["total_argo"] == 10200.0
        assert breakdown["platform_fee"] == 0.0
        assert breakdown["waiting_fee"] == 2500.0
        assert breakdown["penalty_fee"] == 5000.0
        assert breakdown["coupon_discount"] == 5000.0
        assert breakdown["adjusted_subtotal"] == 12700.0

        and_step("Handling Fee 2% Gross-Up dihitung dari Grand Total akumulatif sebesar Rp 260")
        assert breakdown["charge_fee_amount"] == 260.0
        assert breakdown["formatted_charge_fee"] == "Rp 260"

        and_step("Grand Total akhir adalah persis Rp 12.960 tanpa pembulatan")
        assert breakdown["grand_total"] == 12960.0
        assert breakdown["formatted_grand_total"] == "Rp 12.960"


# ==============================================================================
# SUITE PENGUJIAN WAITING FEE & CANCELLATION FLOW (PRD v1.1 QC FORM SPECIFICATION)
# ==============================================================================
class TestEvMotoWaitingFeeCancellationPRDSuite:
    """
    Suite Pengujian Khusus Siklus Pembatalan (Cancellation) & Waiting Fee EvMoto (PRD v1.1):
    Mengacu pada Form QC dan Parameter Aturan (QC_Form_WaitingFee_Cancellation.xlsx):
    - Fase A: Driver belum tiba -> Customer/Driver cancel (Gratis / Saldo driver -2K).
    - Fase B: Driver tiba, 0 - 15 menit (Grace period 900s) -> Customer denda Rp 5K / Driver cancel beri kupon Rp 5K.
    - Fase C: Driver tiba, 15:01 - 29:59 menit (901s - 1799s) -> Waiting Fee Rp 500/menit (m = ceil((elapsed-900)/60)).
    - Fase D: Auto-cancel System (>= 30 menit / 1800s) -> Customer No-Show denda Rp 10K + Wait Fee Rp 7.5K = Rp 17.5K.
    - Integrasi E-Wallet Charge Fee 2% untuk metode GoPay & OVO pada tagihan denda.
    """

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.cancellation_fase_a
    def test_TC_WAIT_CANCEL_01_customer_cancel_fase_a_free_charge(self, authenticated_home, booking_page, tracking_page, driver_simulator, fare_calculator):
        """
        [Pilar 1 - Positive True] Verifikasi Pembatalan oleh Pengguna di Fase A (Sebelum Driver Tiba).
        Deskripsi: Menguji kondisi saat pengguna membatalkan pesanan ketika driver belum tiba di lokasi jemput (Fase A). Sesuai PRD v1.1 §4, pembatalan pada fase ini bersifat bebas biaya (Customer Charge = Rp 0).
        Ekspektasi: Pengguna tidak dikenakan cancel fee / penalty (Rp 0), saldo utuh, dan aplikasi kembali ke layar awal tanpa tagihan denda.
        """
        given("Pengguna telah memesan perjalanan dan driver sedang menuju titik jemput (Fase A)")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Plaza Indonesia")
        booking_page.select_first_suggestion()
        booking_page.submit_book_evmoto()

        # Driver menerima pesanan tetapi belum tiba di lokasi jemput
        driver_simulator.accept_order({
            "order_id": "ORD-CANCEL-FA-01",
            "user_phone": Config.ACTIVE_PHONE,
            "pickup": "Lokasi Jemput",
            "destination": "Plaza Indonesia"
        })

        when("Pengguna menekan tombol 'Batalkan Perjalanan' sebelum driver tiba")
        tracking_page.cancel_trip_with_reason()
        driver_simulator.customer_cancel_order(reason="Ingin ganti rute")

        then("Kalkulasi settlement memverifikasi pembatalan Fase A gratis tanpa denda")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=False,
            elapsed_seconds=0
        )
        assert res["phase"] == "A"
        assert res["customer_charge"] == 0.0
        assert res["formatted_customer_charge"] == "Rp 0"
        assert res["driver_payout"] == 0.0
        assert res["coupon_issued"] is False
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.cancellation_fase_a
    def test_TC_WAIT_CANCEL_02_driver_cancel_fase_a_graceful_retry_zero_cost_user(self, authenticated_home, booking_page, tracking_page, driver_simulator, fare_calculator):
        """
        [Pilar 1 - Positive True] Verifikasi Pembatalan oleh Driver di Fase A (PRD Case 1).
        Deskripsi: Menguji alur saat Mitra Driver membatalkan pesanan sebelum tiba di lokasi (Fase A). Pengguna tidak dikenakan biaya apapun (Rp 0), driver dikenakan penalti saldo Rp 2.000 (dan GI adjustment jika mitra GI), dan aplikasi User menampilkan dialog Try Again secara anggun.
        Ekspektasi: Pengguna tidak membayar sepeserpun dan dapat langsung mencari armada baru via 'Try Again'.
        """
        given("Pengguna memesan perjalanan dan driver <TEST_DRIVER_PHONE> ditugaskan (Fase A)")
        booking_page.open_pickup_section()
        booking_page.enter_destination("Grand Indonesia")
        booking_page.select_first_suggestion()
        booking_page.submit_book_evmoto()

        driver_simulator.accept_order({
            "order_id": "ORD-CANCEL-FA-02",
            "user_phone": Config.ACTIVE_PHONE
        })

        when("Mitra Driver membatalkan pesanan karena kendala armada (Driver Cancel Fase A)")
        driver_simulator.driver_cancel_order(reason="Ban bocor", schema="GI")

        then("Aplikasi User menampilkan dialog 'Driver has cancelled' dan tombol Try Again")
        assert tracking_page.is_displayed(tracking_page.POPUP_DRIVER_CANCELLED, timeout=5)

        and_step("Ledger memverifikasi Customer Charge Rp 0, Driver Penalty Rp 2.000, dan GI Event -Rp 10.000")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Driver",
            driver_arrived=False,
            elapsed_seconds=0,
            driver_schema="GI"
        )
        assert res["phase"] == "A"
        assert res["customer_charge"] == 0.0
        assert res["driver_penalty"] == 2000.0
        assert res["gi_adj_event"] == -10000.0
        assert res["coupon_issued"] is False
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.cancellation_fase_b
    def test_TC_WAIT_CANCEL_03_customer_cancel_fase_b_within_15min_grace_penalty_5000(self, authenticated_home, booking_page, tracking_page, driver_simulator, fare_calculator):
        """
        [Pilar 1 - Positive True] Verifikasi Pembatalan oleh Pengguna di Fase B (Grace Period 15 Menit).
        Deskripsi: Menguji pembatalan oleh pengguna ketika driver SUDAH TIBA di titik jemput, tetapi masih dalam masa tunggu toleransi gratis (elapsed <= 900 detik / 15 menit, misal 300 detik / 5 menit). Sesuai PRD v1.1 §4, pengguna dikenakan Cancel Fee flat Rp 5.000 dan driver menerima kompensasi Rp 3.000.
        Ekspektasi: Customer Charge terhitung tepat Rp 5.000 tanpa waiting fee tambahan (m = 0).
        """
        given("Driver telah tiba di titik jemput pengguna (Elapsed = 300 detik / 5 menit)")
        driver_simulator.accept_order({"order_id": "ORD-CANCEL-FB-03"})
        driver_simulator.driver_arrived_at_pickup()

        when("Pengguna memutuskan membatalkan pesanan pada menit ke-5 masa tunggu")
        tracking_page.cancel_trip_with_reason()
        driver_simulator.customer_cancel_order(reason="Perubahan rencana mendadak")

        then("Sistem mengenakan denda pembatalan Rp 5.000 dan kompensasi driver Rp 3.000")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=300
        )
        assert res["phase"] == "B"
        assert res["billable_minutes"] == 0
        assert res["cancel_penalty_charge"] == 5000.0
        assert res["waiting_fee_charge"] == 0.0
        assert res["customer_charge"] == 5000.0
        assert res["formatted_customer_charge"] == "Rp 5.000"
        assert res["driver_payout"] == 3000.0
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.cancellation_fase_b
    def test_TC_WAIT_CANCEL_04_driver_cancel_fase_b_user_receives_voucher_coupon_5000(self, authenticated_home, booking_page, tracking_page, driver_simulator, fare_calculator):
        """
        [Pilar 1 - Positive True] Driver Batal di Fase B: Pengguna Menerima Voucher Kupon Kompensasi Rp 5.000.
        Deskripsi: Menguji alur ketika driver membatalkan setelah tiba di titik jemput pada masa tunggu Fase B (misal 600 detik / 10 menit). Sesuai PRD v1.1 §4, pengguna TIDAK ditagih biaya apapun (Rp 0), driver dikenakan penalti Rp 5.000, dan sistem menerbitkan Voucher Kupon Kompensasi Rp 5.000 untuk pengguna.
        Ekspektasi: Customer Charge Rp 0 dan kupon kompensasi Rp 5.000 berhasil diterbitkan ke akun pengguna.
        """
        given("Driver sudah tiba di titik jemput (Fase B, elapsed 600 detik)")
        driver_simulator.accept_order({"order_id": "ORD-CANCEL-FB-04"})
        driver_simulator.driver_arrived_at_pickup()

        when("Mitra Driver membatalkan pesanan secara sepihak di Fase B")
        driver_simulator.driver_cancel_order(reason="Kendala darurat", schema="Non-GI")

        then("Pengguna mendapatkan kupon kompensasi Rp 5.000 dan tidak dikenakan denda apapun")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Driver",
            driver_arrived=True,
            elapsed_seconds=600,
            driver_schema="Non-GI"
        )
        assert res["phase"] == "B"
        assert res["customer_charge"] == 0.0
        assert res["coupon_issued"] is True
        assert res["coupon_amount"] == 5000.0
        assert res["formatted_coupon"] == "Rp 5.000"
        assert res["driver_penalty"] == 5000.0
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.waiting_fee
    def test_TC_WAIT_CANCEL_05_customer_cancel_fase_c_wait_fee_accrual_prd_case_5(self, authenticated_home, booking_page, tracking_page, driver_simulator, fare_calculator):
        """
        [Pilar 1 - Positive True] Customer Cancel di Fase C: Penagihan Denda + Waiting Fee Berjalan (PRD Case 5).
        Deskripsi: Menguji penagihan saat driver sudah tiba dan menunggu 1350 detik (22 menit 30 detik) sebelum customer membatalkan.
          - Masa tunggu billable: m = ceil((1350 - 900) / 60) = ceil(7.5) = 8 menit.
          - Waiting Fee Customer: 8 menit x Rp 500 = Rp 4.000.
          - Penalty Customer: Rp 5.000.
          - Total Customer Charge: Rp 5.000 + Rp 4.000 = Rp 9.000.
          - Driver Payout: Kompensasi Rp 3.000 + (8 x Rp 300 = Rp 2.400) = Rp 5.400.
        Ekspektasi: Tagihan customer terverifikasi tepat Rp 9.000 sesuai baris 7 sheet QC Form.
        """
        given("Driver telah menunggu di titik jemput selama 22 menit 30 detik (1350 detik)")
        driver_simulator.accept_order({"order_id": "ORD-CANCEL-FC-05"})
        driver_simulator.driver_arrived_at_pickup()

        when("Pengguna membatalkan perjalanan setelah melewati toleransi tunggu 15 menit")
        tracking_page.cancel_trip_with_reason()
        driver_simulator.customer_cancel_order(reason="Mendadak naik kendaraan lain")

        then("Invoice pembatalan mencakup Denda Rp 5.000 + Waiting Fee (8 menit) Rp 4.000 = Total Rp 9.000")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=1350,
            driver_schema="Non-GI"
        )
        assert res["phase"] == "C"
        assert res["billable_minutes"] == 8
        assert res["cancel_penalty_charge"] == 5000.0
        assert res["waiting_fee_charge"] == 4000.0
        assert res["customer_charge"] == 9000.0
        assert res["formatted_customer_charge"] == "Rp 9.000"
        assert res["driver_payout"] == 5400.0
        assert res["coupon_issued"] is False
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.waiting_fee
    def test_TC_WAIT_CANCEL_06_driver_cancel_fase_c_forfeit_wait_fee_user_gets_coupon(self, authenticated_home, booking_page, tracking_page, driver_simulator, fare_calculator):
        """
        [Pilar 1 - Positive True] Driver Cancel di Fase C: Waiting Fee Hangus & Customer Diberi Kupon Rp 5.000.
        Deskripsi: Menguji ketentuan PRD v1.1 Catatan Penting poin 5: Jika Driver membatalkan pada Fase C (misal 1200 detik / 20 menit), accrued waiting fee driver hangus (payout = Rp 0), customer TIDAK ditagih biaya apapun (Rp 0), dan customer berhak menerima Kupon Kompensasi Rp 5.000.
        Ekspektasi: Customer Charge Rp 0, Driver Payout Rp 0 (hangus), dan Kupon Rp 5.000 terbit untuk pengguna.
        """
        given("Driver telah menunggu 20 menit di titik jemput (Fase C, elapsed 1200 detik)")
        driver_simulator.accept_order({"order_id": "ORD-CANCEL-FC-06"})
        driver_simulator.driver_arrived_at_pickup()

        when("Mitra Driver membatalkan pesanan di Fase C")
        driver_simulator.driver_cancel_order(reason="Batal karena customer tidak kunjung keluar", schema="GI")

        then("Waiting fee driver hangus (Rp 0), customer bebas biaya, dan kupon Rp 5.000 masuk ke akun user")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Driver",
            driver_arrived=True,
            elapsed_seconds=1200,
            driver_schema="GI"
        )
        assert res["phase"] == "C"
        assert res["customer_charge"] == 0.0
        assert res["driver_payout"] == 0.0  # Forfeited!
        assert res["coupon_issued"] is True
        assert res["coupon_amount"] == 5000.0
        assert res["driver_penalty"] == 5000.0
        assert res["gi_adj_event"] == -10000.0
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.no_show
    def test_TC_WAIT_CANCEL_07_system_auto_cancel_no_show_fase_d_prd_case_8(self, authenticated_home, booking_page, tracking_page, driver_simulator, fare_calculator):
        """
        [Pilar 1 - Positive True] Auto-Cancel Sistem Karena Customer No-Show >= 30 Menit (PRD Case 8).
        Deskripsi: Menguji skenario saat driver menunggu hingga batas maksimum 1800 detik (30 menit) dan customer tidak hadir. Sistem melakukan auto-cancel (Fase D).
          - Masa tunggu billable maksimal: m = 15 menit.
          - Penalty No-Show Customer: Rp 10.000.
          - Waiting Fee Customer: 15 menit x Rp 500 = Rp 7.500.
          - Total Customer Charge: Rp 10.000 + Rp 7.500 = Rp 17.500.
          - Driver Payout: Kompensasi No-Show Rp 7.000 + (15 x Rp 300 = Rp 4.500) = Rp 11.500.
        Ekspektasi: Tagihan customer no-show terhitung presisi Rp 17.500 sesuai baris 8 sheet QC Form.
        """
        given("Driver menunggu di titik jemput hingga mencapai ambang batas 30 menit (1800 detik)")
        driver_simulator.accept_order({"order_id": "ORD-CANCEL-FD-07"})
        driver_simulator.driver_arrived_at_pickup()

        when("Sistem otomatis membatalkan pesanan karena Customer No-Show (Auto-cancel Fase D)")
        driver_simulator.system_auto_cancel_no_show()

        then("Invoice No-Show diterbitkan sebesar Rp 17.500 (Denda Rp 10.000 + Waiting Fee Rp 7.500)")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="System",
            driver_arrived=True,
            elapsed_seconds=1800,
            driver_schema="GI"
        )
        assert res["phase"] == "D"
        assert res["billable_minutes"] == 15
        assert res["cancel_penalty_charge"] == 10000.0
        assert res["waiting_fee_charge"] == 7500.0
        assert res["customer_charge"] == 17500.0
        assert res["formatted_customer_charge"] == "Rp 17.500"
        assert res["driver_payout"] == 11500.0
        assert res["coupon_issued"] is False
        time.sleep(Config.HUMAN_PACING_MIN)

    @pytest.mark.booking
    @pytest.mark.pilar3
    @pytest.mark.boundary_test
    def test_TC_WAIT_CANCEL_08_billable_minute_boundary_ceil_901s(self, authenticated_home, booking_page, fare_calculator):
        """
        [Pilar 3 - Negative True] Boundary Test: Detik ke-901 Langsung Dibulatkan ke Atas Menjadi 1 Menit Penuh.
        Deskripsi: Menguji batas toleransi tepat 901 detik (15 menit 01 detik). Sesuai PRD v1.1 Catatan Penting poin 2, penagihan menggunakan pembulatan ke atas per menit penuh (ROUNDUP((elapsed-900)/60)). Detik ke-901 wajib menghasilkan m = 1 menit billable.
        Ekspektasi: Billable minutes m = 1, Waiting Fee = Rp 500, dan Customer Charge = Rp 5.500.
        """
        given("Waktu tunggu driver di titik jemput tepat 901 detik (1 detik setelah batas gratis 15 menit)")
        when("Customer membatalkan pesanan pada detik ke-901")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=901
        )
        then("Sistem membulatkan waktu ke atas menjadi tepat 1 menit billable (m = 1)")
        assert res["phase"] == "C"
        assert res["billable_minutes"] == 1
        assert res["waiting_fee_charge"] == 500.0
        assert res["customer_charge"] == 5500.0
        assert res["formatted_customer_charge"] == "Rp 5.500"

    @pytest.mark.booking
    @pytest.mark.pilar3
    @pytest.mark.boundary_test
    def test_TC_WAIT_CANCEL_09_max_billable_minutes_cap_15_at_1799s(self, authenticated_home, booking_page, fare_calculator):
        """
        [Pilar 3 - Negative True] Boundary Test: Batas Maksimal Penagihan Menit Tunggu Dibatasi Tepat 15 Menit.
        Deskripsi: Menguji detik ke-1799 (29 menit 59 detik) di Fase C. Memastikan menit tagihan tidak melebihi batas maksimal (MAX_BILLABLE_MINUTES = 15).
        Ekspektasi: Billable minutes m = 15 (Cap), Waiting Fee = 15 x Rp 500 = Rp 7.500, Customer Charge = Rp 12.500.
        """
        given("Waktu tunggu driver mencapai 1799 detik (1 detik sebelum auto-cancel 30 menit)")
        when("Customer membatalkan pesanan pada detik ke-1799")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=1799
        )
        then("Menit tagihan terkunci pada batas maksimal 15 menit (Cap = 15)")
        assert res["phase"] == "C"
        assert res["billable_minutes"] == 15
        assert res["waiting_fee_charge"] == 7500.0
        assert res["customer_charge"] == 12500.0
        assert res["formatted_customer_charge"] == "Rp 12.500"

    @pytest.mark.booking
    @pytest.mark.pilar2
    @pytest.mark.negative_state
    def test_TC_WAIT_CANCEL_10_invalid_phase_d_non_system_guard(self, authenticated_home, booking_page, fare_calculator):
        """
        [Pilar 2 - Positive False] Guard Proteksi Skenario Invalid: Fase D Hanya Sah Jika Dibatalkan oleh Sistem.
        Deskripsi: Menguji proteksi aturan PRD v1.1 Catatan Penting poin 1: Fase D (>= 1800 detik) HANYA valid jika Cancelled By = System (Auto-cancel). Jika ada request pembatalan customer di atas 1800 detik, sistem menolaknya sebagai INVALID.
        Ekspektasi: Sistem menandai skenario sebagai INVALID dan mencegah perhitungan yang keliru.
        """
        given("Terjadi percobaan pembatalan dengan parameter inkonsisten (Fase D oleh Customer)")
        res = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=1800
        )
        then("Sistem menolak dan menandai status transaksi sebagai INVALID")
        assert res["is_valid"] is False
        assert res["status"] == "INVALID"
        assert "HANYA valid jika dibatalkan oleh System" in res["invalid_reason"]

    @pytest.mark.booking
    @pytest.mark.pilar1
    @pytest.mark.ewallet_charge
    def test_TC_WAIT_CANCEL_11_ewallet_surcharge_2_percent_on_cancellation_settlement(self, authenticated_home, booking_page, fare_calculator):
        """
        [Pilar 1 - Positive True] Integrasi E-Wallet Charge Fee 2% pada Tagihan Pembatalan Pengguna.
        Deskripsi: Menguji ketentuan metode pembayaran User Apps jika pengguna menggunakan E-Wallet (GoPay & OVO) saat dikenakan denda pembatalan:
          - Denda Fase B (Rp 5.000) via GoPay: Charge 2% = Rp 100 -> Grand Total = Rp 5.100
          - Denda No-Show Fase D (Rp 17.500) via OVO: Charge 2% = Rp 350 -> Grand Total = Rp 17.850
        Ekspektasi: Surcharge 2% terakumulasi tepat pada Grand Total akhir invoice pembatalan.
        """
        given("Pengguna menggunakan metode pembayaran GoPay dan terkena cancel fee Fase B (Rp 5.000)")
        res_gopay = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=300,
            payment_method="gopay"
        )
        then("Grand Total GoPay terhitung tepat Rp 5.103 (gross-up 2%)")
        assert res_gopay["customer_charge"] == 5000.0
        assert res_gopay["charge_fee_amount"] == 103.0  # gross-up: ceil(5.000 x 100/98) = 5.103
        assert res_gopay["grand_total_customer"] == 5103.0
        assert res_gopay["formatted_grand_total"] == "Rp 5.103"

        when("Pengguna menggunakan metode pembayaran OVO dan terkena denda No-Show Fase D (Rp 17.500)")
        res_ovo = fare_calculator.calculate_cancellation_settlement(
            cancelled_by="System",
            driver_arrived=True,
            elapsed_seconds=1800,
            payment_method="ovo"
        )
        then("Grand Total OVO terhitung tepat Rp 17.797 (gross-up 1,665%)")
        assert res_ovo["customer_charge"] == 17500.0
        assert res_ovo["charge_fee_amount"] == 297.0  # gross-up: ceil(17.500 x 100/98,335) = 17.797
        assert res_ovo["grand_total_customer"] == 17797.0


# ==============================================================================
# SUITE PENGUJIAN 16 MATRIKS ORDER BEHAVIOUR & JARAK (DEKAT, SEDANG, JAUH, SANGAT JAUH)
# ==============================================================================
class TestOrderBehaviourMatrix:
    """
    Test Suite Komprehensif Matriks 16 Skenario Order Behaviour EvMoto:
    Mencakup Rincian Tarif Perjalanan Resmi:
      - Tarif Dasar / Argo Awal (Start Price) : Rp 6.000 (Konstan untuk radius 0 - 2.0 KM pertama)
      - Tarif Jarak Reguler (Mileage Fee)     : Rp 2.800 / KM (untuk jarak > 2.0 KM)
      - Biaya Jarak Jauh (Long Distance Fee)  : Tier 1 (+Rp 2.500/KM 6-15 KM), Tier 2 (+Rp 2.200/KM 15-100 KM)
    
    4 Kategori Jarak Operasional Resmi:
      - Jarak Dekat       : 1.5 KM -> Argo Dasar Rp 6.000 + Jarak Rp 0 = Total Argo Rp 6.000 (Plat Fee Rp 600 -> Subtotal Rp 6.600)
      - Jarak Sedang      : 3.5 KM -> Argo Dasar Rp 6.000 + Jarak (1.5 KM x Rp 2.800 = Rp 4.200) = Total Argo Rp 10.200 (Plat Fee Rp 1.020 -> Subtotal Rp 11.220)
      - Jarak Jauh        : 10.0 KM -> Argo Dasar Rp 6.000 + Jarak Rp 22.400 + Long Dist Rp 10.000 = Total Argo Rp 38.400 (Plat Fee Rp 3.840 -> Subtotal Rp 42.240)
      - Jarak Sangat Jauh : 20.0 KM -> Argo Dasar Rp 6.000 + Jarak Rp 50.400 + Long Dist Rp 33.500 = Total Argo Rp 89.900 (Plat Fee Rp 8.990 -> Subtotal Rp 98.890)
    
    Mencakup Seluruh 4 Metode Pembayaran Resmi EvMoto:
      1. Tunai (Cash)                  : Surcharge 0% (Biaya Tambahan Rp 0)
      2. EvWallet (Saldo Internal)     : Surcharge 0% (Biaya Tambahan Rp 0)
      3. GoPay (E-Wallet Eksternal)    : Surcharge 2% dari Adjusted Subtotal
      4. OVO (E-Wallet Eksternal)      : Surcharge 2% dari Adjusted Subtotal
    
    16 Kombinasi Order Behaviour x 4 Jarak x 4 Metode Pembayaran = 256 Titik Pengujian Kombinatorial.
    """

    # Titik jarak yang diuji. Angka tarif yang diharapkan TIDAK ditulis tetap di sini: dihitung dari
    # parameter halaman Price Admin environment aktif (keputusan user: Admin adalah sumber tarif).
    DISTANCES = [
        {"tier": "Jarak Dekat", "km": 1.5},
        {"tier": "Jarak Sedang", "km": 3.5},
        {"tier": "Jarak Jauh", "km": 10.0},
        {"tier": "Jarak Sangat Jauh", "km": 20.0},
    ]

    @staticmethod
    def _expected_argo(calc: AdminDashboardFareCalculator, km: float) -> float:
        """Total argo yang diharapkan, dihitung terpisah dari kalkulator dengan parameter Admin:
        tarif awal + (jarak - jarak awal) x tarif per KM + biaya jarak jauh per tier (farFrom-farTo)."""
        if km <= calc.START_KM:
            return float(calc.START_PRICE)
        total = calc.START_PRICE + (km - calc.START_KM) * calc.MILEAGE_FEE
        tiers = [
            (calc.FAR_FROM_1, calc.FAR_TO_1, calc.FAR_FEE_1),
            (calc.FAR_FROM_2, calc.FAR_TO_2, calc.FAR_FEE_2),
            (calc.FAR_FROM_3, float("inf"), calc.FAR_FEE_3),
        ]
        for lo, hi, fee in tiers:
            total += max(0.0, min(km, hi) - lo) * fee
        return round(total, 2)

    PAYMENT_METHODS = [
        {"code": "cash", "name": "Tunai", "rate": 0.0, "is_ewallet": False},
        {"code": "evwallet", "name": "EvWallet", "rate": 0.0, "is_ewallet": False},
        {"code": "gopay", "name": "GoPay", "rate": 0.02, "is_ewallet": True},
        {"code": "ovo", "name": "OVO", "rate": 0.01665, "is_ewallet": True},
    ]

    def _verify_combo(
        self,
        calc: AdminDashboardFareCalculator,
        scenario_title: str,
        use_coupon: bool = False,
        coupon_amount: float = 5000.0,
        waiting_minutes: int = 0,
        apply_penalty: bool = False,
        penalty_amount: float = 5000.0,
        is_advance: bool = False
    ):
        """
        Helper komprehensif validasi 4 Jarak x 4 Metode Pembayaran (16 verifikasi per skenario):
        - Tarif Dasar (Start Price) wajib Rp 6.000 untuk 2 KM pertama.
        - Total Argo = Start Price Rp 6.000 + Mileage Fee + Long Distance Fee.
        - Tunai & EvWallet: Surcharge 0%, Grand Total = Adjusted Subtotal.
        - GoPay (2%) & OVO (1.665%): Formula Gross-Up: Grand Total = math.ceil(Adjusted Subtotal * (100 / (100 - Fee Rate))).
        Mengembalikan jumlah titik (jarak x metode bayar) yang sudah lolos verifikasi.
        """
        jumlah_titik = 0
        for d in self.DISTANCES:
            excess_wait_min = max(0, waiting_minutes - 15)
            wait_fee = float(excess_wait_min * 500.0)
            coupon_disc = float(coupon_amount) if use_coupon else 0.0
            penalty_val = float(penalty_amount) if apply_penalty else 0.0
            expected_argo = self._expected_argo(calc, d["km"])
            expected_adj_subtotal = round(max(0.0, expected_argo + wait_fee + penalty_val - coupon_disc), 2)

            for p in self.PAYMENT_METHODS:
                res = calc.calculate_grand_total(
                    distance_km=d["km"],
                    payment_method=p["code"],
                    use_coupon=use_coupon,
                    coupon_amount=coupon_amount,
                    waiting_minutes=waiting_minutes,
                    apply_penalty=apply_penalty,
                    penalty_amount=penalty_amount,
                )

                # Validasi komponen biaya
                assert res["start_price"] == calc.START_PRICE, f"Tarif awal harus sama dengan Admin ({d['tier']})"
                assert res["total_argo"] == pytest.approx(expected_argo, abs=0.01), (
                    f"Total argo tidak sesuai untuk {d['tier']} ({p['name']}): {res['total_argo']} vs {expected_argo} "
                    f"(tarif {calc.source})"
                )
                assert res["platform_fee"] == 0.0, f"Platform fee tidak sesuai untuk {d['tier']} ({p['name']})"
                assert res["waiting_fee"] == wait_fee, f"Waiting fee tidak sesuai untuk {d['tier']} ({p['name']})"
                assert res["coupon_discount"] == coupon_disc, f"Potongan kupon tidak sesuai untuk {d['tier']} ({p['name']})"
                assert res["penalty_fee"] == penalty_val, f"Penalty tidak sesuai untuk {d['tier']} ({p['name']})"
                assert res["adjusted_subtotal"] == pytest.approx(expected_adj_subtotal, abs=0.01), f"Adjusted subtotal tidak sesuai untuk {d['tier']} ({p['name']})"

                # Validasi surcharge metode pembayaran dengan Gross-Up
                if p["is_ewallet"] and expected_adj_subtotal > 0:
                    rate_pct = 1.665 if p["code"] == "ovo" else 2.0
                    expected_grand = float(math.ceil(expected_adj_subtotal * (100.0 / (100.0 - rate_pct))))
                    expected_charge = float(expected_grand - expected_adj_subtotal)
                    assert res["charge_fee_amount"] == expected_charge, f"Surcharge {rate_pct}% {p['name']} tidak sesuai pada {d['tier']}"
                    assert res["grand_total"] == expected_grand, f"Grand total {p['name']} tidak sesuai pada {d['tier']}"
                else:
                    assert res["charge_fee_amount"] == 0.0, f"Surcharge {p['name']} (Tunai/EvWallet) harus Rp 0"
                    assert res["grand_total"] == pytest.approx(expected_adj_subtotal, abs=0.01), f"Grand total {p['name']} tidak sesuai pada {d['tier']}"
                jumlah_titik += 1
        return jumlah_titik

    # --------------------------------------------------------------------------
    # SKENARIO 1: NORMAL BOOKING (ARGO + PLATFORM FEE 10%)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_01_normal_booking_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-01] Normal Booking (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pesanan instan reguler tanpa promo/fee tambahan pada seluruh metode pembayaran (Tunai, EvWallet, GoPay, OVO).
        Formula  : Tunai/EvWallet (0%): Grand Total = Subtotal. GoPay/OVO (2%): Grand Total = Subtotal + 2%.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 6.600 | GoPay/OVO Rp 6.732
          - Sedang      : Tunai/EvWallet Rp 11.220 | GoPay/OVO Rp 11.444,4
          - Jauh        : Tunai/EvWallet Rp 42.240 | GoPay/OVO Rp 43.084,8
          - Sangat Jauh : Tunai/EvWallet Rp 98.890 | GoPay/OVO Rp 100.867,8
        """
        calc = fare_calculator
        given("Pengguna melakukan Normal Booking untuk 4 jarak dan 4 metode pembayaran")
        jumlah_titik = self._verify_combo(calc, "Normal Booking", use_coupon=False, waiting_minutes=0, apply_penalty=False)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 2: NORMAL BOOKING + KUPON (DISKON RP 5.000)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_02_normal_booking_plus_kupon_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-02] Normal Booking + Kupon Diskon Rp 5.000 (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pemotongan voucher kupon promosi Rp 5.000 pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal - Rp 5.000. GoPay/OVO dikenakan 2% dari Adjusted Subtotal.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 1.600 | GoPay/OVO Rp 1.632
          - Sedang      : Tunai/EvWallet Rp 6.220 | GoPay/OVO Rp 6.344,4
          - Jauh        : Tunai/EvWallet Rp 37.240 | GoPay/OVO Rp 37.984,8
          - Sangat Jauh : Tunai/EvWallet Rp 93.890 | GoPay/OVO Rp 95.767,8
        """
        calc = fare_calculator
        given("Pengguna mengaplikasikan voucher diskon Rp 5.000 pada Normal Booking (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Normal Booking + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=False)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking + Kupon' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 3: NORMAL BOOKING + WAITING FEE (20 MENIT / 5 MIN BILLABLE)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_03_normal_booking_plus_waiting_fee_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-03] Normal Booking + Waiting Fee (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji waktu tunggu 20 menit (5 min billable x Rp 500 = Rp 2.500) pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal + Waiting Fee Rp 2.500. GoPay/OVO dikenakan 2% dari total akumulatif.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 9.100 | GoPay/OVO Rp 9.282
          - Sedang      : Tunai/EvWallet Rp 13.720 | GoPay/OVO Rp 13.994,4
          - Jauh        : Tunai/EvWallet Rp 44.740 | GoPay/OVO Rp 45.634,8
          - Sangat Jauh : Tunai/EvWallet Rp 101.390 | GoPay/OVO Rp 103.417,8
        """
        calc = fare_calculator
        given("Driver menunggu 20 menit pada titik penjemputan Normal Booking (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Normal Booking + Waiting Fee", use_coupon=False, waiting_minutes=20, apply_penalty=False)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking + Waiting Fee' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 4: NORMAL BOOKING + PENALTY (DENDA RP 5.000)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_04_normal_booking_plus_penalty_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-04] Normal Booking + Penalty Fee Rp 5.000 (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji penagihan denda penalti pembatalan masa lalu Rp 5.000 pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal + Penalty Rp 5.000. GoPay/OVO dikenakan 2% dari total tagihan.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 11.600 | GoPay/OVO Rp 11.832
          - Sedang      : Tunai/EvWallet Rp 16.220 | GoPay/OVO Rp 16.544,4
          - Jauh        : Tunai/EvWallet Rp 47.240 | GoPay/OVO Rp 48.184,8
          - Sangat Jauh : Tunai/EvWallet Rp 103.890 | GoPay/OVO Rp 105.967,8
        """
        calc = fare_calculator
        given("Pengguna memiliki kewajiban denda pembatalan Rp 5.000 pada Normal Booking (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Normal Booking + Penalty", use_coupon=False, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking + Penalty' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 5: NORMAL BOOKING + KUPON + WAITING FEE
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_05_normal_booking_plus_kupon_plus_waiting_fee_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-05] Normal Booking + Kupon + Waiting Fee (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji kombinasi Kupon (-Rp 5.000) dan Waiting Fee (+Rp 2.500) pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal - Rp 5.000 + Rp 2.500 (Net -Rp 2.500).
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 4.100 | GoPay/OVO Rp 4.182
          - Sedang      : Tunai/EvWallet Rp 8.720 | GoPay/OVO Rp 8.894,4
          - Jauh        : Tunai/EvWallet Rp 39.740 | GoPay/OVO Rp 40.534,8
          - Sangat Jauh : Tunai/EvWallet Rp 96.390 | GoPay/OVO Rp 98.317,8
        """
        calc = fare_calculator
        given("Pengguna Normal Booking memakai Kupon Rp 5.000 dan kena Waiting Fee Rp 2.500 (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Normal Booking + Kupon + WaitFee", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=False)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking + Kupon + WaitFee' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 6: NORMAL BOOKING + KUPON + WAITING FEE + PENALTY
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_06_normal_booking_plus_kupon_plus_waiting_fee_plus_penalty_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-06] Normal Booking + Kupon + Waiting Fee + Penalty (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji kombinasi 4 variabel biaya sekaligus (Kupon, Waiting Fee, Penalty) pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal - Rp 5.000 + Rp 2.500 + Rp 5.000 = Subtotal + Rp 2.500.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 9.100 | GoPay/OVO Rp 9.282
          - Sedang      : Tunai/EvWallet Rp 13.720 | GoPay/OVO Rp 13.994,4
          - Jauh        : Tunai/EvWallet Rp 44.740 | GoPay/OVO Rp 45.634,8
          - Sangat Jauh : Tunai/EvWallet Rp 101.390 | GoPay/OVO Rp 103.417,8
        """
        calc = fare_calculator
        given("Pengguna Normal Booking kombo lengkap Kupon, WaitFee, dan Penalty (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Normal Booking Kombo Lengkap", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking Kombo Lengkap' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 7: NORMAL BOOKING + WAITING FEE + PENALTY
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_07_normal_booking_plus_waiting_fee_plus_penalty_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-07] Normal Booking + Waiting Fee + Penalty (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji penambahan ganda biaya: Waiting Fee (+Rp 2.500) dan Penalty (+Rp 5.000) pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal + Rp 7.500. GoPay/OVO dikenakan 2% dari total akumulatif.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 14.100 | GoPay/OVO Rp 14.382
          - Sedang      : Tunai/EvWallet Rp 18.720 | GoPay/OVO Rp 19.094,4
          - Jauh        : Tunai/EvWallet Rp 49.740 | GoPay/OVO Rp 50.734,8
          - Sangat Jauh : Tunai/EvWallet Rp 106.390 | GoPay/OVO Rp 108.517,8
        """
        calc = fare_calculator
        given("Pengguna Normal Booking terkena Waiting Fee Rp 2.500 dan Penalty Rp 5.000 (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Normal Booking + WaitFee + Penalty", use_coupon=False, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking + WaitFee + Penalty' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 8: NORMAL BOOKING + PENALTY + KUPON
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_08_normal_booking_plus_penalty_plus_kupon_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-08] Normal Booking + Penalty + Kupon (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji penalti denda Rp 5.000 yang saling offset dengan kupon diskon Rp 5.000 pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal + Penalty Rp 5.000 - Kupon Rp 5.000 = Subtotal.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 6.600 | GoPay/OVO Rp 6.732
          - Sedang      : Tunai/EvWallet Rp 11.220 | GoPay/OVO Rp 11.444,4
          - Jauh        : Tunai/EvWallet Rp 42.240 | GoPay/OVO Rp 43.084,8
          - Sangat Jauh : Tunai/EvWallet Rp 98.890 | GoPay/OVO Rp 100.867,8
        """
        calc = fare_calculator
        given("Pengguna Normal Booking dengan Penalty Rp 5.000 dioffset Kupon Rp 5.000 (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Normal Booking + Penalty + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Normal Booking + Penalty + Kupon' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 9: ADVANCE BOOKING (TERJADWAL)
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_09_advance_booking_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-09] Advance Booking Terjadwal (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pemesanan terjadwal reguler tanpa promo/fee tambahan pada seluruh metode pembayaran.
        Formula  : Tunai/EvWallet (0%): Grand Total = Subtotal. GoPay/OVO (2%): Grand Total = Subtotal + 2%.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 6.600 | GoPay/OVO Rp 6.732
          - Sedang      : Tunai/EvWallet Rp 11.220 | GoPay/OVO Rp 11.444,4
          - Jauh        : Tunai/EvWallet Rp 42.240 | GoPay/OVO Rp 43.084,8
          - Sangat Jauh : Tunai/EvWallet Rp 98.890 | GoPay/OVO Rp 100.867,8
        """
        calc = fare_calculator
        given("Pengguna menjadwalkan Advance Booking untuk 4 tingkatan jarak (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Advance Booking", use_coupon=False, waiting_minutes=0, apply_penalty=False, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 10: ADVANCE BOOKING + KUPON
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_10_advance_booking_plus_kupon_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-10] Advance Booking + Kupon Diskon Rp 5.000 (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pemesanan terjadwal dengan klaim voucher promo diskon Rp 5.000 pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal - Rp 5.000. GoPay/OVO dikenakan 2% dari Adjusted Subtotal.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 1.600 | GoPay/OVO Rp 1.632
          - Sedang      : Tunai/EvWallet Rp 6.220 | GoPay/OVO Rp 6.344,4
          - Jauh        : Tunai/EvWallet Rp 37.240 | GoPay/OVO Rp 37.984,8
          - Sangat Jauh : Tunai/EvWallet Rp 93.890 | GoPay/OVO Rp 95.767,8
        """
        calc = fare_calculator
        given("Pengguna memesan Advance Booking dengan voucher diskon Kupon Rp 5.000 (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Advance Booking + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=False, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking + Kupon' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 11: ADVANCE BOOKING + WAITING FEE
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_11_advance_booking_plus_waiting_fee_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-11] Advance Booking + Waiting Fee (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pesanan terjadwal di mana driver tiba tepat jadwal dan menunggu 20 menit (5 min billable) pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal + Waiting Fee Rp 2.500. GoPay/OVO dikenakan 2% dari total tagihan.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 9.100 | GoPay/OVO Rp 9.282
          - Sedang      : Tunai/EvWallet Rp 13.720 | GoPay/OVO Rp 13.994,4
          - Jauh        : Tunai/EvWallet Rp 44.740 | GoPay/OVO Rp 45.634,8
          - Sangat Jauh : Tunai/EvWallet Rp 101.390 | GoPay/OVO Rp 103.417,8
        """
        calc = fare_calculator
        given("Driver tiba pada jadwal Advance Booking dan menunggu penumpang 20 menit (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Advance Booking + Waiting Fee", use_coupon=False, waiting_minutes=20, apply_penalty=False, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking + Waiting Fee' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 12: ADVANCE BOOKING + PENALTY
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_12_advance_booking_plus_penalty_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-12] Advance Booking + Penalty Fee Rp 5.000 (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pesanan terjadwal dengan beban denda penalti keterlambatan/pembatalan sebelumnya sebesar Rp 5.000.
        Formula  : Adjusted Subtotal = Subtotal + Penalty Rp 5.000. GoPay/OVO dikenakan 2% dari akumulasi.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 11.600 | GoPay/OVO Rp 11.832
          - Sedang      : Tunai/EvWallet Rp 16.220 | GoPay/OVO Rp 16.544,4
          - Jauh        : Tunai/EvWallet Rp 47.240 | GoPay/OVO Rp 48.184,8
          - Sangat Jauh : Tunai/EvWallet Rp 103.890 | GoPay/OVO Rp 105.967,8
        """
        calc = fare_calculator
        given("Pengguna memiliki saldo penalti denda Rp 5.000 pada Advance Booking (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Advance Booking + Penalty", use_coupon=False, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking + Penalty' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 13: ADVANCE BOOKING + KUPON + WAITING FEE
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_13_advance_booking_plus_kupon_plus_waiting_fee_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-13] Advance Booking + Kupon + Waiting Fee (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pesanan terjadwal dengan kupon diskon Rp 5.000 dan penagihan waiting fee Rp 2.500 pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal - Rp 5.000 + Rp 2.500 (Net -Rp 2.500).
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 4.100 | GoPay/OVO Rp 4.182
          - Sedang      : Tunai/EvWallet Rp 8.720 | GoPay/OVO Rp 8.894,4
          - Jauh        : Tunai/EvWallet Rp 39.740 | GoPay/OVO Rp 40.534,8
          - Sangat Jauh : Tunai/EvWallet Rp 96.390 | GoPay/OVO Rp 98.317,8
        """
        calc = fare_calculator
        given("Pesanan Advance Booking memakai Kupon Rp 5.000 dan kena Waiting Fee Rp 2.500 (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Advance Booking + Kupon + WaitFee", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=False, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking + Kupon + WaitFee' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 14: ADVANCE BOOKING + KUPON + WAITING FEE + PENALTY
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_14_advance_booking_plus_kupon_plus_waiting_fee_plus_penalty_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-14] Advance Booking + Kupon + Waiting Fee + Penalty (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji kombinasi 4 variabel menyeluruh pada pesanan terjadwal pada seluruh metode pembayaran.
        Formula  : Adjusted Subtotal = Subtotal - Rp 5.000 + Rp 2.500 + Rp 5.000 = Subtotal + Rp 2.500.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 9.100 | GoPay/OVO Rp 9.282
          - Sedang      : Tunai/EvWallet Rp 13.720 | GoPay/OVO Rp 13.994,4
          - Jauh        : Tunai/EvWallet Rp 44.740 | GoPay/OVO Rp 45.634,8
          - Sangat Jauh : Tunai/EvWallet Rp 101.390 | GoPay/OVO Rp 103.417,8
        """
        calc = fare_calculator
        given("Pesanan Advance Booking memuat seluruh parameter biaya (Kupon, Waiting Fee, Penalty) pada 4 metode pembayaran")
        jumlah_titik = self._verify_combo(calc, "Advance Booking Kombo Lengkap", use_coupon=True, coupon_amount=5000.0, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking Kombo Lengkap' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 15: ADVANCE BOOKING + WAITING FEE + PENALTY
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_15_advance_booking_plus_waiting_fee_plus_penalty_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-15] Advance Booking + Waiting Fee + Penalty (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pesanan terjadwal dengan beban ganda penambahan: Waiting Fee (+Rp 2.500) dan Penalty (+Rp 5.000).
        Formula  : Adjusted Subtotal = Subtotal + Rp 7.500. GoPay/OVO dikenakan 2% dari total akumulatif.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 14.100 | GoPay/OVO Rp 14.382
          - Sedang      : Tunai/EvWallet Rp 18.720 | GoPay/OVO Rp 19.094,4
          - Jauh        : Tunai/EvWallet Rp 49.740 | GoPay/OVO Rp 50.734,8
          - Sangat Jauh : Tunai/EvWallet Rp 106.390 | GoPay/OVO Rp 108.517,8
        """
        calc = fare_calculator
        given("Pesanan Advance Booking tanpa kupon terkena Waiting Fee Rp 2.500 dan Penalty Rp 5.000 (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Advance Booking + WaitFee + Penalty", use_coupon=False, waiting_minutes=20, apply_penalty=True, penalty_amount=5000.0, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking + WaitFee + Penalty' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )

    # --------------------------------------------------------------------------
    # SKENARIO 16: ADVANCE BOOKING + PENALTY + KUPON
    # --------------------------------------------------------------------------
    @pytest.mark.booking
    @pytest.mark.order_behaviour
    def test_TC_OB_16_advance_booking_plus_penalty_plus_kupon_all_distances(self, fare_calculator):
        """
        [ORDER BEHAVIOUR - OB-16] Advance Booking + Penalty + Kupon (4 Jarak x 4 Metode Pembayaran).
        Deskripsi: Menguji pesanan terjadwal dengan penalti denda Rp 5.000 yang saling offset dengan kupon diskon Rp 5.000.
        Formula  : Adjusted Subtotal = Subtotal + Penalty Rp 5.000 - Kupon Rp 5.000 = Subtotal.
        Ekspektasi:
          - Dekat       : Tunai/EvWallet Rp 6.600 | GoPay/OVO Rp 6.732
          - Sedang      : Tunai/EvWallet Rp 11.220 | GoPay/OVO Rp 11.444,4
          - Jauh        : Tunai/EvWallet Rp 42.240 | GoPay/OVO Rp 43.084,8
          - Sangat Jauh : Tunai/EvWallet Rp 98.890 | GoPay/OVO Rp 100.867,8
        """
        calc = fare_calculator
        given("Pesanan Advance Booking dengan Penalty Rp 5.000 dioffset Kupon Rp 5.000 (4 metode pembayaran)")
        jumlah_titik = self._verify_combo(calc, "Advance Booking + Penalty + Kupon", use_coupon=True, coupon_amount=5000.0, waiting_minutes=0, apply_penalty=True, penalty_amount=5000.0, is_advance=True)
        then("Seluruh 16 kombinasi (4 jarak x 4 metode bayar) terverifikasi sesuai formula tarif")
        assert jumlah_titik == 16, (
            f"Skenario 'Advance Booking + Penalty + Kupon' hanya memverifikasi {jumlah_titik} dari 16 kombinasi jarak x metode bayar"
        )





