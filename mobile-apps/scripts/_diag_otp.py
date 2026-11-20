"""Pembantu diagnosa OTP pendaftaran Driver: satu sesi Appium baru, alur nomor handphone > OTP > formulir; catat hasil tanpa menekan Kirim."""
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402


def labels(d, n=10):
    xml = d.page_source
    isi = [t.replace("&#10;", "/") for t in dict.fromkeys(re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml)) if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]
    return isi[:n]


def nomor_acak():
    return "899" + "".join(str(random.randint(0, 9)) for _ in range(8))


def sesi_baru():
    d = DriverFactory.create_driver(is_driver_app=True)
    izinkan_lokasi(d)
    DrvLoginPage(d).handle_system_permissions()
    return d, DrvRegisterPage(d)


def alur_otp(reg):
    """Dari layar login: nomor acak > OTP bypass > Lanjutkan. Mengembalikan teks hasil ('formulir TAMPIL' atau alasan gagal)."""
    try:
        reg.click_daftar_driver_baru()
        assert reg.is_phone_step_displayed(), "langkah nomor handphone tidak tampil"
        reg.lewati_verifikasi_nomor(nomor_acak())
        return "formulir TAMPIL"
    except Exception as e:  # noqa: BLE001
        return f"formulir TIDAK tampil ({type(e).__name__}: {str(e)[:60]})"


def tutup(d, out: Path, nama: str):
    try:
        d.save_screenshot(str(out / f"{nama}.png"))
    except Exception:  # noqa: BLE001
        pass
    try:
        d.quit()
    except Exception:  # noqa: BLE001
        pass


def tulis(out: Path, hasil):
    teks = "\n".join(hasil)
    (out / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


__all__ = ["labels", "alur_otp", "sesi_baru", "tutup", "tulis", "time"]
