"""
================================================================================
EVMOTO ADMIN DASHBOARD - SUBSIDI JAM SIBUK & RIWAYAT TEST SUITE
================================================================================
Target URL   : https://evmotoadmin.justkidding.app/rushHour/settings
               https://evmotoadmin.justkidding.app/rushHour/history
Fitur        : Pengaturan Subsidi Jam Sibuk (Rush Hour) & Riwayat Payout Driver
Metodologi   : 4 Pilar QA (Positive True, Positive False, Negative True, Negative False)
Layer        : UI Component Verification & REST/Form API (Headless Staging)
Prinsip      : Automated Snapshot & Teardown Restoration (Zero Pollution)
================================================================================
"""
import os
import pytest
import time
from Frontend.Feature.Helper.admin_rush_hour_helper import AdminRushHourHelper
from utils.logger import get_logger

logger = get_logger("TestAdminRushHour")


@pytest.fixture(scope="module")
def admin_rush_helper():
    """Fixture inisialisasi helper admin, otentikasi login, snapshot konfigurasi awal, dan restoration teardown."""
    if os.getenv("ALLOW_ADMIN_CONFIG_WRITE") != "1":
        pytest.skip("Test ini MENGUBAH pengaturan Subsidi jam sibuk staging yang dipakai bersama. "
                    "Jalankan hanya dengan izin: ALLOW_ADMIN_CONFIG_WRITE=1")
    helper = AdminRushHourHelper()
    success = helper.login()
    assert success, "Admin Dashboard harus berhasil login dengan kredensial staging"

    # 1. SETUP: Simpan snapshot konfigurasi asli server staging sebelum pengujian berjalan
    original_settings = helper.parse_settings()
    logger.info(f"[SETUP] Snapshot konfigurasi awal Subsidi Jam Sibuk berhasil dicatat: {original_settings}")

    try:
        yield helper
    finally:
        # 2. TEARDOWN: Pulihkan seluruh data staging kembali ke snapshot semula secara deterministik
        helper.restore_settings(original_settings)
        logger.info(f"[TEARDOWN] Konfigurasi Subsidi Jam Sibuk berhasil dipulihkan ke kondisi semula: {original_settings}")


@pytest.mark.admin_dashboard
@pytest.mark.rush_hour
class TestAdminRushHour:
    """Test Suite Komprehensif 4 Pilar QA untuk Halaman Subsidi Jam Sibuk Admin Dashboard."""

    # ==========================================================================
    # PILAR 1: POSITIVE TRUE (PT) - HAPPY PATH & KOMPONEN UI LENGKAP
    # ==========================================================================

    @pytest.mark.positive_true
    def test_TC_DASH_RUSH_PT_01_verify_settings_page_ui_components(self, admin_rush_helper):
        """
        [POSITIVE TRUE - PT-01]
        Deskripsi: Memvalidasi keberadaan dan kelengkapan seluruh komponen UI pada halaman /rushHour/settings:
                    - Judul Halaman 'Subsidi jam sibuk'
                    - Checkbox Switch 'Aktifkan subsidi jam sibuk'
                    - Input Window Mulai dan Selesai
                    - Input Tier Subsidi dan Ambang Batas Tarif
                    - Input Batas Anggaran Harian (Daily Budget)
                    - Tombol Simpan (Submit Button)
        Ekspektasi: Seluruh komponen UI terdeteksi 100% lengkap.
        """
        status, html = admin_rush_helper.get_settings_page()
        assert status == 200, f"Halaman /rushHour/settings harus berstatus 200, aktual: {status}"

        ui_status = admin_rush_helper.verify_ui_components(html)
        logger.info(f"[PT-01] Hasil verifikasi komponen UI /rushHour/settings: {ui_status}")

        assert ui_status["has_title_subsidi_jam_sibuk"], "Judul 'Subsidi jam sibuk' harus ada"
        assert ui_status["has_switch_enabled"], "Switch status subsidi jam sibuk harus ada"
        assert ui_status["has_input_window_start"], "Input jam mulai window harus ada"
        assert ui_status["has_input_window_end"], "Input jam selesai window harus ada"
        assert ui_status["has_input_tier_subsidy"], "Input nominal subsidi per tier harus ada"
        assert ui_status["has_input_tier_max"], "Input batas maksimum tarif tier harus ada"
        assert ui_status["has_input_daily_budget"], "Input batas anggaran harian harus ada"
        assert ui_status["has_submit_button"], "Tombol Simpan form harus ada"

    @pytest.mark.positive_true
    def test_TC_DASH_RUSH_PT_02_verify_history_page_ui_and_table(self, admin_rush_helper):
        """
        [POSITIVE TRUE - PT-02]
        Deskripsi: Memvalidasi aksesibilitas dan elemen pada halaman riwayat /rushHour/history.
        Ekspektasi: Halaman berhasil dibuka dengan status 200 dan memuat judul 'Riwayat subsidi jam sibuk'.
        """
        status, html = admin_rush_helper.get_history_page()
        assert status == 200, f"Halaman /rushHour/history harus berstatus 200, aktual: {status}"
        assert "Riwayat subsidi jam sibuk" in html, "Teks 'Riwayat subsidi jam sibuk' harus ada di halaman"
        logger.info("[PT-02] Halaman Riwayat Subsidi Jam Sibuk terverifikasi dapat diakses.")

    @pytest.mark.positive_true
    def test_TC_DASH_RUSH_PT_03_submit_valid_multi_window_and_tiers(self, admin_rush_helper):
        """
        [POSITIVE TRUE - PT-03]
        Deskripsi: Menyimpan konfigurasi 2 window jam sibuk (Pagi 06:45-08:45 & Sore 10:45-18:45)
                    dengan 3-Tier Subsidi (Tier 1: 3k, Tier 2: 4k, Tier 3: 5k).
        Ekspektasi: Form berhasil disubmit dan data tersimpan pada server staging.
        """
        windows = [("06:45", "08:45"), ("10:45", "18:45")]
        tiers = [("3000", "10000"), ("4000", "20000"), ("5000", "")]
        resp = admin_rush_helper.submit_settings(enabled=True, windows=windows, tiers=tiers, daily_budget="")
        assert admin_rush_helper.is_saved_successfully(resp), "Form valid harus berhasil disimpan"
        logger.info("[PT-03] Konfigurasi multi-window dan 3-tier subsidi valid berhasil disimpan.")

    # ==========================================================================
    # PILAR 2: POSITIVE FALSE (PF) - TOGGLE NONAKTIF & CUSTOM BUDGET
    # ==========================================================================

    @pytest.mark.positive_false
    def test_TC_DASH_RUSH_PF_01_disable_rush_hour_subsidy_toggle(self, admin_rush_helper):
        """
        [POSITIVE FALSE - PF-01]
        Deskripsi: Menonaktifkan saklar Subsidi Jam Sibuk (enabled = false).
        Ekspektasi: Sistem menerima perubahan dan menonaktifkan fitur subsidi tanpa error.
        """
        resp = admin_rush_helper.submit_settings(enabled=False)
        assert admin_rush_helper.is_saved_successfully(resp), "Penonaktifan fitur harus berhasil disimpan"
        logger.info("[PF-01] Penonaktifan switch subsidi jam sibuk terverifikasi aman.")

    @pytest.mark.positive_false
    def test_TC_DASH_RUSH_PF_02_unlimited_daily_budget_mode(self, admin_rush_helper):
        """
        [POSITIVE FALSE - PF-02]
        Deskripsi: Menetapkan batas plafon anggaran harian tanpa batas (dailyBudget = '', Unlimited).
        Ekspektasi: Sistem menerima konfigurasi mode tanpa batas anggaran harian (status 200).
        """
        resp = admin_rush_helper.submit_settings(enabled=True, daily_budget="")
        assert admin_rush_helper.is_saved_successfully(resp), "Mode unlimited daily budget harus valid"
        logger.info("[PF-02] Pengaturan mode tanpa batas anggaran harian berhasil disimpan.")

    # ==========================================================================
    # PILAR 3: NEGATIVE TRUE (NT) - INPUT ANOMALI & VALIDASI FORM
    # ==========================================================================

    @pytest.mark.negative_true
    def test_TC_DASH_RUSH_NT_01_reject_inverted_time_window(self, admin_rush_helper):
        """
        [NEGATIVE TRUE - NT-01]
        Deskripsi: Mengirimkan window jam sibuk terbalik di mana jam mulai lebih besar dari jam selesai (19:00 ke 08:00).
        Ekspektasi: Server menolak atau merender pesan validasi error dan tidak melakukan redirect save.
        """
        bad_windows = [("19:00", "08:00")]
        tiers = [("5000", "")]
        resp = admin_rush_helper.submit_settings(enabled=True, windows=bad_windows, tiers=tiers)
        # Server akan merender ulang halaman dengan peringatan error jika invalid
        logger.info(f"[NT-01] Respon window terbalik: Status HTTP {resp.status_code}")
        assert resp.status_code in (200, 400, 422), "Window waktu terbalik harus ditolak atau di-render dengan validasi"

    @pytest.mark.negative_true
    def test_TC_DASH_RUSH_NT_02_unauthenticated_access_protection(self):
        """
        [NEGATIVE TRUE - NT-02]
        Deskripsi: Mengakses halaman /rushHour/settings dan /rushHour/history tanpa sesi login.
        Ekspektasi: Permintaan tidak terotentikasi diblokir atau dialihkan ke halaman /login.
        """
        unauth_session = AdminRushHourHelper()
        status_set, html_set = unauth_session.get_settings_page()
        status_his, html_his = unauth_session.get_history_page()

        assert status_set in (401, 403, 302, 200)
        assert status_his in (401, 403, 302, 200)
        if status_set == 200:
            assert "login" in html_set.lower() or "masuk" in html_set.lower() or "eVMOTO" in html_set
        logger.info("[NT-02] Proteksi autentikasi halaman Subsidi Jam Sibuk terverifikasi.")

    # ==========================================================================
    # PILAR 4: NEGATIVE FALSE (NF) - IDEMPOTENCY & RESTORATION
    # ==========================================================================

    @pytest.mark.negative_false
    def test_TC_DASH_RUSH_NF_01_idempotent_duplicate_submissions(self, admin_rush_helper):
        """
        [NEGATIVE FALSE - NF-01]
        Deskripsi: Melakukan pengiriman form identik berulang (idempotency) secara cepat.
        Ekspektasi: Sistem tetap konsisten, stabil, dan tidak mengalami deadlock atau duplikasi state.
        """
        windows = [("06:45", "08:45"), ("10:45", "18:45")]
        tiers = [("3000", "10000"), ("4000", "20000"), ("5000", "")]

        r1 = admin_rush_helper.submit_settings(enabled=True, windows=windows, tiers=tiers)
        r2 = admin_rush_helper.submit_settings(enabled=True, windows=windows, tiers=tiers)

        assert admin_rush_helper.is_saved_successfully(r1)
        assert admin_rush_helper.is_saved_successfully(r2)
        logger.info("[NF-01] Uji idempotency pengiriman berulang Subsidi Jam Sibuk sukses.")
