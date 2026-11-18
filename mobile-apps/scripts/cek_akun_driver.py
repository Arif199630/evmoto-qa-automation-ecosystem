"""Penyaring kandidat akun Driver: mana yang benar-benar terdaftar sebagai Driver di staging dan bisa dipakai login.

Nomor TIDAK ada di kode: dibaca dari .env (DRIVER_KANDIDAT_1..N, diisi workflow dari secret DRIVER_KANDIDAT). Repo ini publik, jadi hasil hanya
memuat nomor urut dan status, tanpa nomor, tanpa screenshot.

Per kandidat (sesi Appium baru): layar login Driver -> ketik nomor -> 'Join Sekarang' -> klasifikasi:
  BUKAN_DRIVER          : pesan 'Nomor driver belum terdaftar'
  SESI_DI_PERANGKAT_LAIN: modal 'Anda sedang Login di perangkat lain' (TIDAK dikonfirmasi, supaya sesi pemilik akun tidak terputus)
  DRIVER_OTP_MUNCUL     : layar OTP muncul (nomor terdaftar sebagai Driver); lalu OTP bypass dimasukkan
  DRIVER_BISA_MASUK     : setelah OTP, Beranda Driver ('Pesanan Hari Ini') tampil  -> akun layak dipakai
  DRIVER_OTP_GAGAL      : OTP muncul tetapi Beranda tidak tampil
  TIDAK_JELAS           : tidak ada salah satu hasil di atas dalam batas waktu
Nomor yang BUKAN_DRIVER diperiksa lagi di aplikasi User (hanya sampai layar OTP/pesan, tanpa menyelesaikan login):
  USER_TERDAFTAR        : layar OTP User muncul
  BUKAN_USER            : pesan 'Nomor telepon belum terdaftar'
Hasil: reports/repro/cek_akun_driver/index.txt"""
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_home_page import DrvHomePage  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402

OUT = ROOT / "reports" / "repro" / "cek_akun_driver"
index = []


def kandidat():
    hasil = []
    for k in sorted((k for k in os.environ if re.fullmatch(r"DRIVER_KANDIDAT_\d+", k)), key=lambda x: int(x.rsplit("_", 1)[1])):
        if os.environ[k].strip():
            hasil.append((int(k.rsplit("_", 1)[1]), os.environ[k].strip()))
    return hasil


def periksa(nomor_urut, phone):
    d = DriverFactory.create_driver(is_driver_app=True)
    status = "TIDAK_JELAS"
    try:
        login = DrvLoginPage(d)
        login.handle_system_permissions()
        if not login.is_login_screen_displayed():
            return "TIDAK_JELAS (layar login Driver tidak tampil)"
        login.enter_phone_number(phone)
        login.click_join_sekarang()
        batas = time.time() + 20
        while time.time() < batas:
            if d.find_elements(*login.ERROR_DRIVER_NOT_REGISTERED):
                return "BUKAN_DRIVER"
            if d.find_elements(*login.ERROR_LOGGED_IN_OTHER_DEVICE):
                return "SESI_DI_PERANGKAT_LAIN"
            if d.find_elements(*login.TITLE_OTP) or d.find_elements(*login.SUBTITLE_OTP):
                status = "DRIVER_OTP_MUNCUL"
                break
            time.sleep(1)
        if status != "DRIVER_OTP_MUNCUL":
            return "TIDAK_JELAS"
        login.enter_otp(Config.DRIVER_ACTIVE_PIN)
        time.sleep(5)
        login.handle_system_permissions()
        if DrvHomePage(d).is_home_screen_displayed():
            return "DRIVER_BISA_MASUK"
        return "DRIVER_OTP_GAGAL"
    except Exception as e:  # noqa: BLE001
        return f"{status} (galat: {type(e).__name__})"
    finally:
        try:
            d.quit()
        except Exception:
            pass


def periksa_user(phone):
    """Apakah nomor ini akun User? Sampai layar OTP atau pesan 'belum terdaftar', tanpa menyelesaikan login."""
    d = DriverFactory.create_driver()
    try:
        login = LoginPage(d)
        if not login.is_login_screen_displayed(timeout=20):
            return "TIDAK_JELAS (layar login User tidak tampil)"
        login.input_phone_number(phone)
        login.click_submit_login()
        batas = time.time() + 15
        while time.time() < batas:
            if d.find_elements("xpath", "//*[contains(@content-desc,'belum terdaftar') or contains(@text,'belum terdaftar')]"):
                return "BUKAN_USER"
            if d.find_elements(*login.TITLE_OTP):
                return "USER_TERDAFTAR"
            time.sleep(1)
        return "TIDAK_JELAS"
    except Exception as e:  # noqa: BLE001
        return f"TIDAK_JELAS (galat: {type(e).__name__})"
    finally:
        try:
            d.quit()
        except Exception:
            pass


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    daftar = kandidat()
    index.append(f"kandidat terbaca: {len(daftar)}")
    for no, phone in daftar:
        hasil = periksa(no, phone)
        if hasil == "BUKAN_DRIVER":
            hasil += " | aplikasi User: " + periksa_user(phone)
        index.append(f"kandidat {no} (akhiran ..{phone[-2:]}): {hasil}")
        print(index[-1], flush=True)
    ringkas = {}
    for baris in index[1:]:
        s = baris.split(": ", 1)[1].split(" ")[0]  # status Driver; status User ada setelah ' | aplikasi User:' 
        ringkas[s] = ringkas.get(s, 0) + 1
    index.append("RINGKAS: " + ", ".join(f"{k}={v}" for k, v in sorted(ringkas.items())))
    (OUT / "index.txt").write_text("\n".join(index), encoding="utf-8")
    print("\n".join(index))


if __name__ == "__main__":
    main()
