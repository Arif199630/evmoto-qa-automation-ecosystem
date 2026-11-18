"""Sama dengan peta_sedang_berjalan2.py tetapi akun pool 5 (pembanding: apakah banner 'Sedang berjalanan' juga ada di akun lain)."""
import os

os.environ["MAP_POOL"] = "5"
import peta_sedang_berjalan2 as q  # noqa: E402

if __name__ == "__main__":
    q.main()
