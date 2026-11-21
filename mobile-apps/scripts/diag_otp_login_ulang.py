"""Diagnosa: apakah login OTP kedua (aplikasi dan akun yang sama, setelah data aplikasi dihapus) gagal pada runner yang sama?
Dasar: regression penuh 44733709894 (20 Nov 2026): di tiap shard hanya test pertama yang berhasil login; test berikutnya berhenti di layar login dengan nomor terisi
(E2E_01 lulus, E2E_02 sampai 08 gagal di layar login; beberapa test Driver berhenti di layar 'Join Sekarang'). Diagnosa 16.55 WIB menunjukkan tiga jenis OTP berbeda
(login User, pendaftaran Driver, login Driver) lolos berurutan di satu runner. Dugaan: server membatasi satu verifikasi OTP per JENIS per runner.
Urutan (sesi Appium baru tiap tahap; 'bersih' = mobile: clearApp sehingga aplikasi meminta login lagi):
  U1: login User (pertama).  D1: login Driver (pertama).  U2: login User lagi setelah clearApp.  D2: login Driver lagi setelah clearApp.
Dugaan terbukti bila U1 dan D1 lolos sedangkan U2 dan D2 gagal. Tanpa screenshot dan tanpa nomor (repo publik). Keluaran: reports/repro/diag_otp_login_ulang/index.txt."""
import os
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL", "3")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_home_page import DrvHomePage  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.home_page import HomePage  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import buka_aplikasi_bersih, izinkan_lokasi  # noqa: E402

OUT = ROOT / "reports" / "repro" / "diag_otp_login_ulang"
hasil = []
PKG_USER = config.APP_PACKAGE
PKG_DRIVER = getattr(config, "DRIVER_PACKAGE", "com.evmoto.driver.app")


def user_login(d):
    lp = LoginPage(d)
    if lp.is_login_screen_displayed(timeout=20):
        lp.input_phone_number(config.ACTIVE_PHONE)
        lp.click_submit_login()
        lp.input_otp_dev(config.ACTIVE_OTP)
    time.sleep(6)
    return HomePage(d).is_home_screen_displayed(timeout=20)


def driver_login(d):
    DrvLoginPage(d).login_as_driver()
    time.sleep(5)
    return DrvHomePage(d).is_home_screen_displayed()


def tahap(nama, is_driver, fn, bersih=False):
    d = DriverFactory.create_driver(is_driver_app=is_driver)
    try:
        if bersih:
            buka_aplikasi_bersih(d, PKG_DRIVER if is_driver else PKG_USER)
        else:
            izinkan_lokasi(d)
        ok = fn(d)
        hasil.append(f"{nama}: {'LOLOS' if ok else 'TIDAK lolos (layar tidak berpindah)'}")
    except Exception as e:  # noqa: BLE001
        hasil.append(f"{nama}: GAGAL {type(e).__name__}: {str(e)[:100]}")
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        time.sleep(3)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tahap("U1_login_User_pertama", False, user_login)
    tahap("D1_login_Driver_pertama", True, driver_login)
    tahap("U2_login_User_kedua_setelah_clearApp", False, user_login, bersih=True)
    tahap("D2_login_Driver_kedua_setelah_clearApp", True, driver_login, bersih=True)
    teks = "\n".join(hasil)
    (OUT / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


if __name__ == "__main__":
    main()
