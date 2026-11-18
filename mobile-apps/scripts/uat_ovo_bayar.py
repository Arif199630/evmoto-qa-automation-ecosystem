"""UAT OVO B1: E2E dua perangkat (Driver + User), metode bayar OVO, akun UAT A (nomor dari secret DRIVER_KANDIDAT, kandidat 4; OVO sudah tertaut).
Driver memakai akun DRIVER_KANDIDAT_2 (bukan akun Driver utama, supaya tidak bentrok dengan run lain). Vonis tegas (E2E_STRICT=1).
Nama berkas huruf kecil: pola langkah 'skrip' di workflow adalah ^[a-z0-9_]+[.]py$."""
import os
import runpy
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.getenv("DRIVER_KANDIDAT_4") or not os.getenv("DRIVER_KANDIDAT_2"):
    raise SystemExit("DRIVER_KANDIDAT_2 dan _4 harus ada di .env (secret DRIVER_KANDIDAT)")
os.environ["E2E_METODE"] = "ovo"
os.environ["E2E_STRICT"] = "1"
os.environ["E2E_PHONE_VAR"] = "DRIVER_KANDIDAT_4"
os.environ["E2E_USER_POOL_INDEX"] = "0"
os.environ["TEST_DRIVER_POOL_INDEX"] = "1"   # -> DRIVER_KANDIDAT_2 untuk aplikasi Driver
runpy.run_path(str(Path(__file__).with_name("e2e_dua_perangkat.py")), run_name="__main__")
