"""Diagnosa OTP pendaftaran Driver yang berhasil hanya pada test pertama di tiap sesi (run 44507722470: 20 dari 24 test berhenti di langkah OTP).
Skrip membuat sesi Appium baru berkali-kali, seperti tiap test, dan di tiap sesi menjalankan nomor handphone > OTP 1234 > Lanjutkan.
Tahap A: tanpa membersihkan data aplikasi antar sesi. Tahap B: dengan 'mobile: clearApp' + izin lokasi di tiap sesi.
Hasil per sesi: formulir 'Data Informasi Personal' tampil atau tidak, serta isi layar bila tidak. Tidak menekan Kirim; nomor acak awalan 899."""
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402

PAKET = "com.evmoto.driver.app"
OUT = ROOT / "reports" / "repro" / "diag_otp_berulang"
hasil = []


def labels(d):
    xml = d.page_source
    return [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml)) if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]


def satu_sesi(nama, bersih):
    d = DriverFactory.create_driver(is_driver_app=True)
    nomor = "899" + "".join(str(random.randint(0, 9)) for _ in range(8))
    try:
        if bersih:
            d.execute_script("mobile: clearApp", {"appId": PAKET})
            try:
                d.execute_script("mobile: changePermissions", {"permissions": ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
                                                               "appPackage": PAKET, "action": "grant"})
            except Exception:  # noqa: BLE001
                pass
            d.activate_app(PAKET)
            time.sleep(6)
        izinkan_lokasi(d)
        DrvLoginPage(d).handle_system_permissions()
        reg = DrvRegisterPage(d)
        reg.click_daftar_driver_baru()
        assert reg.is_phone_step_displayed()
        reg.lewati_verifikasi_nomor(nomor)
        hasil.append(f"{nama}: formulir TAMPIL")
    except Exception as e:  # noqa: BLE001
        try:
            isi = labels(d)[:14]
        except Exception:  # noqa: BLE001
            isi = []
        hasil.append(f"{nama}: GAGAL {type(e).__name__}: {str(e)[:90]} | layar: {isi}")
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
    for i in range(1, 4):
        satu_sesi(f"A{i}_tanpa_bersih", bersih=False)
    for i in range(1, 4):
        satu_sesi(f"B{i}_dengan_clearApp", bersih=True)
    teks = "\n".join(hasil) + f"\n(OTP bypass panjang {len(str(Config.DRIVER_ACTIVE_PIN))} digit)"
    (OUT / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


if __name__ == "__main__":
    main()
