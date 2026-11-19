"""Bukti layar untuk temuan pada aplikasi: elemen yang diharapkan test case tidak ada di Beranda.
User (akun pool 5): Beranda penuh, panel bawah dibuka (geser ke atas), geser lagi. Driver: Beranda penuh dan digeser ke bawah.
Hanya membaca dan mengambil tangkapan layar; tidak mengubah data. Hasil: reports/repro/bukti_temuan_beranda."""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = "5"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.drv_home_page import DrvHomePage  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402

OUT = ROOT / "reports" / "repro" / "bukti_temuan_beranda"
catatan = []


def simpan(d, nama):
    xml = dump_ringan(d)
    (OUT / f"{nama}.xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(OUT / f"{nama}.png"))
    labels = [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml)) if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]
    catatan.append(f"{nama}: " + " | ".join(labels[:30]))


def geser(d, x1, y1, x2, y2):
    d.swipe(x1, y1, x2, y2, 600)
    time.sleep(2)


def bagian_user():
    d = DriverFactory.create_driver()
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(6)
        for el in d.find_elements("xpath", "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")[:1]:
            el.click()
            time.sleep(2)
        simpan(d, "user_beranda")
        # Panel bawah digeser sedikit demi sedikit (120 px per langkah) supaya semua isinya terlihat
        geser(d, 160, 520, 160, 400)
        for langkah in range(1, 7):
            simpan(d, f"user_beranda_panel_langkah_{langkah}")
            geser(d, 160, 480, 160, 360)
    finally:
        d.quit()


def bagian_driver():
    d = DriverFactory.create_driver(is_driver_app=True)
    try:
        DrvLoginPage(d).handle_system_permissions()
        home = DrvHomePage(d)
        if not home.is_home_screen_displayed():
            DrvLoginPage(d).login_as_driver()
        time.sleep(3)
        home.dismiss_operational_popup()
        home.tutup_dialog_order_masuk()
        simpan(d, "driver_beranda")
        geser(d, 160, 450, 160, 150)
        simpan(d, "driver_beranda_digeser_ke_atas")
        geser(d, 160, 200, 160, 480)
        simpan(d, "driver_beranda_ditarik_ke_bawah")
    finally:
        d.quit()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fungsi in (bagian_user, bagian_driver):
        try:
            fungsi()
        except Exception as e:  # noqa: BLE001
            catatan.append(f"{fungsi.__name__} gagal: {type(e).__name__}: {str(e)[:200]}")
    teks = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(catatan))
    (OUT / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


if __name__ == "__main__":
    main()
