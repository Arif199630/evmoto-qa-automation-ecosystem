"""Peta alur OVO dengan akun UAT A (nomor dari secret DRIVER_KANDIDAT, kandidat 4). MODE HANYA LIHAT: akun sudah tertaut OVO, tidak ada yang diketuk selain navigasi.
Nama berkas harus huruf kecil: langkah 'skrip' di workflow memakai pola ^[a-z0-9_]+[.]py$."""
import os
import runpy
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.getenv("DRIVER_KANDIDAT_4"):
    raise SystemExit("DRIVER_KANDIDAT_4 belum ada di .env (secret DRIVER_KANDIDAT)")
os.environ["UAT_AKUN_VAR"] = "DRIVER_KANDIDAT_4"
os.environ["UAT_HANYA_LIHAT"] = "1"
runpy.run_path(str(Path(__file__).with_name("uat_ovo_alur.py")), run_name="__main__")
