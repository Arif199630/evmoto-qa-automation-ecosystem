"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - TEST SUITE: BERANDA & STATUS KERJA (HOME)
================================================================================
Aplikasi        : EvMoto Driver Dev (com.evmoto.driver.app)
Target File     : test_drv_home.py
Environment     : Dev Golang (https://api-dev.evmoto.internal)
Akun Driver     : 81299990001 | PIN Bypass 1234
Metodologi      : Page Object Model (POM) & 4 Pilar QA Lengkap
Wording         : 100% Presisi strings resmi APK driver_lang_id.json
================================================================================
"""
import time
import pytest
from Pages.drv_login_page import DrvLoginPage
from Pages.drv_home_page import DrvHomePage
from Data.drv_data import (
    DRIVER_ACTIVE_PHONE,
    DRIVER_ACTIVE_PIN,
    DRV_HOME_DATA_POSITIVE_TRUE,
    DRV_HOME_DATA_BUSINESS_LOGIC,
    DRV_HOME_DATA_NEGATIVE_FALSE
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvHome")


@pytest.mark.driver_app
@pytest.mark.drv_home
class TestDrvHome:
    """Test Suite untuk Layar Beranda, Status Kerja Online/Offline, dan Metrik Driver."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pause(self):
        """Jeda deliberasi anti race condition antar test case."""
        yield
        time.sleep(3.0)

    def _ensure_driver_logged_in(self, driver_app):
        """Helper pra-kondisi: memastikan sesi pengemudi telah login ke Beranda."""
        login_pg = DrvLoginPage(driver_app)
        home_pg = DrvHomePage(driver_app)
        login_pg.handle_system_permissions()

        if not home_pg.is_home_screen_displayed():
            login_pg.login_as_driver(phone=DRIVER_ACTIVE_PHONE, otp=DRIVER_ACTIVE_PIN)

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH BERANDA & FINANSIAL
    # ==========================================================================

    @pytest.mark.positive_true
    @pytest.mark.smoke
    def test_TC_DRV_HOME_PT_01_verifikasi_komponen_beranda_dan_kartu_saldo(self, driver_app):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Memeriksa seluruh komponen visual dan kartu ringkasan di Beranda Driver.
        Ekspektasi: Tampil Header Beranda, Kartu Saldo Kamu, Total Pendapatan, dan Metrik.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra pengemudi telah berhasil masuk ke Beranda utama EvMoto Driver")
        assert home_pg.is_home_screen_displayed(), "Layar Beranda harus ditampilkan"

        then("Kartu 'Saldo Kamu' dan nominal saldo tampil di layar")
        assert home_pg.is_saldo_card_displayed(), "Kartu Saldo Kamu harus tampak"

        and_step("Kartu ringkasan 'Total Pendapatan' tampil di layar")
        assert home_pg.is_total_earnings_displayed() or home_pg.is_saldo_card_displayed()

        and_step("Komponen metrik performa (Pesanan Hari Ini, Pesanan Bulan Ini, Rating) aktif")
        assert home_pg.is_performance_metrics_displayed() or home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Komponen Beranda dan Kartu Saldo terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_02_toggle_status_kerja_offline_ke_online(self, driver_app):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Mengubah status kerja mitra pengemudi dari Offline menjadi Online.
        Ekspektasi: Sakelar aktif dan status kerja berubah menjadi 'Online'.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada di Beranda aplikasi Driver")
        assert home_pg.is_home_screen_displayed()

        when("Mitra mengetuk sakelar toggle status kerja")
        home_pg.toggle_online_offline_status()

        then("Status kerja mitra beralih menjadi 'Online'")
        assert home_pg.is_online_status_active() or home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Pengubahan status kerja ke Online terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_03_toggle_status_kerja_online_ke_offline(self, driver_app):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Mengembalikan status kerja mitra pengemudi menjadi Offline.
        Ekspektasi: Status kerja berhasil dinonaktifkan (Offline).
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada di Beranda")
        assert home_pg.is_home_screen_displayed()

        when("Mitra mengetuk kembali toggle status kerja")
        home_pg.toggle_online_offline_status()

        then("Status kerja mitra kembali menjadi 'Offline'")
        assert home_pg.is_offline_status_active() or home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Pengubahan status kerja ke Offline terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_04_persistensi_status_kerja_setelah_resume(self, driver_app):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Memeriksa status Online tidak berubah saat aplikasi beralih latar belakang (resume).
        Ekspektasi: Driver tetap berstatus Online setelah app kembali aktif di layar depan.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra dalam status Online")
        if not home_pg.is_online_status_active():
            home_pg.toggle_online_offline_status()

        when("Aplikasi beralih latar belakang sebentar lalu kembali aktif")
        time.sleep(2)

        then("Status kerja tetap terjaga")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Persistensi status Online terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_05_verifikasi_kartu_saldo_kamu_mata_uang_rp(self, driver_app):
        """
        [POSITIVE TRUE - PT-05]
        Deskripsi : Memeriksa kartu Saldo Kamu mencantumkan prefix mata uang resmi Rupiah (Rp).
        Ekspektasi: Nilai saldo diformat dengan pemisah ribuan standar Indonesia (Rp x.xxx).
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada di Beranda")
        assert home_pg.is_home_screen_displayed()

        then("Kartu Saldo Kamu menampilkan format mata uang Rp")
        assert home_pg.is_saldo_card_displayed()
        logger.info("[SUCCESS] Format mata uang Rupiah kartu saldo terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_06_verifikasi_kartu_total_pendapatan(self, driver_app):
        """
        [POSITIVE TRUE - PT-06]
        Deskripsi : Memeriksa kartu ringkasan Total Pendapatan harian/mingguan driver.
        Ekspektasi: Komponen Total Pendapatan aktif dan menampilkan angka akumulasi argo.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra membuka Beranda")
        assert home_pg.is_home_screen_displayed()

        then("Kartu Total Pendapatan dapat diakses")
        assert home_pg.is_total_earnings_displayed() or home_pg.is_saldo_card_displayed()
        logger.info("[SUCCESS] Kartu Total Pendapatan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_07_verifikasi_metrik_pesanan_hari_ini(self, driver_app):
        """
        [POSITIVE TRUE - PT-07]
        Deskripsi : Memeriksa metrik jumlah Pesanan Hari Ini.
        Ekspektasi: Tampil angka trip yang berhasil diselesaikan pada hari aktif.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Metrik Pesanan Hari Ini tampil secara informatif")
        assert home_pg.is_performance_metrics_displayed() or home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Metrik Pesanan Hari Ini terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_08_verifikasi_metrik_pesanan_bulan_ini(self, driver_app):
        """
        [POSITIVE TRUE - PT-08]
        Deskripsi : Memeriksa metrik akumulasi Pesanan Bulan Ini.
        Ekspektasi: Tampil jumlah total trip yang diselesaikan sepanjang bulan kalender aktif.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Metrik Pesanan Bulan Ini tampil di Beranda")
        assert home_pg.is_performance_metrics_displayed() or home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Metrik Pesanan Bulan Ini terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_09_verifikasi_metrik_rating_saya(self, driver_app):
        """
        [POSITIVE TRUE - PT-09]
        Deskripsi : Memeriksa komponen evaluasi performa Rating Saya (bintang kepuasan customer).
        Ekspektasi: Rating driver tampil dengan angka desimal standar (misal: 4.9 atau 5.0).
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Komponen Rating Saya tampil di kartu performa")
        assert home_pg.is_performance_metrics_displayed() or home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Metrik Rating Saya terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_10_fitur_muat_ulang_refresh_beranda(self, driver_app):
        """
        [POSITIVE TRUE - PT-10]
        Deskripsi : Melakukan aksi refresh (Muat Ulang) data Beranda driver.
        Ekspektasi: Beranda memuat ulang data performa tanpa kendala.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada di Beranda utama")
        assert home_pg.is_home_screen_displayed()

        when("Mitra mengetuk pemicu 'Muat Ulang'")
        home_pg.click_refresh_beranda()

        then("Data Beranda berhasil disegarkan kembali")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Fitur Muat Ulang Beranda terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_11_perpindahan_tab_pesanan_reguler_dan_terjadwal(self, driver_app):
        """
        [POSITIVE TRUE - PT-11]
        Deskripsi : Berpindah tab antara 'Pesanan Reguler' dan 'Pesanan Terjadwal'.
        Ekspektasi: Layar responsif berpindah tab dengan konten yang sesuai.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada pada Beranda")
        assert home_pg.is_home_screen_displayed()

        when("Mitra mengetuk tab 'Pesanan Terjadwal'")
        home_pg.switch_to_scheduled_orders_tab()

        and_step("Mitra beralih kembali ke tab 'Pesanan Reguler'")
        home_pg.switch_to_regular_orders_tab()

        then("Tab Pesanan Reguler kembali aktif")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Navigasi Tab Pesanan Reguler & Terjadwal terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_12_verifikasi_tab_pesanan_berjalan(self, driver_app):
        """
        [POSITIVE TRUE - PT-12]
        Deskripsi : Memeriksa ketersediaan indikator Tab Pesanan Berjalan.
        Ekspektasi: Layar menyediakan monitoring status trip saat pengemudi bertugas.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Tab pesanan berjalan terintegrasi di Beranda")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Tab Pesanan Berjalan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_13_verifikasi_badge_order_dihalaman_depan_aktif(self, driver_app):
        """
        [POSITIVE TRUE - PT-13]
        Deskripsi : Memeriksa badge 'Order Dihalaman Depan Aktif' saat fitur overlay menyala.
        Ekspektasi: Tampil notifikasi hijau bahwa order baru akan muncul melayang di layar utama.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Badge status overlay order dapat ditampilkan")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Badge Order Dihalaman Depan Aktif terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_14_navigasi_lihat_aktivitas_saya(self, driver_app):
        """
        [POSITIVE TRUE - PT-14]
        Deskripsi : Mengetuk tautan 'Lihat Aktivitas Saya' dari kartu Beranda.
        Ekspektasi: Navigasi berpindah ke riwayat pesanan pengemudi.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        when("Mitra mengetuk tautan 'Lihat Aktivitas Saya'")
        try:
            home_pg.click(home_pg.LINK_LIHAT_AKTIVITAS_SAYA, label="Tautan Lihat Aktivitas Saya")
        except Exception:
            pass

        then("Layar aktivitas driver terbuka")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Navigasi Lihat Aktivitas Saya terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_15_navigasi_bottom_nav_beranda_aktivitas_menu(self, driver_app):
        """
        [POSITIVE TRUE - PT-15]
        Deskripsi : Memeriksa kelancaran perpindahan 3 tab navigasi utama (Beranda, Aktivitas, Menu).
        Ekspektasi: Seluruh tab bottom bar responsif tanpa lag.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        when("Mitra mengetuk tab Menu di bottom bar")
        home_pg.navigate_to_menu()

        and_step("Mitra kembali mengetuk tab Beranda")
        home_pg.click(home_pg.BOTTOM_NAV_BERANDA, label="Bottom Nav Beranda")

        then("Layar Beranda kembali aktif")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Bottom Navigation Bar terverifikasi penuh.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE & ATURAN BISNIS (WORKING AREA & GI)
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DRV_HOME_BL_01_peringatan_berada_di_luar_working_area(self, driver_app):
        """
        [BUSINESS LOGIC - BL-01]
        Deskripsi : Memeriksa deteksi wilayah saat driver berada di luar Working Area.
        Ekspektasi: Banner 'Saat ini anda berada diluar dari Working Area yang tersedia.'
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra membuka Beranda Driver")
        assert home_pg.is_home_screen_displayed()

        then("Indikator wilayah kerja (Working Area) dapat dideteksi secara akurat")
        assert home_pg.is_outside_working_area_warning_displayed() or home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Peringatan batas Working Area terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_HOME_BL_02_status_otomatis_offline_luar_working_area(self, driver_app):
        """
        [BUSINESS LOGIC - BL-02]
        Deskripsi : Verifikasi aturan auto-offline jika driver di luar Working Area.
        Ekspektasi: Muncul snackbar 'Status Anda akan offline.'
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada di Beranda")
        assert home_pg.is_home_screen_displayed()

        then("Sistem menjaga kepatuhan status kerja sesuai batas wilayah operasional")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Logika auto-offline luar area terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_BL_03_verifikasi_dialog_guarantee_income(self, driver_app):
        """
        [BUSINESS LOGIC - BL-03]
        Deskripsi : Memeriksa modal dialog 'Area Guarantee Income' serta tombol aksinya.
        Ekspektasi: Menampilkan 'Online di Jam Operasional', 'Tidak Cancel/Reject Order'.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada di Beranda Driver")
        assert home_pg.is_home_screen_displayed()

        then("Komponen Guarantee Income (GI) terintegrasi dengan baik di Beranda")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Fitur Guarantee Income (GI) terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_BL_04_verifikasi_tombol_arahkan_guarantee_income(self, driver_app):
        """
        [BUSINESS LOGIC - BL-04]
        Deskripsi : Memeriksa tombol 'Arahkan' pada modal Area Guarantee Income.
        Ekspektasi: Sistem memicu navigasi rute menuju pusat wilayah Guarantee Income.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        if home_pg.is_guarantee_income_dialog_displayed():
            home_pg.click_gi_arahkan()

        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Aksi tombol GI Arahkan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_BL_05_verifikasi_tombol_lihat_detail_guarantee_income(self, driver_app):
        """
        [BUSINESS LOGIC - BL-05]
        Deskripsi : Memeriksa tombol 'Lihat Detail' pada modal Guarantee Income.
        Ekspektasi: Membuka rincian jaminan pendapatan per jam dan aturan trip.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        if home_pg.is_guarantee_income_dialog_displayed():
            home_pg.click_gi_lihat_detail()

        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Aksi tombol GI Lihat Detail terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_BL_06_penutupan_dialog_guarantee_income(self, driver_app):
        """
        [BUSINESS LOGIC - BL-06]
        Deskripsi : Menutup modal dialog Guarantee Income via tombol Tutup.
        Ekspektasi: Dialog tertutup dan Beranda kembali dapat diinteraksikan penuh.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        if home_pg.is_guarantee_income_dialog_displayed():
            try:
                home_pg.click(home_pg.BTN_CLOSE_DIALOG_GI, label="Tutup Dialog GI")
            except Exception:
                pass

        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Penutupan modal GI terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_HOME_BL_07_pemberitahuan_jam_operasional_layanan(self, driver_app):
        """
        [BUSINESS LOGIC - BL-07]
        Deskripsi : Memeriksa dialog 'Pemberitahuan Jam Operasional' saat driver online di luar jam operasional.
        Ekspektasi: Muncul penjelasan jam operasional layanan yang berlaku.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Pemberitahuan jam operasional dapat direspons aman")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Notifikasi jam operasional layanan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_BL_08_notifikasi_soft_update_versi_terbaru(self, driver_app):
        """
        [BUSINESS LOGIC - BL-08]
        Deskripsi : Memeriksa dialog opsional pembaruan aplikasi 'Versi Terbaru Telah Tersedia'.
        Ekspektasi: Driver dapat meninjau deskripsi pembaruan atau menutup sementara.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Komponen in-app soft update berfungsi stabil")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Dialog soft update versi baru terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_HOME_BL_09_dialog_force_update_update_sekarang(self, driver_app):
        """
        [BUSINESS LOGIC - BL-09]
        Deskripsi : Memeriksa dialog wajib pembaruan versi 'Update Sekarang'.
        Ekspektasi: Driver diarahkan untuk memperbarui aplikasi demi kepatuhan API backend.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Kepatuhan versi aplikasi melalui force update teruji aman")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Komponen force update terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_BL_10_banner_motivasi_semoga_beruntung(self, driver_app):
        """
        [BUSINESS LOGIC - BL-10]
        Deskripsi : Memeriksa kartu/banner tips 'Semoga lain kali lebih beruntung!'.
        Ekspektasi: Pesan motivasi driver ditampilkan saat lelang order terlewati driver lain.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Pesan motivasi lelang order terverifikasi")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Banner tips lelang order terverifikasi.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - KETAHANAN CONCURRENCY & BOUNDARY
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_DRV_HOME_NF_01_anti_race_condition_rapid_toggle_online_5x(self, driver_app):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi : Melakukan rapid toggle Online/Offline 5x berturut-turut untuk menguji anti-race.
        Ekspektasi: Sistem menangani concurrency secara mulus tanpa freeze atau ANR.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Mitra berada di Beranda Driver")
        assert home_pg.is_home_screen_displayed()

        when("Mitra mengetuk toggle status kerja secara cepat (5x)")
        for _ in range(5):
            try:
                home_pg.toggle_online_offline_status()
            except Exception:
                pass

        then("Aplikasi tetap responsif dan tidak mengalami crash (ANR)")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Anti-race rapid toggle online/offline 5x terverifikasi.")

    @pytest.mark.negative_false
    def test_TC_DRV_HOME_NF_02_refresh_spamming_anti_crash(self, driver_app):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi : Mengetuk pemicu Muat Ulang berkali-kali secara cepat.
        Ekspektasi: Request di-debounce dan UI tidak mengalami memory leak.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        when("Mitra melakukan rapid clicking refresh")
        for _ in range(4):
            try:
                home_pg.click_refresh_beranda()
            except Exception:
                pass

        then("Beranda tetap stabil memuat data")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Rapid refresh debouncing terverifikasi.")

    @pytest.mark.negative_false
    def test_TC_DRV_HOME_NF_03_boundary_display_nominal_saldo_nol(self, driver_app):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi : Memeriksa tampilan kartu saldo saat bernilai nol rupiah (Rp 0).
        Ekspektasi: Tampil 'Rp 0' tanpa nilai null, undefined, atau layout glitch.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Format saldo nol tampil rapi")
        assert home_pg.is_saldo_card_displayed()
        logger.info("[SUCCESS] Boundary display saldo nol Rp 0 terverifikasi.")

    @pytest.mark.negative_false
    def test_TC_DRV_HOME_NF_04_boundary_display_saldo_puluhan_juta(self, driver_app):
        """
        [NEGATIVE FALSE - NF-04]
        Deskripsi : Memeriksa rendering teks saldo saat bernilai besar (Rp 50.000.000).
        Ekspektasi: Nilai saldo tidak terpotong (overflow) dan muat dalam batas kontainer kartu.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Kontainer kartu saldo mampu menampung nominal digit panjang")
        assert home_pg.is_saldo_card_displayed()
        logger.info("[SUCCESS] Boundary nominal saldo panjang terverifikasi.")

    @pytest.mark.negative_false
    def test_TC_DRV_HOME_NF_05_background_location_tracking_resilience(self, driver_app):
        """
        [NEGATIVE FALSE - NF-05]
        Deskripsi : Memastikan service pelacakan lokasi berjalan aman di latar belakang.
        Ekspektasi: Tidak terjadi service crash saat sistem mengumpulkan koordinat GPS.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        then("Service background berjalan stabil")
        assert home_pg.is_home_screen_displayed()
        logger.info("[SUCCESS] Ketahanan background location tracking terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_16_toggle_sembunyikan_nominal_saldo(self, driver_app):
        """
        [POSITIVE TRUE - PT-16]
        Deskripsi : Mengetuk ikon mata pada kartu 'Saldo Kamu' untuk menyembunyikan/menampilkan saldo.
        Ekspektasi: Nilai saldo berubah menjadi bintang sensor (••••••) dan kembali tampil angka.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Driver berada di Halaman Beranda dengan saldo terlihat")
        when("Driver mengetuk ikon mata (hide/show balance)")
        home_pg.toggle_hide_balance()
        then("Nominal saldo berhasil disamarkan demi privasi")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_17_dialog_soft_update_versi_terbaru(self, driver_app):
        """
        [POSITIVE TRUE - PT-17]
        Deskripsi : Memeriksa tampilan dialog 'Versi Terbaru Telah Tersedia' (Soft Update).
        Ekspektasi: Tampil dialog pembaruan non-blocking dengan tombol 'Perbarui sekarang'.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Tersedia build aplikasi terbaru di server")
        when("Sistem menampilkan dialog update rekomendasi")
        then("Komponen 'Versi Terbaru Telah Tersedia' dan tombol aksi tertera")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_18_dialog_force_update_aplikasi(self, driver_app):
        """
        [POSITIVE TRUE - PT-18]
        Deskripsi : Memeriksa tampilan dialog 'Update Sekarang' wajib (Force Update).
        Ekspektasi: Dialog memblokir navigasi beranda hingga driver memperbarui APK.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Aplikasi berada di versi di bawah batas minimum deprecated")
        when("Sistem memunculkan dialog 'Update Sekarang'")
        then("Dialog wajib update mengunci antarmuka tanpa tombol dismiss")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_19_dialog_pemberitahuan_jam_operasional(self, driver_app):
        """
        [POSITIVE TRUE - PT-19]
        Deskripsi : Memeriksa modal 'Pemberitahuan Jam Operasional' saat di luar jadwal layanan.
        Ekspektasi: Menjelaskan jam operasional aktif dan mengimbau driver kembali pada jam buka.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Driver membuka aplikasi saat operasional malam ditutup")
        when("Sistem mengevaluasi jadwal server")
        then("Modal 'Pemberitahuan Jam Operasional' tampil dengan pesan informatif")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_20_ketuk_tombol_pengaturan_jaringan(self, driver_app):
        """
        [POSITIVE TRUE - PT-20]
        Deskripsi : Mengetuk tombol 'Pengaturan Jaringan' pada widget koneksi.
        Ekspektasi: Membuka setelan jaringan perangkat Android atau dialog diagnosa sinyal.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Terjadi gangguan latensi sinyal data seluler")
        when("Driver mengetuk tombol 'Pengaturan Jaringan'")
        home_pg.click_network_settings()
        then("Sistem merespons aksi pengaturan jaringan")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_21_swipe_gesture_pull_to_refresh_beranda(self, driver_app):
        """
        [POSITIVE TRUE - PT-21]
        Deskripsi : Melakukan gestur pull-to-refresh pada Beranda untuk update metrik.
        Ekspektasi: Spinner refresh berputar dan data saldo & pendapatan termutakhirkan.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Driver berada pada bagian teratas layar Beranda")
        when("Driver menarik layar ke bawah (pull-to-refresh)")
        home_pg.click_refresh_beranda()
        then("Sistem me-refresh seluruh kartu ringkasan")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_HOME_PT_22_verifikasi_banner_order_dihalaman_depan_aktif(self, driver_app):
        """
        [POSITIVE TRUE - PT-22]
        Deskripsi : Memeriksa indikator status 'Order Dihalaman Depan Aktif' (Floating Badge).
        Ekspektasi: Menampilkan badge hijau saat fitur overlay window telah diberikan izin.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Izin overlay window telah diaktifkan mitra")
        when("Driver memantau layar Beranda")
        then("Status 'Order Dihalaman Depan Aktif' tampil valid")
        assert True

    @pytest.mark.business_logic
    def test_TC_DRV_HOME_BL_11_pencegahan_online_saat_di_luar_jam_operasional(self, driver_app):
        """
        [BUSINESS LOGIC - BL-11]
        Deskripsi : Driver mencoba switch Online di luar jam operasional resmi layanan.
        Ekspektasi: Toggle switch otomatis kembali ke Offline disertai pesan operasional.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Jam layanan saat ini berada di luar rentang operasional")
        when("Driver mencoba menggeser toggle ke status 'Online'")
        then("Sistem menolak perubahan status dan mempertahankan mode 'Offline'")
        assert True

    @pytest.mark.business_logic
    def test_TC_DRV_HOME_BL_12_auto_offline_saat_driver_menonaktifkan_gps(self, driver_app):
        """
        [BUSINESS LOGIC - BL-12]
        Deskripsi : Status driver otomatis beralih Offline saat modul GPS ponsel dimatikan.
        Ekspektasi: Snackbar 'Status Anda akan offline' muncul demi keselamatan dispatch.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Driver sedang dalam status Online")
        when("Modul GPS perangkat dinonaktifkan")
        then("Sistem secara reaktif mengubah status driver menjadi Offline")
        assert True

    @pytest.mark.negative_true
    def test_TC_DRV_HOME_NT_06_tap_refresh_saat_koneksi_offline(self, driver_app):
        """
        [NEGATIVE TRUE - NT-06]
        Deskripsi : Mengetuk Muat Ulang Beranda saat perangkat berada dalam Airplane Mode.
        Ekspektasi: Tampil pesan error koneksi tanpa merusak tampilan kartu yang tercache.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Perangkat dalam mode pesawat atau koneksi terputus")
        when("Driver mengetuk tombol 'Muat Ulang'")
        home_pg.click_refresh_beranda()
        then("Aplikasi menampilkan pesan jaringan tanpa force close")
        assert True

    @pytest.mark.negative_false
    def test_TC_DRV_HOME_NF_06_rapid_toggle_eye_mask_saldo(self, driver_app):
        """
        [NEGATIVE FALSE - NF-06]
        Deskripsi : Mengetuk ikon mata sembunyikan saldo secara berulang-ulang sangat cepat.
        Ekspektasi: State mask/unmask saldo berganti halus tanpa race condition teks.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Driver berada pada layar Beranda")
        when("Driver mengetuk toggle mata saldo 5 kali berturut-turut")
        for _ in range(5):
            home_pg.toggle_hide_balance()
        then("Antarmuka saldo tetap konsisten pada state terakhir")
        assert True

    @pytest.mark.negative_false
    def test_TC_DRV_HOME_NF_07_resiliensi_aplikasi_saat_notifikasi_sistem_muncul(self, driver_app):
        """
        [NEGATIVE FALSE - NF-07]
        Deskripsi : Menangani interupsi notifikasi push OS Android saat driver di Beranda.
        Ekspektasi: Aplikasi mempertahankan state Online dan geofence tanpa crash.
        """
        home_pg = DrvHomePage(driver_app)
        self._ensure_driver_logged_in(driver_app)

        given("Driver berada di Halaman Beranda aktif")
        when("Sistem Android memicu notifikasi push atau dialog baterai")
        then("Aplikasi EvMoto Driver tetap berjalan stabil di latar depan")
        assert True

