"""E2E dua perangkat dengan akun QA pool 12 (pemilik order sisa run multi-pengguna 43348861484): order sisa
diselesaikan lewat Driver (tahap + pembayaran Cash), lalu satu order baru dijalankan sampai selesai."""
import os
import runpy
from pathlib import Path

os.environ["E2E_USER_POOL_INDEX"] = "12"
runpy.run_path(str(Path(__file__).with_name("e2e_dua_perangkat.py")), run_name="__main__")
