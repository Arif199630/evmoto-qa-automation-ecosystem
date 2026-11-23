"""Diagnosa: peta isi Menu Driver (UAT 1.9.27) setelah digulir sampai bawah, lalu isi sub-menu 'Kelola Akun' dan 'Pengaturan Lainnya'.
Dasar: test DRV_MENU AL_01/02/04/05, PT_04, PT_16 mencari 'Keluar dari Akun', 'Hapus Akun', 'Bersihkan cache', 'Tentang Kami' langsung di layar Menu
dan tidak menemukannya meski layar sudah digulir; di dasar daftar hanya tampil judul 'Pengaturan Lainnya' dan 'Kelola Akun'.
Hanya teks label menu yang dicatat (tanpa nomor/nama akun). Keluaran: reports/repro/diag_menu_driver/index.txt."""
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_home_page import DrvHomePage  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_menu_page import DrvMenuPage  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402

OUT = ROOT / "reports" / "repro" / "diag_menu_driver"
baris = []


def label(d):
    src = d.page_source
    teks = re.findall(r'(?:content-desc|text)="([^"]{2,60})"', src)
    hasil = []
    for t in teks:
        t = t.replace("\n", " ")
        if re.search(r"\d{4}\*{4,}|\*{6,}", t) or t.startswith("Ping"):
            continue
        if t not in hasil:
            hasil.append(t)
    return hasil


def catat(judul, d):
    baris.append(f"{judul}: {label(d)}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver(is_driver_app=True)
    try:
        izinkan_lokasi(d)
        DrvLoginPage(d).login_as_driver()
        home = DrvHomePage(d)
        home.is_home_screen_displayed()
        home.navigate_to_menu()
        menu = DrvMenuPage(d)
        time.sleep(2)
        catat("menu_atas", d)
        for i in range(1, 5):
            menu.scroll_down()
            catat(f"menu_gulir_{i}", d)
        for nama in ("Kelola Akun", "Pengaturan Lainnya"):
            els = d.find_elements("xpath", f"//*[@content-desc='{nama}' or @text='{nama}']")
            if not els:
                baris.append(f"{nama}: tidak ditemukan")
                continue
            els[0].click()
            time.sleep(3)
            catat(f"isi_{nama}", d)
            try:
                d.save_screenshot(str(OUT / f"{nama.replace(' ', '_')}.png"))
            except Exception:  # noqa: BLE001
                pass
            d.press_keycode(4)
            time.sleep(2)
    except Exception as e:  # noqa: BLE001
        baris.append(f"GAGAL {type(e).__name__}: {str(e)[:120]}")
    finally:
        teks = "\n".join(baris)
        (OUT / "index.txt").write_text(teks, encoding="utf-8")
        print(teks)
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
