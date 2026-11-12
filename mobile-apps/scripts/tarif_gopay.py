"""Tarif per kategori jarak x metode bayar memakai akun User yang GoPay-nya tertaut (nomor dari GOPAY_TEST_PHONE di
.env / Secret ENV_MOBILE_APPS, tidak pernah dicetak utuh). Isi pengujian sama dengan tarif_metode_bayar.py."""
import os
import runpy
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.getenv("GOPAY_TEST_PHONE"):
    raise SystemExit("GOPAY_TEST_PHONE belum ada di Secret ENV_MOBILE_APPS")
os.environ["TARIF_PHONE_VAR"] = "GOPAY_TEST_PHONE"
runpy.run_path(str(Path(__file__).with_name("tarif_metode_bayar.py")), run_name="__main__")
