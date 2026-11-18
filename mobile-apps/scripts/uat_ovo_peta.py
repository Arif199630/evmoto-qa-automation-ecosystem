"""Peta layar Pengaturan Pembayaran / Aktifkan OVO untuk persiapan UAT OVO (hanya membaca, tidak mengubah data).
Memakai akun QA pool 15 (OVO belum tertaut) agar tidak bentrok dengan akun utama yang dipakai run lain.
Isi sama dengan map_pembayaran.py (TIDAK mengetik nomor e-wallet, tidak membayar)."""
import os
import runpy
from pathlib import Path

os.environ.setdefault("MAP_POOL_INDEX", "15")
runpy.run_path(str(Path(__file__).with_name("map_pembayaran.py")), run_name="__main__")
