"""Diagnosa: apakah pembatasan OTP berlaku per runner (lintas aplikasi dan lintas nomor)?
Dugaan dari E2E dua perangkat (run 44712346217): login aplikasi User lolos, lalu login aplikasi Driver di emulator lain pada runner yang sama berhenti di layar login.
Urutan di satu runner, tiap tahap sesi Appium baru dan satu kali OTP (kode bypass dev):
  L1: login aplikasi User dengan akun uji pool (OTP pertama dari runner ini).
  L2: pendaftaran Driver dengan nomor acak berformat valid (OTP kedua; aplikasi dan nomor berbeda).
  L3: login aplikasi Driver dengan akun uji (OTP ketiga).
Bila L1 lolos dan L2 serta L3 gagal, pembatasan bukan per nomor atau per aplikasi, melainkan per runner/alamat jaringan.
Nomor akun uji tidak dicetak; tanpa screenshot pada L1 dan L3. Keluaran: reports/repro/diag_otp_lintas_aplikasi/index.txt."""
import os
import random
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
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402
from Pages.home_page import HomePage  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402

OUT = ROOT / "reports" / "repro" / "diag_otp_lintas_aplikasi"
hasil = []


def tahap(nama, fn, driver_driver_app=False, foto=True):
    d = DriverFactory.create_driver(is_driver_app=driver_driver_app)
    try:
        izinkan_lokasi(d)
        ok = fn(d)
        hasil.append(f"{nama}: {'LOLOS' if ok else 'TIDAK lolos (layar tidak berpindah)'}")
    except Exception as e:  # noqa: BLE001
        hasil.append(f"{nama}: GAGAL {type(e).__name__}: {str(e)[:90]}")
    finally:
        if foto:
            try:
                d.save_screenshot(str(OUT / f"{nama}.png"))
            except Exception:  # noqa: BLE001
                pass
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        time.sleep(3)


def l1(d):
    lp = LoginPage(d)
    if lp.is_login_screen_displayed(timeout=20):
        lp.input_phone_number(config.ACTIVE_PHONE)
        lp.click_submit_login()
        lp.input_otp_dev(config.ACTIVE_OTP)
    time.sleep(6)
    return HomePage(d).is_home_screen_displayed(timeout=20)


def l2(d):
    DrvLoginPage(d).handle_system_permissions()
    reg = DrvRegisterPage(d)
    reg.MAKS_SIKLUS_OTP = 1
    reg.click_daftar_driver_baru()
    nomor = random.choice(("812", "813", "821", "857", "878")) + "".join(str(random.randint(0, 9)) for _ in range(8))
    try:
        reg.lewati_verifikasi_nomor(nomor)
        return True
    except AssertionError:
        return False


def l3(d):
    DrvLoginPage(d).login_as_driver()
    time.sleep(5)
    return DrvHomePage(d).is_home_screen_displayed()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tahap("L1_login_User", l1, foto=False)
    tahap("L2_daftar_Driver_nomor_valid", l2, driver_driver_app=True)
    tahap("L3_login_Driver", l3, driver_driver_app=True, foto=False)
    teks = "\n".join(hasil)
    (OUT / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


if __name__ == "__main__":
    main()
