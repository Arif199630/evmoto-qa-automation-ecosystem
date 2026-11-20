"""Diagnosa dugaan: OTP pendaftaran Driver hanya lolos bila aplikasi mendapat lokasi perangkat.
Bukti (run 44510121045): screenshot sesi yang lolos (A1) menampilkan ikon lokasi di bilah status; semua sesi yang gagal (A2, A3, B1-B3) tidak.
Pada A1 dialog izin lokasi dijawab langsung ('Saat aplikasi digunakan'); pada sesi lain izin sudah diberikan sebelumnya / lewat Appium, sehingga tidak ada dialog.
Tahap (tiap tahap = satu sesi Appium baru, nomor acak awalan 899, kode bypass dev, tidak menekan Kirim):
  V1a, V1b: clearApp TANPA memberi izin; dialog izin dijawab langsung saat muncul (meniru A1).
  V2: tanpa clearApp, izin sudah ada; lokasi emulator diatur lewat Appium set_location sebelum nomor dikirim.
  V3: izin lokasi dicabut lewat 'pm revoke' (tanpa clearApp); dialog dijawab langsung saat muncul.
Setiap tahap mencatat: mode lokasi perangkat, status izin, apakah ikon lokasi/dialog muncul, dan apakah formulir 'Data Informasi Personal' tampil.
Keluaran: reports/repro/diag_otp_lokasi/index.txt dan screenshot."""
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402
from _diag_util import PERMISSION_ALLOW  # noqa: E402

PAKET = "com.evmoto.driver.app"
IZIN = ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"]
OUT = ROOT / "reports" / "repro" / "diag_otp_lokasi"
hasil = []


def adb(*args):
    exe = shutil.which("adb")
    if not exe:
        return "adb tidak ada"
    r = subprocess.run([exe, *args], capture_output=True, text=True, timeout=60)
    return (r.stdout + r.stderr).strip()


def status_izin():
    dump = adb("shell", "dumpsys", "package", PAKET)
    baris = [b.strip() for b in dump.splitlines() if "ACCESS_FINE_LOCATION" in b and "granted" in b]
    mode = adb("shell", "settings", "get", "secure", "location_mode")
    return f"location_mode={mode[:6]}; izin={' | '.join(baris)[:90] or 'tidak terbaca'}"


def jawab_dialog_langsung(d, tunggu=14):
    """Tunggu sampai dialog izin lokasi muncul lalu ketuk 'Saat aplikasi digunakan'; True bila dialog muncul."""
    batas = time.time() + tunggu
    while time.time() < batas:
        els = d.find_elements("xpath", PERMISSION_ALLOW)
        if els:
            els[0].click()
            time.sleep(2)
            return True
        time.sleep(1)
    return False


def labels(d):
    xml = d.page_source
    return [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml)) if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]


def satu_sesi(nama, persiapan=None, tunggu_dialog=False, lokasi_appium=False):
    if persiapan:
        persiapan()
    d = DriverFactory.create_driver(is_driver_app=True)
    nomor = "899" + "".join(str(random.randint(0, 9)) for _ in range(8))
    catatan = [status_izin()]
    try:
        if tunggu_dialog:
            catatan.append(f"dialog izin muncul={jawab_dialog_langsung(d)}")
        else:
            catatan.append("dialog izin tidak ditunggu")
        if lokasi_appium:
            try:
                d.set_location(-6.2088, 106.8456, 10)
                catatan.append("set_location berhasil")
            except Exception as e:  # noqa: BLE001
                catatan.append(f"set_location gagal {type(e).__name__}")
        DrvLoginPage(d).handle_system_permissions()
        reg = DrvRegisterPage(d)
        reg.click_daftar_driver_baru()
        assert reg.is_phone_step_displayed()
        reg.lewati_verifikasi_nomor(nomor)
        hasil.append(f"{nama}: formulir TAMPIL | " + " | ".join(catatan))
    except Exception as e:  # noqa: BLE001
        try:
            isi = labels(d)[:8]
        except Exception:  # noqa: BLE001
            isi = []
        hasil.append(f"{nama}: GAGAL {type(e).__name__}: {str(e)[:70]} | layar={isi} | " + " | ".join(catatan))
    finally:
        try:
            d.save_screenshot(str(OUT / f"{nama}.png"))
        except Exception:  # noqa: BLE001
            pass
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass


def bersih_tanpa_izin():
    adb("shell", "pm", "clear", PAKET)


def cabut_izin():
    for izin in IZIN:
        adb("shell", "pm", "revoke", PAKET, izin)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    satu_sesi("V1a_clearApp_dialog_langsung", persiapan=bersih_tanpa_izin, tunggu_dialog=True)
    satu_sesi("V1b_clearApp_dialog_langsung", persiapan=bersih_tanpa_izin, tunggu_dialog=True)
    satu_sesi("V2_izin_ada_set_location", lokasi_appium=True)
    satu_sesi("V3_cabut_izin_dialog_langsung", persiapan=cabut_izin, tunggu_dialog=True)
    teks = "\n".join(hasil) + f"\n(OTP bypass panjang {len(str(Config.DRIVER_ACTIVE_PIN))} digit)"
    (OUT / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


if __name__ == "__main__":
    main()
