"""Peta halaman Akun dengan akun QA pool 14 (agar bisa dijalankan bersamaan dengan peta_akun.py yang memakai pool 15)."""
import os
import runpy
from pathlib import Path

os.environ.setdefault("MAP_POOL", "14")
runpy.run_path(str(Path(__file__).with_name("peta_akun.py")), run_name="__main__")
