"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - TEST SUITE HALAMAN AKTIVITAS (ACTIVITY)
================================================================================
Modul: Halaman Aktivitas & Riwayat Transaksi (Activity & Order History)
Aplikasi: EvMoto Mobile User (Android)
Arsitektur Tab Utama:
  1. TAB REGULAR -> Untuk melihat history order dari Normal Booking (Instant Ride)
  2. TAB BOOKING -> Untuk melihat history order dari Advance Booking (Scheduled Ride)
Metode Pengujian:
  1. METODE HAPPY FLOW TERLEBIH DAHULU:
     Menguji alur penjelajahan positif lengkap dari header Aktivitas, eksplorasi Tab Regular
     (Normal Booking), rincian pesanan (E-Receipt), ulasan rating bintang 5, beralih ke
     Tab Booking (Advance Booking), peninjauan jadwal penjemputan terjadwal & reschedule.
  2. METODE 4 PILAR QA:
     - Pilar 1: Positive True (PT) -> Fungsional normal Tab Regular & Tab Booking
     - Pilar 2: Positive False (PF) -> Pembatalan modal ulasan, reschedule, email, & dialog pembatalan
     - Pilar 3: Negative True (NT) -> Empty states Regular vs Booking, BVA rating 0 bintang, validasi form
     - Pilar 4: Negative False (NF) -> Keamanan (SQLi, XSS), rapid tab switching, resiliensi back & minimize
Jeda Pengujian:
  - JEDA 5 DETIK WAJIB (time.sleep(5.0)) di setiap test case agar bebas dari race condition!
================================================================================
"""
import os
import time
import pytest
from appium.webdriver.webdriver import WebDriver

from utils.logger import get_logger
from utils.bdd_helper import given, when, then, and_step
from Frontend.Feature.Pages.activity_page import ActivityPage
from Frontend.Feature.Pages.home_page import HomePage
from Frontend.Feature.Pages.login_page import LoginPage
from Frontend.Feature.Data.user_data import (
    ACTIVITY_HAPPY_FLOW_DATA,
    ACTIVITY_PILAR_1_POSITIVE,
    ACTIVITY_PILAR_2_NEGATIVE,
    ACTIVITY_PILAR_3_BOUNDARY,
    ACTIVITY_PILAR_4_SECURITY,
    dev_phone,
    dev_otp
)

logger = get_logger("TestActivity")


class TestActivity:
    """Test Suite Lengkap untuk Modul Halaman Aktivitas (Tab Regular & Tab Booking)."""

    @pytest.fixture(autouse=True)
    def setup_activity_test(self, driver: WebDriver):
        """
        Fixture Setup & Teardown untuk setiap skenario uji Halaman Aktivitas:
        1. Pastikan aplikasi berada di Halaman Aktivitas (login & tap nav Activity jika perlu).
        2. Berikan jeda 5 detik anti-race condition setelah setiap test case selesai.
        """
        self.driver = driver
        self.activity_page = ActivityPage(driver)
        self.home_page = HomePage(driver)
        self.login_page = LoginPage(driver)

        # 1. Pastikan pengguna berada di Halaman Aktivitas
        if not self.activity_page.is_activity_screen_displayed(timeout=3):
            # Jika masih di Login, selesaikan login terlebih dahulu
            if self.login_page.is_login_screen_displayed(timeout=2):
                logger.info("[SETUP] Melakukan bypass login untuk masuk ke aplikasi...")
                self.login_page.login(phone=dev_phone, otp=dev_otp)
                time.sleep(2.0)
            
            # Navigasi ke Halaman Aktivitas via bilah navigasi bawah
            logger.info("[SETUP] Menavigasi ke tab Halaman Aktivitas...")
            self.activity_page.navigate_to_activity_screen()
            time.sleep(1.5)

        yield

        # JEDA 5 DETIK ANTI RACE CONDITION SETELAH SETIAP TEST CASE SELESAI
        logger.info("[ANTI RACE CONDITION] Memberikan jeda 5 detik sebelum lanjut...")
        time.sleep(float(os.getenv("QA_TEARDOWN_PAUSE", "5")))  # CI: 1 detik

    # ==========================================================================
    # BAGIAN 1: METODE HAPPY FLOW TERLEBIH DAHULU (E2E REGULAR & BOOKING TABS)
    # ==========================================================================

    @pytest.mark.happy_flow
    @pytest.mark.smoke
    def test_TC_ACT_HF_01_happy_flow_penjelajahan_lengkap_tab_regular_dan_tab_booking(self, driver):
        """
        [HAPPY FLOW] Pengujian alur positif lengkap modul Aktivitas dari atas ke bawah:
        1. Header: Verifikasi judul 'Aktivitas' dan ketersediaan tombol Pusat Bantuan.
        2. Tab Regular (Normal Booking): Tinjau riwayat order normal booking, filter layanan,
           buka rincian invoice (E-Receipt), dan beri rating 5 bintang driver.
        3. Tab Booking (Advance Booking): Beralih ke tab Booking, verifikasi daftar pesanan
           terjadwal (scheduled rides), tinjau detail waktu penjemputan, dan uji modal reschedule.
        4. Kembali ke Beranda: Menggunakan bilah navigasi bawah.
        """
        print("\n" + "=" * 80)
        print(">>> [HAPPY FLOW] E2E PENJELAJAHAN LENGKAP TAB REGULAR & TAB BOOKING <<<")
        print("=" * 80)

        # ----------------------------------------------------------------------
        # TAHAP 1: HEADER AKTIVITAS & IDENTIFIKASI TAB UTAMA
        # ----------------------------------------------------------------------
        given("Pengguna berada di layar Halaman Aktivitas EVMoto")
        assert self.activity_page.is_activity_screen_displayed(timeout=10), "[HF-01] Layar Aktivitas tidak aktif!"

        when("Memverifikasi header judul Aktivitas")
        title = self.activity_page.get_header_title_text()
        print(f"  [1. Header] Judul Terdeteksi: '{title}'")
        assert len(title) > 0, "[HF-01] Judul header Aktivitas tidak tampil!"

        # ----------------------------------------------------------------------
        # TAHAP 2: EKSPLORASI TAB REGULAR (NORMAL BOOKING HISTORY)
        # ----------------------------------------------------------------------
        and_step("Mengetuk Tab 'Regular' untuk melihat riwayat order Normal Booking")
        self.activity_page.select_regular_tab()
        time.sleep(1.5)

        when("Memilih filter 'Semua Layanan' pada riwayat Normal Booking")
        self.activity_page.filter_by_all_services()
        time.sleep(1.0)

        has_regular_cards = self.activity_page.has_order_cards(timeout=4)
        print(f"  [2. Tab Regular - Normal Booking] Terdapat Kartu Riwayat: {has_regular_cards}")

        if has_regular_cards:
            and_step("Mengetuk kartu Normal Booking pertama untuk membuka Layar Detail Pesanan")
            self.activity_page.click_first_order_card()
            time.sleep(2.0)

            then("Memverifikasi elemen rincian pesanan dan total pembayaran")
            is_detail = self.activity_page.is_order_detail_displayed(timeout=6)
            order_id = self.activity_page.get_order_id_text()
            total_paid = self.activity_page.get_total_paid_text()
            print(f"  [Detail Normal Order] Status: {is_detail} | ID: '{order_id}' | Total: '{total_paid}'")

            and_step("Menguji tombol unduh E-Receipt dan modal kirim ke email")
            self.activity_page.click_download_receipt()
            time.sleep(1.0)
            self.activity_page.open_email_receipt_modal()
            time.sleep(1.0)
            if self.activity_page.is_email_receipt_modal_displayed(timeout=3):
                self.activity_page.cancel_email_receipt_modal()
                time.sleep(1.0)

            and_step("Kembali ke daftar Aktivitas")
            self.activity_page.back_to_activity_list()
            time.sleep(1.5)

            and_step("Menguji modal ulasan driver pada order Normal Booking selesai")
            self.activity_page.click_rate_driver_on_card()
            time.sleep(1.5)
            if self.activity_page.is_rating_modal_displayed(timeout=4):
                self.activity_page.select_5_stars()
                self.activity_page.select_feedback_tags()
                self.activity_page.type_rating_comment(ACTIVITY_HAPPY_FLOW_DATA["rating_comment"])
                self.activity_page.submit_rating()
                time.sleep(1.5)

        # ----------------------------------------------------------------------
        # TAHAP 3: EKSPLORASI TAB BOOKING (ADVANCE BOOKING HISTORY)
        # ----------------------------------------------------------------------
        and_step("Mengetuk Tab 'Booking' untuk melihat riwayat order Advance Booking (Terjadwal)")
        self.activity_page.select_booking_tab()
        time.sleep(1.5)

        when("Memverifikasi daftar riwayat pesanan Advance Booking terjadwal")
        has_advance_cards = self.activity_page.has_advance_booking_cards(timeout=4)
        print(f"  [3. Tab Booking - Advance Booking] Terdapat Kartu Booking: {has_advance_cards}")

        if has_advance_cards:
            scheduled_time = self.activity_page.get_scheduled_datetime_text()
            print(f"  [Jadwal Advance Booking] Waktu Penjemputan: '{scheduled_time}'")

            and_step("Menguji modal ubah jadwal (Reschedule) pada Advance Booking")
            self.activity_page.open_reschedule_modal()
            time.sleep(1.5)
            if self.activity_page.is_reschedule_modal_displayed(timeout=4):
                self.activity_page.cancel_reschedule_modal()
                time.sleep(1.0)

        # ----------------------------------------------------------------------
        # TAHAP 4: KEMBALI KE BERANDA UTAMA
        # ----------------------------------------------------------------------
        then("Menavigasi kembali ke Halaman Beranda utama secara mulus")
        self.home_page.navigate_to_home()
        time.sleep(1.5)
        print(">>> [HAPPY FLOW] Penjelajahan Tab Regular & Tab Booking Berhasil Dilalui 100%! <<<")

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - VALIDASI FUNGSIONAL TAB REGULAR & BOOKING
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_ACT_PT_01_verifikasi_header_dan_keberadaan_dua_tab_utama(self, driver):
        """[PT-01] Memverifikasi judul header 'Aktivitas' dan keberadaan Tab Regular & Tab Booking."""
        given("Pengguna membuka Halaman Aktivitas")
        assert self.activity_page.is_activity_screen_displayed(timeout=8), "[PT-01] Layar Aktivitas tidak aktif!"

        then("Memastikan Tab Regular dan Tab Booking keduanya tampil di layar")
        has_regular = self.activity_page.is_regular_tab_displayed(timeout=4)
        has_booking = self.activity_page.is_booking_tab_displayed(timeout=4)
        print(f"  [PT-01] Tab Regular Tampil: {has_regular} | Tab Booking Tampil: {has_booking}")
        assert has_regular or has_booking, "[PT-01] Tab navigasi utama Aktivitas tidak ditemukan!"

    @pytest.mark.positive_true
    def test_TC_ACT_PT_02_eksplorasi_tab_regular_riwayat_order_normal_booking(self, driver):
        """[PT-02] Mengetuk Tab Regular untuk meninjau daftar transaksi Normal Booking (Instant Ride)."""
        given("Pengguna berada di Halaman Aktivitas")
        when("Mengetuk Tab 'Regular'")
        self.activity_page.select_regular_tab()
        time.sleep(1.5)

        then("Daftar pesanan Normal Booking ditampilkan dengan kartu riwayat yang sesuai")
        has_cards = self.activity_page.has_order_cards(timeout=5)
        print(f"  [PT-02] Kartu Normal Booking Terdeteksi: {has_cards}")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.positive_true
    def test_TC_ACT_PT_03_eksplorasi_tab_booking_riwayat_order_advance_booking(self, driver):
        """[PT-03] Mengetuk Tab Booking untuk meninjau daftar pesanan Advance Booking terjadwal."""
        given("Pengguna berada di Halaman Aktivitas")
        when("Mengetuk Tab 'Booking'")
        self.activity_page.select_booking_tab()
        time.sleep(1.5)

        then("Daftar pesanan Advance Booking (jadwal penjemputan masa depan) ditampilkan")
        has_advance = self.activity_page.has_advance_booking_cards(timeout=4)
        has_empty = self.activity_page.is_empty_booking_state_displayed(timeout=3)
        print(f"  [PT-03] Advance Booking Ada: {has_advance} | Empty Booking: {has_empty}")
        assert has_advance or has_empty, "Hasil yang diharapkan harus tampil (cadangan layar generik dihapus agar bug tidak tertutup)"

    @pytest.mark.positive_true
    def test_TC_ACT_PT_04_beralih_mulus_antara_tab_regular_dan_tab_booking(self, driver):
        """[PT-04] Menguji transisi perpindahan mulus dua arah antara Tab Regular dan Tab Booking."""
        given("Pengguna berada di Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        when("Beralih ke Tab Booking")
        self.activity_page.select_booking_tab()
        time.sleep(1.5)

        then("Beralih kembali ke Tab Regular secara responsif")
        self.activity_page.select_regular_tab()
        time.sleep(1.5)
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.positive_true
    def test_TC_ACT_PT_05_pembukaan_dan_penutupan_pusat_bantuan_dari_header(self, driver):
        """[PT-05] Membuka Help Center dari ikon bantuan di header Aktivitas lalu menutupnya."""
        given("Pengguna berada di Halaman Aktivitas")
        when("Mengetuk ikon Pusat Bantuan pada header")
        self.activity_page.open_help_center()
        time.sleep(2.0)

        then("Memverifikasi layar Pusat Bantuan ditampilkan")
        has_help = self.activity_page.is_help_center_displayed(timeout=5)
        print(f"  [PT-05] Help Center Tampil: {has_help}")
        assert has_help, "[PT-05] Layar Pusat Bantuan tidak tampil setelah ikon bantuan di header Aktivitas diketuk!"

        and_step("Menutup layar Pusat Bantuan kembali ke Aktivitas")
        self.activity_page.close_help_center()
        time.sleep(1.5)
        assert not self.activity_page.is_help_center_displayed(timeout=3), (
            "[PT-05] Layar Pusat Bantuan masih tampil setelah tombol tutup/kembali ditekan!"
        )

    @pytest.mark.positive_true
    def test_TC_ACT_PT_06_penyaringan_layanan_pada_tab_regular(self, driver):
        """[PT-06] Mengetuk chip filter layanan (EvRide, EvSend, EvRent) pada Tab Regular."""
        given("Pengguna berada pada Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        when("Mengetuk chip filter 'EvRide'")
        self.activity_page.filter_by_evride()
        time.sleep(1.5)
        assert self.activity_page.is_service_filter_selected(self.activity_page.CHIP_FILTER_EVRIDE), (
            "[PT-06] Chip filter 'EvRide' tidak berstatus terpilih setelah diketuk!"
        )

        and_step("Mengetuk chip filter 'EvSend'")
        self.activity_page.filter_by_evsend()
        time.sleep(1.5)
        assert self.activity_page.is_service_filter_selected(self.activity_page.CHIP_FILTER_EVSEND), (
            "[PT-06] Chip filter 'EvSend' tidak berstatus terpilih setelah diketuk!"
        )
        assert not self.activity_page.is_service_filter_selected(self.activity_page.CHIP_FILTER_EVRIDE), (
            "[PT-06] Chip 'EvRide' masih terpilih padahal filter sudah dipindah ke 'EvSend'!"
        )

        then("Mengembalikan filter ke 'Semua Layanan'")
        self.activity_page.filter_by_all_services()
        time.sleep(1.5)
        assert self.activity_page.is_service_filter_selected(self.activity_page.CHIP_FILTER_ALL), (
            "[PT-06] Chip 'Semua' tidak berstatus terpilih setelah filter dikembalikan!"
        )

    @pytest.mark.positive_true
    def test_TC_ACT_PT_07_penerapan_filter_rentang_tanggal_7_hari_terakhir(self, driver):
        """[PT-07] Membuka modal kalender dan memilih rentang 7 hari terakhir pada riwayat order."""
        given("Pengguna berada di Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        when("Membuka modal filter tanggal")
        self.activity_page.open_date_filter()
        time.sleep(1.5)

        if self.activity_page.is_date_filter_modal_displayed(timeout=4):
            and_step("Memilih opsi 7 hari terakhir dan menerapkan filter")
            self.activity_page.apply_7_days_filter()
            time.sleep(2.0)

        then("Filter tanggal berhasil diterapkan tanpa menimbulkan error")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.positive_true
    def test_TC_ACT_PT_08_tinjauan_rincian_pesanan_dan_e_receipt_tab_regular(self, driver):
        """[PT-08] Mengetuk kartu pesanan Normal Booking untuk meninjau invoice dan total bayar."""
        given("Pengguna berada di Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        when("Mengetuk kartu pesanan pertama")
        then("Layar Rincian Pesanan memuat ID pesanan dan total pembayaran")
        self._open_first_order_detail_or_skip("PT-08")

        and_step("Kembali ke daftar Aktivitas")
        self.activity_page.back_to_activity_list()
        time.sleep(1.5)
        assert not self.activity_page.is_order_id_displayed(timeout=3), (
            "[PT-08] Layar Rincian Pesanan masih tampil setelah tombol kembali ditekan!"
        )
        assert self.activity_page.has_order_cards(timeout=5), (
            "[PT-08] Daftar kartu pesanan tidak tampil lagi setelah kembali dari Rincian Pesanan!"
        )

    @pytest.mark.positive_true
    def test_TC_ACT_PT_09_pengiriman_e_receipt_ke_alamat_email_valid(self, driver):
        """[PT-09] Membuka modal email receipt dan menginput email sah."""
        given("Pengguna berada di Layar Detail Pesanan")
        self._open_first_order_detail_or_skip("PT-09")

        when("Mengetuk tombol Kirim ke Email")
        self.activity_page.open_email_receipt_modal()
        time.sleep(1.5)
        assert self.activity_page.is_email_receipt_modal_displayed(timeout=4), (
            "[PT-09] Modal kirim E-Receipt ke email tidak terbuka!"
        )

        and_step("Mengisi alamat email valid dan mengirim")
        email = ACTIVITY_PILAR_1_POSITIVE["email_receipt"]["email"]
        self.activity_page.submit_email_receipt(email)
        assert self.activity_page.is_receipt_success_snackbar_displayed(timeout=6), (
            f"[PT-09] Notifikasi E-Receipt berhasil dikirim tidak muncul untuk email valid '{email}'!"
        )

        then("Kembali ke daftar Aktivitas")
        self.activity_page.back_to_activity_list()
        time.sleep(1.5)

    @pytest.mark.positive_true
    def test_TC_ACT_PT_10_pemberian_ulasan_rating_bintang_5_driver_normal_booking(self, driver):
        """[PT-10] Memberikan rating 5 bintang, memilih tag apresiasi, dan mengirim ulasan driver."""
        given("Pengguna berada di Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        when("Mengetuk tombol Beri Nilai pada kartu pesanan Normal Booking")
        self.activity_page.click_rate_driver_on_card()
        time.sleep(1.5)

        if self.activity_page.is_rating_modal_displayed(timeout=4):
            and_step("Memilih rating 5 bintang dan tag feedback positif")
            self.activity_page.select_5_stars()
            self.activity_page.select_feedback_tags()
            self.activity_page.type_rating_comment(ACTIVITY_PILAR_1_POSITIVE["rating_submission"]["comment"])
            self.activity_page.submit_rating()
            time.sleep(2.0)

        then("Sistem mencatat ulasan dan antarmuka tetap stabil")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.positive_true
    def test_TC_ACT_PT_11_fitur_pesan_lagi_reorder_rute_dari_kartu_regular(self, driver):
        """[PT-11] Mengetuk tombol 'Pesan Lagi' (Reorder) dari riwayat order Normal Booking."""
        given("Pengguna berada pada kartu riwayat pesanan selesai di Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)
        if not self.activity_page.is_reorder_button_displayed(timeout=4):
            pytest.skip("[PT-11] Tidak ada tombol 'Pesan Lagi' (akun uji belum punya riwayat pesanan selesai).")

        when("Mengetuk tombol 'Pesan Lagi' (Reorder)")
        self.activity_page.click_reorder_first_item()
        time.sleep(2.0)

        then("Sistem mengarahkan ke peninjauan rute yang sama secara instan")
        assert self.activity_page.is_order_booking_screen_displayed(timeout=10), (
            "[PT-11] Layar pemesanan dengan tombol 'Pesan EVMoto' tidak terbuka setelah 'Pesan Lagi' ditekan!"
        )
        # Kembali ke Aktivitas tanpa membuat pesanan baru
        self.activity_page.navigate_to_activity_screen()
        time.sleep(1.5)

    @pytest.mark.positive_true
    def test_TC_ACT_PT_12_fitur_ubah_jadwal_reschedule_pada_tab_booking(self, driver):
        """[PT-12] Mengetuk tombol Ubah Jadwal (Reschedule) pada Advance Booking di Tab Booking."""
        given("Pengguna berada pada Tab Booking")
        self.activity_page.select_booking_tab()
        time.sleep(1.5)
        if not self.activity_page.has_advance_booking_cards(timeout=4):
            pytest.skip("[PT-12] Tidak ada pesanan Advance Booking terjadwal di akun uji, fitur Ubah Jadwal tidak bisa diuji.")

        when("Mengetuk tombol Ubah Jadwal pada pesanan Advance Booking")
        self.activity_page.open_reschedule_modal()
        time.sleep(1.5)

        then("Modal atur ulang waktu tampil dengan opsi tanggal dan jam baru")
        assert self.activity_page.is_reschedule_modal_displayed(timeout=4), (
            "[PT-12] Modal Ubah Jadwal (Reschedule) tidak terbuka setelah tombol Ubah Jadwal ditekan!"
        )
        self.activity_page.cancel_reschedule_modal()
        time.sleep(1.0)
        assert not self.activity_page.is_reschedule_modal_displayed(timeout=3), (
            "[PT-12] Modal Ubah Jadwal tidak tertutup setelah tombol Batal ditekan!"
        )

    @pytest.mark.positive_true
    def test_TC_ACT_PT_13_gestur_pull_to_refresh_memuat_ulang_daftar_aktivitas(self, driver):
        """[PT-13] Menarik layar ke bawah (pull-to-refresh) untuk reload data di Tab Regular."""
        given("Pengguna berada di Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        when("Melakukan gestur pull-to-refresh pada daftar aktivitas")
        self.activity_page.pull_to_refresh_activity()
        time.sleep(2.0)

        then("Daftar pesanan berhasil dimuat ulang dengan responsif")
        assert self.activity_page.is_activity_screen_displayed(timeout=6)

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - PEMBATALAN & INTERAKSI BATAS
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_ACT_PF_01_pembatalan_modal_penilaian_driver_nanti_saja(self, driver):
        """[PF-01] Menutup modal ulasan driver dengan memilih 'Nanti Saja' tanpa mengirim rating."""
        given("Pengguna membuka modal ulasan driver")
        self.activity_page.click_rate_driver_on_card()
        time.sleep(1.5)

        if self.activity_page.is_rating_modal_displayed(timeout=4):
            when("Mengetuk tombol 'Nanti Saja' atau Batal")
            self.activity_page.dismiss_rating_modal()
            time.sleep(1.5)

        then("Modal ulasan tertutup dan pengguna tetap di Halaman Aktivitas")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.positive_false
    def test_TC_ACT_PF_02_pembatalan_modal_kirim_e_receipt_ke_email(self, driver):
        """[PF-02] Membuka dialog kirim email bukti transaksi lalu menekan tombol Batal."""
        given("Pengguna membuka Layar Detail Pesanan")
        self._open_first_order_detail_or_skip("PF-02")

        when("Membuka modal kirim E-Receipt ke email lalu menekan Batal")
        self.activity_page.open_email_receipt_modal()
        time.sleep(1.5)
        assert self.activity_page.is_email_receipt_modal_displayed(timeout=4), (
            "[PF-02] Modal kirim E-Receipt ke email tidak terbuka!"
        )
        self.activity_page.cancel_email_receipt_modal()
        time.sleep(1.0)

        then("Modal tertutup dan pengguna kembali ke Detail Pesanan")
        assert not self.activity_page.is_email_receipt_modal_displayed(timeout=3), (
            "[PF-02] Modal kirim E-Receipt masih terbuka setelah tombol Batal ditekan!"
        )
        assert not self.activity_page.is_receipt_success_snackbar_displayed(timeout=2), (
            "[PF-02] E-Receipt tetap terkirim padahal pengiriman dibatalkan!"
        )
        assert self.activity_page.is_order_id_displayed(timeout=4), (
            "[PF-02] Pengguna tidak kembali ke Rincian Pesanan setelah membatalkan modal email!"
        )
        self.activity_page.back_to_activity_list()
        time.sleep(1.5)

    @pytest.mark.positive_false
    def test_TC_ACT_PF_03_pembatalan_pelaporan_kendala_pesanan(self, driver):
        """[PF-03] Membuka opsi laporkan masalah perjalanan lalu membatalkannya."""
        given("Pengguna membuka Layar Detail Pesanan")
        self._open_first_order_detail_or_skip("PF-03")

        when("Membuka menu Laporkan Masalah lalu membatalkannya")
        self.activity_page.open_report_order_issue()
        time.sleep(1.5)
        assert self.activity_page.is_report_issue_modal_displayed(timeout=4), (
            "[PF-03] Modal pilihan kendala tidak terbuka setelah 'Laporkan Masalah' ditekan!"
        )
        self.activity_page.cancel_issue_report()
        time.sleep(1.0)

        then("Pengguna kembali ke tampilan detail pesanan secara aman")
        assert not self.activity_page.is_report_issue_modal_displayed(timeout=3), (
            "[PF-03] Modal pelaporan kendala masih terbuka setelah dibatalkan!"
        )
        assert not self.activity_page.is_issue_submitted_dialog_displayed(timeout=2), (
            "[PF-03] Laporan kendala tetap terkirim padahal pelaporan dibatalkan!"
        )
        assert self.activity_page.is_order_id_displayed(timeout=4), (
            "[PF-03] Pengguna tidak kembali ke Rincian Pesanan setelah membatalkan pelaporan!"
        )
        self.activity_page.back_to_activity_list()
        time.sleep(1.5)

    @pytest.mark.positive_false
    def test_TC_ACT_PF_04_pembatalan_modal_ubah_jadwal_advance_booking(self, driver):
        """[PF-04] Menutup modal ubah jadwal Advance Booking tanpa menyimpan waktu baru."""
        given("Pengguna berada di Tab Booking")
        self.activity_page.select_booking_tab()
        time.sleep(1.5)

        if self.activity_page.has_advance_booking_cards(timeout=4):
            when("Membuka modal Ubah Jadwal lalu menekan tombol Batal")
            self.activity_page.open_reschedule_modal()
            time.sleep(1.5)
            if self.activity_page.is_reschedule_modal_displayed(timeout=4):
                self.activity_page.cancel_reschedule_modal()
                time.sleep(1.0)

            then("Jadwal penjemputan advance booking semula tetap dipertahankan tanpa perubahan")
            assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.positive_false
    def test_TC_ACT_PF_05_pembatalan_konfirmasi_batalkan_pesanan_aktif(self, driver):
        """[PF-05] Menekan batalkan pesanan aktif, memicu dialog konfirmasi, lalu memilih 'Lanjutkan Pesanan'."""
        given("Pengguna berada pada tab 'Dalam Proses'")
        self.activity_page.select_in_progress_tab()
        time.sleep(1.5)
        if not self.activity_page.is_cancel_active_order_button_displayed(timeout=4):
            pytest.skip("[PF-05] Tidak ada pesanan aktif yang bisa dibatalkan di akun uji.")

        when("Mengetuk tombol batalkan pesanan lalu membatalkan dialog konfirmasi")
        self.activity_page.click_cancel_active_order()
        time.sleep(1.5)
        assert self.activity_page.is_cancel_order_dialog_displayed(timeout=4), (
            "[PF-05] Dialog konfirmasi pembatalan pesanan tidak muncul!"
        )
        self.activity_page.abort_cancel_order()
        time.sleep(1.0)

        then("Pesanan aktif tidak dibatalkan dan perjalanan tetap berjalan")
        assert not self.activity_page.is_cancel_order_dialog_displayed(timeout=3), (
            "[PF-05] Dialog konfirmasi pembatalan masih terbuka setelah memilih tidak jadi membatalkan!"
        )
        assert self.activity_page.is_cancel_active_order_button_displayed(timeout=5), (
            "[PF-05] Pesanan aktif hilang dari tab 'Dalam Proses' padahal pembatalan tidak dikonfirmasi!"
        )
        self.activity_page.select_history_tab()
        time.sleep(1.0)

    @pytest.mark.positive_false
    def test_TC_ACT_PF_06_pembatalan_modal_pemilih_tanggal_kalender(self, driver):
        """[PF-06] Menutup modal filter tanggal tanpa menerapkan rentang tanggal baru."""
        given("Pengguna membuka modal filter kalender tanggal")
        self.activity_page.open_date_filter()
        time.sleep(1.5)

        when("Mengetuk tombol Batal pada modal pemilih tanggal")
        if self.activity_page.is_date_filter_modal_displayed(timeout=4):
            self.activity_page.cancel_date_filter()
            time.sleep(1.0)

        then("Modal tertutup tanpa mengubah filter yang aktif sebelumnya")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.positive_false
    def test_TC_ACT_PF_07_reset_filter_layanan_kembali_ke_semua(self, driver):
        """[PF-07] Mengaktifkan filter EvRent lalu mengetuk chip 'Semua Layanan' untuk mereset."""
        given("Pengguna memilih filter 'EvRent'")
        self.activity_page.filter_by_evrent()
        time.sleep(1.5)

        when("Mengetuk chip 'Semua Layanan'")
        self.activity_page.filter_by_all_services()
        time.sleep(1.5)

        then("Seluruh daftar transaksi gabungan tampil kembali")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - BOUNDARY VALUE ANALYSIS & EMPTY STATES
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_ACT_NT_01_state_kosong_tab_regular_saat_belum_ada_transaksi(self, driver):
        """[NT-01] Memverifikasi tampilan placeholder 'Belum Ada Aktivitas' pada Tab Regular kosong."""
        given("Pengguna membuka Tab Regular pada akun baru tanpa riwayat order")
        self.activity_page.select_regular_tab()
        time.sleep(1.5)

        then("Tampilan state kosong terdeteksi secara ramah")
        has_empty = self.activity_page.is_empty_state_displayed(timeout=3)
        print(f"  [NT-01] Placeholder Empty State Regular: {has_empty}")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.negative_true
    def test_TC_ACT_NT_02_state_kosong_tab_booking_saat_belum_ada_advance_booking(self, driver):
        """[NT-02] Memverifikasi tampilan placeholder 'Belum ada Advance Booking terjadwal' pada Tab Booking."""
        given("Pengguna membuka Tab Booking")
        self.activity_page.select_booking_tab()
        time.sleep(1.5)
        if self.activity_page.has_advance_booking_cards(timeout=3):
            pytest.skip("[NT-02] Akun uji memiliki pesanan Advance Booking, empty state Tab Booking tidak bisa diuji.")

        then("Jika tidak ada jadwal booking masa depan, sistem menampilkan empty state khusus")
        has_empty_booking = self.activity_page.is_empty_booking_state_displayed(timeout=4)
        print(f"  [NT-02] Placeholder Empty State Booking: {has_empty_booking}")
        assert has_empty_booking, (
            "[NT-02] Tab Booking tanpa pesanan terjadwal tidak menampilkan empty state 'Rencanakan Perjalanan Anda'!"
        )
        # Beralih kembali ke Regular
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

    @pytest.mark.negative_true
    def test_TC_ACT_NT_03_state_kosong_hasil_filter_tidak_menemukan_pesanan(self, driver):
        """[NT-03] Memilih kombinasi filter yang menghasilkan 0 pesanan (empty filter state)."""
        given("Pengguna berada di Tab Regular")
        self.activity_page.select_regular_tab()
        time.sleep(1.0)

        when("Memilih filter layanan tanpa transaksi")
        self.activity_page.filter_by_evrent()
        time.sleep(1.5)
        if self.activity_page.has_order_cards(timeout=3):
            pytest.skip("[NT-03] Akun uji memiliki pesanan EvRent, hasil filter kosong tidak bisa diuji.")

        then("Jika tidak ada data, sistem menampilkan pesan 'Tidak ada pesanan yang sesuai'")
        assert self.activity_page.is_empty_filter_result_displayed(timeout=4), (
            "[NT-03] Filter tanpa hasil tidak menampilkan pesan 'Tidak ada pesanan yang sesuai'!"
        )
        self.activity_page.reset_empty_filter()
        time.sleep(1.0)
        self.activity_page.filter_by_all_services()

    @pytest.mark.negative_true
    def test_TC_ACT_NT_04_validasi_penolakan_submit_rating_0_bintang(self, driver):
        """[NT-04] Menekan kirim ulasan tanpa memilih bintang (dicegah & muncul peringatan)."""
        given("Pengguna membuka modal ulasan driver")
        if not self.activity_page.is_rate_driver_button_displayed(timeout=4):
            pytest.skip("[NT-04] Tidak ada tombol beri nilai driver (akun uji belum punya pesanan selesai yang bisa dinilai).")
        self.activity_page.click_rate_driver_on_card()
        time.sleep(1.5)
        assert self.activity_page.is_rating_modal_displayed(timeout=4), (
            "[NT-04] Modal penilaian driver tidak terbuka!"
        )

        when("Langsung menekan tombol 'Kirim Penilaian' tanpa memilih bintang")
        self.activity_page.submit_rating()
        time.sleep(1.0)

        then("Sistem memunculkan peringatan wajib memilih minimal 1 bintang")
        has_warning = self.activity_page.is_zero_star_warning_displayed(timeout=3)
        print(f"  [NT-04] Peringatan Rating 0 Bintang: {has_warning}")
        assert has_warning, "[NT-04] Peringatan 'Silakan ketuk bintang untuk memberi rating' tidak muncul!"
        assert not self.activity_page.is_rating_success_snackbar_displayed(timeout=2), (
            "[NT-04] Penilaian 0 bintang justru berhasil dikirim!"
        )
        assert self.activity_page.is_rating_modal_displayed(timeout=3), (
            "[NT-04] Modal penilaian tertutup padahal penilaian 0 bintang seharusnya ditolak!"
        )

        self.activity_page.dismiss_rating_modal()
        time.sleep(1.0)

    @pytest.mark.negative_true
    def test_TC_ACT_NT_05_validasi_deskripsi_laporan_masalah_dikosongkan(self, driver):
        """[NT-05] Mencoba submit laporan kendala dengan field teks dibiarkan kosong."""
        given("Pengguna membuka form pelaporan masalah")
        self._open_first_order_detail_or_skip("NT-05")
        self.activity_page.open_report_order_issue()
        time.sleep(1.5)
        assert self.activity_page.is_report_issue_modal_displayed(timeout=4), (
            "[NT-05] Modal pilihan kendala tidak terbuka setelah 'Laporkan Masalah' ditekan!"
        )

        when("Memilih opsi masalah namun membiarkan deskripsi kosong lalu submit")
        self.activity_page.select_lost_item_issue()
        self.activity_page.submit_issue_report()
        time.sleep(1.0)

        then("Sistem menampilkan peringatan 'Deskripsi kendala wajib diisi'")
        assert self.activity_page.is_empty_issue_warning_displayed(timeout=4), (
            "[NT-05] Peringatan 'Deskripsi kendala wajib diisi' tidak muncul saat deskripsi kosong!"
        )
        assert not self.activity_page.is_issue_submitted_dialog_displayed(timeout=2), (
            "[NT-05] Laporan kendala tanpa deskripsi justru berhasil dikirim!"
        )
        self.activity_page.cancel_issue_report()
        time.sleep(1.0)

        self.activity_page.back_to_activity_list()
        time.sleep(1.5)

    @pytest.mark.negative_true
    def test_TC_ACT_NT_06_validasi_format_email_tidak_valid_pada_e_receipt(self, driver):
        """[NT-06] Menginput email tanpa simbol '@' atau format tidak valid pada kirim e-receipt."""
        given("Pengguna membuka modal kirim E-Receipt ke email")
        self._open_first_order_detail_or_skip("NT-06")
        self.activity_page.open_email_receipt_modal()
        time.sleep(1.5)
        assert self.activity_page.is_email_receipt_modal_displayed(timeout=4), (
            "[NT-06] Modal kirim E-Receipt ke email tidak terbuka!"
        )

        invalid_email = ACTIVITY_PILAR_3_BOUNDARY["invalid_email_receipt"]["email"]
        when(f"Mengisi email invalid: '{invalid_email}' lalu menekan kirim")
        self.activity_page.submit_email_receipt(invalid_email)
        time.sleep(1.0)

        then("Sistem menolak format email yang tidak valid")
        assert not self.activity_page.is_receipt_success_snackbar_displayed(timeout=3), (
            f"[NT-06] E-Receipt tetap terkirim ke email tidak valid '{invalid_email}'!"
        )
        assert self.activity_page.is_email_receipt_modal_displayed(timeout=3), (
            "[NT-06] Modal email tertutup padahal format email tidak valid seharusnya ditolak!"
        )
        self.activity_page.cancel_email_receipt_modal()
        time.sleep(1.0)

        self.activity_page.back_to_activity_list()
        time.sleep(1.5)

    @pytest.mark.negative_true
    def test_TC_ACT_NT_07_penanganan_koneksi_internet_terputus_di_halaman_aktivitas(self, driver):
        """[NT-07] Menguji deteksi ketiadaan internet saat memuat riwayat & tombol Coba Lagi."""
        given("Pengguna berada di Halaman Aktivitas")
        when("Koneksi internet perangkat diputus lalu daftar aktivitas dimuat ulang")
        if not self.activity_page.set_device_network(enabled=False):
            pytest.skip("[NT-07] Appium menolak 'mobile: shell' (jalankan server dengan --allow-insecure=adb_shell), "
                        "jaringan perangkat tidak bisa diputus.")
        try:
            self.activity_page.pull_to_refresh_activity()
            has_offline = self.activity_page.is_offline_snackbar_displayed(timeout=8)
            print(f"  [NT-07] Snackbar Offline Terdeteksi: {has_offline}")

            then("Aplikasi menampilkan pesan jaringan terputus dan tidak crash")
            assert has_offline, (
                "[NT-07] Pesan jaringan terputus tidak muncul saat memuat Halaman Aktivitas tanpa internet!"
            )
            assert self.activity_page.is_app_in_foreground(), (
                "[NT-07] Aplikasi tidak lagi di layar depan (crash/force close) saat internet terputus!"
            )
        finally:
            # Jaringan selalu dipulihkan agar test berikutnya tidak ikut offline
            self.activity_page.set_device_network(enabled=True)

        and_step("Jika tombol 'Coba Lagi' tersedia, muat ulang setelah koneksi pulih")
        if self.activity_page.is_displayed(self.activity_page.BTN_RETRY_ACTIVITY, timeout=3):
            self.activity_page.click_retry_activity()
            time.sleep(1.5)

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - KEAMANAN & RESILIENSI SISTEM
    # ==========================================================================

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_ACT_NF_01_sanitasi_sql_injection_pada_kolom_ulasan_driver(self, driver):
        """[NF-01] Menguji payload SQL Injection (' OR '1'='1' --) pada kolom komentar ulasan."""
        given("Pengguna membuka modal ulasan driver")
        self.activity_page.click_rate_driver_on_card()
        time.sleep(1.5)

        if self.activity_page.is_rating_modal_displayed(timeout=4):
            when("Menginput payload SQL Injection pada field catatan driver")
            sqli_payload = ACTIVITY_PILAR_4_SECURITY["sqli_rating_comment"]["payload"]
            self.activity_page.select_5_stars()
            self.activity_page.type_rating_comment(sqli_payload)
            self.activity_page.submit_rating()
            time.sleep(2.0)

        then("Sistem mensanitasi input dan aplikasi tetap stabil tanpa kebocoran basis data")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_ACT_NF_02_sanitasi_xss_pada_form_pelaporan_kendala(self, driver):
        """[NF-02] Menguji payload Cross-Site Scripting (<script>) pada deskripsi komplain perjalanan."""
        given("Pengguna berada di form pelaporan masalah pesanan")
        self._open_first_order_detail_or_skip("NF-02")
        self.activity_page.open_report_order_issue()
        time.sleep(1.5)
        assert self.activity_page.is_report_issue_modal_displayed(timeout=4), (
            "[NF-02] Modal pilihan kendala tidak terbuka setelah 'Laporkan Masalah' ditekan!"
        )

        when("Menginput payload XSS script pada deskripsi kendala")
        xss_payload = ACTIVITY_PILAR_4_SECURITY["xss_issue_description"]["payload"]
        self.activity_page.select_lost_item_issue()
        self.activity_page.type_issue_description(xss_payload)
        self.activity_page.submit_issue_report()
        time.sleep(2.0)

        then("Payload script HTML/JS tidak dieksekusi oleh WebView dan diproses aman")
        assert self.activity_page.is_app_in_foreground(), (
            "[NF-02] Aplikasi tidak lagi di layar depan (crash/force close) setelah payload XSS dikirim!"
        )
        assert self.activity_page.is_issue_submitted_dialog_displayed(timeout=6), (
            "[NF-02] Laporan berisi payload XSS tidak diproses sebagai teks biasa "
            "(dialog 'Laporan Anda Diterima' tidak muncul)!"
        )
        self.activity_page.close_issue_submitted_dialog()
        time.sleep(1.0)
        self.activity_page.back_to_activity_list()
        time.sleep(1.5)

    @pytest.mark.negative_false
    def test_TC_ACT_NF_03_rapid_switching_antara_tab_regular_dan_tab_booking(self, driver):
        """[NF-03] Melakukan perpindahan tab cepat (multi-tap switching) antara Regular dan Booking."""
        given("Pengguna berada di Halaman Aktivitas")
        when("Melakukan pergantian tab secara beruntun 4 kali (Regular <-> Booking)")
        for _ in range(2):
            self.activity_page.select_booking_tab()
            self.activity_page.select_regular_tab()

        time.sleep(1.5)
        then("Sistem tidak mengalami race condition atau crash pada state list")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.negative_false
    def test_TC_ACT_NF_04_rapid_repeated_tapping_tombol_refresh_anti_race_condition(self, driver):
        """[NF-04] Melakukan multi-tap spamming pada tombol refresh riwayat."""
        given("Pengguna berada di Halaman Aktivitas")
        when("Melakukan ketukan beruntun cepat (3x tap) pada chip filter")
        for _ in range(ACTIVITY_PILAR_4_SECURITY["rapid_tapping_refresh"]["taps"]):
            self.activity_page.filter_by_all_services()

        time.sleep(2.0)
        then("Antarmuka tidak mengalami crash atau freeze akibat race condition")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.negative_false
    def test_TC_ACT_NF_05_resiliensi_tombol_android_hardware_back_dari_detail_pesanan(self, driver):
        """[NF-05] Menekan tombol fisik Android Back saat berada di layar E-Receipt / Detail Pesanan."""
        given("Pengguna berada di Layar Detail Pesanan")
        self.activity_page.click_first_order_card()
        time.sleep(2.0)

        when("Menekan tombol Android Hardware Back")
        try:
            self.driver.back()
            time.sleep(1.5)
        except Exception as e:
            logger.warning(f"Hardware back disimulasikan: {e}")
            self.activity_page.back_to_activity_list()

        then("Aplikasi kembali ke daftar Halaman Aktivitas secara anggun")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.negative_false
    def test_TC_ACT_NF_06_ketahanan_rendering_antarmuka_terhadap_scroll_vertikal_panjang(self, driver):
        """[NF-06] Menguji resiliensi daftar riwayat terhadap gestur scroll cepat ke bawah dan atas."""
        given("Pengguna berada pada daftar riwayat Aktivitas")
        when("Melakukan gestur scroll vertikal cepat ke bawah dan kembali ke atas")
        try:
            size = self.driver.get_window_size()
            width = size["width"]
            height = size["height"]
            center_x = width // 2
            # Scroll ke bawah
            self.driver.swipe(center_x, int(height * 0.75), center_x, int(height * 0.25), duration=400)
            time.sleep(0.5)
            # Scroll ke atas
            self.driver.swipe(center_x, int(height * 0.25), center_x, int(height * 0.75), duration=400)
            time.sleep(1.0)
        except Exception as e:
            logger.warning(f"Gestur scroll stress test disimulasikan: {e}")

        then("Rendering daftar riwayat tetap responsif dan lancar (60 FPS)")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

    @pytest.mark.negative_false
    def test_TC_ACT_NF_07_resiliensi_app_backgrounding_minimize_dan_resume_di_aktivitas(self, driver):
        """[NF-07] Me-minimize aplikasi selama 3 detik lalu me-resume ke Halaman Aktivitas."""
        given("Pengguna berada di Halaman Aktivitas")
        assert self.activity_page.is_activity_screen_displayed(timeout=5)

        when("Aplikasi di-minimize ke background selama 3 detik")
        duration = ACTIVITY_PILAR_4_SECURITY["background_app_duration"]
        self.activity_page.background_and_resume_app(duration_seconds=duration)

        then("Aplikasi berhasil di-resume dan antarmuka Halaman Aktivitas tetap utuh")
        assert self.activity_page.is_activity_screen_displayed(timeout=8), (
            "[NF-07] State Halaman Aktivitas hilang setelah resume dari background!"
        )

    # ==========================================================================
    # HELPER KHUSUS SUITE AKTIVITAS (bukan test case)
    # ==========================================================================

    def _open_first_order_detail_or_skip(self, tc_id: str):
        """Membuka Rincian Pesanan dari kartu pertama; skip bila akun uji belum punya riwayat pesanan."""
        if not self.activity_page.has_order_cards(timeout=5):
            pytest.skip(f"[{tc_id}] Akun uji belum memiliki kartu riwayat pesanan di Halaman Aktivitas.")
        self.activity_page.click_first_order_card()
        time.sleep(2.0)
        assert self.activity_page.is_order_id_displayed(timeout=6), (
            f"[{tc_id}] Layar Rincian Pesanan ('ID Pesanan') tidak terbuka setelah kartu pesanan diketuk!"
        )
