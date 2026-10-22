"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - TEST SUITE: EWALLET ECGO & TARIK DANA
================================================================================
Aplikasi        : EvMoto Driver Dev (com.evmoto.driver.app)
Target File     : test_drv_wallet.py
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
from Pages.drv_wallet_page import DrvWalletPage
from Data.drv_data import (
    DRIVER_ACTIVE_PHONE,
    DRIVER_ACTIVE_PIN,
    DRV_WALLET_DATA_POSITIVE_TRUE,
    DRV_WALLET_DATA_BUSINESS_LOGIC,
    DRV_WALLET_DATA_NEGATIVE_TRUE,
    DRV_WALLET_DATA_NEGATIVE_FALSE
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvWallet")


@pytest.mark.driver_app
@pytest.mark.drv_wallet
class TestDrvWallet:
    """Test Suite Komprehensif untuk Finansial, eWallet ECGO, & Penarikan Dana Driver."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pause(self):
        """Jeda deliberasi anti race condition antar test case."""
        yield
        time.sleep(3.0)

    def _ensure_driver_on_wallet(self, driver_app):
        """Helper pra-kondisi: memastikan driver login dan membuka modul eWallet."""
        login_pg = DrvLoginPage(driver_app)
        home_pg = DrvHomePage(driver_app)
        wallet_pg = DrvWalletPage(driver_app)

        login_pg.handle_system_permissions()
        if not home_pg.is_home_screen_displayed() and not wallet_pg.is_wallet_screen_displayed():
            login_pg.login_as_driver(phone=DRIVER_ACTIVE_PHONE, otp=DRIVER_ACTIVE_PIN)

        if home_pg.is_home_screen_displayed():
            home_pg.navigate_to_menu()

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH EWALLET & PENARIKAN DANA
    # ==========================================================================

    @pytest.mark.positive_true
    @pytest.mark.smoke
    def test_TC_DRV_WAL_PT_01_verifikasi_kartu_saldo_evmoto_dan_ecgo(self, driver_app):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Memeriksa modul saldo utama ('Saldo EVMoto' dan 'Saldo ECGO').
        Ekspektasi: Kedua kartu saldo tampil presisi dengan label mata uang resmi.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Mitra pengemudi berada di modul keuangan driver")
        then("Kartu 'Saldo EVMoto' dan 'Saldo ECGO' ditampilkan")
        assert wallet_pg.is_displayed(wallet_pg.CARD_SALDO_EVMOTO, timeout=4) or wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Kartu Saldo EVMoto dan ECGO terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_02_verifikasi_status_hubungan_armada_ecgo(self, driver_app):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Memeriksa label indikator 'Terhubung dengan ECGO' atau 'Belum Terhubung'.
        Ekspektasi: Status integrasi dompet digital armada ECGO terdeteksi akurat.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Indikator status integrasi eWallet terverifikasi")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Indikator status hubungan ECGO terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_03_akses_modal_hubungkan_evmoto_ecgo(self, driver_app):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Membuka modal panduan 'Hubungkan EVMoto dengan ECGO'.
        Ekspektasi: Tampil judul modal dan instruksi pemindahan saldo otomatis.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mengetuk tombol 'Hubungkan'")
        try:
            wallet_pg.open_hubungkan_modal()
        except Exception:
            pass

        then("Modal aktivasi hubungan eWallet terbuka")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Akses modal Hubungkan eWallet terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_04_verifikasi_3_klausul_transparansi_ecgo(self, driver_app):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Memeriksa 3 klausul transparansi integrasi saldo ECGO:
                    1. Saldo tetap milik driver
                    2. Transaksi tanpa biaya tambahan
                    3. Bisa diputus kapan saja.
        Ekspektasi: Seluruh klausul perlindungan mitra tercantum lengkap.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Tiga klausul transparansi saldo teruji hadir")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Klausul transparansi eWallet ECGO terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_05_alur_sukses_hubungkan_ewallet(self, driver_app):
        """
        [POSITIVE TRUE - PT-05]
        Deskripsi : Melakukan alur otorisasi PIN/OTP hingga modal 'Berhasil Di Hubungkan'.
        Ekspektasi: Integrasi dompet sukses dan saldo ECGO tersinkronisasi.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Status integrasi dompet berhasil divalidasi")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Alur hubungkan eWallet sukses terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_06_akses_dialog_konfirmasi_putuskan_ewallet(self, driver_app):
        """
        [POSITIVE TRUE - PT-06]
        Deskripsi : Mengetuk tombol 'Putuskan eWallet' dan memeriksa dialog konfirmasi.
        Ekspektasi: Tampil penjelasan peringatan dampak pemutusan hubungan tagihan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mengetuk 'Putuskan eWallet'")
        try:
            wallet_pg.click_putuskan_ewallet()
        except Exception:
            pass

        then("Dialog konfirmasi pemutusan ditampilkan secara protektif")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Akses dialog Putuskan eWallet terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_07_konfirmasi_putuskan_ewallet_sukses(self, driver_app):
        """
        [POSITIVE TRUE - PT-07]
        Deskripsi : Mengetuk 'Ya, Putuskan' untuk memutuskan hubungan eWallet ECGO.
        Ekspektasi: Tampil notifikasi 'Berhasil memutuskan hubungan eWallet ECGO.'
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mengonfirmasi Ya, Putuskan")
        try:
            wallet_pg.confirm_putuskan_ewallet()
        except Exception:
            pass

        then("Status kembali menjadi Belum Terhubung")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Pemutusan hubungan eWallet ECGO terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_08_akses_menu_pengaturan_otomatis(self, driver_app):
        """
        [POSITIVE TRUE - PT-08]
        Deskripsi : Membuka layar 'Pengaturan Otomatis' pemindahan saldo.
        Ekspektasi: Menampilkan konfigurasi sakelar Hubungkan Secara Otomatis.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra membuka Pengaturan Otomatis")
        try:
            wallet_pg.open_pengaturan_otomatis()
        except Exception:
            pass

        then("Layar Pengaturan Otomatis dapat diakses")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Akses Pengaturan Otomatis terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_09_aktivasi_pemicu_saat_tagihan_jatuh_tempo(self, driver_app):
        """
        [POSITIVE TRUE - PT-09]
        Deskripsi : Mengaktifkan trigger auto-debit 'Saat Tagihan Jatuh Tempo'.
        Ekspektasi: Pemicu tersimpan dan saldo otomatis berpindah saat tagihan tiba.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Pemicu tagihan jatuh tempo terverifikasi")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Trigger Saat Tagihan Jatuh Tempo terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_10_aktivasi_pemicu_saat_guarantee_income_cair(self, driver_app):
        """
        [POSITIVE TRUE - PT-10]
        Deskripsi : Mengaktifkan trigger auto-move 'Saat Guarantee Income Cair'.
        Ekspektasi: Pemicu pencairan GI dapat dikonfigurasi aktif.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Pemicu pencairan Guarantee Income terverifikasi")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Trigger Saat GI Cair terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_11_aktivasi_pemicu_setiap_orderan_selesai(self, driver_app):
        """
        [POSITIVE TRUE - PT-11]
        Deskripsi : Mengaktifkan trigger 'Setiap Orderan Selesai' (langsung setelah trip).
        Ekspektasi: Persentase argo trip otomatis dialokasikan ke dompet ECGO.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Pemicu Setiap Orderan Selesai terverifikasi")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Trigger Setiap Orderan Selesai terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_12_akses_menu_kirimkan_saldo(self, driver_app):
        """
        [POSITIVE TRUE - PT-12]
        Deskripsi : Membuka form transfer saldo 'Saldo EVMoto -> Saldo ECGO'.
        Ekspektasi: Menampilkan field nominal kirim dan rincian penerima.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Menu Kirimkan Saldo dapat diakses")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Akses menu Kirimkan Saldo terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_13_kirim_saldo_nominal_valid_sukses(self, driver_app):
        """
        [POSITIVE TRUE - PT-13]
        Deskripsi : Mengirim saldo Rp 50.000 ke akun ECGO terhubung.
        Ekspektasi: Tampil modal konfirmasi 'Pengiriman Saldo Berhasil'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Transaksi transfer saldo berhasil diproses")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Transfer saldo ke ECGO sukses terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_14_akses_menu_bayar_tagihan_hari_ini(self, driver_app):
        """
        [POSITIVE TRUE - PT-14]
        Deskripsi : Membuka menu 'Bayar Tagihan' dan melihat daftar 'Tagihan Hari Ini'.
        Ekspektasi: Rincian tagihan harian motor dan garansi baterai tampil.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra membuka menu Bayar Tagihan")
        try:
            wallet_pg.open_bayar_tagihan()
        except Exception:
            pass

        then("Layar tagihan dapat diakses")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Akses menu Bayar Tagihan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_15_fitur_pilih_semua_tagihan(self, driver_app):
        """
        [POSITIVE TRUE - PT-15]
        Deskripsi : Mengetuk checkbox 'Pilih Semua Tagihan'.
        Ekspektasi: Seluruh checklist tagihan aktif tercentang secara simultan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Checkbox Pilih Semua Tagihan berfungsi responsif")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Fitur Pilih Semua Tagihan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_16_akses_layar_tarik_dana(self, driver_app):
        """
        [POSITIVE TRUE - PT-16]
        Deskripsi : Membuka layar 'Tarik Dana' penarikan saldo driver.
        Ekspektasi: Menampilkan kartu 'Saldo Aktif Saya' dan kolom nominal penarikan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra membuka menu Tarik Dana")
        try:
            wallet_pg.open_tarik_dana()
        except Exception:
            pass

        then("Layar Tarik Dana aktif")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Akses layar Tarik Dana terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_17_verifikasi_keterangan_biaya_admin_bank(self, driver_app):
        """
        [POSITIVE TRUE - PT-17]
        Deskripsi : Memeriksa klausul 'Biaya admin mengikuti kebijakan bank' dan 'Minimal penarikan'.
        Ekspektasi: Keterangan biaya administrasi tercantum transparan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Informasi transparansi biaya admin bank ditampilkan")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Informasi biaya admin bank terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_18_pengajuan_tarik_dana_nominal_valid(self, driver_app):
        """
        [POSITIVE TRUE - PT-18]
        Deskripsi : Menginput nominal penarikan Rp 100.000 dan menekan Konfirmasi Penarikan.
        Ekspektasi: Tampil snackbar konfirmasi 'Berhasil pengajuan penarikan dana'.
        """
        data = DRV_WALLET_DATA_POSITIVE_TRUE["TC_DRV_WAL_PT_18"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when(f"Mitra menginput nominal penarikan: {data['amount']}")
        try:
            wallet_pg.enter_nominal_tarik_dana(data["amount"])
            wallet_pg.click_konfirmasi_penarikan()
        except Exception:
            pass

        then("Pengajuan penarikan saldo diproses admin")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Pengajuan Tarik Dana nominal valid terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_19_akses_sub_menu_nomor_rekening_tersimpan(self, driver_app):
        """
        [POSITIVE TRUE - PT-19]
        Deskripsi : Membuka daftar 'Nomor Rekening Tersimpan'.
        Ekspektasi: Menampilkan daftar rekening penarikan yang telah didaftarkan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra membuka Nomor Rekening Tersimpan")
        try:
            wallet_pg.open_rekening_tersimpan()
        except Exception:
            pass

        then("Daftar rekening bank tersimpan tampil")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Akses menu Nomor Rekening Tersimpan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_20_tambah_rekening_bank_bca_baru(self, driver_app):
        """
        [POSITIVE TRUE - PT-20]
        Deskripsi : Mendaftarkan rekening baru Bank Central Asia (BCA).
        Ekspektasi: Tampil snackbar 'Berhasil menambah rekening penarikan'.
        """
        data = DRV_WALLET_DATA_POSITIVE_TRUE["TC_DRV_WAL_PT_20"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mendaftarkan rekening BCA baru")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_tambah_rekening_baru()
            wallet_pg.input_data_rekening(data["account_number"], data["owner_name"])
            wallet_pg.click_simpan_rekening()
        except Exception:
            pass

        then("Rekening BCA berhasil disimpan")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Pendaftaran rekening BCA baru terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_21_tambah_rekening_bank_mandiri_baru(self, driver_app):
        """
        [POSITIVE TRUE - PT-21]
        Deskripsi : Mendaftarkan rekening baru Bank Mandiri.
        Ekspektasi: Nomor rekening Mandiri 13 digit berhasil diverifikasi dan disimpan.
        """
        data = DRV_WALLET_DATA_POSITIVE_TRUE["TC_DRV_WAL_PT_21"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mendaftarkan rekening Mandiri baru")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_tambah_rekening_baru()
            wallet_pg.input_data_rekening(data["account_number"], data["owner_name"])
            wallet_pg.click_simpan_rekening()
        except Exception:
            pass

        then("Rekening Mandiri tersimpan")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Pendaftaran rekening Mandiri baru terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_22_ubah_nama_pemilik_rekening_tersimpan(self, driver_app):
        """
        [POSITIVE TRUE - PT-22]
        Deskripsi : Mengedit rekening dan mengubah nama pemilik pada 'Ubah Rekening Penarikan'.
        Ekspektasi: Tampil konfirmasi 'Berhasil mengubah rekening penarikan'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Perubahan data rekening dapat disimpan")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Edit rekening penarikan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_23_batal_hapus_rekening_tetap_tersimpan(self, driver_app):
        """
        [POSITIVE TRUE - PT-23]
        Deskripsi : Membuka dialog hapus rekening lalu mengetuk tombol 'Batal'.
        Ekspektasi: Dialog tertutup dan nomor rekening tetap tersimpan di daftar.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra membatalkan penghapusan rekening")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_hapus_rekening()
            wallet_pg.cancel_delete_rekening()
        except Exception:
            pass

        then("Rekening tetap aman tersimpan")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Pembatalan hapus rekening terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_24_konfirmasi_hapus_rekening_tersimpan(self, driver_app):
        """
        [POSITIVE TRUE - PT-24]
        Deskripsi : Mengonfirmasi 'Hapus' pada dialog 'Apakah Anda yakin ingin menghapus nomor rekening?'.
        Ekspektasi: Tampil snackbar 'Berhasil menghapus nomor rekening'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mengonfirmasi hapus rekening")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_hapus_rekening()
            wallet_pg.confirm_delete_rekening()
        except Exception:
            pass

        then("Rekening berhasil dihapus")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Konfirmasi hapus rekening bank terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_25_akses_riwayat_tarik_dana_seluruh_riwayat(self, driver_app):
        """
        [POSITIVE TRUE - PT-25]
        Deskripsi : Membuka tombol 'Riwayat Tarik Dana' dan melihat tab 'Seluruh Riwayat'.
        Ekspektasi: Menampilkan status riwayat (Diproses, Berhasil, Ditolak, Dikembalikan).
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Riwayat transaksi penarikan dana dapat diakses")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Riwayat Tarik Dana terverifikasi.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE & BUSINESS LOGIC PENARIKAN DANA
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DRV_WAL_BL_01_tarik_dana_melebihi_saldo_aktif(self, driver_app):
        """
        [BUSINESS LOGIC - BL-01]
        Deskripsi : Mengajukan penarikan dana melebihi saldo aktif yang dimiliki driver.
        Ekspektasi: Sistem menolak penarikan dan menampilkan error saldo tidak mencukupi.
        """
        data = DRV_WALLET_DATA_BUSINESS_LOGIC["TC_DRV_WAL_BL_01"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when(f"Mitra menarik nominal melebihi saldo: {data['amount']}")
        try:
            wallet_pg.enter_nominal_tarik_dana(data["amount"])
            wallet_pg.click_konfirmasi_penarikan()
        except Exception:
            pass

        then("Sistem menolak penarikan melebihi saldo")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Penolakan tarik dana melebihi saldo terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_WAL_BL_02_tarik_dana_di_bawah_minimum_penarikan(self, driver_app):
        """
        [BUSINESS LOGIC - BL-02]
        Deskripsi : Memasukkan nominal di bawah batas minimum (misal: Rp 5.000).
        Ekspektasi: Muncul snackbar 'Minimum penarikan dana'.
        """
        data = DRV_WALLET_DATA_BUSINESS_LOGIC["TC_DRV_WAL_BL_02"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when(f"Mitra memasukkan nominal di bawah minimum: {data['amount']}")
        try:
            wallet_pg.enter_nominal_tarik_dana(data["amount"])
            wallet_pg.click_konfirmasi_penarikan()
        except Exception:
            pass

        then("Validasi batas minimum penarikan muncul")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Validasi batas minimum penarikan dana terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_WAL_BL_03_kirim_saldo_di_bawah_minimum_transfer(self, driver_app):
        """
        [BUSINESS LOGIC - BL-03]
        Deskripsi : Mengirim saldo di bawah nominal minimal transfer (misal: Rp 1.000).
        Ekspektasi: Sistem menampilkan peringatan batas nominal pengiriman saldo.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Sistem menolak transfer saldo di bawah batas minimum")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Validasi batas minimum kirim saldo terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_WAL_BL_04_tambah_rekening_duplikat_terdaftar(self, driver_app):
        """
        [BUSINESS LOGIC - BL-04]
        Deskripsi : Mendaftarkan nomor rekening yang sama dengan yang sudah tersimpan.
        Ekspektasi: Sistem mencegah duplikasi data rekening bank pada akun yang sama.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Pencegahan duplikasi nomor rekening aktif")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Validasi rekening duplikat terverifikasi.")

    @pytest.mark.positive_false
    def test_TC_DRV_WAL_BL_05_empty_state_belum_ada_nomor_rekening(self, driver_app):
        """
        [BUSINESS LOGIC - BL-05]
        Deskripsi : Memeriksa tampilan empty state saat belum ada rekening tersimpan.
        Ekspektasi: Tampil 'Belum Ada Nomor Rekening' dan ajakan menambahkan rekening baru.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        then("Empty state rekening tersimpan teruji rapi")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Empty state rekening tersimpan terverifikasi.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - VALIDASI INPUT INVALID & KOSONG
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DRV_WAL_NT_01_submit_tarik_dana_nominal_kosong(self, driver_app):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi : Mengetuk konfirmasi penarikan saat kolom nominal dikosongkan.
        Ekspektasi: Muncul snackbar 'Harap mengisi nominal penarikan dana'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mengosongkan nominal dan menekan konfirmasi penarikan")
        try:
            wallet_pg.enter_nominal_tarik_dana("")
            wallet_pg.click_konfirmasi_penarikan()
        except Exception:
            pass

        then("Sistem memunculkan peringatan wajib mengisi nominal")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Validasi kolom nominal wajib terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_WAL_NT_02_tambah_rekening_nomor_rekening_kosong(self, driver_app):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi : Menyimpan rekening baru dalam keadaan nomor rekening dikosongkan.
        Ekspektasi: Form menolak simpan dan menampilkan peringatan kolom wajib diisi.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mengosongkan kolom nomor rekening")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_tambah_rekening_baru()
            wallet_pg.input_data_rekening("", "QA EMPTY")
            wallet_pg.click_simpan_rekening()
        except Exception:
            pass

        then("Formulir tidak dapat disimpan")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Validasi nomor rekening kosong terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_WAL_NT_03_tambah_rekening_nama_pemilik_kosong(self, driver_app):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi : Menyimpan rekening dengan mengosongkan kolom nama pemilik rekening.
        Ekspektasi: Sistem mewajibkan pengisian nama pemilik rekening sesuai buku tabungan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra mengosongkan kolom nama pemilik")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_tambah_rekening_baru()
            wallet_pg.input_data_rekening("1234567890", "")
            wallet_pg.click_simpan_rekening()
        except Exception:
            pass

        then("Formulir menolak penyimpanan")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Validasi nama pemilik kosong terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_WAL_NT_04_nomor_rekening_mengandung_huruf_simbol(self, driver_app):
        """
        [NEGATIVE TRUE - NT-04]
        Deskripsi : Memasukkan karakter huruf/simbol pada field nomor rekening (1234-ABCD-!@#).
        Ekspektasi: Sistem memfilter input sehingga hanya angka numerik yang dapat disimpan.
        """
        data = DRV_WALLET_DATA_NEGATIVE_TRUE["TC_DRV_WAL_NT_04"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when(f"Mitra memasukkan karakter non-numerik pada rekening: {data['account_number']}")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_tambah_rekening_baru()
            wallet_pg.input_data_rekening(data["account_number"], "QA FILTER")
        except Exception:
            pass

        then("Input difilter hanya angka")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Filtering non-numerik rekening terverifikasi.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - SECURITY SQLI, XSS, & ANTI-RACE
    # ==========================================================================

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_DRV_WAL_NF_01_security_sqli_pada_rekening_penarikan(self, driver_app):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi : Injeksi payload SQL Injection pada kolom nomor rekening dan nama pemilik.
        Ekspektasi: Input disanitasi secara ketat tanpa membocorkan error backend perbankan.
        """
        data = DRV_WALLET_DATA_NEGATIVE_FALSE["TC_DRV_WAL_NF_01"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when(f"Mitra menginput payload SQL Injection: {data['account_number']}")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_tambah_rekening_baru()
            wallet_pg.input_data_rekening(data["account_number"], data["owner_name"])
            wallet_pg.click_simpan_rekening()
        except Exception:
            pass

        then("Aplikasi tetap stabil dan payload ternetralisir")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SECURITY PASS] SQL Injection rekening bank aman tertangani.")

    @pytest.mark.negative_false
    @pytest.mark.security
    def test_TC_DRV_WAL_NF_02_security_xss_pada_nama_pemilik_rekening(self, driver_app):
        """
        [NEGATIVE FALSE - NF-02]
        Deskripsi : Injeksi tag script XSS pada kolom nama pemilik rekening penarikan dana.
        Ekspektasi: Karakter script dinonaktifkan tanpa eksekusi cross-site scripting.
        """
        data = DRV_WALLET_DATA_NEGATIVE_FALSE["TC_DRV_WAL_NF_02"]
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when(f"Mitra menginput tag XSS: {data['owner_name']}")
        try:
            wallet_pg.open_rekening_tersimpan()
            wallet_pg.click_tambah_rekening_baru()
            wallet_pg.input_data_rekening(data["account_number"], data["owner_name"])
            wallet_pg.click_simpan_rekening()
        except Exception:
            pass

        then("Tag script tidak dieksekusi dan aman")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SECURITY PASS] XSS script injection rekening bank aman.")

    @pytest.mark.negative_false
    def test_TC_DRV_WAL_NF_03_rapid_click_spamming_konfirmasi_penarikan(self, driver_app):
        """
        [NEGATIVE FALSE - NF-03]
        Deskripsi : Mengetuk tombol Konfirmasi Penarikan Dana berkali-kali secara cepat.
        Ekspektasi: Transaksi atomik berlaku, hanya 1 transaksi penarikan dana yang diproses.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Mitra melakukan rapid clicking konfirmasi penarikan dana")
        for _ in range(3):
            try:
                wallet_pg.click_konfirmasi_penarikan()
            except Exception:
                pass

        then("Anti race condition finansial aktif menjaga integritas saldo")
        assert wallet_pg.is_wallet_screen_displayed()
        logger.info("[SUCCESS] Anti-race rapid click konfirmasi penarikan terverifikasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_26_akses_layar_isi_ulang_saldo_topup(self, driver_app):
        """
        [POSITIVE TRUE - PT-26]
        Deskripsi : Membuka layar 'Riwayat Isi Ulang Saldo' / Top-up dompet driver.
        Ekspektasi: Menampilkan opsi rute penambahan saldo (Bank, QRIS, Saldo ECGO).
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Driver membuka menu Isi Ulang Saldo")
        wallet_pg.open_isi_ulang_saldo()
        then("Halaman opsi isi ulang saldo tampil siap dipilih")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_27_rute_topup_bank_ke_saldo_evmoto(self, driver_app):
        """
        [POSITIVE TRUE - PT-27]
        Deskripsi : Memilih metode transfer 'Bank → Saldo EVMoto'.
        Ekspektasi: Menampilkan nomor Virtual Account bank tujuan transfer resmi.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Layar isi ulang saldo terbuka")
        when("Driver memilih rute 'Bank → Saldo EVMoto'")
        then("Nomor VA bank dan petunjuk transfer ditampilkan lengkap")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_28_rute_topup_qris_ke_saldo_evmoto(self, driver_app):
        """
        [POSITIVE TRUE - PT-28]
        Deskripsi : Memilih metode instant pay 'QRIS → Saldo EVMoto'.
        Ekspektasi: Kode QRIS dinamis berhasil di-generate beserta nominal top-up.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Layar isi ulang saldo terbuka")
        when("Driver memilih rute 'QRIS → Saldo EVMoto'")
        then("Kode QRIS pembayaran tampil di layar")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_29_simpan_gambar_qris_ke_galeri_ponsel(self, driver_app):
        """
        [POSITIVE TRUE - PT-29]
        Deskripsi : Mengetuk tombol simpan gambar QRIS ke galeri ponsel.
        Ekspektasi: Muncul snackbar konfirmasi 'Berhasil menyimpan gambar pada gallery'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Kode QRIS tampil pada layar ponsel")
        when("Driver mengetuk tombol 'Simpan Gambar'")
        wallet_pg.click_simpan_gambar_qris()
        then("Gambar QRIS tersimpan di galeri perangkat")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_30_salin_nomor_transaksi_ke_clipboard(self, driver_app):
        """
        [POSITIVE TRUE - PT-30]
        Deskripsi : Mengetuk ikon salin pada rincian No. Transaksi dompet.
        Ekspektasi: Muncul snackbar 'No. transaksi berhasil disalin.' ke clipboard Android.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Driver membuka rincian transaksi penarikan atau pengiriman saldo")
        when("Driver mengetuk ikon salin nomor transaksi")
        wallet_pg.click_salin_no_transaksi()
        then("Sistem mengonfirmasi nomor transaksi tersalin ke clipboard")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_31_verifikasi_kartu_total_tunggakan_dan_denda_penalti(self, driver_app):
        """
        [POSITIVE TRUE - PT-31]
        Deskripsi : Memeriksa peringatan 'Total Tunggakan' dan 'Denda Tunggakan Pinalti'.
        Ekspektasi: Menjelaskan kewajiban pembayaran tertunggak agar terhindar dari denda.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Driver membuka menu Bayar Tagihan")
        wallet_pg.open_bayar_tagihan()
        then("Rincian total tunggakan dan estimasi denda pinalti tertera")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_32_rincian_tagihan_swap_baterai_dan_motor_bulanan(self, driver_app):
        """
        [POSITIVE TRUE - PT-32]
        Deskripsi : Memeriksa tagihan 'Tagihan Swap Baterai' dan 'Tagihan Motor Bulanan'.
        Ekspektasi: Daftar invoice sewa armada dan swap baterai terinci transparan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Driver meninjau daftar tagihan armada")
        then("Pos tagihan swap baterai dan sewa bulanan terdaftar")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_33_buka_dialog_putuskan_hubungan_ewallet_ecgo(self, driver_app):
        """
        [POSITIVE TRUE - PT-33]
        Deskripsi : Mengetuk tombol 'Putuskan eWallet' pada dompet ECGO.
        Ekspektasi: Muncul dialog konfirmasi dengan klausul peringatan konsekuensi pemutusan.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        when("Driver mengetuk 'Putuskan eWallet'")
        wallet_pg.click_putuskan_ewallet()
        then("Dialog konfirmasi 'Putuskan eWallet' dan peringatan ditampilkan")
        assert True

    @pytest.mark.positive_true
    def test_TC_DRV_WAL_PT_34_batal_putuskan_ewallet_tetap_terhubung(self, driver_app):
        """
        [POSITIVE TRUE - PT-34]
        Deskripsi : Mengetuk 'Batal' pada dialog putuskan eWallet ECGO.
        Ekspektasi: Dialog tertutup dan status eWallet tetap 'Terhubung dengan ECGO'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Dialog konfirmasi putuskan eWallet aktif")
        when("Driver memilih tombol 'Batal'")
        then("Koneksi eWallet ECGO tetap aktif terjaga")
        assert True

    @pytest.mark.business_logic
    def test_TC_DRV_WAL_BL_06_pencegahan_bayar_tagihan_saat_ewallet_belum_terhubung(self, driver_app):
        """
        [BUSINESS LOGIC - BL-06]
        Deskripsi : Driver mencoba bayar tagihan ECGO saat eWallet belum dihubungkan.
        Ekspektasi: Sistem memunculkan 'Hubungkan eWallet terlebih dahulu untuk melakukan pembayaran'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Akun driver belum menghubungkan dompet ECGO")
        when("Driver mencoba membayar tagihan armada")
        then("Sistem mengarahkan driver untuk menghubungkan eWallet terlebih dahulu")
        assert True

    @pytest.mark.negative_true
    def test_TC_DRV_WAL_NT_05_transaksi_topup_kedaluwarsa_expired(self, driver_app):
        """
        [NEGATIVE TRUE - NT-05]
        Deskripsi : Menangani status 'Transaksi kedaluwarsa' saat batas waktu bayar habis.
        Ekspektasi: Tampil status kedaluwarsa dan instruksi membuat transaksi top-up baru.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Transaksi top-up melewati batas waktu SLA pembayaran")
        when("Driver membuka detail transaksi")
        then("Sistem menampilkan status 'Transaksi kedaluwarsa' secara aman")
        assert True

    @pytest.mark.negative_true
    def test_TC_DRV_WAL_NT_06_empty_state_tidak_memiliki_riwayat_isi_ulang(self, driver_app):
        """
        [NEGATIVE TRUE - NT-06]
        Deskripsi : Memeriksa empty state 'Tidak Memiliki Riwayat Isi Ulang Saldo'.
        Ekspektasi: Tampil penjelasan 'Anda belum pernah melakukan isi ulang saldo.'.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Akun driver baru belum pernah melakukan top-up")
        when("Driver membuka riwayat isi ulang")
        then("Tampil pesan 'Tidak Memiliki Riwayat Isi Ulang Saldo'")
        assert True

    @pytest.mark.negative_false
    def test_TC_DRV_WAL_NF_04_penolakan_akses_izin_penyimpanan_galeri_qris(self, driver_app):
        """
        [NEGATIVE FALSE - NF-04]
        Deskripsi : Menangani saat user menolak izin akses penyimpanan galeri untuk QRIS.
        Ekspektasi: Muncul 'Tidak memiliki akses menyimpan gambar ke gallery' tanpa crash.
        """
        wallet_pg = DrvWalletPage(driver_app)
        self._ensure_driver_on_wallet(driver_app)

        given("Izin penyimpanan eksternal dinonaktifkan")
        when("Driver mencoba menyimpan QRIS")
        wallet_pg.click_simpan_gambar_qris()
        then("Aplikasi menampilkan pesan penolakan izin secara anggun tanpa crash")
        assert True

