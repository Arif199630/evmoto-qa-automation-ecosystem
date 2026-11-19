"""Peta wizard pendaftaran Driver, versi satu-halaman-gulir (dasar: run 44480066561).
Temuan: 'Data Informasi Personal' (2/3) adalah satu halaman yang digulir: Foto KTP, nama, jenis kelamin, tempat tinggal, No. KTP, pengalaman,
Foto SIM, STNK depan/belakang, lokasi layanan, 'Apakah Anda ECGO Driver?' (RadioButton Ya/Tidak), Foto SKCK, 'Driver Selfie dengan KTP', Foto Avatar,
tombol 'Lanjutkan' tetap di bawah. Skrip ini menggulir dari atas ke bawah dan di tiap posisi mengisi kolom, memilih dropdown dan 'Tidak', serta
mengunggah foto lewat Galeri; lalu 'Lanjutkan' dan mengulang untuk halaman berikutnya sampai ada Kirim/Submit (tidak ditekan).
Nomor acak awalan 899; OTP kode bypass dev. Hasil: reports/repro/peta_drv_register7."""
import hashlib
import random
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import peta_drv_register4 as g  # noqa: E402
import peta_drv_register6 as m  # noqa: E402
from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402

q = m.q
q.OUT = ROOT / "reports" / "repro" / "peta_drv_register7"
BTN_LANJUT = m.BTN_LANJUT
catat = m.catat
XP_LABEL_FOTO = "//*[starts-with(@content-desc,'Foto ') or starts-with(@text,'Foto ') or contains(@content-desc,'Selfie') or contains(@text,'Selfie')]"


def isi_halaman(d, nomor_halaman):
    hash_lama = None
    for lintasan in range(1, 13):
        q.isi_kolom(d)
        q.pilih_dropdown(d, f"h{nomor_halaman}_l{lintasan}")
        for el in d.find_elements("xpath", "//android.widget.RadioButton[@content-desc='Tidak' or @text='Tidak']")[:1]:
            if "Tidak" not in m.sudah:
                m.sudah.add("Tidak")
                el.click()
                time.sleep(1)
                catat("opsi 'Tidak' (ECGO Driver) dipilih")
        for el in d.find_elements("xpath", XP_LABEL_FOTO):
            nama = (el.get_attribute("content-desc") or el.get_attribute("text") or "").split("\n")[0].replace("&#10;", " ").strip()
            if not nama or nama.startswith("Foto diambil") or nama in ("Update Foto",) or nama in m.sudah:
                continue
            m.sudah.add(nama)
            try:
                m.unggah_foto(d, el, nama)
            except Exception as ex:  # noqa: BLE001
                catat(f"'{nama}' gagal diunggah: {type(ex).__name__}: {str(ex)[:100]}")
        xml = q.save(d, f"h{nomor_halaman}_lintasan_{lintasan}")
        h = hashlib.md5(re.sub(r"\s+", "", xml).encode()).hexdigest()
        if h == hash_lama:
            break
        hash_lama = h
        ukuran = d.get_window_size()
        d.swipe(ukuran["width"] // 2, int(ukuran["height"] * 0.70), ukuran["width"] // 2, int(ukuran["height"] * 0.30), 500)
        time.sleep(1)


def main():
    q.OUT.mkdir(parents=True, exist_ok=True)
    lokal = q.OUT / "ktp_uji.png"
    lokal.write_bytes(g.png_bytes())
    for nm in ("ktp_uji", "sim_uji"):
        subprocess.run(["adb", "push", str(lokal), f"/sdcard/Pictures/{nm}.png"], capture_output=True, timeout=60)
        subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file:///sdcard/Pictures/{nm}.png"],
                       capture_output=True, timeout=60)
    d = DriverFactory.create_driver(is_driver_app=True)
    nomor = "899" + "".join(str(random.randint(0, 9)) for _ in range(8))
    try:
        DrvLoginPage(d).handle_system_permissions()
        DrvRegisterPage(d).click_daftar_driver_baru()
        time.sleep(2)
        kolom = d.find_elements("xpath", "//android.widget.EditText")[0]
        kolom.click()
        time.sleep(0.5)
        kolom.send_keys(nomor)
        time.sleep(1)
        try:
            if d.is_keyboard_shown():
                d.hide_keyboard()
        except Exception:  # noqa: BLE001
            pass
        d.find_elements("xpath", BTN_LANJUT)[0].click()
        time.sleep(3)
        d.find_elements("xpath", "//android.widget.EditText")[0].click()
        for ch in str(Config.DRIVER_ACTIVE_PIN):
            d.press_keycode(7 + int(ch))
            time.sleep(0.2)
        time.sleep(1)
        d.find_elements("xpath", BTN_LANJUT)[0].click()
        time.sleep(6)
        for halaman in range(1, 4):
            isi_halaman(d, halaman)
            lanjut = d.find_elements("xpath", BTN_LANJUT)
            catat(f"halaman {halaman}: tombol Lanjutkan={len(lanjut)} enabled={lanjut[0].get_attribute('enabled') if lanjut else '-'}")
            if not lanjut:
                break
            lanjut[0].click()
            time.sleep(5)
            xml = q.save(d, f"h{halaman}_setelah_lanjutkan")
            catat(f"setelah Lanjutkan halaman {halaman}: {q.semua_label(xml)[:16]}")
            if re.search(r"(?i)kirim|submit|selesaikan|ajukan", " ".join(q.semua_label(xml))):
                catat("layar akhir (Kirim/Submit) terdeteksi: BERHENTI, tidak ditekan")
                break
            m.sudah.clear()
    except Exception as e:  # noqa: BLE001
        q.index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            q.save(d, "saat_error")
        except Exception:  # noqa: BLE001
            pass
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        text = "\n".join(q.index).replace(nomor, "899********")
        (q.OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
