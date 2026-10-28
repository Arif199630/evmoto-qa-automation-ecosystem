"""
================================================================================
EVMOTO RUSH HOUR DRIVER SUBSIDY ENGINE & CALCULATOR (PRODUCTION GRADE)
================================================================================
Fitur: Subsidi Rush Hour Driver (Income Bonus Jam Sibuk)
Aturan Bisnis:
  1. Setting dan konfigurasi harga, tier, dan jam sibuk berada di Dashboard Admin:
     https://evmotoadmin.justkidding.app/rushHour/settings
  2. Subsidi dihitung HANYA berdasarkan 'Argo Original' (Base Fare murni perjalanan).
     - Potongan Voucher / Kupon Promo TIDAK mengurangi nilai acuan subsidi.
     - Waiting Fee (Biaya Menunggu) TIDAK menambah nilai acuan subsidi.
     - Penalty / Denda Pembatalan TIDAK mempengaruhi tier subsidi.
  3. Window Waktu (Jam Mulai s/d Jam Selesai) bersifat inklusif batasnya.
     - Jika waktu order berada di dalam window: berhak mendapatkan subsidi sesuai tier.
     - Jika waktu order berada di luar window: subsidi = Rp 0.
  4. Toggle Status 'Bayar Subsidi':
     - Jika enabled = False: Tidak ada subsidi yang dibayarkan (Rp 0).
  5. Bersifat Seamless dari sisi Driver:
     - Driver menerima akumulasi penghasilan bersih (net payout) yang bertambah,
       tanpa menampilkan badge/aturan internal subsidi pada UI order driver.
  6. Batas Harian (Daily Budget): Di-bypass/diabaikan sesuai arahan bisnis saat ini.
================================================================================
"""

from datetime import datetime, time
from typing import Dict, Any, List, Optional, Union
from utils.logger import get_logger

logger = get_logger("RushHourCalculator")


class RushHourSubsidyCalculator:
    """Kalkulator perhitungan Subsidi Jam Sibuk Driver EvMoto resmi."""

    DEFAULT_SETTINGS = {
        "enabled": True,
        "windows": [
            {"start": "06:45", "end": "08:45"},
            {"start": "10:45", "end": "18:45"}
        ],
        "tiers": [
            {"max": 10000, "subsidy": 3000},
            {"max": 20000, "subsidy": 4000},
            {"max": None, "subsidy": 5000}
        ],
        "dailyBudget": None
    }

    @staticmethod
    def parse_time(time_str: str) -> time:
        """Parse format HH:MM ke objek datetime.time."""
        parts = time_str.strip().split(":")
        return time(int(parts[0]), int(parts[1]))

    @classmethod
    def is_within_rush_hour(
        cls,
        order_time: Union[datetime, time, str],
        windows: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        Memeriksa apakah waktu order berada di dalam salah satu window jam sibuk.
        Batas jam mulai dan selesai bersifat INKLUSIF.
        """
        if windows is None:
            windows = cls.DEFAULT_SETTINGS["windows"]

        # Konversi ke datetime.time
        if isinstance(order_time, datetime):
            target_time = order_time.time()
        elif isinstance(order_time, str):
            if " " in order_time:
                # Format: YYYY-MM-DD HH:MM:SS
                dt = datetime.strptime(order_time.strip(), "%Y-%m-%d %H:%M:%S")
                target_time = dt.time()
            else:
                target_time = cls.parse_time(order_time)
        elif isinstance(order_time, time):
            target_time = order_time
        else:
            raise ValueError(f"Tipe waktu order tidak valid: {type(order_time)}")

        for w in windows:
            start_t = cls.parse_time(w["start"])
            end_t = cls.parse_time(w["end"])
            # Inklusif: start_t <= target_time <= end_t
            # Note: per detik diabaikan jika format HH:MM atau perbandingan time langsung
            target_minute_precision = time(target_time.hour, target_time.minute)
            if start_t <= target_minute_precision <= end_t:
                return True

        return False

    @classmethod
    def get_tier_subsidy(
        cls,
        original_base_fare: float,
        tiers: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        Menentukan nominal subsidi berdasarkan Tier harga argo original.
        Batas atas (max) bersifat inklusif dan harus dievaluasi berurutan menaik.
        """
        if tiers is None:
            tiers = cls.DEFAULT_SETTINGS["tiers"]

        for tier in tiers:
            max_val = tier.get("max")
            subsidy = int(tier.get("subsidy", 0))

            if max_val is None:
                # Tier tanpa batas (unlimited)
                return subsidy
            elif float(original_base_fare) <= float(max_val):
                return subsidy

        return 0

    @classmethod
    def calculate_order_subsidy(
        cls,
        order_time: Union[datetime, time, str],
        original_base_fare: float,
        voucher_discount: float = 0.0,
        waiting_fee: float = 0.0,
        penalty_fee: float = 0.0,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Kalkulasi resmi Subsidi Jam Sibuk Driver untuk satu order:
          - Memastikan penentuan tier HANYA menggunakan original_base_fare murni.
          - Menghitung isolasi terhadap voucher, waiting fee, dan penalty.
          - Mengembalikan rincian komprehensif untuk validasi audit QA.
        """
        cfg = settings or cls.DEFAULT_SETTINGS
        is_enabled = cfg.get("enabled", True)
        windows = cfg.get("windows", cls.DEFAULT_SETTINGS["windows"])
        tiers = cfg.get("tiers", cls.DEFAULT_SETTINGS["tiers"])

        # 1. Cek apakah fitur aktif di Dashboard Admin
        if not is_enabled:
            return {
                "is_rush_hour": False,
                "is_enabled": False,
                "applied_subsidy": 0,
                "original_base_fare": original_base_fare,
                "user_paid_fare": original_base_fare - voucher_discount + waiting_fee + penalty_fee,
                "reason": "Fitur Subsidi Jam Sibuk dinonaktifkan (enabled = False) di Admin Dashboard."
            }

        # 2. Cek apakah waktu order berada dalam window aktif
        in_window = cls.is_within_rush_hour(order_time, windows)
        if not in_window:
            return {
                "is_rush_hour": False,
                "is_enabled": True,
                "applied_subsidy": 0,
                "original_base_fare": original_base_fare,
                "user_paid_fare": original_base_fare - voucher_discount + waiting_fee + penalty_fee,
                "reason": f"Waktu order ({order_time}) berada di luar window jam sibuk yang disetup."
            }

        # 3. Tentukan Subsidi murni dari original_base_fare
        subsidy_amount = cls.get_tier_subsidy(original_base_fare, tiers)

        # 4. Verifikasi bahwa user_paid_fare (setelah voucher/fee) TIDAK mempengaruhi tier
        user_paid_fare = original_base_fare - voucher_discount + waiting_fee + penalty_fee

        return {
            "is_rush_hour": True,
            "is_enabled": True,
            "applied_subsidy": subsidy_amount,
            "original_base_fare": original_base_fare,
            "voucher_discount": voucher_discount,
            "waiting_fee": waiting_fee,
            "penalty_fee": penalty_fee,
            "user_paid_fare": user_paid_fare,
            "calculation_basis": "STRICT_ORIGINAL_BASE_FARE",
            "matched_tier": next(
                (f"<= {t['max']}" if t['max'] else "Tanpa Batas" for t in tiers if (t['max'] is None or original_base_fare <= t['max'])),
                "None"
            ),
            "reason": f"Order valid jam sibuk. Subsidi Rp {subsidy_amount:,} diberikan berdasarkan argo original Rp {original_base_fare:,}."
        }
