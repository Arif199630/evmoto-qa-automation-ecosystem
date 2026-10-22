"""
================================================================================
EVMOTO CASHLESS WALLET BALANCE HELPER & TRANSACTION LEDGER AUDITOR
================================================================================
Tujuan: Memvalidasi pemotongan saldo dompet digital cashless (EvWallet) pengguna
        secara presisi saat memesan dan menyelesaikan perjalanan di aplikasi User.
Aturan Bisnis:
  1. Sebelum order: Catat Saldo Awal (balance_before).
  2. Saat order selesai: Potong saldo sebesar Total Tarif Perjalanan (fare_amount).
  3. Formula: balance_after == balance_before - fare_amount.
  4. Audit: Tidak boleh terjadi double-deduction atau potongan yang tidak sesuai.
================================================================================
"""
from typing import Dict, Any, Tuple
from utils.logger import get_logger

logger = get_logger("WalletBalanceHelper")


class WalletBalanceHelper:
    """Helper Pengelola & Auditor Saldo Dompet Digital Cashless (EvWallet)."""

    def __init__(self, initial_balance: int = 150000):
        self._current_balance = initial_balance
        self._initial_balance = initial_balance
        self._transactions = []
        logger.info(f"[WALLET HELPER] Saldo Awal Pengguna Diinisialisasi: Rp {self._current_balance:,}")

    def get_current_balance(self) -> int:
        """Mengambil saldo saat ini."""
        return self._current_balance

    def get_formatted_balance(self) -> str:
        """Mengambil teks saldo terformat (misal: 'Rp 150.000')."""
        return f"Rp {self._current_balance:,}".replace(",", ".")

    def deduct_fare(self, fare_amount: int, order_id: str = "ORD-DEV-001") -> Dict[str, Any]:
        """
        Memproses pemotongan saldo cashless sebesar tarif pesanan.
        """
        balance_before = self._current_balance
        if balance_before < fare_amount:
            raise ValueError(f"Saldo tidak cukup! Saldo: Rp {balance_before:,}, Tagihan: Rp {fare_amount:,}")

        balance_after = balance_before - fare_amount
        self._current_balance = balance_after

        txn = {
            "order_id": order_id,
            "type": "TRIP_PAYMENT_CASHLESS",
            "fare_deducted": fare_amount,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "status": "SUCCESS"
        }
        self._transactions.append(txn)
        logger.info(
            f"[WALLET MUTATION] Pemotongan Cashless Order {order_id}: "
            f"Saldo Awal = Rp {balance_before:,} - Tarif = Rp {fare_amount:,} -> Saldo Akhir = Rp {balance_after:,}"
        )
        return txn

    def verify_deduction(
        self,
        balance_before: int,
        balance_after: int,
        expected_fare: int
    ) -> Tuple[bool, str]:
        """
        Memvalidasi keakuratan matematis dari pemotongan saldo cashless.
        """
        actual_deduction = balance_before - balance_after
        is_exact = (actual_deduction == expected_fare) and (balance_after < balance_before)

        msg = (
            f"Audit Pemotongan Saldo: "
            f"Awal = Rp {balance_before:,} | "
            f"Akhir = Rp {balance_after:,} | "
            f"Terpotong = Rp {actual_deduction:,} | "
            f"Tarif Argo = Rp {expected_fare:,} -> "
            f"{'VALID & BERKURANG AKURAT (PASS)' if is_exact else 'ANOMALI PEMOTONGAN SALDO (FAIL)'}"
        )
        logger.info(msg)
        return is_exact, msg
