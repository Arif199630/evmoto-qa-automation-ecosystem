"""Peta pembatalan order dari sisi User saat status 'Sedang mencari driver' (staging, akun QA pool 14).

Tujuan: mengetahui tombol pembatalan yang sebenarnya (panel bawah berukuran 320x640 memotong tombolnya) supaya test bisa
membersihkan order sisa. Alur: pesan order -> panel pencarian -> geser panel ke atas -> catat semua elemen yang bisa diketuk ->
ketuk tombol batal -> catat dialog -> konfirmasi pembatalan -> pastikan akun kembali bersih. Order yang dibuat langsung dibatalkan.
Hasil: reports/repro/peta_batal_order/NN_<layar>.xml|.png dan index.txt."""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL", "14")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from Pages.booking_page import BookingPage  # noqa: E402
from _diag_util import izinkan_lokasi, log, pesan_order  # noqa: E402

OUT = ROOT / "reports" / "repro" / "peta_batal_order"
index = []
step = 0
LANJUTKAN = "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']"


def labels(xml):
    return [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text)="([^"]{1,80})"', xml))
            if t.strip() and t not in ("true", "false") and not t.startswith(("Ping", "PlatformException"))]


def bisa_diketuk(xml):
    hasil = []
    for m in re.finditer(r'<(\S+)\s([^>]*?)/?>', xml):
        a = m.group(2)
        if 'clickable="true"' not in a:
            continue
        d = re.search(r'content-desc="([^"]*)"', a) or re.search(r'text="([^"]*)"', a)
        b = re.search(r'bounds="([^"]+)"', a)
        lab = (d.group(1) if d else "(tanpa label)").replace("&#10;", "/")[:45]
        if lab.startswith("Ping"):
            continue
        hasil.append(f"{m.group(1).split('.')[-1]} {b.group(1) if b else ''} '{lab}'")
    return hasil


def save(d, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(labels(xml)[:30]))
    index.append("      bisa diketuk: " + " ; ".join(bisa_diketuk(xml)[:14]))
    log(index[-2][:150])
    return xml


def tutup_popup(d):
    for el in d.find_elements("xpath", LANJUTKAN)[:1]:
        el.click()
        time.sleep(1.5)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    dipesan = False
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(5)
        tutup_popup(d)
        save(d, "beranda_awal")
        BookingPage(d).open_place_order("Senayan City")
        save(d, "place_order")
        dipesan = pesan_order(d)
        index.append(f"   order dipesan: {dipesan}")
        time.sleep(4)
        save(d, "panel_pencarian")
        size = d.get_window_size()
        x = size["width"] // 2
        # Panel bawah terpotong: geser ke atas agar tombol terlihat
        d.swipe(x, int(size["height"] * 0.93), x, int(size["height"] * 0.55), 600)
        time.sleep(1.5)
        save(d, "panel_digeser_atas")
        batal = d.find_elements("xpath", "//*[contains(@content-desc,'Batalkan') or contains(@text,'Batalkan') or "
                                         "contains(@content-desc,'Batal') or contains(@text,'Batal')]")
        index.append(f"   elemen berlabel 'Batal...': {len(batal)}")
        if batal:
            batal[0].click()
        else:  # tombol kiri (abu-abu) di dasar panel, dugaan: Batalkan
            d.execute_script("mobile: clickGesture", {"x": int(size["width"] * 0.30), "y": int(size["height"] * 0.93)})
        time.sleep(2)
        save(d, "setelah_ketuk_batal")
        for label in ("Ya, Batalkan", "Batalkan Pesanan", "Ya", "Konfirmasi"):
            els = d.find_elements("xpath", f"//*[@content-desc='{label}' or @text='{label}']")
            if els:
                index.append(f"   mengetuk konfirmasi '{label}'")
                els[0].click()
                time.sleep(2)
                save(d, f"setelah_konfirmasi_{label.replace(' ', '_').replace(',', '')}")
                break
        # Alasan pembatalan bila diminta
        radio = d.find_elements("xpath", "//android.widget.RadioButton | //*[contains(@content-desc,'Alasan')]")
        if radio:
            index.append(f"   layar alasan pembatalan terdeteksi ({len(radio)} elemen)")
            save(d, "alasan_pembatalan")
        time.sleep(3)
        xml = save(d, "akhir")
        bersih = "Sedang mencari driver" not in xml
        index.append(f"   HASIL: akun kembali bersih (tanpa 'Sedang mencari driver') = {bersih}")
    except Exception as e:
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
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
