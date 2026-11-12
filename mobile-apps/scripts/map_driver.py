"""
Peta layar lengkap aplikasi Driver (termasuk bagian yang perlu digulir dan tab ketiga), untuk memperbaiki locator
test_drv_menu / test_drv_activity berdasarkan layar asli.

Hanya membuka layar lalu kembali: tidak Online, tidak logout, tidak menghapus akun, tidak mengirim masukan.
'Cara Penggunaan Aplikasi' dibuka paling akhir karena emulator CI mati saat layar itu terbuka (run 43134989584).
Hasil: reports/repro/map_driver/NN_<layar>.xml|.png dan index.txt
"""
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_home_page import DrvHomePage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "map_driver"
index = []
step = 0


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml) if t.strip() and t not in ("true", "false")]


def save(driver, nama):
    global step
    step += 1
    log(f"simpan layar {step:02d}_{nama}")
    xml = driver.page_source
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    driver.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(teks(xml)[:24]).replace("&#10;", "\\n"))


def tap(driver, xpath, nama, tunggu=3):
    log(f"ketuk {nama}")
    izinkan_lokasi(driver)
    els = driver.find_elements("xpath", xpath)
    if not els:
        index.append(f"   tidak ditemukan: {nama} ({xpath})")
        return False
    els[0].click()
    time.sleep(tunggu)
    save(driver, nama)
    return True


def gulir(driver, nama, kali=3):
    size = driver.get_window_size()
    for i in range(kali):
        driver.swipe(size["width"] // 2, int(size["height"] * 0.75), size["width"] // 2, int(size["height"] * 0.3), 600)
        time.sleep(1.5)
        save(driver, f"{nama}_gulir_{i + 1}")


def back(driver):
    driver.back()
    time.sleep(2)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    driver = DriverFactory.create_driver(is_driver_app=True)
    try:
        log("login driver")
        DrvLoginPage(driver).login_as_driver()
        time.sleep(5)
        izinkan_lokasi(driver)
        try:
            DrvHomePage(driver).dismiss_operational_popup()
        except Exception:
            pass
        save(driver, "beranda")
        gulir(driver, "beranda", 2)
        # Menu (bagian bawah biasanya berisi bahasa, logout, hapus akun)
        if tap(driver, "//*[starts-with(@content-desc, 'Menu')]", "menu", 3):
            gulir(driver, "menu", 3)
        tap(driver, "//*[starts-with(@content-desc, 'Beranda')]", "kembali_beranda", 3)
        # Aktivitas Saya: tiga tab (tab ketiga di luar layar, perlu digeser)
        if tap(driver, "//*[@content-desc='Aktivitas Saya']", "aktivitas_saya", 4):
            tap(driver, "//*[starts-with(@content-desc, 'Coupon Income')]", "tab_coupon_income", 3)
            size = driver.get_window_size()
            driver.swipe(int(size["width"] * 0.85), 110, int(size["width"] * 0.15), 110, 500)  # geser baris tab
            time.sleep(1)
            save(driver, "tab_digeser")
            tap(driver, "//*[contains(@content-desc, 'Tab 3 dari 3') or contains(@content-desc, 'Tab 3 of 3')]", "tab_ketiga", 3)
            back(driver)
        if tap(driver, "//*[@content-desc='Order Saya']", "order_saya", 4):
            tap(driver, "//*[starts-with(@content-desc, 'Normal Order')]", "tab_normal_order", 3)
            tap(driver, "//*[starts-with(@content-desc, 'Advance Booking')]", "tab_advance_booking", 3)
            back(driver)
        if tap(driver, "//*[starts-with(@content-desc, 'Menu')]", "menu_lagi", 3):
            if tap(driver, "//*[@content-desc='Kirim Masukan']", "kirim_masukan", 3):
                back(driver)
            if tap(driver, "//*[@content-desc='Evaluasi Saya']", "evaluasi_saya", 3):
                back(driver)
            if tap(driver, "//*[@content-desc='Cara Penggunaan Aplikasi']", "cara_penggunaan_5dtk", 5):
                gulir(driver, "cara_penggunaan", 3)
                back(driver)
                save(driver, "setelah_cara_penggunaan")
    except Exception as e:
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(driver, "saat_error")
        except Exception:
            pass
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(index))
        (OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
