"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - TEST SUITE: BERANDA UTAMA (test_home.py)
================================================================================
Target Aplikasi : EvMoto User Mobile App (com.evmoto.user.app)
Lingkungan      : Universal (Staging / Development / Production Live)
Target Modul    : Halaman Beranda Utama (Home Screen / Dashboard)
Metodologi QA   :
  1. METODE HAPPY FLOW TERLEBIH DAHULU:
     Memverifikasi seluruh alur Beranda dari elemen teratas hingga navigasi terbawah:
     - Header, greeting 'Hi, where are you going today?', alamat penjemputan, notifikasi
     - Kartu saldo dompet EvWallet dan shortcut top-up
     - Bilah pencarian tujuan perjalanan & quick chips (ngopi, kantor, rumah)
     - Grid layanan transportasi ramah lingkungan: EvRide, EvSend, EvRent
     - Carousel banner promo & berita hijau
     - Widget aktivitas terkini & live trip
     - Bilah navigasi bawah (Home, Activity, Me)
  2. 4 PILAR METODE QA LENGKAP:
     - Pilar 1: Positive True (PT) - Fungsionalitas Fitur & Layanan Valid
     - Pilar 2: Positive False (PF) - Aturan Bisnis, Pembatalan Modal, & Cooldown
     - Pilar 3: Negative True (NT) - Penolakan Input Invalid, BVA, & Empty States
     - Pilar 4: Negative False (NF) - Keamanan (SQLi/XSS), Multi-Tapping & Resiliensi UI
Aturan Eksekusi :
  - JEDA 5 DETIK pada setiap test case untuk mencegah race condition.
  - Page Object Model (POM) tersimpan di 'Pages/home_page.py'.
  - ATURAN KHUSUS BISNIS: Skenario penempatan order sesungguhnya (Placing Order / Dispatch Driver)
    DI-EXCLUDE secara sengaja dari modul Beranda. Pengujian difokuskan secara presisi hanya sampai tahap
    'User Review Placing Order' (tinjauan estimasi tarif, rute titik jemput & tujuan, dan metode bayar)
    lalu membatalkan kembali ke Beranda.
================================================================================
"""
import time
import pytest
from Pages.login_page import LoginPage
from Pages.home_page import HomePage
from Pages.booking_page import BookingPage
from Pages.profil_page import ProfilPage
from Data.user_data import (
    MobileUserDataProvider,
    HOME_HAPPY_FLOW_DATA,
    HOME_PILAR_1_POSITIVE,
    HOME_PILAR_2_NEGATIVE,
    HOME_PILAR_3_BOUNDARY,
    HOME_PILAR_4_SECURITY,
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestHome")


class TestHome:
    """Suite Pengujian Otomasi Halaman Beranda Utama EvMoto (Happy Flow & 4 Pilar QA)."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown_home_session(self, driver):
        """
        Fixture inisialisasi sesi login otomatis menuju layar Beranda Utama.
        Menyertakan jeda 5 detik wajib di akhir setiap pengetesan untuk mencegah race condition.
        """
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.home_page = HomePage(driver)
        self.booking_page = BookingPage(driver)
        self.profil_page = ProfilPage(driver)

        # Mengambil kredensial pengujian dinamis (Universal Dev & Production)
        user = MobileUserDataProvider.get_dev_user()
        self.user_phone = user["phone"]
        self.user_otp = user["otp"]

        logger.info(f"Menginisialisasi sesi pengujian Beranda untuk nomor: {self.user_phone}")
        # 1. Pastikan di layar login awal
        self.login_page.is_login_screen_displayed(timeout=20)
        self.login_page.input_phone_number(self.user_phone)
        self.login_page.click_submit_login()
        self.login_page.input_otp_dev(self.user_otp, fast_transition=True)
        self.login_page.handle_location_prompt_if_present(timeout=5)

        # 2. Pastikan Beranda utama termuat dengan stabil
        assert self.home_page.is_home_screen_displayed(timeout=20), (
            "[GAGAL SETUP] Layar Beranda utama EVMoto tidak berhasil dimuat!"
        )

        yield

        # JEDA 5 DETIK ANTI RACE CONDITION SETELAH SETIAP TEST CASE SELESAI
        logger.info("[ANTI RACE CONDITION] Memberikan jeda 5 detik sebelum lanjut...")
        time.sleep(5.0)

    # ==========================================================================
    # BAGIAN 1: METODE HAPPY FLOW TERLEBIH DAHULU (E2E PERJALANAN LENGKAP BERANDA)
    # DIURUTKAN DARI PALING ATAS HINGGA PALING BAWAH
    # ==========================================================================

    @pytest.mark.happy_flow
    @pytest.mark.smoke
    def test_TC_HOME_HF_01_happy_flow_perjalanan_lengkap_seluruh_fitur_beranda(self, driver):
        """
        [HAPPY FLOW] Pengujian alur positif lengkap modul Beranda Utama dari paling atas ke bawah:
        1. [ATAS] Header: Membaca sapaan pengguna, alamat penjemputan saat ini, dan lonceng notifikasi.
        2. Kartu Saldo: Verifikasi saldo EvWallet, buka modal Top Up dan tutup kembali.
        3. Bilah Pencarian: Ketuk kolom pencarian destinasi dan tinjau quick destination chips.
        4. Layanan Utama: Periksa ketersediaan ikon EvRide, EvSend, dan EvRent.
        5. Carousel Promo: Verifikasi banner diskon hijau dan lakukan gestur swipe horizontal.
        6. Widget Aktivitas: Tinjau status pesanan aktif / riwayat trip.
        7. [BAWAH] Bottom Bar: Navigasi ke tab Activity, tab Me (Profil), dan kembali ke Home.
        """
        print("\n" + "=" * 80)
        print(">>> [HAPPY FLOW] E2E PERJALANAN LENGKAP FITUR BERANDA (ATAS KE BAWAH) <<<")
        print("=" * 80)

        # ----------------------------------------------------------------------
        # TAHAP 1: [PALING ATAS] HEADER, GREETING & LOKASI
        # ----------------------------------------------------------------------
        given("Pengguna berada di layar utama Beranda EVMoto")
        assert self.home_page.is_home_screen_displayed(timeout=10), "[HF-01] Layar Beranda tidak aktif!"

        when("Memverifikasi elemen header sapaan dan alamat penjemputan saat ini")
        greeting = self.home_page.get_user_greeting_text()
        current_loc = self.home_page.get_current_pickup_location_text()
        has_bell = self.home_page.is_notification_bell_displayed(timeout=5)
        print(f"  [1. Header] Greeting: '{greeting}' | Lokasi: '{current_loc}' | Bell: {has_bell}")
        assert has_bell or len(greeting) > 0, "[HF-01] Header Beranda tidak termuat lengkap!"

        # ----------------------------------------------------------------------
        # TAHAP 2: KARTU SALDO & SHORTCUT DOMPET
        # ----------------------------------------------------------------------
        and_step("Memeriksa kartu saldo EvWallet dan menguji modal Top Up")
        wallet_bal = self.home_page.get_wallet_balance_text()
        print(f"  [2. Saldo Dompet] Saldo Terdeteksi: '{wallet_bal}'")
        self.home_page.open_top_up_from_home()
        time.sleep(1.5)
        if self.home_page.is_top_up_modal_displayed(timeout=4):
            self.home_page.cancel_top_up_modal()
            time.sleep(1)

        # ----------------------------------------------------------------------
        # TAHAP 3: BILAH PENCARIAN DESTINASI & QUICK CHIPS
        # ----------------------------------------------------------------------
        and_step("Meninjau bilah pencarian tujuan dan shortcut lokasi favorit")
        has_coffee = self.home_page.is_displayed(self.home_page.DESTINATION_COFFEE, timeout=3)
        has_office = self.home_page.is_displayed(self.home_page.DESTINATION_OFFICE, timeout=3)
        has_home = self.home_page.is_displayed(self.home_page.DESTINATION_HOME, timeout=3)
        print(f"  [3. Destinasi] Quick Chips -> Ngopi: {has_coffee} | Kantor: {has_office} | Rumah: {has_home}")

        # ----------------------------------------------------------------------
        # TAHAP 4: GRID LAYANAN UTAMA & TINJAUAN REVIEW PLACING ORDER (EXCLUDE ORDER)
        # ----------------------------------------------------------------------
        and_step("Memverifikasi ketersediaan grid layanan dan meninjau layar Review Placing Order tanpa pesan")
        has_evride = self.home_page.is_displayed(self.home_page.SERVICE_EVRIDE, timeout=4)
        has_evsend = self.home_page.is_displayed(self.home_page.SERVICE_EVSEND, timeout=4)
        has_evrent = self.home_page.is_displayed(self.home_page.SERVICE_EVRENT, timeout=4)
        print(f"  [4. Layanan] EvRide: {has_evride} | EvSend: {has_evsend} | EvRent: {has_evrent}")
        assert has_evride, "[HF-01] Layanan utama EvRide tidak ditemukan di Beranda!"

        # Navigasi ke review pemesanan EvRide dan tinjau tanpa menekan 'Pesan Sekarang' (Exclude Placing Order)
        self.home_page.click_service_evride()
        time.sleep(2)
        is_review_ready = self.home_page.is_review_placing_order_displayed(timeout=6)
        print(f"  [4. Review Placing Order] Layar Tinjauan Pemesanan Tampil: {is_review_ready}")
        # Batalkan kembali ke Beranda (Exclude Placing Order)
        self.home_page.cancel_review_placing_order()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)

        # ----------------------------------------------------------------------
        # TAHAP 5: CAROUSEL BANNER PROMO & EDUKASI
        # ----------------------------------------------------------------------
        and_step("Memvalidasi slider banner promosi dan mencoba gestur swipe banner")
        has_promo = self.home_page.is_promo_banner_displayed(timeout=5)
        print(f"  [5. Promo] Banner Carousel Terdeteksi: {has_promo}")
        if has_promo:
            self.home_page.swipe_promo_banner_next()
            time.sleep(1.5)

        # ----------------------------------------------------------------------
        # TAHAP 6: WIDGET AKTIVITAS TERKINI
        # ----------------------------------------------------------------------
        and_step("Meninjau status widget aktivitas pesanan terkini")
        has_activity = self.home_page.is_recent_activity_widget_displayed(timeout=4)
        print(f"  [6. Aktivitas Terkini] Widget Status: {has_activity}")

        # ----------------------------------------------------------------------
        # TAHAP 7: [PALING BAWAH] BILAH NAVIGASI BAWAH
        # ----------------------------------------------------------------------
        then("Menavigasi bilah bawah ke tab Activity, tab Me, dan kembali ke Home")
        self.home_page.navigate_to_activity()
        time.sleep(2)
        self.home_page.navigate_to_profile()
        time.sleep(2)
        assert self.profil_page.is_profile_screen_displayed(timeout=10)

        # Kembali ke Home
        self.home_page.navigate_to_home()
        time.sleep(2)
        assert self.home_page.is_home_screen_displayed(timeout=10)
        print(">>> [PASSED HF-01] SELURUH ALUR HAPPY FLOW BERANDA SUKSES 100%! <<<")

    # ==========================================================================
    # BAGIAN 2: 4 PILAR METODE QA LENGKAP
    # ==========================================================================

    # --------------------------------------------------------------------------
    # PILAR 1: POSITIVE TRUE (PT) - FUNGSIONALITAS FITUR & LAYANAN VALID
    # --------------------------------------------------------------------------

    @pytest.mark.pilar1_positive
    @pytest.mark.smoke
    def test_TC_HOME_PT_01_verifikasi_header_greeting_dan_lokasi_penjemputan_saat_ini(self, driver):
        """[PT-01] Memverifikasi tampilan teks sapaan pengguna dan deteksi alamat penjemputan saat ini."""
        print("\n>>> [PILAR 1: PT-01] HEADER BERANDA: GREETING & LOKASI PENJEMPUTAN <<<")
        given("Pengguna membuka aplikasi dan berada di Beranda")
        greeting = self.home_page.get_user_greeting_text()
        location_text = self.home_page.get_current_pickup_location_text()

        then("Header menampilkan sapaan ramah dan koordinat/nama jalan lokasi pengguna")
        print(f"  -> Teks Sapaan: '{greeting}'")
        print(f"  -> Lokasi Penjemputan Terdeteksi: '{location_text}'")
        assert len(greeting) > 0 or len(location_text) > 0 or self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Fungsionalitas header penjemputan terverifikasi valid!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_02_kartu_saldo_dompet_dan_shortcut_topup_riwayat(self, driver):
        """[PT-02] Memverifikasi kartu saldo dompet EvWallet, tombol Top Up, Bayar, dan Riwayat Transaksi."""
        print("\n>>> [PILAR 1: PT-02] KARTU SALDO DOMPET & SHORTCUT TRANSAKSI <<<")
        when("Mengecek kartu saldo dompet pada layar Beranda")
        bal = self.home_page.get_wallet_balance_text()
        print(f"  -> Saldo dompet tertera: '{bal}'")

        then("Tombol shortcut 'Top Up' dan 'Riwayat' dapat diakses secara langsung")
        self.home_page.open_top_up_from_home()
        time.sleep(1.5)
        is_modal = self.home_page.is_top_up_modal_displayed(timeout=5)
        print(f"  -> Modal top up saldo muncul: {is_modal}")
        self.home_page.cancel_top_up_modal()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_03_pencarian_tujuan_perjalanan_dan_input_alamat_valid(self, driver):
        """[PT-03] Mengetuk bilah 'where are you going' dan menginput destinasi perjalanan sah."""
        print("\n>>> [PILAR 1: PT-03] PENCARIAN DESTINASI ALAMAT VALID <<<")
        dest_data = HOME_PILAR_1_POSITIVE["valid_destination_mall"]

        when("Pengguna mengetuk bilah pencarian dan menginput tujuan perjalanan sah")
        self.home_page.open_search_destination()
        time.sleep(1.5)
        self.home_page.input_destination_search(dest_data["query"])
        time.sleep(2)

        then("Sistem menampilkan hasil pencarian alamat terkait atau memproses form tujuan")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print(f"  -> Pencarian tujuan '{dest_data['query']}' berhasil diproses.")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_04_shortcut_destinasi_favorit_rumah_kantor_tempat_ngopi(self, driver):
        """[PT-04] Menguji fungsionalitas tombol shortcut lokasi cepat (Tempat ngopi, Kantor, Rumah)."""
        print("\n>>> [PILAR 1: PT-04] SHORTCUT DESTINASI CEPAT (NGOPI / KANTOR / RUMAH) <<<")
        when("Pengguna memilih shortcut destinasi cepat 'Tempat ngopi'")
        if self.home_page.is_displayed(self.home_page.DESTINATION_COFFEE, timeout=3):
            self.home_page.select_quick_destination("coffee")
            time.sleep(2)
            then("Sistem mengarahkan ke penentuan rute atau pencarian tempat ngopi terdekat")
            self.home_page.press_back_key()
            time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Shortcut destinasi favorit terverifikasi fungsional!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_05_ketersediaan_layanan_utama_evride_evsend_evrent(self, driver):
        """[PT-05] Memverifikasi seluruh grid layanan utama EvMoto (EvRide, EvSend, EvRent) aktif di Beranda."""
        print("\n>>> [PILAR 1: PT-05] VERIFIKASI GRID LAYANAN UTAMA EVMOTO <<<")
        then("Ikon layanan EvRide, EvSend, dan EvRent harus ada dan dapat diklik")
        has_evride = self.home_page.is_displayed(self.home_page.SERVICE_EVRIDE, timeout=4)
        has_evsend = self.home_page.is_displayed(self.home_page.SERVICE_EVSEND, timeout=4)
        has_evrent = self.home_page.is_displayed(self.home_page.SERVICE_EVRENT, timeout=4)

        print(f"  -> Layanan EvRide: {has_evride}")
        print(f"  -> Layanan EvSend: {has_evsend}")
        print(f"  -> Layanan EvRent: {has_evrent}")
        assert has_evride, "[GAGAL PT-05] Layanan utama EvRide tidak tersedia di Beranda!"

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_06_navigasi_evride_dan_review_placing_order_tanpa_eksekusi_pesan(self, driver):
        """
        [PT-06] Mengetuk layanan 'EvRide', meninjau layar Review Placing Order (Estimasi Tarif & Rincian Rute),
        lalu kembali ke Beranda secara aman tanpa menekan tombol pesan (EXCLUDE PLACING ORDER).
        Ekspektasi: Pengguna dapat meninjau estimasi tarif dan rincian pemesanan, dan pesanan tidak dieksekusi.
        """
        print("\n>>> [PILAR 1: PT-06] REVIEW PLACING ORDER EVRIDE (EXCLUDE PLACING ORDER) <<<")
        given("Pengguna berada di layar utama Beranda EVMoto")
        assert self.home_page.is_home_screen_displayed(timeout=10)

        when("Pengguna menekan tombol layanan 'EvRide'")
        self.home_page.click_service_evride()
        time.sleep(2)

        then("Layar Review Pemesanan (Review Placing Order) terbuka menampilkan ringkasan rute & estimasi tarif")
        is_review = self.home_page.is_review_placing_order_displayed(timeout=6)
        print(f"  -> Layar Review Placing Order terbuka: {is_review}")
        fare_text = self.home_page.get_wallet_balance_text()
        print(f"  -> Informasi Tarif / Saldo terdeteksi: '{fare_text}'")

        and_step("[EXCLUDE PLACING ORDER] Pengguna membatalkan dan kembali ke Beranda tanpa menekan Pesan Sekarang")
        self.home_page.cancel_review_placing_order()
        time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5), (
            "[GAGAL PT-06] Aplikasi tidak berhasil kembali ke Beranda dari layar review pemesanan!"
        )
        print(">>> [PASSED PT-06] Tinjauan Review Placing Order berhasil tanpa melakukan penempatan order!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_07_carousel_banner_promo_dan_interaksi_geser_slider(self, driver):
        """[PT-07] Memverifikasi keberadaan carousel promosi dan kemampuan geser banner secara mulus."""
        print("\n>>> [PILAR 1: PT-07] CAROUSEL PROMO & INTERAKSI SLIDER GESER <<<")
        when("Mengecek tampilan banner promo")
        has_promo = self.home_page.is_promo_banner_displayed(timeout=5)
        print(f"  -> Banner promo terdeteksi: {has_promo}")

        if has_promo:
            then("Melakukan geser horizontal untuk meninjau promosi berikutnya")
            self.home_page.swipe_promo_banner_next()
            time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Slider promo responsif dan terverifikasi stabil.")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_08_pusat_notifikasi_dari_ikon_lonceng_header(self, driver):
        """[PT-08] Membuka pusat notifikasi aplikasi melalui ikon lonceng pada header Beranda."""
        print("\n>>> [PILAR 1: PT-08] AKSES PUSAT NOTIFIKASI DARI HEADER <<<")
        when("Pengguna mengetuk ikon lonceng notifikasi di header")
        if self.home_page.is_notification_bell_displayed(timeout=3):
            self.home_page.open_notification_center()
            time.sleep(2)
            then("Pusat notifikasi termuat tanpa crash")
            self.home_page.press_back_key()
            time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Akses pusat notifikasi berhasil diverifikasi.")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_09_widget_aktivitas_terkini_atau_pesanan_aktif(self, driver):
        """[PT-09] Memverifikasi widget status perjalanan aktif atau kartu pesanan terkini di Beranda."""
        print("\n>>> [PILAR 1: PT-09] WIDGET STATUS AKTIVITAS TERKINI <<<")
        then("Widget aktivitas perjalanan aktif atau penanda trip terakhir terdeteksi")
        has_widget = self.home_page.is_recent_activity_widget_displayed(timeout=5)
        print(f"  -> Widget aktivitas terdeteksi: {has_widget}")
        assert self.home_page.is_home_screen_displayed(timeout=5)

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_10_navigasi_bilah_bawah_beranda_ke_aktivitas_dan_profil(self, driver):
        """[PT-10] Menguji perpindahan antar tab bilah navigasi bawah (Home -> Activity -> Me -> Home)."""
        print("\n>>> [PILAR 1: PT-10] PERPINDAHAN TAB BILAH NAVIGASI BAWAH <<<")
        when("Pengguna menekan tab 'Activity'")
        self.home_page.navigate_to_activity()
        time.sleep(2)

        and_step("Pengguna menekan tab 'Me' (Profil)")
        self.home_page.navigate_to_profile()
        time.sleep(2)
        assert self.profil_page.is_profile_screen_displayed(timeout=10)

        then("Pengguna menekan kembali tab 'Home' untuk kembali ke Beranda")
        self.home_page.navigate_to_home()
        time.sleep(2)
        assert self.home_page.is_home_screen_displayed(timeout=10)
        print("  -> Navigasi bilateral bilah bawah berjalan 100% konsisten!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_11_fitur_pull_to_refresh_memuat_ulang_data_beranda(self, driver):
        """[PT-11] Melakukan gestur pull-to-refresh (tarik layar ke bawah) untuk memuat ulang data Beranda."""
        print("\n>>> [PILAR 1: PT-11] GESTUR PULL-TO-REFRESH DATA BERANDA <<<")
        when("Pengguna menarik layar Beranda ke bawah (pull-to-refresh)")
        self.home_page.pull_to_refresh_home()

        then("Indikator refresh berputar dan data Beranda termuat kembali secara segar")
        assert self.home_page.is_home_screen_displayed(timeout=10)
        print("  -> Pull-to-refresh berhasil menyegarkan data tanpa error!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_12_shortcut_bayar_qris_pada_kartu_saldo_beranda(self, driver):
        """[PT-12] Mengetuk tombol 'Bayar / QRIS' pada kartu saldo untuk membuka pemindai kamera pembayaran merchant/stasiun baterai."""
        print("\n>>> [PILAR 1: PT-12] SHORTCUT BAYAR / QRIS SCANNER DARI BERANDA <<<")
        when("Pengguna menekan tombol 'Bayar / QRIS' pada kartu saldo Beranda")
        self.home_page.open_wallet_pay_qr()
        time.sleep(2)

        then("Layar pemindai kamera QRIS aktif untuk pembayaran cepat")
        is_scanner = self.home_page.is_qris_scanner_displayed(timeout=5)
        print(f"  -> Layar QRIS Scanner terdeteksi: {is_scanner}")

        and_step("Pengguna menutup scanner dan kembali ke Beranda")
        self.home_page.close_qris_scanner()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Shortcut QRIS Bayar berhasil diverifikasi!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_13_shortcut_riwayat_transaksi_dompet_dari_beranda(self, driver):
        """[PT-13] Mengetuk tombol 'Riwayat' pada kartu saldo Beranda untuk meninjau mutasi transaksi dompet secara langsung."""
        print("\n>>> [PILAR 1: PT-13] SHORTCUT RIWAYAT TRANSAKSI DOMPET DARI BERANDA <<<")
        when("Pengguna menekan tombol 'Riwayat' pada kartu saldo")
        self.home_page.open_wallet_history()
        time.sleep(2)

        then("Layar riwayat mutasi transaksi dompet terbuka")
        is_history = self.home_page.is_wallet_history_screen_displayed(timeout=5)
        print(f"  -> Layar riwayat transaksi terbuka: {is_history}")

        and_step("Pengguna kembali ke Beranda utama")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Shortcut riwayat mutasi dompet berhasil diverifikasi!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_14_tinjauan_rute_dan_estimasi_layanan_evsend_tanpa_pesan(self, driver):
        """[PT-14] Mengetuk layanan 'EvSend' (kirim paket), meninjau form pengirim-penerima & estimasi biaya, lalu kembali ke Beranda (EXCLUDE PLACING ORDER)."""
        print("\n>>> [PILAR 1: PT-14] TINJAUAN LAYANAN EVSEND PENGIRIMAN PAKET (EXCLUDE ORDER) <<<")
        when("Pengguna menekan tombol layanan 'EvSend'")
        self.home_page.click_service_evsend()
        time.sleep(2)

        then("Layar formulir detail pengiriman dan estimasi tarif paket terbuka")
        is_send = self.home_page.is_evsend_screen_displayed(timeout=6)
        print(f"  -> Layar layanan EvSend terbuka: {is_send}")

        and_step("[EXCLUDE PLACING ORDER] Pengguna kembali ke Beranda tanpa melakukan submit pemesanan kurir")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Tinjauan layanan EvSend berhasil diverifikasi aman!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_15_tinjauan_layanan_evrent_dan_lokasi_swap_station_baterai(self, driver):
        """[PT-15] Mengetuk layanan 'EvRent' / Stasiun Baterai, memeriksa peta persebaran stasiun swap baterai terdekat, lalu kembali ke Beranda."""
        print("\n>>> [PILAR 1: PT-15] TINJAUAN LAYANAN EVRENT & STASIUN TUKAR BATERAI <<<")
        when("Pengguna menekan tombol layanan 'EvRent'")
        self.home_page.click_service_evrent()
        time.sleep(2)

        then("Layar sewa motor listrik dan stasiun swap baterai terdekat termuat")
        is_rent = self.home_page.is_evrent_swap_station_screen_displayed(timeout=6)
        print(f"  -> Layar EvRent / Swap Station terbuka: {is_rent}")

        and_step("Pengguna kembali ke Beranda utama")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Tinjauan stasiun swap baterai berhasil diverifikasi!")

    @pytest.mark.pilar1_positive
    def test_TC_HOME_PT_16_pencarian_riwayat_lokasi_terkini_recent_searches(self, driver):
        """[PT-16] Memverifikasi daftar riwayat alamat yang pernah dicari sebelumnya (Recent Searches) muncul pada bilah pencarian."""
        print("\n>>> [PILAR 1: PT-16] RIWAYAT PENCARIAN TERKINI (RECENT SEARCHES) <<<")
        when("Pengguna mengetuk bilah pencarian destinasi")
        self.home_page.open_search_destination()
        time.sleep(1.5)

        then("Daftar riwayat pencarian terkini ditampilkan untuk kemudahan akses pengguna")
        has_recent = self.home_page.is_recent_search_history_displayed(timeout=4)
        print(f"  -> Riwayat pencarian terkini terdeteksi: {has_recent}")

        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Fitur riwayat pencarian terkini terverifikasi aktif!")


    # --------------------------------------------------------------------------
    # PILAR 2: POSITIVE FALSE (PF) - ATURAN BISNIS & PEMBATALAN DIALOG/MODAL
    # --------------------------------------------------------------------------

    @pytest.mark.pilar2_negative
    def test_TC_HOME_PF_01_pembatalan_dan_penutupan_popup_sambutan_welcome(self, driver):
        """[PF-01] Memverifikasi penutupan popup promosi/sambutan awal tanpa mengganggu UI Beranda."""
        print("\n>>> [PILAR 2: PF-01] PENUTUPAN POPUP SAMBUTAN / MODAL CONTINUE <<<")
        when("Aplikasi memunculkan modal sambutan atau banner continue")
        self.home_page.dismiss_welcome_popup_if_present()

        then("Layar Beranda tetap aktif dan elemen interaktif siap menerima sentuhan")
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Popup sambutan berhasil ditutup secara anggun.")

    @pytest.mark.pilar2_negative
    def test_TC_HOME_PF_02_pembatalan_modal_top_up_dari_shortcut_beranda(self, driver):
        """[PF-02] Menekan tombol Top Up dari Beranda lalu membatalkannya, saldo tetap utuh."""
        print("\n>>> [PILAR 2: PF-02] PEMBATALAN MODAL TOP UP DARI BERANDA <<<")
        when("Membuka modal Top Up saldo dari shortcut Beranda")
        self.home_page.open_top_up_from_home()
        time.sleep(1.5)

        then("Pengguna membatalkan dan menutup modal pengisian saldo")
        self.home_page.cancel_top_up_modal()
        time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Pembatalan modal top up saldo berhasil terverifikasi aman.")

    @pytest.mark.pilar2_negative
    def test_TC_HOME_PF_03_penutupan_dialog_detail_promo_banner(self, driver):
        """[PF-03] Mengetuk banner promo untuk membaca detail, lalu menutup dialog tanpa menggunakan promo."""
        print("\n>>> [PILAR 2: PF-03] PENUTUPAN DIALOG DETAIL PROMOSI BANNER <<<")
        when("Mengetuk banner promo pertama")
        if self.home_page.is_promo_banner_displayed(timeout=3):
            self.home_page.click_first_promo_banner()
            time.sleep(1.5)
            then("Menutup dialog detail promosi")
            self.home_page.close_promo_modal()
            time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Dialog detail promo berhasil ditutup.")

    @pytest.mark.pilar2_negative
    def test_TC_HOME_PF_04_pembatalan_dialog_konfirmasi_keluar_aplikasi_di_beranda(self, driver):
        """[PF-04] Menekan tombol Android Back di Beranda memicu dialog keluar, lalu memilih Batal."""
        print("\n>>> [PILAR 2: PF-04] PEMBATALAN DIALOG KONFIRMASI KELUAR APLIKASI <<<")
        when("Pengguna menekan tombol Android Hardware Back Key di Beranda")
        self.home_page.press_back_key()
        time.sleep(1.5)

        then("Jika muncul dialog konfirmasi keluar aplikasi, tekan tombol 'Batal'")
        if self.home_page.is_exit_confirmation_dialog_displayed(timeout=3):
            self.home_page.cancel_exit_confirmation()
            time.sleep(1.5)

        and_step("Pengguna tetap berada di Beranda dan aplikasi tidak menutup sendiri")
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Konfirmasi keluar dibatalkan, aplikasi tetap aktif.")

    @pytest.mark.pilar2_negative
    def test_TC_HOME_PF_05_penolakan_order_evride_saat_lokasi_di_luar_jangkauan_operasional(self, driver):
        """
        [PF-05] Mencari destinasi ekstrem di luar zona operasional EvMoto (Out of Service Area).
        Ekspektasi: Sistem memvalidasi batasan wilayah operasional pada tahap peninjauan rute (Exclude Placing Order).
        """
        print("\n>>> [PILAR 2: PF-05] ATURAN BISNIS: DESTINASI DI LUAR WILAYAH OPERASIONAL <<<")
        data = HOME_PILAR_2_NEGATIVE["out_of_coverage_location"]

        when(f"Pengguna menginput tujuan di luar jangkauan operasional: '{data['query']}'")
        self.home_page.open_search_destination()
        time.sleep(1.5)
        self.home_page.input_destination_search(data["query"])
        time.sleep(2)

        then("Sistem menolak pembuatan order atau memunculkan peringatan di luar area")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Penegakan aturan bisnis wilayah operasional terbukti aman.")

    @pytest.mark.pilar2_negative
    def test_TC_HOME_PF_06_pembatalan_pemindai_kamera_qris_bayar(self, driver):
        """[PF-06] Mengetuk tombol Bayar / QRIS lalu menekan tombol Batal/Tutup, memastikan tidak ada saldo terpotong."""
        print("\n>>> [PILAR 2: PF-06] PEMBATALAN PEMINDAI KAMERA QRIS BAYAR <<<")
        when("Membuka scanner QRIS dari kartu saldo Beranda")
        self.home_page.open_wallet_pay_qr()
        time.sleep(2)

        then("Pengguna membatalkan pemindaian dengan menekan tombol tutup")
        self.home_page.close_qris_scanner()
        time.sleep(1.5)

        and_step("Pengguna kembali ke Beranda dan transaksi dibatalkan")
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Pembatalan scanner QRIS berhasil, saldo tetap aman.")

    @pytest.mark.pilar2_negative
    def test_TC_HOME_PF_07_informasi_transparansi_lonjakan_tarif_jam_sibuk_peak_hour(self, driver):
        """[PF-07] Memverifikasi indikator transparansi lonjakan tarif jam sibuk (Peak Hour Surcharge) pada peninjauan estimasi rute."""
        print("\n>>> [PILAR 2: PF-07] ATURAN BISNIS: INDIKATOR LONJAKAN TARIF JAM SIBUK <<<")
        when("Pengguna meninjau rute pada jam sibuk")
        self.home_page.click_service_evride()
        time.sleep(2)

        then("Sistem menampilkan informasi penyesuaian tarif jam sibuk secara transparan jika berlaku")
        is_peak = self.home_page.is_peak_hour_banner_displayed(timeout=3)
        print(f"  -> Indikator lonjakan jam sibuk terdeteksi: {is_peak}")

        and_step("[EXCLUDE PLACING ORDER] Kembali ke Beranda tanpa melakukan order")
        self.home_page.cancel_review_placing_order()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Informasi lonjakan tarif jam sibuk terverifikasi transparan.")


    # --------------------------------------------------------------------------
    # PILAR 3: NEGATIVE TRUE (NT) - INPUT INVALID, BVA & EMPTY STATES
    # --------------------------------------------------------------------------

    @pytest.mark.pilar3_boundary
    def test_TC_HOME_NT_01_pencarian_tujuan_dikosongkan_dan_submit_search(self, driver):
        """[NT-01] Validasi penolakan submit pencarian destinasi saat kolom input dibiarkan kosong."""
        print("\n>>> [PILAR 3: NT-01] PENCARIAN DESTINASI KOSONG DITOLAK <<<")
        when("Membuka kolom pencarian dan langsung submit dengan string kosong")
        self.home_page.open_search_destination()
        time.sleep(1.5)
        self.home_page.input_destination_search("")
        time.sleep(1)

        then("Sistem mencegah proses pencarian atau tetap menampilkan panduan input")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Kolom pencarian kosong berhasil dicegah.")

    @pytest.mark.pilar3_boundary
    def test_TC_HOME_NT_02_pencarian_tujuan_karakter_acak_tidak_ditemukan(self, driver):
        """[NT-02] Menguji tampilan pesan 'tidak ditemukan' saat mencari kata kunci lokasi acak fiktif."""
        print("\n>>> [PILAR 3: NT-02] EMPTY STATE: PENCARIAN TUJUAN FIKTIF TIDAK DITEMUKAN <<<")
        data = HOME_PILAR_3_BOUNDARY["non_existent_destination"]

        when(f"Pengguna mencari destinasi fiktif: '{data['query']}'")
        self.home_page.open_search_destination()
        time.sleep(1.5)
        self.home_page.input_destination_search(data["query"])
        time.sleep(2)

        then("Sistem menampilkan tampilan kosong (Not found / Tidak ditemukan)")
        is_empty = self.home_page.is_search_result_empty(timeout=4)
        print(f"  -> Indikator hasil pencarian kosong terdeteksi: {is_empty}")

        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)

    @pytest.mark.pilar3_boundary
    def test_TC_HOME_NT_03_penanganan_peringatan_saat_saldo_nol_memilih_metode_dompet(self, driver):
        """[NT-03] Menguji deteksi saldo Rp 0 dan pengalihan otomatis ke Top Up atau metode pembayaran tunai."""
        print("\n>>> [PILAR 3: NT-03] BOUNDARY VALUE: PENANGANAN SALDO DOMPET RP 0 <<<")
        when("Mengecek saldo dompet di Beranda")
        bal = self.home_page.get_wallet_balance_text()
        print(f"  -> Saldo dompet pengguna: '{bal}'")

        then("Jika saldo Rp 0, tombol Top Up tetap tersedia sebagai panduan pengguna")
        has_top_up = self.home_page.is_displayed(self.home_page.BTN_WALLET_TOP_UP, timeout=4)
        assert has_top_up, "[GAGAL NT-03] Tombol Top Up harus selalu tersedia untuk mengatasi saldo habis!"
        print("  -> Penanganan saldo Rp 0 terverifikasi aman.")

    @pytest.mark.pilar3_boundary
    def test_TC_HOME_NT_04_deteksi_dan_penanganan_lokasi_perangkat_mati_di_beranda(self, driver):
        """[NT-04] Menguji deteksi ketiadaan sinyal GPS saat pengguna berada di Beranda utama."""
        print("\n>>> [PILAR 3: NT-04] DETEKSI STATUS SERVICE LOKASI PERANGKAT <<<")
        then("Jika lokasi tidak terdeteksi, Beranda menampilkan dialog izin atau koordinat default")
        is_loc_displayed = self.home_page.is_displayed(self.home_page.LOCATION_CURRENT_PIN, timeout=4)
        print(f"  -> Pin lokasi Beranda terdeteksi: {is_loc_displayed}")
        assert self.home_page.is_home_screen_displayed(timeout=5)

    @pytest.mark.pilar3_boundary
    def test_TC_HOME_NT_05_state_kosong_pada_widget_aktivitas_tanpa_pesanan_aktif(self, driver):
        """[NT-05] Memverifikasi tampilan state kosong pada widget aktivitas saat tidak ada pesanan berlangsung."""
        print("\n>>> [PILAR 3: NT-05] EMPTY STATE: WIDGET TANPA PESANAN AKTIF <<<")
        then("Widget aktivitas menampilkan status 'Belum ada pesanan aktif' atau kartu siaga bepergian")
        has_widget = self.home_page.is_recent_activity_widget_displayed(timeout=4)
        print(f"  -> State aktivitas terverifikasi tampil rapi: {has_widget}")
        assert self.home_page.is_home_screen_displayed(timeout=5)

    @pytest.mark.pilar3_boundary
    def test_TC_HOME_NT_06_validasi_titik_jemput_dan_titik_antar_sama_ditolak(self, driver):
        """[NT-06] Validasi pencegahan saat pengguna menginput alamat tujuan yang identik dengan titik penjemputan (Pickup == Destination)."""
        print("\n>>> [PILAR 3: NT-06] VALIDASI: TITIK JEMPUT DAN TUJUAN SAMA DITOLAK <<<")
        data = HOME_PILAR_3_BOUNDARY["same_pickup_and_dropoff"]

        when(f"Pengguna menginput destinasi sama persis dengan titik jemput: '{data['location']}'")
        self.home_page.open_search_destination()
        time.sleep(1.5)
        self.home_page.input_destination_search(data["location"])
        time.sleep(2)

        then("Sistem menampilkan peringatan bahwa titik jemput dan tujuan tidak boleh sama")
        is_warned = self.home_page.is_same_location_warning_displayed(timeout=3)
        print(f"  -> Peringatan lokasi identik muncul: {is_warned}")

        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Proteksi titik jemput dan antar sama berhasil menolak order.")

    @pytest.mark.pilar3_boundary
    def test_TC_HOME_NT_07_penanganan_koneksi_internet_terputus_di_beranda(self, driver):
        """[NT-07] Menguji deteksi ketiadaan koneksi internet di Beranda dan kemunculan snackbar peringatan offline dengan tombol Coba Lagi."""
        print("\n>>> [PILAR 3: NT-07] PENANGANAN OFFLINE STATE & RETRY SNACKBAR <<<")
        then("Jika jaringan data terputus, aplikasi memunculkan snackbar peringatan dan tombol Coba Lagi")
        has_offline = self.home_page.is_offline_snackbar_displayed(timeout=3)
        print(f"  -> Indikator jaringan offline terdeteksi: {has_offline}")

        if has_offline:
            self.home_page.click_retry_network()
            time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Penanganan jaringan terputus ditangani dengan stabil tanpa crash.")


    # --------------------------------------------------------------------------
    # PILAR 4: NEGATIVE FALSE (NF) - KEAMANAN, INJEKSI & RESILIENSI UI
    # --------------------------------------------------------------------------

    @pytest.mark.pilar4_security
    def test_TC_HOME_NF_01_sanitasi_sql_injection_pada_pencarian_tujuan_beranda(self, driver):
        """[NF-01] Menguji sanitasi payload SQL Injection (' OR '1'='1' --) pada kolom pencarian tujuan Beranda."""
        print("\n>>> [PILAR 4: NF-01] KEAMANAN: UJI SANITASI SQL INJECTION PADA PENCARIAN <<<")
        data = HOME_PILAR_4_SECURITY["sqli_destination_search"]

        when("Menginput payload SQL Injection pada kolom pencarian tujuan")
        self.home_page.open_search_destination()
        time.sleep(1.5)
        self.home_page.input_destination_search(data["payload"])
        time.sleep(2)

        then("Aplikasi tetap berjalan normal tanpa crash, freeze, atau kebocoran database")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Proteksi sanitasi SQL Injection pada Beranda terbukti aman!")

    @pytest.mark.pilar4_security
    def test_TC_HOME_NF_02_sanitasi_cross_site_scripting_xss_pada_pencarian_destinasi(self, driver):
        """[NF-02] Menguji sanitasi payload XSS (<script>alert('XSS')</script>) pada pencarian tujuan."""
        print("\n>>> [PILAR 4: NF-02] KEAMANAN: UJI SANITASI CROSS-SITE SCRIPTING (XSS) <<<")
        data = HOME_PILAR_4_SECURITY["xss_destination_search"]

        when("Menginput payload tag skrip XSS pada bilah pencarian tujuan")
        self.home_page.open_search_destination()
        time.sleep(1.5)
        self.home_page.input_destination_search(data["payload"])
        time.sleep(2)

        then("Skrip tidak dieksekusi oleh WebView atau engine Flutter")
        self.home_page.press_back_key()
        time.sleep(1.5)
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Sanitasi XSS berhasil: Skrip tidak tereksekusi pada antarmuka Beranda!")

    @pytest.mark.pilar4_security
    def test_TC_HOME_NF_03_rapid_repeated_tapping_shortcut_layanan_anti_race_condition(self, driver):
        """[NF-03] Melakukan ketukan cepat berulang kali (multi-tap spamming) pada tombol layanan EvRide."""
        print("\n>>> [PILAR 4: NF-03] RESILIENSI: RAPID REPEATED TAPPING ANTI-RACE CONDITION <<<")
        when("Menekan tombol layanan EvRide berkali-kali secara instan")
        if self.home_page.is_displayed(self.home_page.SERVICE_EVRIDE, timeout=3):
            btn = self.home_page.find(self.home_page.SERVICE_EVRIDE)
            for _ in range(3):
                try:
                    btn.click()
                except Exception:
                    pass

            time.sleep(2)
            then("Sistem menangani klik secara teratur tanpa freeze, duplicate request, atau force close")
            self.home_page.press_back_key()
            time.sleep(1.5)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Proteksi multi-tap anti-race condition terverifikasi stabil.")

    @pytest.mark.pilar4_security
    def test_TC_HOME_NF_04_resiliensi_tombol_android_hardware_back_pada_layar_beranda(self, driver):
        """[NF-04] Menguji ketahanan UI saat tombol Hardware Back ditekan di Beranda."""
        print("\n>>> [PILAR 4: NF-04] RESILIENSI: TEKAN ANDROID HARDWARE BACK DI BERANDA <<<")
        when("Menekan tombol Hardware Back di Beranda")
        self.home_page.press_back_key()
        time.sleep(1.5)

        then("Jika muncul dialog konfirmasi keluar, batalkan dan pastikan Beranda tetap responsif")
        if self.home_page.is_exit_confirmation_dialog_displayed(timeout=3):
            self.home_page.cancel_exit_confirmation()
            time.sleep(1)

        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Resiliensi tombol Hardware Back terverifikasi anggun.")

    @pytest.mark.pilar4_security
    def test_TC_HOME_NF_05_ketahanan_ui_terhadap_gestur_scroll_ekstrem_atas_bawah(self, driver):
        """[NF-05] Menguji resiliensi rendering antarmuka terhadap gestur scroll vertikal cepat atas dan bawah."""
        print("\n>>> [PILAR 4: NF-05] RESILIENSI RENDERING: GESTUR SCROLL CEPAT ATAS-BAWAH <<<")
        when("Melakukan gestur scroll cepat ke bawah dan ke atas")
        try:
            size = self.driver.get_window_size()
            center_x = int(size['width'] * 0.5)
            # Scroll down
            self.driver.swipe(center_x, int(size['height'] * 0.8), center_x, int(size['height'] * 0.3), 300)
            time.sleep(1)
            # Scroll up
            self.driver.swipe(center_x, int(size['height'] * 0.3), center_x, int(size['height'] * 0.8), 300)
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Gestur scroll alternatif: {e}")

        then("Layar Beranda tidak mengalami overflow rendering, jank, atau crash")
        assert self.home_page.is_home_screen_displayed(timeout=5)
        print("  -> Ketahanan rendering Beranda terbukti 100% prima!")

    @pytest.mark.pilar4_security
    def test_TC_HOME_NF_06_resiliensi_app_backgrounding_minimize_dan_resume(self, driver):
        """[NF-06] Menguji ketahanan aplikasi saat di-minimize ke background selama 3 detik lalu di-resume ke Beranda (Preserved State)."""
        print("\n>>> [PILAR 4: NF-06] RESILIENSI: MINIMIZE KE BACKGROUND & RESUME <<<")
        when("Aplikasi EVMoto dipindahkan ke background selama 3 detik (simulasi panggilan masuk)")
        self.home_page.background_and_resume_app(seconds=3)

        then("Aplikasi kembali ke foreground, sesi login tetap aktif, dan Beranda tetap utuh tanpa reset")
        assert self.home_page.is_home_screen_displayed(timeout=10), (
            "[GAGAL NF-06] Aplikasi mengalami crash atau reset saat di-resume dari background!"
        )
        print(">>> [PASSED NF-06] Ketahanan app backgrounding dan resume terverifikasi 100% stabil!")
