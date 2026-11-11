"""
Reproduksi 3 dugaan bug registrasi aplikasi User dengan bukti di SETIAP langkah (screenshot + struktur layar).

Kasus:
  1. Daftar ulang nomor yang SUDAH terdaftar dan sudah lengkap (akun QA Auto 03, sudah punya nama).
  2. Daftar dengan Nama Lengkap hanya angka ("1234567890"), nomor baru rentang 0800 (bukan nomor HP).
  3. Daftar dengan nomor berawalan 0 ("0800...").
Hasil: reports/repro/<kasus>/NN_<langkah>.xml|.png dan reports/repro/ringkasan.txt
Jalankan saat Appium + emulator aktif: python scripts/reproduce_register.py
"""
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402

OUT = ROOT / "reports" / "repro"
OTP = os.getenv("EVMOTO_OTP_BYPASS", "")
POOL = os.getenv("TEST_USER_POOL_PREFIX", "")
summary = []


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text)="([^"]{1,70})"', xml) if t.strip() and t not in ("true", "false")]


def kolom(driver):
    """Isi semua kolom input saat ini (urut di layar)."""
    return [(el.get_attribute("text") or "") for el in driver.find_elements("xpath", "//android.widget.EditText")]


def bukti(driver, folder, step, nama):
    xml = driver.page_source
    (folder / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    driver.save_screenshot(str(folder / f"{step:02d}_{nama}.png"))
    summary.append(f"  {step:02d} {nama}: kolom={kolom(driver)} | layar={' | '.join(teks(xml)[:14])}")


def ketik(driver, index, value):
    fields = driver.find_elements("xpath", "//android.widget.EditText")
    fields[index].click()
    time.sleep(0.3)
    fields[index].send_keys(value)
    time.sleep(0.8)


def ketuk(driver, label):
    driver.find_element("xpath", f"//*[@content-desc='{label}' or @text='{label}']").click()
    time.sleep(2.5)


def ketik_otp(driver):
    # Kolom tepat di bawah label 'Kode OTP' (kolom terakhir adalah 'Kode Referral (Opsional)')
    field = driver.find_element("xpath", "//*[@content-desc='Kode OTP' or @text='Kode OTP']/following::android.widget.EditText[1]")
    field.click()
    time.sleep(0.3)
    for ch in OTP:
        driver.press_keycode(int(ch) + 7)  # tombol angka satu per satu (kolom PIN Flutter)
        time.sleep(0.15)
    time.sleep(1.5)


def kasus(nama, phone, full_name, langkah_otp=True):
    folder = OUT / nama
    folder.mkdir(parents=True, exist_ok=True)
    summary.append(f"== {nama} (nomor {phone[:4]}****{phone[-2:]}, nama '{full_name}')")
    driver = DriverFactory.create_driver()
    try:
        login = LoginPage(driver)
        login.is_login_screen_displayed(timeout=20)
        login.navigate_to_register()
        time.sleep(2)
        bukti(driver, folder, 1, "form_daftar")
        ketik(driver, 0, phone)
        bukti(driver, folder, 2, "sesudah_isi_nomor")
        ketik(driver, 1, full_name)
        driver.hide_keyboard() if driver.is_keyboard_shown() else None
        time.sleep(0.8)
        bukti(driver, folder, 3, "sesudah_isi_nama")
        ketuk(driver, "Minta Kode OTP")
        bukti(driver, folder, 4, "sesudah_minta_otp")
        if langkah_otp and driver.find_elements("xpath", "//*[@content-desc='Kode OTP' or @text='Kode OTP']"):
            ketik_otp(driver)
            bukti(driver, folder, 5, "sesudah_isi_otp")
            # Keyboard angka menutupi tombol 'Buat Akun' (bukti run 43007065338): tutup dulu, baru ketuk
            if driver.is_keyboard_shown():
                driver.hide_keyboard()
                time.sleep(1)
            bukti(driver, folder, 6, "sebelum_buat_akun")
            ketuk(driver, "Buat Akun")
            time.sleep(3)
            bukti(driver, folder, 7, "hasil_buat_akun")
    except Exception as e:
        summary.append(f"  langkah gagal: {type(e).__name__}: {str(e)[:160]}")
        try:
            bukti(driver, folder, 99, "saat_error")
        except Exception:
            pass
    finally:
        driver.quit()


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    baru = f"8003{int(time.time()) % 10000000:07d}"  # rentang 0800: bukan nomor HP
    kasus("1_nomor_sudah_terdaftar_lengkap", f"{POOL}03", "QA Auto Duplikat")
    kasus("2_nama_hanya_angka", baru, "1234567890")
    if os.getenv("REPRO_KASUS3", "0") == "1":  # kasus 3 sudah terbukti bukan bug (11 Nov 2026)
        kasus("3_nomor_awalan_0", "0" + baru[:-1] + "9", "QA Awalan Nol")
    (OUT / "ringkasan.txt").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))
