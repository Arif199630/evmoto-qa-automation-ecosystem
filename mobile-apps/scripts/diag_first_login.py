"""
Diagnosa layar 'Masukkan nama pengguna' setelah login akun QA Auto, dengan bukti di setiap langkah.

Pertanyaan yang dijawab:
  1. Berapa detik setelah OTP layar nama (atau Beranda) muncul?
  2. Apakah nama yang diketik benar-benar masuk ke kolom, dan apakah 'Simpan' membawa ke Beranda?
  3. Setelah aplikasi dibuka ulang, apakah layar nama muncul lagi (nama tidak tersimpan) atau langsung Beranda?
Hasil: reports/repro/diag_first_login/NN_<langkah>.xml|.png dan ringkasan.txt
Akun: QA Auto dengan indeks DIAG_POOL_INDEX (default 13), tidak dipakai job lain saat run ini.
"""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("DIAG_POOL_INDEX", "13")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402

OUT = ROOT / "reports" / "repro" / "diag_first_login"
NAME_SCREEN = "//*[@content-desc='Masukkan nama pengguna' or @text='Masukkan nama pengguna']"
HOME = "//*[starts-with(@content-desc, 'Hai, mau ke mana') or @content-desc='Saldo Anda']"
summary = []
step = 0


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml) if t.strip() and t not in ("true", "false")]


def bukti(driver, nama):
    global step
    step += 1
    xml = driver.page_source
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    driver.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    fields = [(e.get_attribute("text") or "") for e in driver.find_elements("xpath", "//android.widget.EditText")]
    line = f"{step:02d} {nama}: kolom={fields} | layar={' | '.join(teks(xml)[:10])}"
    summary.append(re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", line))


def layar(driver):
    if driver.find_elements("xpath", NAME_SCREEN):
        return "nama"
    if driver.find_elements("xpath", HOME):
        return "beranda"
    return "lain"


def tunggu_hasil(driver, label, detik=45):
    """Catat layar tiap 3 detik sampai layar nama / Beranda muncul."""
    mulai = time.time()
    while time.time() - mulai < detik:
        s = layar(driver)
        if s != "lain":
            summary.append(f"   {label}: layar '{s}' muncul setelah {time.time() - mulai:.1f} detik")
            return s
        time.sleep(3)
    summary.append(f"   {label}: tidak ada layar nama/Beranda dalam {detik} detik")
    return "lain"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    phone = config.ACTIVE_PHONE
    summary.append(f"akun {phone[:4]}****{phone[-2:]} (indeks {os.environ['TEST_USER_POOL_INDEX']})")
    driver = DriverFactory.create_driver()
    try:
        login = LoginPage(driver)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(phone)
            login.click_submit_login()
            login.find(login.TITLE_OTP, timeout=15)
            field = login.find(login.FIELD_OTP, timeout=10)
            field.click()
            for ch in config.ACTIVE_OTP:
                driver.press_keycode(int(ch) + 7)
                time.sleep(0.15)
            bukti(driver, "sesudah_otp")
        else:
            bukti(driver, "bukan_layar_login_saat_dibuka")
        s = tunggu_hasil(driver, "setelah OTP")
        bukti(driver, f"layar_{s}")
        if s == "nama":
            f = driver.find_element("xpath", "//android.widget.EditText")
            f.click()
            time.sleep(0.5)
            f.send_keys("QA Auto")
            time.sleep(1)
            bukti(driver, "sesudah_ketik_nama")
            if driver.is_keyboard_shown():
                driver.hide_keyboard()
                time.sleep(1)
            driver.find_element("xpath", "//android.widget.Button[@content-desc='Simpan' or @text='Simpan']").click()
            for t in (2, 5, 10):
                time.sleep(t if t == 2 else t - (2 if t == 5 else 5))
                bukti(driver, f"sesudah_simpan_{t}dtk")
            tunggu_hasil(driver, "setelah Simpan", 20)
        # Buka ulang aplikasi: apakah layar nama muncul lagi?
        driver.terminate_app(config.APP_PACKAGE)
        time.sleep(2)
        driver.activate_app(config.APP_PACKAGE)
        s2 = tunggu_hasil(driver, "setelah aplikasi dibuka ulang", 30)
        bukti(driver, f"buka_ulang_{s2}")
    except Exception as e:
        summary.append(f"   langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            bukti(driver, "saat_error")
        except Exception:
            pass
    finally:
        driver.quit()
        (OUT / "ringkasan.txt").write_text("\n".join(summary), encoding="utf-8")
        print("\n".join(summary))


if __name__ == "__main__":
    main()
