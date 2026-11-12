"""
Peta layar halaman Aktivitas aplikasi User (akun utama yang punya riwayat pesanan), untuk memperbaiki
locator test_activity berdasarkan layar asli.

Hanya membuka layar lalu kembali: tidak mengirim penilaian, tidak memesan, tidak membatalkan apa pun.
Hasil: reports/repro/map_activity/NN_<layar>.xml|.png dan index.txt
"""
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "map_activity"
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
    index.append(f"{step:02d}_{nama}: " + " | ".join(teks(xml)[:16]).replace("&#10;", "\\n"))


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


def back(driver):
    driver.back()
    time.sleep(2)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    driver = DriverFactory.create_driver()
    try:
        log("driver siap, cek layar login")
        izinkan_lokasi(driver)
        login = LoginPage(driver)
        if login.is_login_screen_displayed(timeout=20):
            log("login akun utama")
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        log("OTP selesai, tunggu Beranda")
        time.sleep(5)
        izinkan_lokasi(driver)
        for label in ("Lanjutkan", "Nanti", "Tutup", "OK"):  # popup sambutan / jam operasional bila ada
            els = driver.find_elements("xpath", f"//*[@content-desc='{label}' or @text='{label}']")
            if els:
                els[0].click()
                time.sleep(1)
        save(driver, "beranda")
        tap(driver, "//*[@content-desc='Aktivitas' and @clickable='true']", "aktivitas_reguler", 5)
        tap(driver, "//*[starts-with(@content-desc, 'Booking')]", "tab_booking", 4)
        tap(driver, "//*[starts-with(@content-desc, 'Reguler')]", "tab_reguler_lagi", 4)
        if tap(driver, "(//*[starts-with(@content-desc, 'Normal') and @clickable='true'])[1]", "detail_kartu_pertama", 5):
            for t in range(3):  # gulir rincian untuk melihat seluruh isi
                driver.swipe(160, 500, 160, 200, 600)
                time.sleep(1)
                save(driver, f"detail_gulir_{t + 1}")
            back(driver)
        if tap(driver, "//*[@content-desc='Beri penilaian']", "modal_beri_penilaian", 4):
            back(driver)
        save(driver, "setelah_kembali")
        if tap(driver, "(//*[@content-desc='Pesan Lagi'])[1]", "pesan_lagi", 5):
            back(driver)
            save(driver, "setelah_kembali_dari_pesan_lagi")
    except Exception as e:
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(driver, "saat_error")
        except Exception:
            pass
    finally:
        driver.quit()
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(index))
        (OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
