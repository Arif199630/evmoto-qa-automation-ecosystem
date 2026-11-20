"""Verifikasi pembersih order sisa yang dipakai test (BasePage.batalkan_order_sisa_jika_ada: ketuk banner + dragGesture dari judul panel) pada akun pool 3, 12, 14
yang kemarin menyimpan order sisa. Mencatat hasil fungsi (True = order sisa dibatalkan), layar sebelum dan sesudah, dan memastikan Beranda kembali bersih.
Keluaran: reports/repro/diag_batal_sisa3/<pool>/index.txt dan screenshot."""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOLS = ("3", "12", "14")


def anak(pool: str):
    os.environ["TEST_USER_POOL_INDEX"] = pool
    sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]
    import peta_sedang_berjalan as p
    from config import config
    from core.driver_factory import DriverFactory
    from Pages.login_page import LoginPage
    from _diag_util import izinkan_lokasi

    p.OUT = ROOT / "reports" / "repro" / "diag_batal_sisa3" / pool
    p.OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(6)
        p.tutup_popup(d)
        time.sleep(2)
        p.save(d, "sebelum")
        t0 = time.time()
        hasil = login.batalkan_order_sisa_jika_ada()
        p.index.append(f"   batalkan_order_sisa_jika_ada() -> {hasil} dalam {time.time() - t0:.0f} dtk")
        time.sleep(3)
        xml = p.save(d, "sesudah")
        bersih = not d.find_elements("xpath", "//*[contains(@content-desc,'Sedang berjalan') or contains(@content-desc,'Menunggu Konfirmasi Driver') or contains(@content-desc,'Sedang mencari driver')]")
        p.index.append(f"   >> sesudah: Beranda bersih dari order sisa={bersih}; label={p.labels(xml)[:9]}")
    except Exception as e:  # noqa: BLE001
        p.index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        teks = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(p.index))
        (p.OUT / "index.txt").write_text(teks, encoding="utf-8")
        print(f"=== pool {pool}\n{teks}", flush=True)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--pool":
        anak(sys.argv[2])
        return
    for pool in POOLS:
        subprocess.run([sys.executable, str(Path(__file__).resolve()), "--pool", pool], timeout=900, check=False)


if __name__ == "__main__":
    main()
