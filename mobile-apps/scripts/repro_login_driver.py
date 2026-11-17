"""
Reproduksi kandidat bug login aplikasi Driver (test_drv_login PF-03, NT-04, NT-06, NF-01, NF-04, regression 16 Nov 2026).

Test mengetik nomor tidak valid, mengetuk 'Join Sekarang', lalu mengharapkan tetap di layar login. Hasil CI: layar
berpindah ke 'Registrasi Driver Baru'. Skrip ini merekam tiap langkah untuk memastikan apa yang terjadi: isi kolom
nomor setelah diketik, status tombol 'Join Sekarang' (aktif/tidak), dan layar setelah tombol diketuk.
Tidak ada OTP yang dikirim untuk nomor valid; nomor yang dipakai sama dengan data test (drv_data.py).
Hasil: reports/repro/login_driver/<kasus>_NN_<langkah>.xml|.png dan ringkasan.txt (nomor disensor).
"""
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from _diag_util import buka_aplikasi_bersih, izinkan_lokasi  # noqa: E402

OUT = ROOT / "reports" / "repro" / "login_driver"
summary = []

KASUS = [
    ("PF_03_7_digit", "8123456"),
    ("NT_04_3_digit", "812"),
    ("NT_06_awalan_123", "123456789"),
    ("NF_01_sqli", "' OR '1'='1"),
    ("NF_04_terlalu_panjang", os.environ.get("TEST_USER_PHONE", "81234567890") + "12345678901234"),
]


def sensor(s: str) -> str:
    return re.sub(r"(\d{4})\d{4,}(\d{2})", r"\1****\2", s or "")


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml)
            if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]


def simpan(driver, nama):
    xml = dump_ringan(driver)
    (OUT / f"{nama}.xml").write_text(sensor(xml), encoding="utf-8")
    driver.save_screenshot(str(OUT / f"{nama}.png"))
    return xml


def satu_kasus(driver, nama, nomor):
    summary.append(f"\n== {nama}: input '{sensor(nomor)}' ({len(nomor)} karakter)")
    buka_aplikasi_bersih(driver, Config.DRIVER_PACKAGE)
    pg = DrvLoginPage(driver)
    pg.handle_system_permissions()
    if not pg.is_login_screen_displayed():
        simpan(driver, f"{nama}_00_bukan_login")
        summary.append("  layar login tidak tampil: " + " | ".join(teks(dump_ringan(driver))[:8]))
        return
    tombol = pg.find(pg.BTN_JOIN_SEKARANG)
    summary.append(f"  1. layar login tampil; tombol Join Sekarang enabled={tombol.get_attribute('enabled')} (kolom kosong)")
    simpan(driver, f"{nama}_01_login")
    pg.enter_phone_number(nomor)
    time.sleep(1.5)
    field = pg.find(pg.FIELD_PHONE)
    isi = field.get_attribute("text") or ""
    aktif = pg.find(pg.BTN_JOIN_SEKARANG).get_attribute("enabled")
    summary.append(f"  2. setelah diketik: isi kolom '{sensor(isi)}' ({len(isi)} karakter), tombol Join Sekarang enabled={aktif}")
    simpan(driver, f"{nama}_02_setelah_ketik")
    pg.find(pg.BTN_JOIN_SEKARANG).click()
    time.sleep(4)
    izinkan_lokasi(driver)
    xml = simpan(driver, f"{nama}_03_setelah_ketuk")
    layar = teks(xml)
    summary.append("  3. setelah tombol diketuk: " + sensor(" | ".join(layar[:10])))
    hint = re.findall(r'hint="([^"]+)"', xml)
    isi_baru = re.findall(r'class="android.widget.EditText"[^>]*text="([^"]*)"', xml)
    summary.append(f"     kolom di layar ini: isi {[sensor(x) for x in isi_baru]}, hint {hint[:2]}")
    if any("Registrasi Driver Baru" in t for t in layar):
        summary.append("  HASIL: pindah ke 'Registrasi Driver Baru'")
    elif pg.is_login_screen_displayed():
        summary.append("  HASIL: tetap di layar login")
    elif any("OTP" in t or "verifikasi" in t.lower() for t in layar):
        summary.append("  HASIL: pindah ke layar OTP")
    else:
        summary.append("  HASIL: layar lain")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    driver = DriverFactory.create_driver(is_driver_app=True)
    try:
        for nama, nomor in KASUS:
            try:
                satu_kasus(driver, nama, nomor)
            except Exception as e:  # noqa: BLE001 - catat lalu lanjut ke kasus berikutnya
                summary.append(f"  langkah gagal: {type(e).__name__}: {sensor(str(e))[:200]}")
    finally:
        driver.quit()
        text = sensor("\n".join(summary))
        (OUT / "ringkasan.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
