"""Peta akhir wizard pendaftaran Driver di APK UAT: kolom tanggal 'Pengalaman Berkendara Sejak' dan layar sesudah 'Lanjutkan'.
Dasar: run 44482720465 (formulir satu halaman gulir; kolom tanggal tetap kosong karena bukan kolom teks biasa). Skrip memakai isi_halaman dari
peta_drv_register7, lalu mencari kolom tanggal, mengetuknya, mencatat pemilih tanggal, memilih tanggal, dan menekan 'Lanjutkan' sambil mencatat
tiga layar berikutnya. Berhenti sebelum Kirim/Submit (tidak ditekan). Nomor acak awalan 899. Hasil: reports/repro/peta_drv_register8."""
import random
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import peta_drv_register4 as g  # noqa: E402
import peta_drv_register7 as s7  # noqa: E402
from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402

q = s7.q
q.OUT = ROOT / "reports" / "repro" / "peta_drv_register8"
catat = s7.catat
BTN_LANJUT = s7.BTN_LANJUT
XP_TANGGAL = "//android.widget.EditText[contains(@hint,'2025') or contains(@hint,'Misalnya 20')]"


def cari_tanggal(d):
    for _ in range(14):
        el = d.find_elements("xpath", XP_TANGGAL)
        if el:
            return el[0]
        ukuran = d.get_window_size()
        d.swipe(ukuran["width"] // 2, int(ukuran["height"] * 0.30), ukuran["width"] // 2, int(ukuran["height"] * 0.70), 500)
        time.sleep(1)
    return None


def main():
    q.OUT.mkdir(parents=True, exist_ok=True)
    lokal = q.OUT / "ktp_uji.png"
    lokal.write_bytes(g.png_bytes())
    subprocess.run(["adb", "push", str(lokal), "/sdcard/Pictures/ktp_uji.png"], capture_output=True, timeout=60)
    subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", "file:///sdcard/Pictures/ktp_uji.png"],
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
        s7.isi_halaman(d, 1)
        tgl = cari_tanggal(d)
        catat(f"kolom tanggal ditemukan: {tgl is not None}")
        if tgl is not None:
            q.save(d, "tanggal_terlihat")
            catat(f"atribut tanggal: class={tgl.get_attribute('class')} focusable={tgl.get_attribute('focusable')} enabled={tgl.get_attribute('enabled')} text='{tgl.get_attribute('text')}'")
            tgl.click()
            time.sleep(3)
            xml = q.save(d, "setelah_ketuk_tanggal")
            catat(f"setelah ketuk tanggal: {q.semua_label(xml)[:20]}")
            for kata in ("OK", "Pilih", "Simpan", "Selesai", "Konfirmasi", "Batal"):
                for el in d.find_elements("xpath", f"//*[@text='{kata}' or @content-desc='{kata}']")[:1]:
                    catat(f"tombol di pemilih tanggal: '{kata}'")
            # coba ketik langsung bila kolom menerima teks
            try:
                tgl.send_keys("2024-01-15")
                time.sleep(1)
                q.save(d, "setelah_ketik_tanggal")
                catat(f"nilai kolom setelah ketik: '{tgl.get_attribute('text')}'")
            except Exception as ex:  # noqa: BLE001
                catat(f"ketik tanggal gagal: {type(ex).__name__}")
            for kata in ("OK", "Pilih", "Simpan", "Selesai", "Konfirmasi"):
                el = d.find_elements("xpath", f"//*[@text='{kata}' or @content-desc='{kata}']")
                if el:
                    el[0].click()
                    time.sleep(2)
                    break
            xml = q.save(d, "setelah_pilih_tanggal")
            catat(f"setelah pilih tanggal: {q.semua_label(xml)[:20]}")
        lanjut = d.find_elements("xpath", BTN_LANJUT)
        catat(f"tombol Lanjutkan={len(lanjut)}")
        if lanjut:
            lanjut[0].click()
            for detik in (3, 6):
                time.sleep(detik)
                xml = q.save(d, f"setelah_lanjutkan_{detik}dtk")
                catat(f"setelah Lanjutkan {detik} dtk: {q.semua_label(xml)[:24]}")
            s7.isi_halaman(d, 2)
            lanjut = d.find_elements("xpath", BTN_LANJUT)
            catat(f"halaman 2 tombol Lanjutkan={len(lanjut)}")
            if lanjut and not re.search(r"(?i)kirim|submit|selesaikan|ajukan", " ".join(q.semua_label(q.save(d, 'sebelum_lanjutkan_2')))):
                lanjut[0].click()
                time.sleep(5)
                xml = q.save(d, "setelah_lanjutkan_2")
                catat(f"setelah Lanjutkan 2: {q.semua_label(xml)[:24]}")
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
