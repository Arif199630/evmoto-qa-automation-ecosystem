"""
================================================================================
UNIT VERIFICATION SUITE: EVMOTO FARE & PRICING ENGINE (6 KONDISI BISNIS)
================================================================================
"""
import pytest
from Frontend.Feature.Helper.admin_fare_calculator import AdminDashboardFareCalculator

class TestFareEnginePureUnit:

    def test_condition_1_normal_pricing_short_medium_long(self):
        calc = AdminDashboardFareCalculator()
        
        # Jarak Dekat (<= 2 KM)
        r_dekat = calc.calculate_base_argo(1.5)
        assert r_dekat["total_argo"] == 6000.0
        assert r_dekat["formatted_argo"] == "Rp 6.000"

        # Jarak Sedang (3.5 KM)
        r_sedang = calc.calculate_base_argo(3.5)
        assert r_sedang["total_argo"] == 10200.0
        assert r_sedang["formatted_argo"] == "Rp 10.200"

        # Jarak Jauh (10.0 KM - Sesuai Dashboard Production: Base 6K + Mileage 22.4K + FarFee 10K = Rp 38.400)
        r_jauh = calc.calculate_base_argo(10.0)
        assert r_jauh["total_argo"] == 38400.0
        assert r_jauh["formatted_argo"] == "Rp 38.400"
        assert r_jauh["long_distance_charge"] == 10000.0

    def test_condition_2_seamless_platform_fee_10_percent(self):
        calc = AdminDashboardFareCalculator()
        breakdown = calc.calculate_grand_total(3.5, payment_method="cash")
        
        assert breakdown["total_argo"] == 10200.0
        assert breakdown["platform_fee"] == 1020.0
        assert breakdown["formatted_platform_fee"] == "Rp 1.020"
        assert breakdown["grand_total"] == 11220.0
        assert breakdown["formatted_grand_total"] == "Rp 11.220"

    def test_condition_3_waiting_fee_after_15_minutes(self):
        calc = AdminDashboardFareCalculator()
        
        # 12 menit (dalam toleransi)
        r_free = calc.calculate_grand_total(3.5, payment_method="cash", waiting_minutes=12)
        assert r_free["excess_wait_minutes"] == 0
        assert r_free["waiting_fee"] == 0.0

        # 20 menit (5 menit kelebihan x Rp 500 = Rp 2.500)
        r_charged = calc.calculate_grand_total(3.5, payment_method="cash", waiting_minutes=20)
        assert r_charged["excess_wait_minutes"] == 5
        assert r_charged["waiting_fee"] == 2500.0
        assert r_charged["formatted_waiting_fee"] == "Rp 2.500"
        assert r_charged["grand_total"] == 13720.0
        assert r_charged["formatted_grand_total"] == "Rp 13.720"

    def test_condition_4_coupon_discount_5000(self):
        calc = AdminDashboardFareCalculator()
        r_coupon = calc.calculate_grand_total(3.5, payment_method="cash", use_coupon=True, coupon_amount=5000.0)
        
        assert r_coupon["coupon_discount"] == 5000.0
        assert r_coupon["formatted_coupon"] == "Rp 5.000"
        assert r_coupon["grand_total"] == 6220.0
        assert r_coupon["formatted_grand_total"] == "Rp 6.220"

    def test_condition_5_cancellation_penalty_5000(self):
        calc = AdminDashboardFareCalculator()
        r_pen = calc.calculate_grand_total(3.5, payment_method="cash", apply_penalty=True, penalty_amount=5000.0)
        
        assert r_pen["penalty_fee"] == 5000.0
        assert r_pen["formatted_penalty"] == "Rp 5.000"
        assert r_pen["grand_total"] == 16220.0
        assert r_pen["formatted_grand_total"] == "Rp 16.220"

    def test_condition_6_ewallet_charge_fee_2_percent(self):
        calc = AdminDashboardFareCalculator()
        
        # Tunai -> 0%
        r_cash = calc.calculate_grand_total(3.5, payment_method="cash")
        assert r_cash["charge_fee_amount"] == 0.0
        assert r_cash["grand_total"] == 11220.0

        # EvWallet -> 0%
        r_wallet = calc.calculate_grand_total(3.5, payment_method="evwallet")
        assert r_wallet["charge_fee_amount"] == 0.0
        assert r_wallet["grand_total"] == 11220.0

        # GoPay -> 2%
        r_gopay = calc.calculate_grand_total(3.5, payment_method="gopay")
        assert r_gopay["is_ewallet_surcharge"] is True
        assert r_gopay["charge_fee_amount"] == 224.4
        assert r_gopay["formatted_charge_fee"] == "Rp 224,4"
        assert r_gopay["grand_total"] == 11444.4
        assert r_gopay["formatted_grand_total"] == "Rp 11.444,4"

        # OVO -> 2%
        r_ovo = calc.calculate_grand_total(3.5, payment_method="ovo")
        assert r_ovo["charge_fee_amount"] == 224.4
        assert r_ovo["grand_total"] == 11444.4

    def test_condition_all_in_one_grand_total(self):
        calc = AdminDashboardFareCalculator()
        breakdown = calc.calculate_grand_total(
            distance_km=3.5,
            payment_method="ovo",
            waiting_minutes=20,
            use_coupon=True,
            coupon_amount=5000.0,
            apply_penalty=True,
            penalty_amount=5000.0
        )
        assert breakdown["total_argo"] == 10200.0
        assert breakdown["platform_fee"] == 1020.0
        assert breakdown["waiting_fee"] == 2500.0
        assert breakdown["penalty_fee"] == 5000.0
        assert breakdown["coupon_discount"] == 5000.0
        assert breakdown["adjusted_subtotal"] == 13720.0
        assert breakdown["charge_fee_amount"] == 274.4
        assert breakdown["formatted_charge_fee"] == "Rp 274,4"
        assert breakdown["grand_total"] == 13994.4
        assert breakdown["formatted_grand_total"] == "Rp 13.994,4"


class TestWaitingFeeCancellationQCFormUnit:
    """
    Unit Verification Suite untuk Form QC Waiting Fee & Cancellation Flow (PRD v1.1).
    Memvalidasi seluruh formula expected value sesuai Sheet 'QC Form' & 'Parameter'.
    """

    def test_prd_case_1_driver_gi_cancel_fase_a(self):
        """PRD Case 1: Driver GI cancel di Fase A (belum tiba, elapsed 0s)."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Driver",
            driver_arrived=False,
            elapsed_seconds=0,
            driver_schema="GI"
        )
        assert res["phase"] == "A"
        assert res["billable_minutes"] == 0
        assert res["driver_penalty"] == 2000.0
        assert res["driver_payout"] == 0.0
        assert res["customer_charge"] == 0.0
        assert res["coupon_issued"] is False
        assert res["gi_adj_event"] == -10000.0
        assert res["platform_net"] == 2000.0  # 0 + 2000 - 0 = 2000
        assert res["is_valid"] is True

    def test_prd_case_5_customer_cancel_fase_c_22m30s(self):
        """PRD Case 5: Customer cancel di Fase C (elapsed 1350s = 22m 30s, m=8)."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=1350,
            driver_schema="Non-GI"
        )
        assert res["phase"] == "C"
        assert res["billable_minutes"] == 8
        assert res["driver_penalty"] == 0.0
        assert res["driver_payout"] == 5400.0   # 3000 + (8 * 300) = 5400
        assert res["customer_charge"] == 9000.0 # 5000 + (8 * 500) = 9000
        assert res["coupon_issued"] is False
        assert res["gi_adj_event"] == 0.0
        assert res["platform_net"] == 3600.0    # 9000 + 0 - 5400 = 3600
        assert res["formatted_customer_charge"] == "Rp 9.000"

    def test_prd_case_8_system_auto_cancel_no_show_fase_d_30m(self):
        """PRD Case 8: System auto-cancel No-Show di Fase D (elapsed 1800s = 30m, m=15)."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="System",
            driver_arrived=True,
            elapsed_seconds=1800,
            driver_schema="GI"
        )
        assert res["phase"] == "D"
        assert res["billable_minutes"] == 15
        assert res["driver_penalty"] == 0.0
        assert res["driver_payout"] == 11500.0   # (15 * 300) + 7000 = 11500
        assert res["customer_charge"] == 17500.0 # 10000 + (15 * 500) = 17500
        assert res["coupon_issued"] is False
        assert res["gi_adj_event"] == 0.0
        assert res["platform_net"] == 6000.0     # 17500 + 0 - 11500 = 6000
        assert res["formatted_customer_charge"] == "Rp 17.500"

    def test_customer_cancel_fase_a_free_cancellation(self):
        """Customer membatalkan sebelum driver tiba (Fase A) -> Gratis Rp 0."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=False,
            elapsed_seconds=0
        )
        assert res["phase"] == "A"
        assert res["customer_charge"] == 0.0
        assert res["driver_payout"] == 0.0
        assert res["formatted_customer_charge"] == "Rp 0"

    def test_customer_cancel_fase_b_grace_period_penalty_5000(self):
        """Customer membatalkan saat driver tiba di Fase B (300s) -> Denda Rp 5.000."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=300
        )
        assert res["phase"] == "B"
        assert res["billable_minutes"] == 0
        assert res["customer_charge"] == 5000.0
        assert res["driver_payout"] == 3000.0
        assert res["formatted_customer_charge"] == "Rp 5.000"

    def test_driver_cancel_fase_b_issues_user_coupon_5000(self):
        """Driver cancel saat tiba di Fase B (600s) -> User dapat kupon Rp 5.000, Charge Rp 0."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Driver",
            driver_arrived=True,
            elapsed_seconds=600,
            driver_schema="Non-GI"
        )
        assert res["phase"] == "B"
        assert res["customer_charge"] == 0.0
        assert res["coupon_issued"] is True
        assert res["coupon_amount"] == 5000.0
        assert res["driver_penalty"] == 5000.0
        assert res["formatted_coupon"] == "Rp 5.000"

    def test_driver_cancel_fase_c_wait_fee_forfeited_and_coupon_issued(self):
        """Driver cancel di Fase C (1200s) -> Waiting fee hangus, User dapat kupon Rp 5.000."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Driver",
            driver_arrived=True,
            elapsed_seconds=1200,
            driver_schema="GI"
        )
        assert res["phase"] == "C"
        assert res["customer_charge"] == 0.0
        assert res["driver_payout"] == 0.0  # Forfeit!
        assert res["coupon_issued"] is True
        assert res["coupon_amount"] == 5000.0
        assert res["driver_penalty"] == 5000.0
        assert res["gi_adj_event"] == -10000.0

    def test_customer_cancel_fase_c_boundary_901s_m1(self):
        """Boundary Test: 901s (15m 01s) -> m=1, Charge Rp 5.500."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=901
        )
        assert res["phase"] == "C"
        assert res["billable_minutes"] == 1
        assert res["customer_charge"] == 5500.0  # 5000 + (1 * 500)
        assert res["driver_payout"] == 3300.0    # 3000 + (1 * 300)

    def test_customer_cancel_fase_c_boundary_1799s_cap_m15(self):
        """Boundary Test: 1799s (29m 59s) -> Cap m=15, Charge Rp 12.500."""
        calc = AdminDashboardFareCalculator()
        res = calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=1799
        )
        assert res["phase"] == "C"
        assert res["billable_minutes"] == 15
        assert res["customer_charge"] == 12500.0  # 5000 + (15 * 500)
        assert res["driver_payout"] == 7500.0     # 3000 + (15 * 300)

    def test_invalid_combinations_fase_d(self):
        """Invalid test: Fase D dengan CancelledBy selain System."""
        calc = AdminDashboardFareCalculator()
        res_cust = calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=1800
        )
        assert res_cust["is_valid"] is False
        assert res_cust["status"] == "INVALID"

        res_sys_early = calc.calculate_cancellation_settlement(
            cancelled_by="System",
            driver_arrived=True,
            elapsed_seconds=1200
        )
        assert res_sys_early["is_valid"] is False
        assert res_sys_early["status"] == "INVALID"

    def test_cancellation_charge_with_ewallet_surcharge_2_percent(self):
        """Integrasi Surcharge 2% E-Wallet pada Charge Pembatalan."""
        calc = AdminDashboardFareCalculator()
        # Fase B (Rp 5.000) dengan GoPay
        res_gopay = calc.calculate_cancellation_settlement(
            cancelled_by="Customer",
            driver_arrived=True,
            elapsed_seconds=300,
            payment_method="gopay"
        )
        assert res_gopay["customer_charge"] == 5000.0
        assert res_gopay["charge_fee_amount"] == 100.0 # 2% dari 5000
        assert res_gopay["grand_total_customer"] == 5100.0
        assert res_gopay["formatted_grand_total"] == "Rp 5.100"

        # Fase D No-Show (Rp 17.500) dengan OVO
        res_ovo = calc.calculate_cancellation_settlement(
            cancelled_by="System",
            driver_arrived=True,
            elapsed_seconds=1800,
            payment_method="ovo"
        )
        assert res_ovo["customer_charge"] == 17500.0
        assert res_ovo["charge_fee_amount"] == 350.0 # 2% dari 17500
        assert res_ovo["grand_total_customer"] == 17850.0
        assert res_ovo["formatted_grand_total"] == "Rp 17.850"

