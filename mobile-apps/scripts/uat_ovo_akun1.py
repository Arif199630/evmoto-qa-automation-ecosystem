"""Peta alur penautan OVO memakai akun UAT nomor 1 (nomor dari secret UAT_OVO_PHONES -> .env: UAT_OVO_NOMOR1). Hanya mengamati."""
import os
import runpy
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.getenv("UAT_OVO_NOMOR1"):
    raise SystemExit("UAT_OVO_NOMOR1 belum ada: jalankan dengan apk_set=uat (secret UAT_OVO_PHONES)")
os.environ["UAT_AKUN_VAR"] = "UAT_OVO_NOMOR1"
runpy.run_path(str(Path(__file__).with_name("uat_ovo_alur.py")), run_name="__main__")
