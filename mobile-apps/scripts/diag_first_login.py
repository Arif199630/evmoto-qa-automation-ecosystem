"""
Diagnosa layar 'Masukkan nama pengguna' setelah login akun QA Auto, dengan bukti di setiap langkah.

Pertanyaan yang dijawab:
  1. Berapa detik setelah OTP layar nama (atau Beranda) muncul?
  2. Apakah nama yang diketik benar-benar masuk ke kolom, dan apakah 'Simpan' membawa ke Beranda?
  3. Setelah aplikasi dibuka ulang, apakah layar nama muncul lagi (nama tidak tersimpan) atau langsung Beranda?
Hasil: reports/repro/diag_first_login/NN_<langkah>.xml|.png dan ringkasan.txt
Akun: semua akun QA Auto indeks 02-15 (DIAG_POOL_INDEXES, mis. "2-15" atau "3,13"), satu per satu di emulator
yang sama; data aplikasi dibersihkan di antara akun. Akun yang masih di layar nama diisi 'QA Auto' (data uji staging).
"""
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import buka_aplikasi_bersih, izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "diag_first_login"
PREFIX = os.getenv("TEST_USER_POOL_PREFIX", "")
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
        if izinkan_lokasi(driver):
            summary.append(f"   {label}: dialog izin lokasi Android diketuk 'Saat aplikasi digunakan'")
        s = layar(driver)
        if s != "lain":
            summary.append(f"   {label}: layar '{s}' muncul setelah {time.time() - mulai:.1f} detik")
            return s
        time.sleep(3)
    summary.append(f"   {label}: tidak ada layar nama/Beranda dalam {detik} detik")
    return "lain"


def indexes():
    raw = os.getenv("DIAG_POOL_INDEXES", "2-15")
    if "-" in raw:
        a, b = raw.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in raw.split(",") if x.strip()]


def satu_akun(driver, idx):
    phone = f"{PREFIX}{idx:02d}"
    summary.append(f"== akun indeks {idx:02d} ({phone[:4]}****{phone[-2:]})")
    log(f"akun {idx:02d}: buka aplikasi bersih")
    buka_aplikasi_bersih(driver, config.APP_PACKAGE)
    login = LoginPage(driver)
    if not login.is_login_screen_displayed(timeout=25):
        bukti(driver, f"a{idx:02d}_bukan_layar_login")
        return "tidak sampai layar login"
    login.input_phone_number(phone)
    login.click_submit_login()
    login.find(login.TITLE_OTP, timeout=15)
    field = login.find(login.FIELD_OTP, timeout=10)
    field.click()
    for ch in config.ACTIVE_OTP:
        driver.press_keycode(int(ch) + 7)
        time.sleep(0.15)
    s = tunggu_hasil(driver, "setelah OTP", 45)
    bukti(driver, f"a{idx:02d}_layar_{s}")
    if s == "beranda":
        return "langsung Beranda"
    if s != "nama":
        return "macet (bukan layar nama / Beranda)"
    f = driver.find_element("xpath", "//android.widget.EditText")
    f.click()
    time.sleep(0.5)
    f.send_keys("QA Auto")
    time.sleep(1)
    bukti(driver, f"a{idx:02d}_sesudah_ketik_nama")
    if driver.is_keyboard_shown():
        driver.hide_keyboard()
        time.sleep(1)
    driver.find_element("xpath", "//android.widget.Button[@content-desc='Simpan' or @text='Simpan']").click()
    time.sleep(2)
    bukti(driver, f"a{idx:02d}_sesudah_simpan")
    s2 = tunggu_hasil(driver, "setelah Simpan", 30)
    bukti(driver, f"a{idx:02d}_hasil_simpan_{s2}")
    if s2 != "beranda":
        return "layar nama -> Simpan -> TIDAK sampai Beranda"
    driver.terminate_app(config.APP_PACKAGE)
    time.sleep(2)
    driver.activate_app(config.APP_PACKAGE)
    s3 = tunggu_hasil(driver, "setelah dibuka ulang", 30)
    bukti(driver, f"a{idx:02d}_buka_ulang_{s3}")
    return "layar nama -> Simpan -> Beranda; dibuka ulang: " + s3


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hasil = []
    driver = DriverFactory.create_driver()
    try:
        for idx in indexes():
            try:
                hasil.append(f"akun {idx:02d}: {satu_akun(driver, idx)}")
            except Exception as e:
                summary.append(f"   langkah gagal: {type(e).__name__}: {str(e)[:200]}")
                hasil.append(f"akun {idx:02d}: error {type(e).__name__}")
                try:
                    bukti(driver, f"a{idx:02d}_saat_error")
                except Exception:
                    pass
    finally:
        driver.quit()
        summary.append("== RINGKASAN")
        summary.extend(hasil)
        (OUT / "ringkasan.txt").write_text("\n".join(summary), encoding="utf-8")
        print("\n".join(summary))


if __name__ == "__main__":
    main()
