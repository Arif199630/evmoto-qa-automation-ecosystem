"""E2E dua perangkat (Driver + User), metode bayar GoPay, akun dari GOPAY_TEST_PHONE (GoPay tertaut). Pass/fail tegas (E2E_STRICT=1): keluar kode 1 bila metode
tidak terpilih, order tidak terkirim/diterima/selesai. Isi alur sama dengan e2e_dua_perangkat.py."""
import os
import runpy
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.getenv("GOPAY_TEST_PHONE"):
    raise SystemExit("GOPAY_TEST_PHONE belum ada di Secret ENV_MOBILE_APPS")
os.environ["E2E_PHONE_VAR"] = "GOPAY_TEST_PHONE"

os.environ["E2E_METODE"] = "gopay"
os.environ["E2E_STRICT"] = "1"
os.environ.setdefault("E2E_USER_POOL_INDEX", "0")
runpy.run_path(str(Path(__file__).with_name("e2e_dua_perangkat.py")), run_name="__main__")
