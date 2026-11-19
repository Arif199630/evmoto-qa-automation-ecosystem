"""Peta unggah Foto ID KTP lewat 'Galeri' di wizard pendaftaran Driver (langkah 2 dari 3).
Temuan run 44475870422: mengetuk kotak foto membuka pilihan 'Galeri' / 'Kamera'. Di sini sebuah PNG dibuat, dikirim ke emulator (adb push + pindai media),
lalu 'Galeri' diketuk dan layar pemilih foto dicatat (paket, label), foto pertama dipilih, dan layar sesudahnya dicatat.
Tidak menekan 'Kirim'; nomor acak awalan 899. Hasil: reports/repro/peta_drv_register4/NN_<layar>.xml|.png dan index.txt."""
import random
import struct
import subprocess
import sys
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import peta_drv_register as p  # noqa: E402
from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402

p.OUT = ROOT / "reports" / "repro" / "peta_drv_register4"
BTN_LANJUT = "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']"


def png_bytes(w=200, h=120):
    mentah = b"".join(b"\x00" + b"".join(bytes([(x * 2) % 256, (y * 2) % 256, 160]) for x in range(w)) for y in range(h))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(mentah)) + chunk(b"IEND", b"")


def adb(*args):
    r = subprocess.run(["adb", *args], capture_output=True, text=True, timeout=60)
    return (r.stdout + r.stderr).strip()[:200]


def catat(d, teks):
    try:
        teks += f" [paket={d.current_package} activity={d.current_activity}]"
    except Exception:  # noqa: BLE001
        pass
    p.index.append("   " + teks)


def main():
    p.OUT.mkdir(parents=True, exist_ok=True)
    lokal = p.OUT / "ktp_uji.png"
    lokal.write_bytes(png_bytes())
    catat_adb = [adb("shell", "mkdir", "-p", "/sdcard/Pictures"), adb("push", str(lokal), "/sdcard/Pictures/ktp_uji.png"),
                 adb("shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", "file:///sdcard/Pictures/ktp_uji.png")]
    p.index.append("   adb: " + " || ".join(catat_adb))
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
        p.save(d, "data_informasi_personal")
        d.tap([(160, 335)], 200)
        time.sleep(3)
        p.save(d, "pilihan_sumber_foto")
        galeri = d.find_elements("xpath", "//*[@content-desc='Galeri' or @text='Galeri']")
        catat(d, f"elemen 'Galeri' ditemukan: {len(galeri)}")
        if galeri:
            galeri[0].click()
            for detik in (3, 4):
                time.sleep(detik)
                xml = p.save(d, f"setelah_galeri_{detik}dtk")
                catat(d, f"setelah ketuk Galeri ({detik} dtk)")
            # izin media bila diminta
            for kata in ("Izinkan", "Allow", "While using", "Saat aplikasi digunakan"):
                for el in d.find_elements("xpath", f"//*[contains(@text,'{kata}') or contains(@content-desc,'{kata}')]")[:1]:
                    catat(d, f"dialog izin: mengetuk '{kata}'")
                    el.click()
                    time.sleep(2)
            xml = p.save(d, "pemilih_foto")
            catat(d, f"isi pemilih foto: {p.semua_label(xml)[:14]}")
            # pilih gambar pertama (ImageView/ViewGroup bertanda 'Photo' / nama berkas) bila ada
            kandidat = d.find_elements("xpath", "//*[contains(@content-desc,'Photo') or contains(@content-desc,'ktp_uji') or contains(@text,'ktp_uji')]")
            catat(d, f"kandidat foto: {len(kandidat)}")
            if kandidat:
                kandidat[0].click()
                time.sleep(3)
                xml = p.save(d, "setelah_pilih_foto")
                catat(d, f"setelah pilih foto: {p.semua_label(xml)[:14]}")
                for kata in ("Tambah", "Add", "Selesai", "Done", "Pilih", "Konfirmasi", "Gunakan", "Crop", "Potong"):
                    for el in d.find_elements("xpath", f"//*[@text='{kata}' or @content-desc='{kata}']")[:1]:
                        catat(d, f"tombol sesudah pilih foto: '{kata}'")
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
        text = "\n".join(p.index).replace(nomor, "899********")
        (p.OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
