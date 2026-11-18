"""Peta lengkap halaman Akun (tab 'Me') sampai ke dalam 'Kelola Akun': daftar menu di tiap posisi gulir.
Hanya membaca: tidak menekan Log Out, Hapus Akun, atau tombol yang mengubah data. Akun QA pool MAP_POOL (default 15).
Hasil: reports/repro/peta_akun/NN_<layar>.xml dan index.txt (teks + daftar elemen yang bisa diketuk)."""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL", "15")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "peta_akun"
index = []
step = 0
LANJUTKAN = "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']"


def label_layar(xml):
    return [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text)="([^"]{1,80})"', xml))
            if t.strip() and t not in ("true", "false") and not t.startswith(("Ping", "PlatformException"))]


def save(d, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    try:
        versi = f" [{d.current_package}]"
    except Exception:
        versi = ""
    index.append(f"{step:02d}_{nama}{versi}: " + " | ".join(label_layar(xml)[:40]))
    log(index[-1][:150])
    return xml


def tutup_popup(d):
    for el in d.find_elements("xpath", LANJUTKAN)[:1]:
        el.click()
        time.sleep(1.5)


def ketuk(d, xpath, nama, tunggu=3):
    tutup_popup(d)
    els = d.find_elements("xpath", xpath)
    if not els:
        index.append(f"   tidak ditemukan: {nama}")
        return False
    els[0].click()
    time.sleep(tunggu)
    save(d, nama)
    return True


def gulir_dan_catat(d, awalan, kali=5):
    size = d.get_window_size()
    x = size["width"] // 2
    terakhir = None
    for i in range(kali):
        d.swipe(x, int(size["height"] * 0.75), x, int(size["height"] * 0.30), 500)
        time.sleep(1.0)
        xml = save(d, f"{awalan}_gulir_{i + 1}")
        sekarang = tuple(label_layar(xml))
        if sekarang == terakhir:
            index.append(f"   {awalan}: sudah di dasar halaman setelah {i + 1} gulir")
            break
        terakhir = sekarang


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
        time.sleep(5)
        akun_xpath = "//android.widget.ImageView[starts-with(@content-desc, 'Akun')]"
        for percobaan in range(1, 5):
            tutup_popup(d)
            d.find_elements("xpath", akun_xpath)[0].click() if d.find_elements("xpath", akun_xpath) else None
            time.sleep(3)
            if d.find_elements("xpath", "//*[@content-desc='Pengaturan Pembayaran']"):
                break
        save(d, "akun_atas")
        gulir_dan_catat(d, "akun")
        # Masuk 'Kelola Akun' (dibaca saja). Gulir balik ke atas dulu agar elemen terlihat bila perlu.
        if ketuk(d, "//*[contains(@content-desc,'Kelola Akun')]", "kelola_akun", 4):
            save(d, "kelola_akun_atas")
            gulir_dan_catat(d, "kelola")
    except Exception as e:
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:160]}")
        try:
            save(d, "saat_error")
        except Exception:
            pass
    finally:
        try:
            d.quit()
        except Exception:
            pass
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(index))
        (OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
