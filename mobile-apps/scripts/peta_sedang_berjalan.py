"""Peta order 'Sedang berjalan' yang tertinggal di akun QA pool (hanya membaca): login pool MAP_POOL (default 3), ketuk kartu 'Sedang berjalan' di Beranda,
catat layar order (status, driver, tombol batal) di beberapa posisi gulir. Tidak membatalkan atau mengubah apa pun.
Latar belakang: pengamatan sirene (runs 44272370313 dan 44280723609) gagal karena Beranda User pool 13 dan pool 3 menampilkan 'Sedang berjalan'."""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL", "3")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "peta_sedang_berjalan"
index = []
step = 0


def labels(xml):
    return [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text|hint)="([^"]{1,80})"', xml))
            if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]


def bisa_diketuk(xml):
    hasil = []
    for m in re.finditer(r'<(\S+)\s([^>]*?)/?>', xml):
        a = m.group(2)
        if 'clickable="true"' not in a:
            continue
        d = re.search(r'content-desc="([^"]*)"', a) or re.search(r'text="([^"]*)"', a)
        b = re.search(r'bounds="([^"]+)"', a)
        lab = (d.group(1) if d else "(tanpa label)").replace("&#10;", "/")[:45]
        if not lab.startswith("Ping"):
            hasil.append(f"{m.group(1).split('.')[-1]} {b.group(1) if b else ''} '{lab}'")
    return hasil


def save(d, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(labels(xml)[:34]))
    index.append("      bisa diketuk: " + " ; ".join(bisa_diketuk(xml)[:14]))
    log(index[-2][:150])
    return xml


def tutup_popup(d):
    for el in d.find_elements("xpath", "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")[:1]:
        el.click()
        time.sleep(1.5)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(6)
        tutup_popup(d)
        xml = save(d, "beranda")
        kartu = d.find_elements("xpath", "//*[contains(@content-desc,'Sedang berjalan')]")
        index.append(f"   kartu 'Sedang berjalan' ditemukan: {len(kartu)}")
        if not kartu:
            return
        rc = kartu[0].rect
        d.execute_script("mobile: clickGesture", {"x": rc["x"] + rc["width"] // 2, "y": rc["y"] + rc["height"] // 2})
        for detik in (2, 5):
            time.sleep(detik)
            save(d, f"setelah_ketuk_kartu_{detik}dtk")
        size = d.get_window_size()
        x = size["width"] // 2
        for i in range(2):
            d.swipe(x, int(size["height"] * 0.90), x, int(size["height"] * 0.50), 600)
            time.sleep(1.5)
            save(d, f"panel_digeser_{i + 1}")
    except Exception as e:  # noqa: BLE001
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(d, "saat_error")
        except Exception:  # noqa: BLE001
            pass
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(index))
        (OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
