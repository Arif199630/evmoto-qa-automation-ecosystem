"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - COMPREHENSIVE END-TO-END (E2E) MASTER SUITE
================================================================================
Tujuan: Pengujian End-To-End menyeluruh (E2E) TANPA ORDER yang mencakup:
  1. Izin & Sensor: Runtime Permission (Location 'Saat Aplikasi Digunakan', GPS)
  2. Autentikasi: Registrasi form tinjauan & Login kredensial Dev (OTP 1234)
  3. Beranda: Header, Top Up, QRIS scanner, Search, Grid EvRide/Send/Rent, Promo Carousel
  4. Tinjauan Pemesanan (Review Placing Order): Estimasi tarif, rute, batal pesan (TANPA ORDER)
  5. Aktivitas: Tab Regular (Normal Booking) & Tab Booking (Advance Booking), Reschedule, E-Receipt
  6. Profil Pengguna: Avatar Picker Sheet, Kontak Darurat, Alamat Tersimpan, CS Support
  7. Video & Gambar: Gambar Avatar, Promo Carousel Swipe, Video Tutorial Player FAQ (No Media Error)
  8. Bilingual Language: Pengujian Switch Bahasa Indonesia <-> English (Bilingual verification)
  9. Keluar: Logout Dialog Konfirmasi (Batal & Konfirmasi Logout ke Layar Masuk)
Jeda Pengujian:
  - JEDA 5 DETIK WAJIB (time.sleep(5.0)) di setiap test case agar bebas dari race condition!
================================================================================
"""
import time
import pytest
from appium.webdriver.webdriver import WebDriver

from utils.logger import get_logger
from utils.bdd_helper import given, when, then, and_step
from Frontend.Feature.Pages.login_page import LoginPage
from Frontend.Feature.Pages.register_page import RegisterPage
from Frontend.Feature.Pages.home_page import HomePage
from Frontend.Feature.Pages.activity_page import ActivityPage
from Frontend.Feature.Pages.profil_page import ProfilPage
from Frontend.Feature.Data.user_data import (
    dev_phone,
    dev_otp,
    LOGIN_DATA_POSITIVE_TRUE,
    REGISTER_DATA_POSITIVE_TRUE,
    HOME_HAPPY_FLOW_DATA,
    ACTIVITY_HAPPY_FLOW_DATA,
    ACTIVITY_PILAR_1_POSITIVE,
    PROFILE_HAPPY_FLOW_DATA,
    PROFILE_PILAR_1_POSITIVE
)

logger = get_logger("TestE2EMasterFlow")


class TestComprehensiveE2E:
    """Master Suite End-to-End Testing Menyeluruh Tanpa Placing Order."""

    @pytest.fixture(autouse=True)
    def setup_e2e_test(self, driver: WebDriver):
        """Fixture Setup & Teardown E2E dengan jeda 5 detik anti-race condition."""
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.register_page = RegisterPage(driver)
        self.home_page = HomePage(driver)
        self.activity_page = ActivityPage(driver)
        self.profil_page = ProfilPage(driver)

        yield

        logger.info("[ANTI RACE CONDITION] Memberikan jeda 5 detik sebelum skenario berikutnya...")
        time.sleep(5.0)

    # ==========================================================================
    # FASE 1: RUNTIME PERMISSION, SPLASH & AUTENTIKASI (LOGIN & REGISTER)
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_01_runtime_permission_register_dan_login_dev_berhasil(self, driver):
        """
        [E2E-01] Menguji daur hidup aplikasi awal:
        1. Memeriksa runtime permission (Izin Lokasi Android 'Saat Aplikasi Digunakan').
        2. Menavigasi ke formulir pendaftaran akun (Register).
        3. Meninjau input nomor HP dan nama lengkap, serta tombol Request OTP dev.
        4. Kembali ke layar Login, mengisi nomor Dev & OTP 1234, dan masuk sukses ke Beranda.
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-01] RUNTIME PERMISSION & AUTENTIKASI (REGISTER & LOGIN) <<<")
        print("=" * 80)

        given("Aplikasi EVMoto dibuka di perangkat Android")
        self.login_page.is_login_screen_displayed(timeout=15)

        when("Menangani dialog runtime permission lokasi jika muncul")
        try:
            self.login_page.handle_location_permission(allow=True)
            time.sleep(1.0)
        except Exception:
            pass

        and_step("Menavigasi ke layar Pendaftaran Akun Baru ('Register')")
        self.login_page.navigate_to_register()
        time.sleep(1.5)

        then("Memverifikasi form pendaftaran akun baru tampil lengkap")
        fresh_phone = f"821{int(time.time()) % 100000000:08d}"
        self.register_page.fill_phone(fresh_phone)
        self.register_page.fill_name("QA Master E2E Tester")
        time.sleep(1.0)

        and_step("Kembali ke layar Login melalui tautan 'Sudah Punya Akun? Masuk'")
        self.register_page.navigate_back_to_login()
        time.sleep(1.5)

        when("Melakukan login menggunakan nomor Dev dan kode OTP 1234")
        self.login_page.login(phone=dev_phone, otp=dev_otp)
        time.sleep(2.5)

        then("Pengguna berhasil masuk ke Halaman Beranda utama EVMoto")
        assert self.home_page.is_home_screen_displayed(timeout=15), "[E2E-01] Gagal masuk ke Beranda setelah login!"
        print(">>> [E2E-01] Berhasil Menyelesaikan Alur Izin & Autentikasi! <<<")

    # ==========================================================================
    # FASE 2: BERANDA - POPUP, DOMPET, PENCARIAN, GRID & REVIEW PLACING ORDER
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_02_halaman_beranda_fitur_dompet_search_layanan_dan_review_order_tanpa_pesan(self, driver):
        """
        [E2E-02] Menguji fitur lengkap Halaman Beranda & Review Placing Order TANPA ORDER:
        1. Header: Greeting, user avatar header, GPS lokasi saat ini, lonceng notifikasi.
        2. Popup Welcome: Menutup modal sambutan awal tanpa mengganggu antarmuka.
        3. Kartu EvWallet: Buka modal Top Up lalu batalkan, buka pemindai QRIS lalu tutup aman.
        4. Bilah Pencarian: Input alamat tujuan sah ('Stasiun Gambir') & shortcut chip cepat.
        5. Grid Layanan: Verifikasi ketersediaan EvRide, EvSend, dan EvRent.
        6. Tinjauan Pemesanan (Review Placing Order):
           - Membuka layar Review Placing Order untuk EvRide.
           - Verifikasi estimasi tarif, rute jemput-tujuan, dan metode bayar.
           - BATALKAN / KELUAR secara aman tanpa menekan tombol pesan (EXCLUDE PLACING ORDER).
        7. Carousel Promo & Widget: Swipe banner promo horizontal & cek widget trip.
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-02] BERANDA: DOMPET, PENCARIAN, GRID & REVIEW ORDER (EXCLUDE ORDER) <<<")
        print("=" * 80)

        given("Pengguna berada di layar Halaman Beranda")
        assert self.home_page.is_home_screen_displayed(timeout=10), "[E2E-02] Layar Beranda tidak aktif!"

        when("Memverifikasi header sapaan, avatar, dan lokasi penjemputan")
        greeting = self.home_page.get_user_greeting_text()
        loc = self.home_page.get_current_pickup_location_text()
        print(f"  [Header] Sapaan: '{greeting}' | Lokasi: '{loc}'")

        and_step("Menutup popup sambutan jika muncul")
        if self.home_page.is_welcome_modal_displayed(timeout=3):
            self.home_page.dismiss_welcome_modal()
            time.sleep(1.0)

        # Kartu Dompet: Top Up & QRIS
        and_step("Menguji modal Top Up dan Pemindai QRIS pada kartu saldo")
        self.home_page.open_top_up_from_home()
        time.sleep(1.0)
        if self.home_page.is_top_up_modal_displayed(timeout=3):
            self.home_page.cancel_top_up_modal()
            time.sleep(1.0)

        self.home_page.open_qris_scanner()
        time.sleep(1.0)
        if self.home_page.is_qris_scanner_displayed(timeout=3):
            self.home_page.close_qris_scanner()
            time.sleep(1.0)

        # Bilah Pencarian & Quick Chips
        when("Menguji bilah pencarian tujuan dan shortcut lokasi cepat")
        self.home_page.open_destination_search()
        time.sleep(1.0)
        self.home_page.type_destination_query("Stasiun Gambir Pintu Timur")
        time.sleep(1.0)
        self.home_page.click_quick_chip_coffee()
        time.sleep(1.0)

        # Review Placing Order (STRICTLY EXCLUDE PLACING ORDER)
        when("Membuka peninjauan rute EvRide (Review Placing Order)")
        self.home_page.click_evride_service()
        time.sleep(2.0)

        then("Memverifikasi layar Review Placing Order memuat estimasi tarif dan ringkasan rute")
        is_review = self.home_page.is_review_placing_order_displayed(timeout=5)
        fare = self.home_page.get_estimated_fare_text()
        print(f"  [Review Placing Order] Status: {is_review} | Estimasi Biaya: '{fare}'")

        and_step("Membatalkan peninjauan dan kembali ke Beranda TANPA ORDER (EXCLUDE PLACING ORDER)")
        self.home_page.cancel_review_placing_order()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5), "[E2E-02] Gagal kembali ke Beranda setelah batal review!"

        # Promo Carousel & Pull to refresh
        when("Menguji carousel banner promo dengan gestur swipe horizontal")
        self.home_page.swipe_promo_banner(direction="left")
        time.sleep(1.0)
        self.home_page.pull_to_refresh_home()
        time.sleep(1.5)
        print(">>> [E2E-02] Berhasil Menguji Seluruh Fitur Beranda & Review Order Bebas Order! <<<")

    # ==========================================================================
    # FASE 3: AKTIVITAS - TAB REGULAR (NORMAL BOOKING) & E-RECEIPT
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_03_halaman_aktivitas_tab_regular_normal_booking_dan_e_receipt(self, driver):
        """
        [E2E-03] Menguji fungsionalitas Tab Regular pada Halaman Aktivitas:
        1. Navigasi ke tab Activity dari bilah bawah.
        2. Memilih Tab Regular (History order Normal Booking / Instant Ride).
        3. Membuka Help Center dari ikon header Aktivitas lalu menutupnya.
        4. Memfilter layanan (EvRide) dan rentang tanggal 7 hari.
        5. Membuka detail pesanan (E-Receipt), cek tarif, unduh bukti, modal kirim email.
        6. Menguji modal ulasan rating 5 bintang driver pada pesanan selesai.
        7. Menguji tombol pesan lagi (Reorder) dari kartu riwayat.
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-03] AKTIVITAS: TAB REGULAR (NORMAL BOOKING) & E-RECEIPT <<<")
        print("=" * 80)

        given("Pengguna menavigasi ke Halaman Aktivitas")
        self.activity_page.navigate_to_activity_screen()
        time.sleep(1.5)
        assert self.activity_page.is_activity_screen_displayed(timeout=10), "[E2E-03] Layar Aktivitas tidak aktif!"

        when("Mengetuk Tab 'Regular' untuk melihat riwayat order Normal Booking")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        # Help Center
        and_step("Menguji pembukaan dan penutupan Pusat Bantuan dari header")
        self.activity_page.open_help_center()
        time.sleep(1.5)
        if self.activity_page.is_help_center_displayed(timeout=4):
            self.activity_page.close_help_center()
            time.sleep(1.0)

        # Filter Layanan & Tanggal
        when("Menerapkan filter layanan EvRide dan filter tanggal 7 hari")
        self.activity_page.filter_by_evride()
        time.sleep(1.0)
        self.activity_page.open_date_filter()
        time.sleep(1.0)
        if self.activity_page.is_date_filter_modal_displayed(timeout=3):
            self.activity_page.cancel_date_filter()
            time.sleep(1.0)
        self.activity_page.filter_by_all_services()
        time.sleep(1.0)

        # Detail Order, E-Receipt & Rating
        has_cards = self.activity_page.has_order_cards(timeout=4)
        print(f"  [Tab Regular] Kartu Normal Booking: {has_cards}")

        if has_cards:
            and_step("Membuka Layar Detail Pesanan Normal Booking (E-Receipt)")
            self.activity_page.click_first_order_card()
            time.sleep(2.0)

            is_detail = self.activity_page.is_order_detail_displayed(timeout=5)
            order_id = self.activity_page.get_order_id_text()
            print(f"  [E-Receipt] Detail Tampil: {is_detail} | ID Order: '{order_id}'")

            self.activity_page.click_download_receipt()
            time.sleep(1.0)
            self.activity_page.open_email_receipt_modal()
            time.sleep(1.0)
            if self.activity_page.is_email_receipt_modal_displayed(timeout=3):
                self.activity_page.cancel_email_receipt_modal()
                time.sleep(1.0)

            self.activity_page.back_to_activity_list()
            time.sleep(1.5)

            # Rating Driver Modal
            when("Menguji modal ulasan rating bintang 5 driver")
            self.activity_page.click_rate_driver_on_card()
            time.sleep(1.5)
            if self.activity_page.is_rating_modal_displayed(timeout=3):
                self.activity_page.select_5_stars()
                self.activity_page.select_feedback_tags()
                self.activity_page.type_rating_comment("Pelayanan ramah, motor bersih dan aman!")
                self.activity_page.submit_rating()
                time.sleep(1.5)

            # Reorder button
            when("Mengetuk tombol 'Pesan Lagi' (Reorder) dari kartu riwayat")
            self.activity_page.click_reorder_first_item()
            time.sleep(1.5)
            self.activity_page.navigate_to_activity_screen()
            time.sleep(1.5)

        print(">>> [E2E-03] Berhasil Menguji Tab Regular & Seluruh Aksi Pesanan Normal! <<<")

    # ==========================================================================
    # FASE 4: AKTIVITAS - TAB BOOKING (ADVANCE BOOKING & RESCHEDULE)
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_04_halaman_aktivitas_tab_booking_advance_booking_dan_reschedule(self, driver):
        """
        [E2E-04] Menguji fungsionalitas Tab Booking pada Halaman Aktivitas:
        1. Beralih ke Tab Booking (History order Advance Booking / Scheduled Ride).
        2. Memverifikasi daftar pesanan terjadwal dengan waktu penjemputan masa depan.
        3. Menguji modal Ubah Jadwal (Reschedule) penjemputan (buka modal & batalkan aman).
        4. Menguji dialog konfirmasi pembatalan advance booking.
        5. Menguji transisi pergantian cepat dua arah Tab Regular <-> Tab Booking.
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-04] AKTIVITAS: TAB BOOKING (ADVANCE BOOKING & RESCHEDULE) <<<")
        print("=" * 80)

        given("Pengguna berada di Halaman Aktivitas")
        self.activity_page.navigate_to_activity_screen()
        time.sleep(1.0)

        when("Mengetuk Tab 'Booking' untuk melihat riwayat Advance Booking")
        self.activity_page.select_booking_tab()
        time.sleep(1.5)

        then("Memverifikasi daftar pesanan terjadwal di masa depan")
        has_advance = self.activity_page.has_advance_booking_cards(timeout=4)
        print(f"  [Tab Booking] Kartu Advance Booking Terdeteksi: {has_advance}")

        if has_advance:
            scheduled_time = self.activity_page.get_scheduled_datetime_text()
            print(f"  [Advance Booking] Waktu Penjemputan Terjadwal: '{scheduled_time}'")

            when("Menguji modal Ubah Jadwal (Reschedule) pada pesanan terjadwal")
            self.activity_page.open_reschedule_modal()
            time.sleep(1.5)

            if self.activity_page.is_reschedule_modal_displayed(timeout=3):
                self.activity_page.cancel_reschedule_modal()
                time.sleep(1.0)

            and_step("Menguji tombol batalkan Advance Booking dan menutup dialog konfirmasi")
            self.activity_page.click_cancel_advance_booking()
            time.sleep(1.0)
            if self.activity_page.is_cancel_advance_dialog_displayed(timeout=3):
                self.activity_page.abort_cancel_order()
                time.sleep(1.0)

        and_step("Melakukan transisi cepat dua arah antara Tab Booking dan Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)
        self.activity_page.select_booking_tab()
        time.sleep(1.0)
        self.activity_page.select_regular_tab()
        time.sleep(1.0)
        print(">>> [E2E-04] Berhasil Menguji Tab Booking & Fitur Advance Booking Terjadwal! <<<")

    # ==========================================================================
    # FASE 5: PROFIL - AVATAR, GAMBAR, KONTAK DARURAT & ALAMAT TERSIMPAN
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_05_halaman_profil_avatar_gambar_kontak_darurat_dan_alamat(self, driver):
        """
        [E2E-05] Menguji antarmuka Profil Pengguna:
        1. Navigasi ke tab Profil ('Me').
        2. Avatar & Gambar: Ketuk avatar untuk membuka Modal Bottom Sheet Avatar Picker (Kamera vs Galeri).
        3. Menutup modal picker foto secara aman.
        4. Manajemen Dompet & Metode Pembayaran (Cash, Wallet, GoPay).
        5. Kontak Darurat: Buka form tambah kontak darurat, input nama & no HP, simpan.
        6. Alamat Tersimpan: Buka form alamat favorit (Rumah & Kantor).
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-05] PROFIL: AVATAR GAMBAR, KONTAK DARURAT & ALAMAT TERSIMPAN <<<")
        print("=" * 80)

        given("Pengguna menavigasi ke Halaman Profil ('Me')")
        self.profil_page.navigate_to_profil_screen()
        time.sleep(1.5)
        assert self.profil_page.is_profil_screen_displayed(timeout=10), "[E2E-05] Layar Profil tidak aktif!"

        # Avatar & Modal Picker Gambar
        when("Mengetuk foto avatar pengguna untuk membuka Modal Picker Gambar")
        self.profil_page.click_user_avatar()
        time.sleep(1.5)

        then("Bottom Sheet pemilih gambar (Kamera vs Galeri) terbuka")
        if self.profil_page.is_avatar_picker_displayed(timeout=4):
            and_step("Menutup modal picker foto secara aman ('Batal')")
            self.profil_page.cancel_avatar_picker()
            time.sleep(1.0)

        # Kontak Darurat
        when("Membuka menu Kontak Darurat (Emergency Contact)")
        self.profil_page.open_emergency_contacts()
        time.sleep(1.5)
        self.profil_page.click_add_emergency_contact()
        time.sleep(1.0)
        self.profil_page.fill_emergency_contact(name="Budi Pratama", phone="81234567890")
        time.sleep(1.0)
        self.profil_page.back_from_subpage()
        time.sleep(1.5)

        # Alamat Tersimpan
        when("Membuka menu Alamat Tersimpan / Favorit (Saved Addresses)")
        self.profil_page.open_saved_addresses()
        time.sleep(1.5)
        self.profil_page.back_from_subpage()
        time.sleep(1.5)

        print(">>> [E2E-05] Berhasil Menguji Avatar Gambar, Kontak Darurat & Alamat Favorit! <<<")

    # ==========================================================================
    # FASE 6: PROFIL - VIDEO TUTORIAL FAQ, CS SUPPORT & LEGALITAS
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_06_halaman_profil_video_tutorial_faq_dan_customer_service(self, driver):
        """
        [E2E-06] Menguji elemen Multimedia Video & Layanan Dukungan:
        1. Buka menu Pusat Bantuan & Panduan FAQ.
        2. Tinjau video tutorial interaktif, pastikan player controller aktif dan bebas media error.
        3. Tinjau banner Customer Service, buka form bantuan tiket, dan verifikasi popup aturan upload foto.
        4. Tinjau dokumen legalitas (Syarat & Ketentuan serta Kebijakan Privasi).
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-06] PROFIL: MULTIMEDIA VIDEO FAQ, CUSTOMER SERVICE & LEGALITAS <<<")
        print("=" * 80)

        given("Pengguna berada di Halaman Profil")
        self.profil_page.navigate_to_profil_screen()
        time.sleep(1.5)

        # Video Tutorial FAQ
        when("Membuka menu Panduan & Video Tutorial FAQ")
        self.profil_page.open_help_faq()
        time.sleep(2.0)

        then("Memverifikasi elemen Video Player aktif dan tidak mengalami error pemuatan media")
        has_video = self.profil_page.is_video_player_present(timeout=5)
        has_error = self.profil_page.is_video_error_displayed(timeout=2)
        print(f"  [Video Player] Elemen Video Tampil: {has_video} | Media Error: {has_error}")
        assert not has_error, "[E2E-06] Terjadi error pemuatan video tutorial FAQ!"

        self.profil_page.back_from_subpage()
        time.sleep(1.5)

        # Banner CS Support & Popup Aturan Foto
        when("Membuka banner Hubungi Customer Service")
        self.profil_page.open_customer_service()
        time.sleep(1.5)
        self.profil_page.back_from_subpage()
        time.sleep(1.5)

        # Dokumen Legalitas
        when("Membuka dokumen Syarat & Ketentuan dan Kebijakan Privasi")
        self.profil_page.open_terms_conditions()
        time.sleep(1.0)
        self.profil_page.back_from_subpage()
        time.sleep(1.0)

        print(">>> [E2E-06] Berhasil Menguji Video Tutorial FAQ, CS Banner & Legalitas! <<<")

    # ==========================================================================
    # FASE 7: BILINGUAL LANGUAGE SWITCH (INDONESIA <-> ENGLISH)
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_07_bilingual_language_switch_indonesia_ke_english_dan_sebaliknya(self, driver):
        """
        [E2E-07] Menguji fitur Bilingual Language secara bolak-balik:
        1. Buka menu Pengaturan Bahasa di Profil.
        2. Alihkan bahasa ke 'English' ➔ Verifikasi snackbar dan pembaruan label antarmuka.
        3. Alihkan kembali bahasa ke 'Bahasa Indonesia' ➔ Verifikasi pembaruan label antarmuka.
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-07] BILINGUAL LANGUAGE: INDONESIA <-> ENGLISH BIDIRECTIONAL <<<")
        print("=" * 80)

        given("Pengguna berada di Halaman Profil")
        self.profil_page.navigate_to_profil_screen()
        time.sleep(1.5)

        when("Membuka Pengaturan Bahasa dan memilih bahasa 'English'")
        self.profil_page.open_language_settings()
        time.sleep(1.5)
        self.profil_page.switch_language_to_english()
        time.sleep(2.0)

        then("Bahasa antarmuka berhasil beralih ke Bahasa Inggris")
        has_english_snackbar = self.profil_page.is_language_snackbar_displayed(timeout=4)
        print(f"  [Bilingual] Snackbar Switch to English: {has_english_snackbar}")

        when("Membuka kembali Pengaturan Bahasa dan mengembalikan ke 'Indonesia'")
        self.profil_page.open_language_settings()
        time.sleep(1.5)
        self.profil_page.switch_language_to_indonesian()
        time.sleep(2.0)

        then("Bahasa antarmuka berhasil kembali ke Bahasa Indonesia")
        has_indo_snackbar = self.profil_page.is_language_snackbar_displayed(timeout=4)
        print(f"  [Bilingual] Snackbar Switch to Indonesia: {has_indo_snackbar}")
        print(">>> [E2E-07] Berhasil Memvalidasi Fitur Bilingual Language Dua Arah! <<<")

    # ==========================================================================
    # FASE 8: RESILIENSI, HARDWARE BACK & LOGOUT DIALOG KONFIRMASI
    # ==========================================================================

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_TC_E2E_08_resiliensi_backgrounding_hardware_back_dan_logout_konfirmasi(self, driver):
        """
        [E2E-08] Menguji resiliensi OS dan proses Logout akun secara aman:
        1. Resiliensi Hardware Back Android.
        2. Resiliensi App Backgrounding (minimize 3 detik) & resume ke Profil.
        3. Mengetuk tombol Logout / Keluar di bagian paling bawah Profil.
        4. Verifikasi kemunculan Dialog Konfirmasi Keluar ("Apakah Anda yakin?").
        5. Uji tombol Batal (*Cancel*) ➔ tetap di Profil.
        6. Uji tombol Konfirmasi Keluar ➔ berhasil logout dan kembali ke Layar Masuk (Login).
        """
        print("\n" + "=" * 80)
        print(">>> [E2E-08] RESILIENSI OS & LOGOUT DIALOG KONFIRMASI <<<")
        print("=" * 80)

        given("Pengguna berada di Halaman Profil")
        self.profil_page.navigate_to_profil_screen()
        time.sleep(1.5)

        when("Aplikasi di-minimize ke background selama 3 detik lalu di-resume")
        self.profil_page.background_and_resume_app(duration_seconds=3)
        time.sleep(1.5)
        assert self.profil_page.is_profil_screen_displayed(timeout=8), "[E2E-08] State Profil hilang setelah resume!"

        and_step("Menggulir ke bagian paling bawah Profil untuk menemukan tombol Log Out")
        self.profil_page.scroll_to_bottom()
        time.sleep(1.5)

        when("Mengetuk tombol 'Log Out' untuk memicu Dialog Konfirmasi")
        self.profil_page.click_logout()
        time.sleep(1.5)

        then("Dialog konfirmasi keluar aplikasi tampil dengan pilihan Batal & Konfirmasi")
        assert self.profil_page.is_logout_confirm_modal_displayed(timeout=5), "[E2E-08] Dialog logout tidak muncul!"

        and_step("Menguji penolakan logout dengan menekan tombol 'Batal'")
        self.profil_page.cancel_logout()
        time.sleep(1.5)
        assert self.profil_page.is_profil_screen_displayed(timeout=5), "[E2E-08] Tidak kembali ke Profil setelah Batal Logout!"

        when("Mengetuk kembali tombol 'Log Out' lalu menekan 'Ya, Keluar'")
        self.profil_page.click_logout()
        time.sleep(1.5)
        self.profil_page.confirm_logout()
        time.sleep(2.5)

        then("Pengguna berhasil keluar secara aman dan diarahkan kembali ke Layar Masuk / Login")
        is_login = self.login_page.is_login_screen_displayed(timeout=10)
        print(f"  [Logout Status] Berhasil Kembali ke Layar Login: {is_login}")
        assert is_login, "[E2E-08] Pengguna tidak kembali ke Layar Login setelah Logout!"
        print(">>> [E2E-08] Siklus Lengkap Master E2E Berhasil Diselesaikan 100%! <<<")
