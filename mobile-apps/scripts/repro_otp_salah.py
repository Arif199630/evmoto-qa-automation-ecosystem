"""
Reproduksi dugaan bug: pesan 'Kode verifikasi salah' tidak muncul saat OTP salah dimasukkan (test_login NT-01/PF-04).

Pesan error Flutter sering berupa snackbar/toast yang hanya tampil 2-4 detik, sehingga layar direkam tiap ±0,4 detik
selama 8 detik setelah OTP salah diketik. Satu kali percobaan saja (tidak memicu batas percobaan).
Hasil: reports/repro/otp_salah/NN_<langkah>.xml|.png dan ringkasan.txt
"""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("REPRO_POOL_INDEX", "12")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from _diag_util import buka_aplikasi_bersih, izinkan_lokasi  # noqa: E402

OUT = ROOT / "reports" / "repro" / "otp_salah"
summary = []


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text)="([^"]{1,70})"', xml)
            if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    phone = config.ACTIVE_PHONE
    otp_benar = config.ACTIVE_OTP
    otp_salah = "".join(str((int(c) + 1) % 10) for c in otp_benar)  # 4 digit, pasti berbeda dari OTP dev
    summary.append(f"akun {phone[:4]}****{phone[-2:]} | OTP salah = OTP dev dengan tiap digit +1")
    driver = DriverFactory.create_driver()
    try:
        buka_aplikasi_bersih(driver, config.APP_PACKAGE)
        login = LoginPage(driver)
        login.is_login_screen_displayed(timeout=25)
        login.input_phone_number(phone)
        login.click_submit_login()
        login.find(login.TITLE_OTP, timeout=15)
        field = login.find(login.FIELD_OTP, timeout=10)
        izinkan_lokasi(driver)
        field = login.find(login.FIELD_OTP, timeout=10)
        field.click()
        t0 = time.time()
        for ch in otp_salah:
            driver.press_keycode(int(ch) + 7)
            time.sleep(0.15)
        seen = {}
        for i in range(20):
            if izinkan_lokasi(driver):
                summary.append(f"  +{time.time() - t0:4.1f} dtk: dialog izin lokasi Android muncul dan diketuk (bukan bagian aplikasi)")
            xml = dump_ringan(driver)
            items = teks(xml)
            for t in items:
                seen.setdefault(t, round(time.time() - t0, 1))
            if i % 4 == 0 or any("salah" in t.lower() or "invalid" in t.lower() or "wrong" in t.lower() for t in items):
                (OUT / f"{i:02d}_detik_{time.time() - t0:.1f}.xml").write_text(xml, encoding="utf-8")
                driver.save_screenshot(str(OUT / f"{i:02d}_detik_{time.time() - t0:.1f}.png"))
            summary.append(f"  +{time.time() - t0:4.1f} dtk: " + " | ".join(items[:8]))
            time.sleep(0.25)
        summary.append("teks yang pernah tampil (detik pertama muncul): " + "; ".join(f"{k} (+{v})" for k, v in seen.items()))
        pesan = [k for k in seen if "salah" in k.lower() or "invalid" in k.lower() or "wrong" in k.lower()]
        summary.append("HASIL: pesan OTP salah " + (f"TAMPIL: {pesan}" if pesan else "TIDAK tampil dalam 8 detik"))
    except Exception as e:
        summary.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
    finally:
        driver.quit()
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(summary))
        (OUT / "ringkasan.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
