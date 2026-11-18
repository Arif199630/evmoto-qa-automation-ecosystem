"""E2E dua perangkat (Driver + User), metode bayar Saldo EVMoto, akun utama (saldo cukup). Pass/fail tegas (E2E_STRICT=1): keluar kode 1 bila metode
tidak terpilih, order tidak terkirim/diterima/selesai, dan saldo User tidak berkurang. Isi alur sama dengan e2e_dua_perangkat.py."""
import os
import runpy
from pathlib import Path

os.environ["E2E_METODE"] = "wallet"
os.environ["E2E_STRICT"] = "1"
os.environ.setdefault("E2E_USER_POOL_INDEX", "0")
runpy.run_path(str(Path(__file__).with_name("e2e_dua_perangkat.py")), run_name="__main__")
