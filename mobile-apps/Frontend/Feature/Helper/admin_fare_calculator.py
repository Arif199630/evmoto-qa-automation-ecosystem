"""
================================================================================
EVMOTO FARE & PRICING ENGINE CALCULATOR (PRODUCTION GRADE)
================================================================================
Modul kalkulator harga resmi EvMoto yang mengimplementasikan 6 kondisi bisnis:
1. Harga Normal:
   - Jarak Dekat (<= 2.0 KM)  : Tarif Awal Rp 6.000 (startPrice)
   - Jarak Sedang (2.0 - 6 KM): Rp 6.000 + (Jarak - 2.0) * Rp 2.800/KM (mileageFee)
   - Jarak Jauh (> 6.0 KM)    : Mengikuti aturan bertingkat Dashboard Production:
                                * Tier 1 (6.0 - 15.0 KM) : +Rp 2.500/KM (farFee1)
                                * Tier 2 (15.0 - 100 KM) : +Rp 2.200/KM (farFee2)
                                * Tier 3 (> 100.0 KM)    : +Rp 2.200/KM (farFee3)
2. Platform Fee (10%):
   - Dihitung 10% dari Tarif Dasar Argo (seamless di sisi User Apps)
3. Waiting Fee:
   - Toleransi penjemputan 15 menit gratis.
   - Kelebihan waktu dikenakan Rp 500 / menit (waitFee = 500).
4. Kupon Diskon Rp 5.000:
   - Potongan kupon promosi Rp 5.000 langsung mengurangi subtotal.
5. Penalty (Denda Pembatalan / Pelanggaran):
   - Biaya penalti (default Rp 5.000) ditambahkan ke tagihan pengguna.
6. Charge Fee 2% E-Wallet (GoPay & OVO):
   - Dikenakan 2% untuk pembayaran via GoPay dan OVO.
   - Jika ada waiting fee & penalty, Charge Fee 2% dihitung dari Grand Total akumulatif.
   - Pembayaran Tunai (Cash) dan EvWallet TIDAK dikenakan Charge Fee (0%).
================================================================================
"""

import re
import math
from typing import Dict, Any, Union
from utils.logger import get_logger

logger = get_logger("AdminFareCalculator")


def format_rupiah_exact(val: Union[int, float]) -> str:
    """
    Format nominal Rupiah persis tanpa pembulatan.
    Contoh:
      11220    -> 'Rp 11.220'
      11444.4  -> 'Rp 11.444,4'
      13994.4  -> 'Rp 13.994,4'
    """
    val_float = float(val)
    if val_float == int(val_float):
        formatted_int = f"{int(val_float):,}".replace(",", ".")
        return f"Rp {formatted_int}"
    else:
        int_part = int(val_float)
        dec_part = round(val_float - int_part, 2)
        dec_str = f"{dec_part:.2f}"[2:].rstrip("0")
        formatted_int = f"{int_part:,}".replace(",", ".")
        return f"Rp {formatted_int},{dec_str}"


class AdminDashboardFareCalculator:
    """Kalkulator perhitungan harga argo, biaya layanan, dan penalti resmi EvMoto."""

    # Konfigurasi dasar resmi Dashboard Admin Production
    START_PRICE = 6000.0       # Rp 6.000 untuk 2.0 KM pertama
    START_KM = 2.0            # 2.0 KM radius awal
    MILEAGE_FEE = 2800.0      # Rp 2.800 / KM (tarif jarak reguler)
    DURATION_FEE = 0.0        # Rp 0 / menit
    PLATFORM_FEE_RATE = 0.10  # 10% Platform fee (seamless)
    WAIT_MINUTES_FREE = 15    # 15 Menit tunggu gratis
    WAIT_FEE_PER_MIN = 500.0  # Rp 500 / menit setelah 15 menit
    DEFAULT_COUPON = 5000.0   # Voucher Kupon Rp 5.000
    DEFAULT_PENALTY = 5000.0  # Penalty pembatalan / denda Rp 5.000
    EWALLET_CHARGE_RATE = 0.02# 2% Charge fee untuk GoPay & OVO

    # Konfigurasi Long Distance Fee resmi Dashboard Admin Production (ID 1626 / 1619)
    FAR_FROM_1 = 6.0          # Batas awal Jarak Jauh Tier 1 (6.0 KM)
    FAR_TO_1 = 15.0           # Batas akhir Jarak Jauh Tier 1 (15.0 KM)
    FAR_FEE_1 = 2500.0        # Rp 2.500 / KM untuk kelebihan jarak 6 - 15 KM

    FAR_FROM_2 = 15.0         # Batas awal Jarak Jauh Tier 2 (15.0 KM)
    FAR_TO_2 = 100.0          # Batas akhir Jarak Jauh Tier 2 (100.0 KM)
    FAR_FEE_2 = 2200.0        # Rp 2.200 / KM untuk kelebihan jarak 15 - 100 KM

    FAR_FROM_3 = 100.0        # Batas awal Jarak Jauh Tier 3 (> 100.0 KM)
    FAR_FEE_3 = 2200.0        # Rp 2.200 / KM untuk kelebihan jarak > 100 KM

    # ==========================================================================
    # KONSTANTA RESMI WAITING FEE & CANCELLATION FLOW (PRD v1.1)
    # Sesuai Sheet 'Parameter' & 'QC Form' di QC_Form_WaitingFee_Cancellation.xlsx
    # ==========================================================================
    PENALTY_DRIVER_FASE_A = 2000.0        # Rp 2.000 (potong saldo driver realtime)
    PENALTY_DRIVER_FASE_BC = 5000.0       # Rp 5.000 (potong saldo driver realtime)
    GI_ADJUSTMENT_PER_CANCEL = -10000.0   # -Rp 10.000 (event midnight batch, hanya GI)
    KOMPENSASI_DRIVER_CANCEL_BC = 3000.0  # Rp 3.000 (dibayar platform ke driver saat customer cancel B/C)
    KOMPENSASI_DRIVER_NOSHOW_D = 7000.0   # Rp 7.000 (dibayar platform ke driver saat no-show Fase D)
    WAIT_FEE_DRIVER_PER_MIN = 300.0       # Rp 300 / menit (dibayar platform ke driver, Fase C)
    WAIT_FEE_CUSTOMER_PER_MIN = 500.0     # Rp 500 / menit (dibayar customer ke platform, Fase C)
    PENALTY_CUSTOMER_CANCEL_BC = 5000.0   # Rp 5.000 (cancel fee customer Fase B/C)
    PENALTY_CUSTOMER_NOSHOW_D = 10000.0   # Rp 10.000 (denda customer no-show Fase D)
    KUPON_DRIVER_CANCEL_BC = 5000.0       # Rp 5.000 (voucher kompensasi user jika driver cancel B/C)
    GRACE_PERIOD_SECONDS = 900            # 900 detik (15 menit sejak arrived_at)
    AUTO_CANCEL_SECONDS = 1800            # 1800 detik (30 menit sejak arrived_at)
    MAX_BILLABLE_MINUTES = 15             # 15 menit maksimal penagihan (15:01 - 30:00)

    def __init__(self):
        logger.info(
            f"[FARE ENGINE INIT] Formula Resmi Dashboard Production Aktif -> Base: Rp {self.START_PRICE:,.0f} ({self.START_KM} KM), "
            f"Mileage: Rp {self.MILEAGE_FEE:,.0f}/KM, FarFee1 (6-15KM): +Rp {self.FAR_FEE_1:,.0f}/KM, "
            f"FarFee2 (15-100KM): +Rp {self.FAR_FEE_2:,.0f}/KM, Platform: 10%, E-Wallet Charge: 2% (GoPay/OVO)"
        )

    def calculate_base_argo(self, distance_km: float) -> Dict[str, Any]:
        """
        Kondisi 1: Menghitung Tarif Argo Normal berdasarkan jarak persis Dashboard Admin Production:
        - Jarak Dekat (<= 2.0 KM)  : Rp 6.000 (Tarif Awal Minimum)
        - Jarak Sedang (2.0 - 6 KM): Rp 6.000 + (Jarak - 2.0) * Rp 2.800
        - Jarak Jauh (> 6.0 KM)    : Rp 6.000 + (Jarak - 2.0) * Rp 2.800 + Long Distance Surcharge (Rp 2.500/KM untuk 6-15 KM)
        """
        distance_float = float(distance_km)
        if distance_float <= self.START_KM:
            additional_km = 0.0
            mileage_charge = 0.0
            long_distance_charge = 0.0
            category = "Jarak Dekat (<= 2 KM)"
        elif distance_float <= self.FAR_FROM_1:  # 2.0 s/d 6.0 KM
            additional_km = distance_float - self.START_KM
            mileage_charge = additional_km * self.MILEAGE_FEE
            long_distance_charge = 0.0
            category = "Jarak Sedang (2.0 - 6.0 KM)"
        else:  # > 6.0 KM (Long Distance Surcharge Persis Dashboard Admin Production)
            additional_km = distance_float - self.START_KM
            mileage_charge = additional_km * self.MILEAGE_FEE
            category = "Jarak Jauh (> 6.0 KM - Sesuai Dashboard Production)"

            if distance_float <= self.FAR_TO_1:  # 6.0 s/d 15.0 KM
                far_km_tier1 = distance_float - self.FAR_FROM_1
                long_distance_charge = far_km_tier1 * self.FAR_FEE_1
            elif distance_float <= self.FAR_TO_2:  # 15.0 s/d 100.0 KM
                tier1_km = self.FAR_TO_1 - self.FAR_FROM_1  # 9.0 KM
                far_km_tier2 = distance_float - self.FAR_FROM_2
                long_distance_charge = (tier1_km * self.FAR_FEE_1) + (far_km_tier2 * self.FAR_FEE_2)
            else:  # > 100.0 KM
                tier1_km = self.FAR_TO_1 - self.FAR_FROM_1  # 9.0 KM
                tier2_km = self.FAR_TO_2 - self.FAR_FROM_2  # 85.0 KM
                far_km_tier3 = distance_float - self.FAR_FROM_3
                long_distance_charge = (tier1_km * self.FAR_FEE_1) + (tier2_km * self.FAR_FEE_2) + (far_km_tier3 * self.FAR_FEE_3)

        total_argo = self.START_PRICE + mileage_charge + long_distance_charge

        return {
            "distance_km": round(distance_float, 2),
            "category": category,
            "start_price": self.START_PRICE,
            "start_km": self.START_KM,
            "additional_km": round(additional_km, 2),
            "mileage_charge": mileage_charge,
            "long_distance_charge": long_distance_charge,
            "total_argo": total_argo,
            "formatted_argo": format_rupiah_exact(total_argo),
            "formatted_long_distance_fee": format_rupiah_exact(long_distance_charge)
        }

    def calculate_grand_total(
        self,
        distance_km: float,
        payment_method: str = "cash",
        waiting_minutes: int = 0,
        use_coupon: bool = False,
        coupon_amount: float = 5000.0,
        apply_penalty: bool = False,
        penalty_amount: float = 5000.0,
    ) -> Dict[str, Any]:
        """
        Kalkulator Menyeluruh untuk 6 Kondisi Bisnis EvMoto:
        1. Jarak (Dekat, Sedang, Jauh)
        2. Platform Fee (10%)
        3. Waiting Fee (Setelah 15 menit, Rp 500/menit)
        4. Kupon Diskon (Rp 5.000)
        5. Penalty (Rp 5.000)
        6. Charge Fee 2% untuk E-Wallet (GoPay & OVO) pada Grand Total akumulatif
        """
        # 1. Hitung Argo Dasar
        argo_info = self.calculate_base_argo(distance_km)
        total_argo = argo_info["total_argo"]

        # 2. Platform Fee 10% (Seamless)
        platform_fee = total_argo * self.PLATFORM_FEE_RATE
        base_subtotal = total_argo + platform_fee

        # 3. Waiting Fee
        excess_wait_minutes = max(0, int(waiting_minutes) - self.WAIT_MINUTES_FREE)
        waiting_fee = float(excess_wait_minutes * self.WAIT_FEE_PER_MIN)

        # 4. Kupon Diskon
        discount_applied = float(coupon_amount) if use_coupon else 0.0

        # 5. Penalty
        penalty_fee = float(penalty_amount) if apply_penalty else 0.0

        # Subtotal Akumulatif Sebelum Charge Fee
        # Grand Total Dasar = Argo + Platform Fee (10%) + Waiting Fee + Penalty - Kupon
        adjusted_subtotal = base_subtotal + waiting_fee + penalty_fee - discount_applied
        adjusted_subtotal = max(0.0, adjusted_subtotal)

        # 6. Charge Fee 2% E-Wallet (GoPay & OVO)
        clean_method = payment_method.strip().lower()
        is_ewallet_surcharge = clean_method in ["gopay", "ovo", "e-wallet", "ewallet"]
        
        if is_ewallet_surcharge:
            charge_fee_rate = self.EWALLET_CHARGE_RATE
            charge_fee_amount = round(adjusted_subtotal * charge_fee_rate, 2)
        else:
            charge_fee_rate = 0.0
            charge_fee_amount = 0.0

        grand_total = round(adjusted_subtotal + charge_fee_amount, 2)

        result = {
            "distance_km": argo_info["distance_km"],
            "category": argo_info["category"],
            "payment_method": payment_method.upper(),
            "start_price": argo_info["start_price"],
            "mileage_charge": argo_info["mileage_charge"],
            "long_distance_charge": argo_info["long_distance_charge"],
            "total_argo": total_argo,
            "platform_fee": platform_fee,
            "base_subtotal": base_subtotal,
            "waiting_minutes": waiting_minutes,
            "excess_wait_minutes": excess_wait_minutes,
            "waiting_fee": waiting_fee,
            "coupon_discount": discount_applied,
            "penalty_fee": penalty_fee,
            "adjusted_subtotal": adjusted_subtotal,
            "is_ewallet_surcharge": is_ewallet_surcharge,
            "charge_fee_rate": charge_fee_rate,
            "charge_fee_amount": charge_fee_amount,
            "grand_total": grand_total,
            # Format Rupiah Persis Tanpa Pembulatan
            "formatted_argo": format_rupiah_exact(total_argo),
            "formatted_platform_fee": format_rupiah_exact(platform_fee),
            "formatted_waiting_fee": format_rupiah_exact(waiting_fee),
            "formatted_coupon": format_rupiah_exact(discount_applied),
            "formatted_penalty": format_rupiah_exact(penalty_fee),
            "formatted_charge_fee": format_rupiah_exact(charge_fee_amount),
            "formatted_grand_total": format_rupiah_exact(grand_total)
        }

        logger.info(
            f"[FARE BREAKDOWN] Jarak: {distance_km} KM ({argo_info['category']}) | "
            f"Argo: {result['formatted_argo']} | Plat(10%): {result['formatted_platform_fee']} | "
            f"Wait({waiting_minutes}m): {result['formatted_waiting_fee']} | "
            f"Kupon: -{result['formatted_coupon']} | Penalty: +{result['formatted_penalty']} | "
            f"Method: {payment_method.upper()} (Charge 2%: {result['formatted_charge_fee']}) -> "
            f"GRAND TOTAL: {result['formatted_grand_total']}"
        )
        return result

    # Metode backward-compatible untuk skrip lama
    def calculate_fare(self, distance_km: float, is_night: bool = False) -> Dict[str, Any]:
        """Kompatibilitas mundur dengan penambahan platform fee 10%."""
        base = self.calculate_base_argo(distance_km)
        breakdown = self.calculate_grand_total(distance_km, payment_method="cash")
        return {
            "distance_km": base["distance_km"],
            "is_night": False,
            "start_price": base["start_price"],
            "start_km": base["start_km"],
            "additional_km": base["additional_km"],
            "distance_charge": base["mileage_charge"],
            "long_distance_charge": base["long_distance_charge"],
            "total_argo": base["total_argo"],
            "platform_fee": breakdown["platform_fee"],
            "total_fare": breakdown["grand_total"],
            "formatted_total": breakdown["formatted_grand_total"]
        }

    @staticmethod
    def parse_numeric_fare(fare_text: str) -> float:
        """Mengekstrak angka desimal dari string harga tampilan UI (misal: 'Rp 11.444,4' -> 11444.4)."""
        if not fare_text:
            return 0.0
        # Bersihkan 'Rp ' dan spasi
        cleaned = fare_text.replace("Rp", "").replace(".", "").replace(" ", "").replace(",", ".").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def calculate_cancellation_settlement(
        self,
        cancelled_by: str,
        driver_arrived: bool,
        elapsed_seconds: int = 0,
        driver_schema: str = "Non-GI",
        payment_method: str = "cash"
    ) -> Dict[str, Any]:
        """
        Kalkulator Resmi Waiting Fee & Cancellation Flow (PRD v1.1):
        Mengikuti seluruh formula dan aturan Sheet 'Parameter' & 'QC Form' di QC_Form_WaitingFee_Cancellation.xlsx:
        - Fase A: Driver belum tiba (elapsed = 0).
        - Fase B: Driver sudah tiba, elapsed 1 - 900 detik (Grace Period 15 menit).
        - Fase C: Driver sudah tiba, elapsed 901 - 1799 detik (Waiting Fee Period 15:01 - 29:59).
        - Fase D: Elapsed >= 1800 detik (Auto-cancel / Customer No-Show >= 30 menit).
        """
        clean_by = cancelled_by.strip().capitalize()
        clean_schema = driver_schema.strip().upper()
        elapsed_int = max(0, int(elapsed_seconds))

        # 1. Tentukan Fase Sesuai Formula Excel:
        # =IF($F="Tidak", "A", IF($G<=900, "B", IF($G<1800, "C", "D")))
        if not driver_arrived or elapsed_int == 0:
            phase = "A"
        elif elapsed_int <= self.GRACE_PERIOD_SECONDS:
            phase = "B"
        elif elapsed_int < self.AUTO_CANCEL_SECONDS:
            phase = "C"
        else:
            phase = "D"

        # 2. Validasi Aturan Kombinasi Skenario:
        # Formula: OR(AND(H="D", D<>"System"), AND(D="System", H<>"D"), AND(D="Driver", E=""))
        is_invalid = False
        invalid_reason = ""
        if phase == "D" and clean_by != "System":
            is_invalid = True
            invalid_reason = "Fase D (>= 1800 detik / 30 menit) HANYA valid jika dibatalkan oleh System (Auto-cancel No-Show)."
        elif clean_by == "System" and phase != "D":
            is_invalid = True
            invalid_reason = "System cancel HANYA berlaku saat mencapai ambang batas Fase D (>= 1800 detik)."
        elif clean_by == "Driver" and not clean_schema:
            is_invalid = True
            invalid_reason = "Pembatalan oleh Driver wajib menyertakan skema driver (GI atau Non-GI)."

        if is_invalid:
            logger.warning(f"[CANCEL SETTLEMENT INVALID] Fase: {phase}, CancelledBy: {clean_by} -> {invalid_reason}")
            return {
                "status": "INVALID",
                "phase": phase,
                "cancelled_by": clean_by,
                "driver_schema": clean_schema,
                "elapsed_seconds": elapsed_int,
                "is_valid": False,
                "invalid_reason": invalid_reason
            }

        # 3. Billable Menit (m)
        # =IF(OR(H="A", G<=900), 0, MIN(ROUNDUP((G-900)/60, 0), 15))
        if phase in ("A", "B") or elapsed_int <= self.GRACE_PERIOD_SECONDS:
            billable_minutes = 0
        else:
            excess_sec = elapsed_int - self.GRACE_PERIOD_SECONDS
            billable_minutes = min(math.ceil(excess_sec / 60.0), int(self.MAX_BILLABLE_MINUTES))

        # 4. Driver Penalty
        # =IF(D="Driver", IF(H="A", 2000, 5000), 0)
        if clean_by == "Driver":
            driver_penalty = self.PENALTY_DRIVER_FASE_A if phase == "A" else self.PENALTY_DRIVER_FASE_BC
        else:
            driver_penalty = 0.0

        # 5. Driver Payout
        # =IF(D="Customer", IF(H="A", 0, IF(H="B", 3000, 3000 + 300*m)), IF(D="System", 300*15 + 7000, 0))
        if clean_by == "Customer":
            if phase == "A":
                driver_payout = 0.0
            elif phase == "B":
                driver_payout = self.KOMPENSASI_DRIVER_CANCEL_BC
            else: # Fase C
                driver_payout = self.KOMPENSASI_DRIVER_CANCEL_BC + (self.WAIT_FEE_DRIVER_PER_MIN * billable_minutes)
        elif clean_by == "System": # Fase D
            driver_payout = (self.WAIT_FEE_DRIVER_PER_MIN * self.MAX_BILLABLE_MINUTES) + self.KOMPENSASI_DRIVER_NOSHOW_D
        else:
            # Driver cancel: accrued waiting fee forfeit (hangus), payout = 0
            driver_payout = 0.0

        # 6. Customer Charge
        # =IF(D="Customer", IF(H="A", 0, IF(H="B", 5000, 5000 + 500*m)), IF(D="System", 10000 + 500*15, 0))
        if clean_by == "Customer":
            if phase == "A":
                customer_charge = 0.0
                cancel_penalty_charge = 0.0
                waiting_fee_charge = 0.0
            elif phase == "B":
                cancel_penalty_charge = self.PENALTY_CUSTOMER_CANCEL_BC
                waiting_fee_charge = 0.0
                customer_charge = cancel_penalty_charge
            else: # Fase C
                cancel_penalty_charge = self.PENALTY_CUSTOMER_CANCEL_BC
                waiting_fee_charge = self.WAIT_FEE_CUSTOMER_PER_MIN * billable_minutes
                customer_charge = cancel_penalty_charge + waiting_fee_charge
        elif clean_by == "System": # Fase D
            cancel_penalty_charge = self.PENALTY_CUSTOMER_NOSHOW_D
            waiting_fee_charge = self.WAIT_FEE_CUSTOMER_PER_MIN * self.MAX_BILLABLE_MINUTES
            customer_charge = cancel_penalty_charge + waiting_fee_charge
        else: # Driver cancel
            cancel_penalty_charge = 0.0
            waiting_fee_charge = 0.0
            customer_charge = 0.0

        # 7. Kupon Kompensasi User (Exp. Kupon Terbit?)
        # =IF(AND(D="Driver", OR(H="B", H="C")), "Ya", "Tidak")
        if clean_by == "Driver" and phase in ("B", "C"):
            coupon_issued = True
            coupon_amount = self.KUPON_DRIVER_CANCEL_BC
        else:
            coupon_issued = False
            coupon_amount = 0.0

        # 8. GI Adjustment Event (Khusus Driver GI saat Cancel)
        # =IF(AND(D="Driver", E="GI"), -10000, 0)
        if clean_by == "Driver" and clean_schema == "GI":
            gi_adj_event = self.GI_ADJUSTMENT_PER_CANCEL
        else:
            gi_adj_event = 0.0

        # 9. Platform Net
        # = Customer Charge + Driver Penalty - Driver Payout
        platform_net = customer_charge + driver_penalty - driver_payout

        # 10. Integrasi Surcharge E-Wallet (GoPay & OVO) 2%
        clean_method = payment_method.strip().lower()
        is_ewallet = clean_method in ["gopay", "ovo", "e-wallet", "ewallet"]
        charge_fee_amount = round(customer_charge * self.EWALLET_CHARGE_RATE, 2) if is_ewallet else 0.0
        grand_total_customer = round(customer_charge + charge_fee_amount, 2)

        res = {
            "status": "VALID",
            "is_valid": True,
            "phase": phase,
            "cancelled_by": clean_by,
            "driver_schema": clean_schema,
            "driver_arrived": driver_arrived,
            "elapsed_seconds": elapsed_int,
            "billable_minutes": billable_minutes,
            # Komponen Pembatalan Sesuai Sheet QC Form
            "driver_penalty": driver_penalty,
            "driver_payout": driver_payout,
            "cancel_penalty_charge": cancel_penalty_charge,
            "waiting_fee_charge": waiting_fee_charge,
            "customer_charge": customer_charge,
            "coupon_issued": coupon_issued,
            "coupon_amount": coupon_amount,
            "gi_adj_event": gi_adj_event,
            "platform_net": platform_net,
            # Komponen Surcharge Metode Bayar User Apps
            "payment_method": clean_method.upper(),
            "is_ewallet_surcharge": is_ewallet,
            "charge_fee_amount": charge_fee_amount,
            "grand_total_customer": grand_total_customer,
            # Format Rupiah Persis
            "formatted_customer_charge": format_rupiah_exact(customer_charge),
            "formatted_driver_payout": format_rupiah_exact(driver_payout),
            "formatted_driver_penalty": format_rupiah_exact(driver_penalty),
            "formatted_coupon": format_rupiah_exact(coupon_amount),
            "formatted_charge_fee": format_rupiah_exact(charge_fee_amount),
            "formatted_grand_total": format_rupiah_exact(grand_total_customer)
        }

        logger.info(
            f"[CANCEL SETTLEMENT] Fase {phase} ({clean_by}) | Elapsed: {elapsed_int}s (m={billable_minutes}) | "
            f"Customer Charge: {res['formatted_customer_charge']} (Penalty: Rp {cancel_penalty_charge:,.0f}, Wait: Rp {waiting_fee_charge:,.0f}) | "
            f"Kupon: {'Ya (Rp 5.000)' if coupon_issued else 'Tidak'} | Driver Payout: {res['formatted_driver_payout']} | "
            f"Method: {clean_method.upper()} -> Grand Total: {res['formatted_grand_total']}"
        )
        return res

