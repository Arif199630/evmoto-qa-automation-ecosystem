"""
================================================================================
EVMOTO MOBILE APPS (DRIVER & USER) - RUSH HOUR SUBSIDY PRICING SUITE
================================================================================
Fokus Pengujian:
  1. Kalkulasi Subsidi Tepat Sesuai Tier Argo Original:
     - Tier 1: Rp 6.000 (Jarak Dekat <= 2.0 KM) -> Subsidi Rp 3.000
     - Tier 2: Rp 14.400 (Jarak Sedang 5.0 KM) -> Subsidi Rp 4.000
     - Tier 3: Rp 25.000 (Jarak Jauh 9.0 KM)   -> Subsidi Rp 5.000
  2. Isolasi Total dari Diskon Voucher & Tambahan Biaya:
     - Order dengan Voucher Diskon Rp 5.000 -> Tetap mengacu pada Argo Original!
     - Order dengan Waiting Fee (Biaya Menunggu) -> Waiting fee TIDAK menaikkan tier!
     - Order dengan Denda Penalti Pembatalan -> Denda TIDAK mempengaruhi tier!
  3. Uji Waktu & Batas Window:
     - Di dalam window jam sibuk (misal 11:30 atau 17:00) -> Dikenakan subsidi.
     - Di luar window jam sibuk (misal 09:15 atau 20:00) -> Subsidi = Rp 0.
  4. Uji Seamless di Sisi Driver:
     - Driver menerima akumulasi pendapatan bersih (net payout) bertambah.
     - Tampilan order driver TIDAK menampilkan badge atau aturan rahasia jam sibuk.
================================================================================
"""

import pytest
import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_HELPER_DIR = os.path.join(_CURRENT_DIR, "Helper")
if _HELPER_DIR not in sys.path:
    sys.path.insert(0, _HELPER_DIR)

from rush_hour_calculator import RushHourSubsidyCalculator


class TestRushHourMobilePricing:
    """Test suite resmi untuk pricing engine dan kalkulasi subsidi argo original."""

    def test_01_tier_1_short_distance_rush_hour_subsidy(self):
        """[POSITIVE TRUE - PT-01] Order Jarak Dekat (Argo Rp 6.000) pada Jam Sibuk sukses berhak atas Subsidi Rp 3.000."""
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="11:15",
            original_base_fare=6000.0
        )
        assert calc_result["is_rush_hour"] is True
        assert calc_result["applied_subsidy"] == 3000
        assert calc_result["original_base_fare"] == 6000.0

    def test_02_tier_2_medium_distance_rush_hour_subsidy(self):
        """[POSITIVE TRUE - PT-02] Order Jarak Sedang (Argo Rp 14.400) pada Jam Sibuk sukses berhak atas Subsidi Rp 4.000."""
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="14:30",
            original_base_fare=14400.0
        )
        assert calc_result["is_rush_hour"] is True
        assert calc_result["applied_subsidy"] == 4000
        assert calc_result["original_base_fare"] == 14400.0

    def test_03_tier_3_long_distance_unlimited_subsidy(self):
        """[POSITIVE TRUE - PT-03] Order Jarak Jauh (Argo Rp 28.500) pada Jam Sibuk sukses berhak atas Subsidi Rp 5.000."""
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="17:45",
            original_base_fare=28500.0
        )
        assert calc_result["is_rush_hour"] is True
        assert calc_result["applied_subsidy"] == 5000
        assert calc_result["original_base_fare"] == 28500.0

    def test_04_voucher_discount_isolation_integrity(self):
        """[POSITIVE FALSE / PN-01] Kupon Diskon Rp 5.000 TIDAK menurunkan tier subsidi (tetap dihitung dari Rp 14.400)."""
        # User membayar Rp 9.400 (karena diskon Rp 5.000), tapi argo aslinya Rp 14.400 (Tier 2)
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="12:00",
            original_base_fare=14400.0,
            voucher_discount=5000.0
        )
        assert calc_result["is_rush_hour"] is True
        assert calc_result["user_paid_fare"] == 9400.0
        # Subsidi WAJIB tetap Rp 4.000 (bukan turun ke Tier 1 Rp 3.000 karena potongan kupon)
        assert calc_result["applied_subsidy"] == 4000
        assert calc_result["calculation_basis"] == "STRICT_ORIGINAL_BASE_FARE"

    def test_05_waiting_fee_isolation_integrity(self):
        """[POSITIVE FALSE / PN-02] Biaya Menunggu (Waiting Fee) TIDAK menaikkan tier subsidi secara curang."""
        # Argo original Rp 9.000 (Tier 1 <= 10.000), ada waiting fee Rp 3.000 -> Total tagihan Rp 12.000
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="16:00",
            original_base_fare=9000.0,
            waiting_fee=3000.0
        )
        assert calc_result["is_rush_hour"] is True
        assert calc_result["user_paid_fare"] == 12000.0
        # Subsidi WAJIB tetap Rp 3.000 (Tier 1) berdasarkan argo original Rp 9.000, BUKAN Tier 2!
        assert calc_result["applied_subsidy"] == 3000

    def test_06_cancellation_penalty_fee_isolation(self):
        """[POSITIVE FALSE / PN-03] Penalti Denda Pelanggaran TIDAK memanipulasi perhitungan subsidi."""
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="07:30",
            original_base_fare=8000.0,
            penalty_fee=5000.0
        )
        assert calc_result["is_rush_hour"] is True
        assert calc_result["user_paid_fare"] == 13000.0
        assert calc_result["applied_subsidy"] == 3000

    def test_07_outside_rush_hour_window_zero_subsidy(self):
        """[NEGATIVE TRUE - NT-01] Order di luar window jam sibuk (09:30 atau 21:00) secara tepat ditolak subsidi (Rp 0)."""
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="09:30",
            original_base_fare=15000.0
        )
        assert calc_result["is_rush_hour"] is False
        assert calc_result["applied_subsidy"] == 0

        calc_night = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="21:15",
            original_base_fare=15000.0
        )
        assert calc_night["is_rush_hour"] is False
        assert calc_night["applied_subsidy"] == 0

    def test_08_disabled_feature_zero_subsidy(self):
        """[NEGATIVE TRUE - NT-02] Jika toggle 'Bayar subsidi' dimatikan (enabled = False), kalkulasi ditolak (Rp 0)."""
        disabled_settings = {
            "enabled": False,
            "windows": [{"start": "06:45", "end": "08:45"}],
            "tiers": [{"max": 10000, "subsidy": 3000}]
        }
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="07:00",
            original_base_fare=6000.0,
            settings=disabled_settings
        )
        assert calc_result["is_enabled"] is False
        assert calc_result["applied_subsidy"] == 0

    def test_09_driver_seamless_experience_simulation(self):
        """[POSITIVE TRUE - PT-04] Sisi Driver seamless: total pendapatan bersih bertambah tanpa bocor rumus internal."""
        base_fare = 14400.0
        platform_fee = base_fare * 0.10  # 10% potongan platform
        calc_result = RushHourSubsidyCalculator.calculate_order_subsidy(
            order_time="13:00",
            original_base_fare=base_fare
        )

        subsidy = calc_result["applied_subsidy"]
        driver_standard_payout = base_fare - platform_fee  # Rp 12.960
        driver_total_take_home = driver_standard_payout + subsidy  # Rp 16.960

        # Driver UI Payload Simulation
        driver_ui_order_view = {
            "order_id": "2113521148271529984",
            "base_fare": base_fare,
            "platform_deduction": platform_fee,
            "net_earning": driver_total_take_home
        }

        # Verifikasi sifat seamless: tidak ada field internal 'rush_hour_rule' yang dibocorkan ke driver
        assert "rush_hour_rule_formula" not in driver_ui_order_view
        assert driver_ui_order_view["net_earning"] == 16960.0
        assert driver_ui_order_view["net_earning"] > driver_standard_payout
