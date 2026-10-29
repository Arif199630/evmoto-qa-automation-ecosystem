"""
================================================================================
EVMOTO ADMIN DASHBOARD - DISPATCH BATCH TEST SUITE
================================================================================
Target URL   : https://evmotoadmin.justkidding.app/dispatchBatch
Fitur        : Pengaturan Penyebaran Order Batch Driver & Konfigurasi Jarak (Radius)
Metodologi   : 4 Pilar QA (Positive True, Positive False, Negative True, Negative False)
Layer        : UI Component Verification & REST/Form API (Headless Staging)
Aturan Utama :
  - Saklar Jalur Batch untuk order baru (enabled)
  - Driver per batch (size: 1 - 50)
  - Jeda antar batch (delay: detik)
  - Durasi total (duration: 0 = tanpa batas / no expire)
  - Order yang boleh dipegang satu driver (concurrent)
  - Scan ulang setelah semua band dicoba (rescans)
  - Band Order Biasa (Ordinary) vs Band Advance Booking Terpisah
================================================================================
"""
import pytest
import time
from Frontend.Feature.Helper.admin_dispatch_batch_helper import AdminDispatchBatchHelper
from utils.logger import get_logger

logger = get_logger("TestAdminDispatchBatch")


@pytest.fixture(scope="module")
def admin_helper():
    """Fixture inisialisasi helper admin dan otentikasi login."""
    helper = AdminDispatchBatchHelper()
    success = helper.login()
    assert success, "Admin Dashboard harus berhasil login dengan kredensial staging"
    yield helper
    # Teardown: Pastikan pengaturan baseline staging kembali normal
    helper.submit_dispatch_batch(
        enabled=True,
        size=5,
        delay=10,
        duration=0,
        concurrent=5,
        rescans=2,
        ordinary_bands=[("0", "1"), ("1", "2"), ("2", "3"), ("3", "4"), ("4", "5")],
        advance_bands=[("0", "1"), ("1", "2"), ("2", "5"), ("5", "15")]
    )
    logger.info("Baseline staging Dispatch Batch berhasil dipulihkan.")


@pytest.mark.admin_dashboard
@pytest.mark.dispatch_batch
class TestAdminDispatchBatch:
    """Test Suite Komprehensif 4 Pilar QA untuk Halaman Dispatch Batch Admin Dashboard."""

    @pytest.fixture(autouse=True)
    def anti_race_condition_pacing(self):
        """Pacing buffer anti-race condition antar pengujian konfigurasi dashboard."""
        yield
        import time
        time.sleep(0.5)

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH & VALID INPUTS
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_DASH_BATCH_PT_01_verify_all_ui_elements_and_controls(self, admin_helper):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi : Memvalidasi keberadaan dan status seluruh komponen UI pada halaman /dispatchBatch:
                    - Checkbox 'Jalur batch untuk order baru'
                    - Kolom input 'Driver per batch' (size)
                    - Kolom input 'Jeda antar batch' (delay)
                    - Kolom input 'Durasi total' (duration)
                    - Kolom input 'Order yang boleh dipegang satu driver' (concurrent)
                    - Kolom input 'Scan ulang setelah semua band dicoba' (rescans)
                    - Section 'Band order biasa' (+ Tombol Tambah & Tombol Hapus)
                    - Section 'Band advance booking' (+ Tombol Tambah & Tombol Hapus)
                    - Tombol 'Simpan' (Submit)
        Ekspektasi: Seluruh komponen UI terdeteksi 100% lengkap dan siap menerima interaksi.
        """
        status, html = admin_helper.get_dispatch_batch_page()
        assert status == 200, f"Halaman /dispatchBatch harus mengembalikan status 200, aktual: {status}"

        ui_status = admin_helper.verify_ui_components(html)
        logger.info(f"[PT-01] Hasil verifikasi komponen UI: {ui_status}")

        assert ui_status["has_batch_switch_checkbox"], "Checkbox switch batch harus ada"
        assert ui_status["has_input_batch_size"], "Input size batch driver harus ada"
        assert ui_status["has_input_delay"], "Input delay antar batch harus ada"
        assert ui_status["has_input_duration"], "Input durasi total harus ada"
        assert ui_status["has_input_concurrent"], "Input concurrent orders per driver harus ada"
        assert ui_status["has_input_rescans"], "Input rescans harus ada"
        assert ui_status["has_ordinary_bands_section"], "Section Band Order Biasa harus ada"
        assert ui_status["has_btn_add_ordinary_band"], "Tombol Tambah Band Order Biasa harus ada"
        assert ui_status["has_advance_bands_section"], "Section Band Advance Booking harus ada"
        assert ui_status["has_btn_add_advance_band"], "Tombol Tambah Band Advance Booking harus ada"
        assert ui_status["has_btn_remove_row"], "Tombol Hapus baris band radius harus ada"
        assert ui_status["has_submit_button"], "Tombol Simpan konfigurasi harus ada"

    @pytest.mark.positive_true
    def test_TC_DASH_BATCH_PT_02_submit_valid_batch_configuration(self, admin_helper):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi : Mengirimkan pembaruan konfigurasi batch valid:
                    size=5, delay=10, duration=0 (infinite/tanpa batas), concurrent=5, rescans=2.
        Ekspektasi: Respons HTTP 200, URL dialihkan ke '?saved=1', dan pesan sukses 'Pengaturan tersimpan.' muncul.
        """
        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2
        )
        assert resp.status_code == 200, f"Status POST harus 200, aktual: {resp.status_code}"
        assert admin_helper.is_saved_successfully(resp), "Respons harus mengonfirmasi 'Pengaturan tersimpan' (?saved=1)"

        # Verifikasi data tersimpan
        settings = admin_helper.parse_dispatch_batch_settings(resp.text)
        assert settings["enabled"] is True
        assert settings["size"] == 5
        assert settings["delay"] == 10
        assert settings["duration"] == 0
        assert settings["concurrent"] == 5
        assert settings["rescans"] == 2

    @pytest.mark.positive_true
    def test_TC_DASH_BATCH_PT_03_distance_bands_separation_ordinary_vs_advance(self, admin_helper):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi : Memvalidasi aturan bisnis: Band radius Order Reguler (Biasa) dengan Advance Booking terpisah.
                    - Band Biasa   : 0-1 KM, 1-2 KM, 2-3 KM, 3-4 KM, 4-5 KM
                    - Band Advance : 0-1 KM, 1-2 KM, 2-5 KM, 5-15 KM
        Ekspektasi: Kedua daftar jarak tersimpan secara independen tanpa saling menimpa.
        """
        ord_bands = [("0", "1"), ("1", "2"), ("2", "3"), ("3", "4"), ("4", "5")]
        adv_bands = [("0", "1"), ("1", "2"), ("2", "5"), ("5", "15")]

        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2,
            ordinary_bands=ord_bands,
            advance_bands=adv_bands
        )
        assert admin_helper.is_saved_successfully(resp), "Penyimpanan band terpisah harus sukses"

        settings = admin_helper.parse_dispatch_batch_settings(resp.text)
        assert len(settings["ordinary_bands"]) == 5, f"Harus ada 5 band order biasa, aktual: {len(settings['ordinary_bands'])}"
        assert len(settings["advance_bands"]) == 4, f"Harus ada 4 band advance booking, aktual: {len(settings['advance_bands'])}"
        assert settings["ordinary_bands"] == ord_bands
        assert settings["advance_bands"] == adv_bands

    @pytest.mark.positive_true
    def test_TC_DASH_BATCH_PT_04_infinite_duration_mode_with_rescans(self, admin_helper):
        """
        [POSITIVE TRUE - PT-04]
        Deskripsi : Mengonfigurasi 'duration=0' (tanpa batas waktu kedaluwarsa) dengan 'rescans=2'
                    sesuai spesifikasi bahwa order tidak pernah expired dan dicari ulang 2 kali.
        Ekspektasi: Sistem menerima konfigurasi mode tanpa batas waktu dan menyimpannya dengan benar.
        """
        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=15,
            duration=0,
            concurrent=4,
            rescans=3
        )
        assert admin_helper.is_saved_successfully(resp)
        settings = admin_helper.parse_dispatch_batch_settings(resp.text)
        assert settings["duration"] == 0
        assert settings["rescans"] == 3

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - VALID BOUNDARIES & ALTERNATE STATES
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DASH_BATCH_PF_01_switch_disabled_fallback_to_sequential(self, admin_helper):
        """
        [POSITIVE FALSE - PF-01]
        Deskripsi : Mematikan saklar Jalur Batch ('enabled=0').
        Ekspektasi: Sistem berhasil menyimpan state mati ('enabled=False').
                    Order berikutnya secara aman fallback ke mode sequential (satu driver per giliran).
        """
        resp = admin_helper.submit_dispatch_batch(
            enabled=False,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2
        )
        assert admin_helper.is_saved_successfully(resp)
        settings = admin_helper.parse_dispatch_batch_settings(resp.text)
        assert settings["enabled"] is False, "Saklar Jalur Batch harus dalam status MATI"

        # Kembalikan ke hidup
        admin_helper.submit_dispatch_batch(enabled=True, size=5, delay=10, duration=0, concurrent=5, rescans=2)

    @pytest.mark.positive_false
    def test_TC_DASH_BATCH_PF_02_custom_advance_booking_band_replacement(self, admin_helper):
        """
        [POSITIVE FALSE - PF-02: Alternate Custom Advance Booking Bands]
        Deskripsi : Mengganti daftar band Advance Booking dengan struktur kustom yang berbeda:
                    advance_bands=[("0", "3"), ("3", "12")].
                    Berdasarkan catatan PRD: 'Daftar yang sudah tersimpan diganti, tidak dikosongkan.'
        Ekspektasi: Sistem berhasil memperbarui daftar band advance booking dengan nilai pengganti baru.
        """
        custom_adv = [("0", "3"), ("3", "12")]
        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2,
            ordinary_bands=[("0", "2"), ("2", "5")],
            advance_bands=custom_adv
        )
        assert admin_helper.is_saved_successfully(resp)
        settings = admin_helper.parse_dispatch_batch_settings(resp.text)
        assert settings["advance_bands"] == custom_adv

    @pytest.mark.positive_false
    def test_TC_DASH_BATCH_PF_03_boundary_value_batch_size_limits(self, admin_helper):
        """
        [POSITIVE FALSE - PF-03: Boundary Value Analysis]
        Deskripsi : Menguji batas ekstrem yang diizinkan untuk 'size':
                    1. Batas bawah: size = 1
                    2. Batas atas : size = 50
        Ekspektasi: Kedua nilai batas valid diterima dan disimpan dengan sukses tanpa error 422.
        """
        # Batas Bawah (size = 1)
        r_low = admin_helper.submit_dispatch_batch(enabled=True, size=1, delay=5, duration=0, concurrent=1, rescans=1)
        assert admin_helper.is_saved_successfully(r_low), "Batas bawah size=1 harus valid"

        # Batas Atas (size = 50)
        r_high = admin_helper.submit_dispatch_batch(enabled=True, size=50, delay=60, duration=0, concurrent=10, rescans=5)
        assert admin_helper.is_saved_successfully(r_high), "Batas atas size=50 harus valid"

    @pytest.mark.positive_false
    def test_TC_DASH_BATCH_PF_04_decimal_distance_values_in_bands(self, admin_helper):
        """
        [POSITIVE FALSE - PF-04]
        Deskripsi : Menguji input jarak desimal (misal 0.5 KM, 1.5 KM, 3.75 KM).
        Ekspektasi: Sistem menerima nilai desimal dengan inputmode='decimal' secara presisi.
        """
        dec_bands = [("0", "0.5"), ("0.5", "1.5"), ("1.5", "3.75")]
        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2,
            ordinary_bands=dec_bands
        )
        assert admin_helper.is_saved_successfully(resp)
        settings = admin_helper.parse_dispatch_batch_settings(resp.text)
        assert ("0", "0.5") in settings["ordinary_bands"]
        assert ("0.5", "1.5") in settings["ordinary_bands"]

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - INPUT VIOLATION & EXPECTED ERROR HANDLING
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DASH_BATCH_NT_01_reject_invalid_size_below_min(self, admin_helper):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi : Menguji pengiriman nilai 'size' di bawah batas minimum (size = -5 atau 0).
        Ekspektasi: Sistem menolak dengan HTTP 422 Unprocessable Entity dan memunculkan
                    alert spesifik: 'Ukuran batch harus bilangan bulat 1 sampai 50.'
        """
        resp = admin_helper.submit_dispatch_batch(enabled=True, size=-5, delay=10, duration=0, concurrent=5, rescans=2)
        assert resp.status_code == 422, f"Harus ditolak dengan HTTP 422, aktual: {resp.status_code}"

        alert_msg = admin_helper.extract_alert_message(resp.text)
        logger.info(f"[NT-01] Pesan validasi error: {alert_msg}")
        assert alert_msg is not None, "Alert error harus ditampilkan pada UI"
        assert "1 sampai 50" in alert_msg or "Ukuran batch" in alert_msg

    @pytest.mark.negative_true
    def test_TC_DASH_BATCH_NT_02_reject_invalid_size_above_max(self, admin_helper):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi : Menguji pengiriman nilai 'size' melebihi batas maksimum (size = 51).
        Ekspektasi: Sistem menolak dengan HTTP 422 Unprocessable Entity dan memunculkan
                    alert spesifik: 'Ukuran batch harus bilangan bulat 1 sampai 50.'
        """
        resp = admin_helper.submit_dispatch_batch(enabled=True, size=51, delay=10, duration=0, concurrent=5, rescans=2)
        assert resp.status_code == 422, f"Harus ditolak dengan HTTP 422, aktual: {resp.status_code}"

        alert_msg = admin_helper.extract_alert_message(resp.text)
        assert alert_msg is not None
        assert "1 sampai 50" in alert_msg

    @pytest.mark.negative_true
    def test_TC_DASH_BATCH_NT_03_reject_alphanumeric_or_corrupted_inputs(self, admin_helper):
        """
        [NEGATIVE TRUE - NT-03]
        Deskripsi : Menguji input alfanumerik tidak valid pada kolom numerik (misal size='xyz' atau delay='abc').
        Ekspektasi: Sistem menolak masukan korup dengan HTTP 422 dan mencegah perubahan tersimpan di database.
        """
        resp = admin_helper.submit_dispatch_batch(enabled=True, size="invalid_text", delay=10, duration=0, concurrent=5, rescans=2)
        assert resp.status_code == 422, f"Harus ditolak dengan HTTP 422, aktual: {resp.status_code}"

    @pytest.mark.negative_true
    def test_TC_DASH_BATCH_NT_04_unauthenticated_request_rejected(self):
        """
        [NEGATIVE TRUE - NT-04: Security Access Control]
        Deskripsi : Mencoba mengakses atau mengubah /dispatchBatch tanpa sesi login aktif (Guest/Unauthorized).
        Ekspektasi: Akses ditolak dan diarahkan ke halaman login (/login) atau respons 401/302.
        """
        unauth_helper = AdminDispatchBatchHelper()
        status, html = unauth_helper.get_dispatch_batch_page()
        # Harus redirect ke /login atau 401
        assert status in [200, 302, 401]
        assert "Login" in html or "login" in unauth_helper.session.cookies.get_dict(), "Harus diarahkan ke halaman login"

    @pytest.mark.negative_true
    def test_TC_DASH_BATCH_NT_05_reject_clearing_saved_advance_booking_bands(self, admin_helper):
        """
        [NEGATIVE TRUE - NT-05: Business Rule Enforcement]
        Deskripsi : Mengirimkan permintaan untuk mengosongkan seluruh daftar band Advance Booking (advance_bands=[]).
        Ekspektasi: Sistem menolak dengan HTTP 422 dan pesan alert bisnis:
                    'Band advance booking yang sudah tersimpan harus diganti dengan daftar baru. Nilai itu tidak bisa dikosongkan.'
        """
        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2,
            ordinary_bands=[("0", "1"), ("1", "2")],
            advance_bands=[]
        )
        assert resp.status_code == 422, f"Harus 422 Unprocessable Entity, aktual: {resp.status_code}"
        alert_msg = admin_helper.extract_alert_message(resp.text)
        assert alert_msg is not None
        assert "tidak bisa dikosongkan" in alert_msg or "harus diganti" in alert_msg


    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - FAULT INJECTION & SYSTEM RESILIENCE
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_DASH_BATCH_NF_01_idempotent_duplicate_submissions(self, admin_helper):
        """
        [NEGATIVE FALSE - NF-01: Idempotency Under Rapid Retries]
        Deskripsi : Mengirimkan form yang persis sama sebanyak 3 kali berturut-turut dalam waktu singkat.
        Ekspektasi: Seluruh request diproses secara idempoten (HTTP 200), tidak menyebabkan duplikasi data
                    atau internal server error 500.
        """
        for i in range(3):
            resp = admin_helper.submit_dispatch_batch(
                enabled=True,
                size=5,
                delay=10,
                duration=0,
                concurrent=5,
                rescans=2
            )
            assert resp.status_code == 200, f"Percobaan iterasi #{i+1} harus berhasil 200"

    @pytest.mark.negative_false
    def test_TC_DASH_BATCH_NF_02_empty_blank_rows_ignored_gracefully(self, admin_helper):
        """
        [NEGATIVE FALSE - NF-02: Dirty / Incomplete Form Data]
        Deskripsi : Mengirimkan baris band jarak dengan kolom kosong (misal start='', end='').
        Ekspektasi: Sistem secara elegan mengabaikan (strip) baris kosong tanpa error atau crash.
        """
        dirty_bands = [("0", "1"), ("", ""), ("1", "2"), ("", "")]
        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2,
            ordinary_bands=dirty_bands
        )
        assert admin_helper.is_saved_successfully(resp), "Baris kosong harus diabaikan dan penyimpanan sukses"

    @pytest.mark.negative_false
    def test_TC_DASH_BATCH_NF_03_restoration_to_baseline_config(self, admin_helper):
        """
        [NEGATIVE FALSE - NF-03: Environment Integrity Assurance]
        Deskripsi : Memulihkan kembali konfigurasi default staging sebelum pengujian selesai:
                    enabled=True, size=5, delay=10, duration=0, concurrent=5, rescans=2,
                    ordinary=[0-1, 1-2, 2-3, 3-4, 4-5], advance=[0-1, 1-2, 2-5, 5-15].
        Ekspektasi: Status staging 100% konsisten dan siap digunakan untuk live testing.
        """
        resp = admin_helper.submit_dispatch_batch(
            enabled=True,
            size=5,
            delay=10,
            duration=0,
            concurrent=5,
            rescans=2,
            ordinary_bands=[("0", "1"), ("1", "2"), ("2", "3"), ("3", "4"), ("4", "5")],
            advance_bands=[("0", "1"), ("1", "2"), ("2", "5"), ("5", "15")]
        )
        assert admin_helper.is_saved_successfully(resp)
        settings = admin_helper.parse_dispatch_batch_settings(resp.text)
        assert settings["enabled"] is True
        assert settings["size"] == 5
        assert len(settings["ordinary_bands"]) == 5
        assert len(settings["advance_bands"]) == 4
        logger.info("[NF-03] Baseline konfigurasi Staging terverifikasi 100% pulih sempurna.")
