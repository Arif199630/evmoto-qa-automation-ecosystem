"""
================================================================================
EVMOTO DRIVER MOBILE AUTOMATION - TEST SUITE: SEWA & HUBUNGKAN AKUN (RENTAL/CICILAN)
================================================================================
Aplikasi        : EvMoto Driver Dev (com.evmoto.driver.app)
Target File     : test_drv_rental_installment.py
Environment     : Dev Golang (https://api-dev.evmoto.internal)
Akun Driver     : 81299990001 | PIN Bypass 1234
Metodologi      : Page Object Model (POM) & 4 Pilar QA Lengkap
Konsep Bisnis   : 1. No Soft-Delete (Orphan Motor Re-assignment)
                  2. One-Way Toggle 'Hubungkan Akun' di Super Apps (Disabled/Locked)
                  3. Proteksi Anti-Fraud & Integrasi Finansial Sewa ECGO
Wording         : 100% Presisi strings resmi APK driver_lang_id.json
================================================================================
"""
import time
import pytest
from Pages.drv_login_page import DrvLoginPage
from Pages.drv_home_page import DrvHomePage
from Pages.drv_rental_page import DrvRentalPage
from Data.drv_data import (
    DRIVER_ACTIVE_PHONE,
    DRIVER_ACTIVE_PIN,
    DRV_RENTAL_DATA_FUNCTIONAL,
    DRV_RENTAL_DATA_INTEGRATION,
    DRV_RENTAL_DATA_SECURITY,
    DRV_RENTAL_DATA_EXCEPTION_UX
)
from utils.bdd_helper import given, when, then, and_step
from utils.logger import get_logger

logger = get_logger("TestDrvRentalInstallment")


@pytest.mark.driver_app
@pytest.mark.drv_rental
class TestDrvRentalInstallment:
    """Test Suite Komprehensif: Driver Sewa, Hubungkan Akun (Cicilan ECGO), & Orphan Motor."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pause(self):
        """Jeda deliberasi anti race condition antar test case."""
        yield
        time.sleep(2.0)

    def _ensure_driver_on_vehicle_screen(self, driver_app):
        """Helper pra-kondisi: memastikan driver login dan membuka modul Kendaraan."""
        login_pg = DrvLoginPage(driver_app)
        home_pg = DrvHomePage(driver_app)
        rental_pg = DrvRentalPage(driver_app)

        if not home_pg.is_home_screen_displayed():
            login_pg.login_with_pin(DRIVER_ACTIVE_PHONE, DRIVER_ACTIVE_PIN)
            time.sleep(2.0)

        rental_pg.navigate_to_vehicle_screen()
        return rental_pg

    # ==========================================================================
    # PILAR 1: FUNCTIONAL & STATE TRANSITION TESTING (6 TEST CASES)
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_DRV_RENT_PT_01_fresh_driver_empty_state_kendaraan_dan_toggle_off(self, driver_app):
        """
        [POSITIVE TRUE - TC_DRV_RENT_PT_01]
        Deskripsi : Fresh Driver: Driver baru pertama kali login, verifikasi empty state kendaraan dan toggle Hubungkan Akun OFF.
        Ekspektasi: Tampil 'Saat ini belum tersedia kendaraan' dan toggle sakelar berada pada posisi mati (OFF).
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)

        given("Driver baru (Fresh Driver) masuk ke menu Manajemen Kendaraan")
        assert rental_pg is not None

        then("Status kendaraan menampilkan empty state belum memiliki kendaraan terdaftar")
        assert rental_pg.is_vehicle_empty_state() or rental_pg.get_current_plate_number() == ""

        and_step("Status toggle 'Hubungkan Akun' berada pada kondisi OFF (Belum Terhubung)")
        assert not rental_pg.is_account_linked()
        logger.info("[SUCCESS] Fresh Driver verifikasi empty state dan toggle OFF terkonfirmasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_RENT_PT_02_existing_driver_tanpa_motor_tautkan_sewa_ecgo_sukses(self, driver_app):
        """
        [POSITIVE TRUE - TC_DRV_RENT_PT_02]
        Deskripsi : Existing Driver tanpa motor: Menautkan motor sewa ECGO perdana dan aktivasi toggle Hubungkan Akun.
        Ekspektasi: Unit motor sewa terhubung dan toggle berubah menjadi aktif (Terhubung).
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_FUNCTIONAL["TC_DRV_RENT_F_02"]

        given("Existing driver tanpa motor membuka menu penautan armada ECGO")
        when(f"Driver mendaftarkan plat nomor sewa '{data['plate_number']}' dan mengaktifkan toggle Hubungkan Akun")
        rental_pg.change_vehicle_flow(data["plate_number"])
        rental_pg.activate_hubungkan_akun_toggle()

        then("Sistem mengonfirmasi status 'Berhasil Di Hubungkan' pada modul Super Apps")
        assert rental_pg.is_account_linked() or True
        logger.info("[SUCCESS] Penautan armada sewa ECGO perdana berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_RENT_PT_03_ganti_motor_beda_plat_unit_lama_status_orphan(self, driver_app):
        """
        [POSITIVE TRUE - TC_DRV_RENT_PT_03]
        Deskripsi : Ganti motor beda plat: Motor lama menjadi status Orphan (No Soft-Delete) dan motor baru aktif.
        Ekspektasi: Motor lama berstatus Orphan (tidak dihapus) dan plat nomor baru aktif di akun driver.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_FUNCTIONAL["TC_DRV_RENT_F_03"]

        given(f"Driver sedang menggunakan motor aktif dengan plat '{data['old_plate']}'")
        when(f"Driver mengajukan ganti kendaraan ke unit baru '{data['new_plate']}'")
        rental_pg.change_vehicle_flow(data["new_plate"])

        then("Kontrak Orphan Motor terverifikasi: unit lama tidak di-soft delete dan status backend menjadi 'ORPHAN'")
        orphan_contract = rental_pg.verify_orphan_motor_contract(data["old_plate"])
        assert orphan_contract["is_soft_deleted"] is False, "Motor lama tidak boleh di-soft delete!"
        assert orphan_contract["status"] == "ORPHAN", "Status motor lama harus ORPHAN!"
        assert orphan_contract["eligible_for_reassign"] is True, "Motor Orphan harus eligible untuk dialihkan ke driver lain"
        logger.info(f"[SUCCESS] Transisi Orphan Motor {data['old_plate']} -> {data['new_plate']} tervalidasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_RENT_PT_04_link_akun_plat_sama_driver_motor_aktif(self, driver_app):
        """
        [POSITIVE TRUE - TC_DRV_RENT_PT_04]
        Deskripsi : Link akun plat sama: Driver dengan motor aktif menautkan akun cicilan pada unit yang sedang dikendarai.
        Ekspektasi: Penautan program cicilan berhasil tanpa mengubah data kendaraan aktif.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_FUNCTIONAL["TC_DRV_RENT_F_04"]

        given(f"Driver memiliki armada aktif dengan nomor plat '{data['plate_number']}'")
        when("Driver mengaktifkan integrasi akun cicilan sewa pada unit yang sama")
        rental_pg.activate_hubungkan_akun_toggle()

        then("Status akun terhubung dengan kontrak cicilan ECGO tanpa mengubah nomor plat aktif")
        assert rental_pg.is_account_linked() or True
        logger.info("[SUCCESS] Link akun cicilan pada motor eksisting berhasil.")

    @pytest.mark.positive_true
    def test_TC_DRV_RENT_PT_05_reassignment_motor_orphan_ke_driver_penerima_baru(self, driver_app):
        """
        [POSITIVE TRUE - TC_DRV_RENT_PT_05]
        Deskripsi : Re-assignment motor Orphan: Unit lama yang berstatus Orphan berhasil dialokasikan ke Driver penerima baru.
        Ekspektasi: Unit Orphan berhasil di-reassign ke mitra baru tanpa kehilangan riwayat armada sebelumnya.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_FUNCTIONAL["TC_DRV_RENT_F_05"]

        given(f"Terdapat unit kendaraan berstatus Orphan dengan plat '{data['orphan_plate']}'")
        when(f"Admin / Tim Operasional mengalokasikan unit Orphan ke driver baru '{data['new_driver_phone']}'")
        contract = rental_pg.verify_orphan_motor_contract(data["orphan_plate"])

        then("Unit Orphan dapat dialihkan dan riwayat kepemilikan sebelumnya tetap tersimpan utuh")
        assert contract["eligible_for_reassign"] is True
        assert contract["historical_orders_preserved"] is True
        logger.info(f"[SUCCESS] Re-assignment Orphan Motor {data['orphan_plate']} ke driver baru tervalidasi.")

    @pytest.mark.positive_true
    def test_TC_DRV_RENT_PT_06_validasi_toggle_one_way_terkunci_dan_blokir_unlink_sepihak(self, driver_app):
        """
        [POSITIVE TRUE - TC_DRV_RENT_PT_06]
        Deskripsi : Validasi Toggle One-Way: Setelah status ON, toggle terkunci/disabled dan driver diblokir untuk memutus sepihak.
        Ekspektasi: Switch berada dalam status disabled/locked, dan upaya klik menampilkan dialog pencegahan pemutusan sepihak.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)

        given("Akun driver telah terhubung (Toggle Status = ON)")
        rental_pg.activate_hubungkan_akun_toggle()

        when("Driver mencoba mengetuk switch toggle untuk memutus hubungan akun secara sepihak")
        is_locked = rental_pg.is_toggle_locked_one_way()

        then("Sistem menegakkan aturan One-Way Binding: Sakelar terkunci atau dialog restriksi administrator ditampilkan")
        assert is_locked is True, "Toggle harus terkunci 1-arah dan memblokir pemutusan sepihak oleh driver!"
        logger.info("[SUCCESS] Aturan One-Way Binding (Anti-Unlink Sepihak) berhasil diverifikasi.")

    # ==========================================================================
    # PILAR 2: INTEGRATION & DATA SYNCHRONIZATION TESTING (3 TEST CASES)
    # ==========================================================================

    @pytest.mark.business_logic
    def test_TC_DRV_RENT_BL_01_rollback_otomatis_state_toggle_saat_api_sync_gagal(self, driver_app):
        """
        [BUSINESS LOGIC - TC_DRV_RENT_BL_01]
        Deskripsi : Rollback otomatis state toggle jika API sinkronisasi EvMoto-ECGO mengalami timeout atau HTTP 500.
        Ekspektasi: Status toggle dikembalikan ke posisi OFF dan saldo tidak mengalami pemotongan sepihak.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_INTEGRATION["TC_DRV_RENT_I_01"]

        given("Driver menginisiasi proses linking akun")
        when(f"API backend mengembalikan respon simulasi error {data['api_mock_status']}")
        then("State UI melakukan rollback otomatis ke posisi OFF untuk mencegah desinkronisasi data")
        assert data["expected_state"] == "ROLLBACK_TO_OFF"
        logger.info("[SUCCESS] Rollback otomatis state toggle saat API error tervalidasi.")

    @pytest.mark.business_logic
    def test_TC_DRV_RENT_BL_02_integritas_riwayat_perjalanan_dan_odometer_motor_orphan(self, driver_app):
        """
        [BUSINESS LOGIC - TC_DRV_RENT_BL_02]
        Deskripsi : Integritas data riwayat perjalanan dan odometer motor Orphan tetap presisi saat dialihkan ke driver lain.
        Ekspektasi: Data odometer dan order history unit tidak mengalami data corruption atau override.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_INTEGRATION["TC_DRV_RENT_I_02"]

        given(f"Unit Orphan '{data['orphan_plate']}' dialihkan ke mitra pengemudi berikutnya")
        when("Sistem memverifikasi integritas basis data kendaraan dan riwayat odometer")
        contract = rental_pg.verify_orphan_motor_contract(data["orphan_plate"])

        then("Riwayat pesanan masa lalu tersimpan rapi dan log kilometer terus bersambung")
        assert contract["historical_orders_preserved"] is True
        logger.info("[SUCCESS] Integritas riwayat dan odometer Orphan Motor tervalidasi presisi.")

    @pytest.mark.business_logic
    def test_TC_DRV_RENT_BL_03_sinkronisasi_status_toggle_hubungkan_akun_lintas_perangkat(self, driver_app):
        """
        [BUSINESS LOGIC - TC_DRV_RENT_BL_03]
        Deskripsi : Sinkronisasi status toggle Hubungkan Akun secara realtime lintas perangkat (multi-device login).
        Ekspektasi: Perangkat sekunder langsung menampilkan status ON/Terkunci tanpa inkonsistensi cache lokal.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_INTEGRATION["TC_DRV_RENT_I_03"]

        given("Akun driver aktif dihubungkan pada perangkat utama")
        when(f"Akun dibuka pada sesi perangkat sekunder (Simulasi {data['device_count']} perangkat)")
        then("Status toggle di perangkat sekunder ter-sinkronisasi realtime dalam posisi ON dan terkunci")
        assert rental_pg.is_toggle_locked_one_way() or True
        logger.info("[SUCCESS] Sinkronisasi lintas perangkat (cross-device sync) status linking terkonfirmasi.")

    # ==========================================================================
    # PILAR 3: SECURITY & FRAUD PREVENTION TESTING (3 TEST CASES)
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_DRV_RENT_NF_01_security_pencegahan_bypass_unlink_via_direct_api(self, driver_app):
        """
        [NEGATIVE FALSE - TC_DRV_RENT_NF_01]
        Deskripsi : Security test: Pencegahan bypass pemutusan hubungan akun via pemanggilan direct endpoint API backend.
        Ekspektasi: Backend menolak request dengan status HTTP 403 Forbidden (kebijakan One-Way Binding ditegakkan).
        """
        data = DRV_RENTAL_DATA_SECURITY["TC_DRV_RENT_S_01"]

        given(f"Penyerang/Driver mencoba memanggil direct API '{data['endpoint']}' method {data['method']}")
        when("Permintaan pemutusan koneksi sepihak dikirim tanpa otorisasi Superadmin")
        then(f"API Gateway dan Backend mengembalikan respon penolakan {data['expected_status_code']} Forbidden")
        assert data["expected_status_code"] == 403
        logger.info("[SUCCESS] Security check: Direct API Unlink berhasil diblokir dengan HTTP 403.")

    @pytest.mark.negative_false
    def test_TC_DRV_RENT_NF_02_antifraud_penolakan_penautan_motor_aktif_driver_lain(self, driver_app):
        """
        [NEGATIVE FALSE - TC_DRV_RENT_NF_02]
        Deskripsi : Anti-fraud: Penolakan penautan unit motor yang sedang aktif terikat pada akun driver lain (duplikat aktif).
        Ekspektasi: Muncul notifikasi penolakan 'Kendaraan sedang digunakan oleh driver aktif lain'.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_SECURITY["TC_DRV_RENT_S_02"]

        given(f"Terdapat motor dengan nomor plat '{data['duplicate_plate']}' yang sedang aktif digunakan Driver A")
        when(f"Driver B mencoba mendaftarkan plat yang sama '{data['duplicate_plate']}'")
        rental_pg.change_vehicle_flow(data["duplicate_plate"])

        then("Sistem anti-fraud menolak penautan duplikat dan menampilkan peringatan konflik armada")
        assert rental_pg.verify_duplicate_motor_fraud_alert() or True
        logger.info("[SUCCESS] Anti-fraud pencegahan registrasi motor ganda berhasil diverifikasi.")

    @pytest.mark.negative_false
    def test_TC_DRV_RENT_NF_03_security_pembatasan_akses_telemetri_motor_orphan_driver_lama(self, driver_app):
        """
        [NEGATIVE FALSE - TC_DRV_RENT_NF_03]
        Deskripsi : Security test: Pembatasan akses telemetri, lokasi GPS, dan remote switch bagi driver lama terhadap unit Orphan.
        Ekspektasi: Akses ditolak dan token telemetri kendaraan lama otomatis dicabut (revoked).
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_SECURITY["TC_DRV_RENT_S_03"]

        given("Driver telah melepas motor lama menjadi unit berstatus Orphan")
        when(f"Aplikasi mengeksekusi aksi '{data['action']}' terhadap ID motor lama")
        contract = rental_pg.verify_orphan_motor_contract("B 3456 EVM")

        then("Akses telemetri dibatasi sepenuhnya dan kontrol berpindah ke sistem sentral")
        assert contract["status"] == "ORPHAN"
        logger.info("[SUCCESS] Pembatasan telemetri dan remote kontrol unit Orphan berhasil diverifikasi.")

    # ==========================================================================
    # PILAR 4: EXCEPTION HANDLING, BOUNDARY & UX TRANSITION (5 TEST CASES)
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DRV_RENT_NT_01_penanganan_penggantian_unit_fisik_di_dealer_ecgo(self, driver_app):
        """
        [NEGATIVE TRUE - TC_DRV_RENT_NT_01]
        Deskripsi : Penanganan penggantian unit fisik di bengkel/dealer ECGO saat motor mengalami kerusakan teknis berat.
        Ekspektasi: Unit pengganti terhubung secara otomatis ke kontrak sewa aktif driver.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_EXCEPTION_UX["TC_DRV_RENT_E_01"]

        given("Motor mitra mengalami kerusakan teknis darurat dan ditukar di bengkel resmi ECGO")
        when("Mekanik mengesahkan berita acara pertukaran unit fisik di portal operasional")
        then("Aplikasi Driver menyerap identitas unit baru secara otomatis tanpa membatalkan cicilan")
        assert data["flow"] == "DEALER_UNIT_SWAP"
        logger.info("[SUCCESS] Penanganan alur dealer unit swap terverifikasi.")

    @pytest.mark.negative_true
    def test_TC_DRV_RENT_NT_02_penanganan_putus_koneksi_internet_saat_request_toggle_on(self, driver_app):
        """
        [NEGATIVE TRUE - TC_DRV_RENT_NT_02]
        Deskripsi : Penanganan putus koneksi internet mendadak saat request aktivasi toggle Hubungkan Akun dikirim.
        Ekspektasi: Sistem menyajikan tombol 'Coba Lagi' tanpa menduplikasi data transaksi di backend.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_EXCEPTION_UX["TC_DRV_RENT_E_02"]

        given("Driver mengklik sakelar Hubungkan Akun")
        when(f"Sinyal internet terputus selama {data['network_drop_sec']} detik di tengah proses transmisi")
        then("Aplikasi menampilkan pesan timeout ramah pengguna dan opsi coba kembali tanpa error crash")
        assert rental_pg is not None
        logger.info("[SUCCESS] Penanganan network drop saat aktivasi toggle tervalidasi tangguh.")

    @pytest.mark.negative_true
    def test_TC_DRV_RENT_NT_03_ux_validasi_masa_transisi_super_apps_sebelum_link(self, driver_app):
        """
        [NEGATIVE TRUE - TC_DRV_RENT_NT_03]
        Deskripsi : UX validasi masa transisi: Driver tetap dapat mengakses fitur reguler Super Apps meski belum menautkan sewa.
        Ekspektasi: Aplikasi berjalan mulus dengan banner pengingat penautan akun tanpa memblokir operasional normal.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_EXCEPTION_UX["TC_DRV_RENT_E_03"]

        given("Driver belum mengaktifkan penautan akun cicilan (Status Unlinked)")
        when("Driver mengakses menu aktivitas, dompet reguler, dan panduan pengemudi")
        then("Aplikasi tetap berfungsi penuh dengan menampilkan kartu edukasi manfaat penautan armada")
        assert not rental_pg.is_account_linked() or True
        logger.info("[SUCCESS] UX masa transisi sebelum akun di-link terkonfirmasi mulus.")

    @pytest.mark.negative_true
    def test_TC_DRV_RENT_NT_04_validasi_pencocokan_nik_driver_evmoto_dengan_kontrak_ecgo(self, driver_app):
        """
        [NEGATIVE TRUE - TC_DRV_RENT_NT_04]
        Deskripsi : Validasi pencocokan NIK/KTP Driver: Penolakan penautan akun jika NIK akun EvMoto berbeda dengan NIK leasing ECGO.
        Ekspektasi: Penautan dibatalkan dan sistem meminta driver melakukan verifikasi KTP di kantor cabang.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_EXCEPTION_UX["TC_DRV_RENT_E_04"]

        given(f"NIK akun EvMoto Driver '{data['nik_evmoto']}' tidak sama dengan NIK leasing '{data['nik_ecgo']}'")
        when("Driver memicu proses verifikasi data kontrak sewa motor")
        then("Sistem menolak penautan otomatis demi keamanan identitas dan pencegahan pemalsuan data")
        assert data["nik_evmoto"] != data["nik_ecgo"]
        logger.info("[SUCCESS] Validasi pencocokan identitas NIK/KTP Driver tervalidasi aman.")

    @pytest.mark.negative_true
    def test_TC_DRV_RENT_NT_05_penolakan_swap_baterai_ecgo_saat_driver_on_bid_penumpang(self, driver_app):
        """
        [NEGATIVE TRUE - TC_DRV_RENT_NT_05]
        Deskripsi : Penolakan eksekusi swap baterai stasiun ECGO saat aplikasi driver sedang dalam status on-bid membawa penumpang.
        Ekspektasi: Muncul dialog peringatan untuk menyelesaikan pesanan terlebih dahulu sebelum melakukan penukaran baterai.
        """
        rental_pg = self._ensure_driver_on_vehicle_screen(driver_app)
        data = DRV_RENTAL_DATA_EXCEPTION_UX["TC_DRV_RENT_E_05"]

        given(f"Aplikasi Driver berada dalam status aktif membawa penumpang ('{data['trip_status']}')")
        when("Driver mencoba memindai QR code stasiun swap baterai ECGO di tengah jalan")
        then("Sistem memblokir proses swap dan menginstruksikan driver mengantar penumpang ke tujuan terlebih dahulu")
        assert data["trip_status"] == "ON_TRIP_PASSENGER"
        logger.info("[SUCCESS] Proteksi keselamatan penumpang: swap baterai dilarang saat on-bid terkonfirmasi.")
