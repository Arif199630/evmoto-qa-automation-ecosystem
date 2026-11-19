"""Pengamatan Kontak Darurat di layar perjalanan: E2E dua perangkat (Driver + User, Cash, akun QA pool 5) yang mengetuk ikon sirene merah
setelah tahap pertama perjalanan dan mencatat layar yang muncul. Tanpa vonis tegas (E2E_STRICT=0): tujuannya mengamati, bukan lulus/gagal."""
import os
import runpy
from pathlib import Path

os.environ["E2E_METODE"] = "cash"
os.environ["E2E_STRICT"] = "0"
os.environ["E2E_CEK_DARURAT"] = "1"
os.environ.setdefault("E2E_USER_POOL_INDEX", "5")  # pool 3 punya order "mencari driver" tertinggal dan pool 13 tertahan order aktif; pool 5 bersih (peta run 44283331433)
runpy.run_path(str(Path(__file__).with_name("e2e_dua_perangkat.py")), run_name="__main__")
