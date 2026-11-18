"""Lanjutan peta banner 'Sedang berjalanan' di Beranda User (hanya membaca). Ketukan tengah banner (run 44282172922) tidak membuka apa pun,
jadi di sini dicoba: ketuk titik, geser banner ke atas, ketuk panah, lalu buka tab Aktivitas. Pool akun lewat MAP_POOL (default 3).
Tujuan: membedakan 'banner selalu ada' dari 'ada order aktif tertinggal'. Tidak membatalkan atau mengubah apa pun."""
import os
import time

os.environ.setdefault("MAP_POOL", "3")
import peta_sedang_berjalan as p  # noqa: E402
from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402

p.OUT = p.ROOT / "reports" / "repro" / ("peta_sedang_berjalan2_pool" + os.environ["MAP_POOL"])


def main():
    p.OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(6)
        p.tutup_popup(d)
        time.sleep(2)
        p.save(d, "beranda")
        d.tap([(160, 520)], 150)
        time.sleep(3)
        p.save(d, "setelah_tap_banner")
        d.swipe(160, 515, 160, 140, 500)
        time.sleep(2)
        p.save(d, "setelah_geser_banner_ke_atas")
        d.tap([(303, 520)], 150)
        time.sleep(3)
        p.save(d, "setelah_tap_panah")
        d.tap([(160, 584)], 150)
        time.sleep(1)
        d.tap([(160, 584)], 150)
        time.sleep(4)
        p.save(d, "tab_aktivitas")
    except Exception as e:  # noqa: BLE001
        p.index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            p.save(d, "saat_error")
        except Exception:  # noqa: BLE001
            pass
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        text = "\n".join(p.index)
        (p.OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
