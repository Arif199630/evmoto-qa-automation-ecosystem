"""Diagnosa lanjutan OTP pendaftaran Driver (run 44510121045: hanya sesi pertama yang lolos OTP, 'clearApp' tidak mengubah hasil).
Menguji tiga dugaan, satu per tahap, memakai nomor acak awalan 899 dan kode bypass dev; tidak menekan Kirim.
  S1: sesi baru pertama (pembanding; diharapkan lolos).
  S2: sesi baru segera sesudah S1 (diharapkan gagal). Bila gagal: tunggu hitung mundur selesai, ketuk 'Kirim ulang kode', isi OTP lagi, Lanjutkan.
  S3: sesi baru setelah mengganti android_id perangkat lewat adb (dugaan: server membatasi per identitas perangkat).
  S4: sesi baru setelah jeda 5 menit (dugaan: server membatasi per waktu).
Hasil per tahap: formulir 'Data Informasi Personal' tampil atau tidak, beserta isi layar. Keluaran: reports/repro/diag_otp_jeda/index.txt."""
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from appium.webdriver.common.appiumby import AppiumBy  # noqa: E402
from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402

OUT = ROOT / "reports" / "repro" / "diag_otp_jeda"
hasil = []


def labels(d):
    xml = d.page_source
    return [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml)) if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]


def adb(*args):
    exe = shutil.which("adb")
    if not exe:
        return "adb tidak ada"
    r = subprocess.run([exe, *args], capture_output=True, text=True, timeout=60)
    return (r.stdout + r.stderr).strip()[:200]


def otp_diisi_lanjutkan(reg):
    """Isi kode bypass ke kolom OTP lalu ketuk Lanjutkan; True bila formulir tampil."""
    kolom = reg.find(reg.FIELD_PHONE, timeout=10)
    kolom.click()
    time.sleep(0.5)
    for digit in str(Config.DRIVER_ACTIVE_PIN):
        reg.driver.press_keycode(7 + int(digit))
        time.sleep(0.2)
    time.sleep(1)
    reg._klik_langsung(reg.BTN_LANJUTKAN, "Lanjutkan (OTP)")
    return reg.is_displayed(reg.PENANDA_FORMULIR, timeout=12)


def satu_sesi(nama, kirim_ulang=False):
    d = DriverFactory.create_driver(is_driver_app=True)
    nomor = "899" + "".join(str(random.randint(0, 9)) for _ in range(8))
    try:
        izinkan_lokasi(d)
        DrvLoginPage(d).handle_system_permissions()
        reg = DrvRegisterPage(d)
        reg.click_daftar_driver_baru()
        assert reg.is_phone_step_displayed()
        kolom = reg.find(reg.FIELD_PHONE, timeout=10)
        kolom.click()
        time.sleep(0.5)
        kolom.send_keys(nomor)
        time.sleep(1)
        reg._sembunyikan_keyboard()
        reg._klik_langsung(reg.BTN_LANJUTKAN, "Lanjutkan (nomor)")
        assert reg.is_displayed(reg.TEXT_OTP_STEP, timeout=15), "layar OTP tidak tampil"
        if otp_diisi_lanjutkan(reg):
            hasil.append(f"{nama}: formulir TAMPIL")
            return
        hasil.append(f"{nama}: formulir TIDAK tampil; layar: {labels(d)[:12]}")
        if kirim_ulang:
            time.sleep(50)  # hitung mundur OTP (sebelumnya terbaca 0:00:17 setelah tiga percobaan)
            tombol = d.find_elements(AppiumBy.XPATH, "//*[@content-desc='Kirim ulang kode' or @text='Kirim ulang kode']")
            hasil.append(f"{nama}: tombol 'Kirim ulang kode' ditemukan={len(tombol)} enabled={tombol[0].get_attribute('enabled') if tombol else '-'}")
            if tombol:
                tombol[0].click()
                time.sleep(3)
                hasil.append(f"{nama}: setelah kirim ulang, layar: {labels(d)[:10]}")
                ok = otp_diisi_lanjutkan(reg)
                hasil.append(f"{nama}: setelah kirim ulang + OTP: {'formulir TAMPIL' if ok else 'formulir TIDAK tampil; layar: ' + str(labels(d)[:10])}")
    except Exception as e:  # noqa: BLE001
        hasil.append(f"{nama}: GAGAL {type(e).__name__}: {str(e)[:100]}")
    finally:
        try:
            d.save_screenshot(str(OUT / f"{nama}.png"))
        except Exception:  # noqa: BLE001
            pass
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    satu_sesi("S1_sesi_pertama")
    satu_sesi("S2_sesi_kedua_segera", kirim_ulang=True)
    lama = adb("shell", "settings", "get", "secure", "android_id")
    baru = "".join(random.choice("0123456789abcdef") for _ in range(16))
    hasil.append(f"S3 persiapan: android_id lama terbaca={'ya' if lama else 'tidak'}; put -> {adb('shell', 'settings', 'put', 'secure', 'android_id', baru) or 'tanpa pesan'}; "
                 f"terbaca ulang berubah={adb('shell', 'settings', 'get', 'secure', 'android_id') == baru}")
    satu_sesi("S3_setelah_ganti_android_id")
    time.sleep(300)
    satu_sesi("S4_setelah_jeda_5_menit")
    teks = "\n".join(hasil)
    (OUT / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


if __name__ == "__main__":
    main()
