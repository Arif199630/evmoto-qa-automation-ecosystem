"""
Ukur waktu mencari elemen di Beranda User (layar dengan Google Maps) dengan beberapa cara, untuk memilih strategi
locator yang tidak macet di emulator CI (pembacaan layar XPath / page source macet 240 dtk, CI 12 Nov 2026).

Cara yang diukur: UiSelector (tanpa membuat XML seluruh layar), accessibility id, XPath, dan page source.
Hasil: reports/repro/ukur_peta/ringkasan.txt (+ screenshot)
"""
import os
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL_INDEX", "12")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "ukur_peta"
hasil = []


def ukur(driver, nama, fn, batas=90):
    """Jalankan fn dengan batas waktu Appium 'newCommandTimeout' bawaan; catat durasi dan jumlah elemen."""
    t0 = time.time()
    try:
        r = fn()
        n = len(r) if isinstance(r, list) else (len(r) if isinstance(r, str) else 1)
        hasil.append(f"{nama:55} {time.time() - t0:6.1f} dtk  hasil={n}")
    except Exception as e:
        hasil.append(f"{nama:55} {time.time() - t0:6.1f} dtk  GAGAL {type(e).__name__}: {str(e)[:90]}")
    log(hasil[-1])


def putaran(driver, label):
    hasil.append(f"== {label}")
    ukur(driver, "UiSelector descriptionContains('Saldo Anda')", lambda: driver.find_elements(
        "-android uiautomator", 'new UiSelector().descriptionContains("Saldo Anda")'))
    ukur(driver, "UiSelector textContains/hint kolom tujuan (EditText)", lambda: driver.find_elements(
        "-android uiautomator", 'new UiSelector().className("android.widget.EditText")'))
    ukur(driver, "accessibility id 'Isi Ulang'", lambda: driver.find_elements("accessibility id", "Isi Ulang"))
    ukur(driver, "XPath //*[@content-desc='Isi Ulang']", lambda: driver.find_elements("xpath", "//*[@content-desc='Isi Ulang']"))
    ukur(driver, "XPath contains(@content-desc,'Rumah')", lambda: driver.find_elements("xpath", "//*[contains(@content-desc,'Rumah')]"))
    ukur(driver, "page_source", lambda: driver.page_source)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    driver = DriverFactory.create_driver()
    try:
        izinkan_lokasi(driver)
        login = LoginPage(driver)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        izinkan_lokasi(driver)
        putaran(driver, "Beranda +0 dtk setelah login")
        time.sleep(15)
        izinkan_lokasi(driver)
        driver.save_screenshot(str(OUT / "beranda_15dtk.png"))
        putaran(driver, "Beranda +15 dtk (peta sudah termuat)")
    except Exception as e:
        hasil.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        (OUT / "ringkasan.txt").write_text("\n".join(hasil), encoding="utf-8")
        print("\n".join(hasil))


if __name__ == "__main__":
    main()
