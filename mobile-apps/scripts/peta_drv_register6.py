"""Peta wizard pendaftaran Driver lanjutan (pilih 'Tidak' untuk ECGO Driver, foto lewat Galeri atau Kamera emulator) (memakai fungsi pemetaan dari peta_drv_register2).
Dasar temuan: run 44478410839 (pemilih foto Android tampil dengan satu foto 'Foto diambil pada ...'). Di tiap langkah: isi kolom teks,
buka dropdown 'Pilih ...', unggah semua foto yang diminta (kotak di bawah label 'Foto ...'), lalu 'Lanjutkan'. Berhenti di layar yang memuat
Kirim/Submit/Selesaikan/Ajukan dan TIDAK menekannya. Nomor acak awalan 899; OTP kode bypass dev. Hasil: reports/repro/peta_drv_register6."""
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import peta_drv_register2 as q  # noqa: E402
import peta_drv_register4 as g  # noqa: E402
from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402

q.OUT = ROOT / "reports" / "repro" / "peta_drv_register6"
BTN_LANJUT = "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']"
sudah = set()


def catat(teks):
    q.index.append("   " + teks)


def unggah_foto(d, label_el, nama):
    """Ketuk kotak foto di bawah label, pilih 'Galeri', pilih foto pertama; True bila kembali ke aplikasi Driver."""
    r = label_el.rect
    d.tap([(int(d.get_window_size()["width"] * 0.5), int(r["y"] + r["height"] + 35))], 150)
    time.sleep(2.5)
    galeri = d.find_elements("xpath", "//*[@content-desc='Galeri' or @text='Galeri']")
    if not galeri:
        kamera = d.find_elements("xpath", "//*[@content-desc='Kamera' or @text='Kamera']")
        catat(f"'{nama}': Galeri tidak muncul; Kamera={len(kamera)}; paket={d.current_package}")
        q.save(d, f"tanpa_galeri_{nama.replace(' ', '_')}")
        if kamera:
            kamera[0].click()
            time.sleep(5)
            xml_k = q.save(d, f"kamera_{nama.replace(' ', '_')}")
            catat(f"'{nama}': layar kamera paket={d.current_package} activity={d.current_activity}; elemen: {q.semua_label(xml_k)[:12]}")
            for xp in ("//*[contains(@resource-id,'shutter')]", "//*[contains(@content-desc,'Shutter') or contains(@content-desc,'Ambil') or contains(@content-desc,'Take')]"):
                tombol = d.find_elements("xpath", xp)
                if tombol:
                    tombol[0].click()
                    time.sleep(4)
                    xml_k = q.save(d, f"setelah_jepret_{nama.replace(' ', '_')}")
                    catat(f"'{nama}': setelah jepret; elemen: {q.semua_label(xml_k)[:12]}")
                    for xp2 in ("//*[contains(@resource-id,'done')]", "//*[@content-desc='Done' or @content-desc='OK' or @text='OK' or @text='Selesai']"):
                        ok = d.find_elements("xpath", xp2)
                        if ok:
                            ok[0].click()
                            time.sleep(4)
                            break
                    break
            q.save(d, f"sesudah_kamera_{nama.replace(' ', '_')}")
            catat(f"'{nama}': sesudah alur kamera paket={d.current_package}")
        return False
    galeri[0].click()
    time.sleep(4)
    foto = d.find_elements("xpath", "//*[starts-with(@content-desc,'Foto diambil pada')]")
    if not foto:
        catat(f"'{nama}': pemilih foto tanpa foto; paket={d.current_package}")
        q.save(d, f"pemilih_kosong_{nama.replace(' ', '_')}")
        d.back()
        return False
    foto[0].click()
    time.sleep(4)
    q.save(d, f"sesudah_pilih_{nama.replace(' ', '_')}")
    catat(f"'{nama}': foto dipilih; paket sekarang={d.current_package}")
    return d.current_package == "com.evmoto.driver.app"


def unggah_semua_terlihat(d):
    for _ in range(5):
        for el in d.find_elements("xpath", "//*[starts-with(@content-desc,'Foto ') or starts-with(@text,'Foto ')]"):
            nama = (el.get_attribute("content-desc") or el.get_attribute("text") or "").split("\n")[0].replace("&#10;", " ").strip()
            if not nama or nama.startswith("Foto diambil") or nama in sudah:
                continue
            sudah.add(nama)
            try:
                unggah_foto(d, el, nama)
            except Exception as ex:  # noqa: BLE001
                catat(f"'{nama}' gagal diunggah: {type(ex).__name__}: {str(ex)[:100]}")
        ukuran = d.get_window_size()
        d.swipe(ukuran["width"] // 2, int(ukuran["height"] * 0.75), ukuran["width"] // 2, int(ukuran["height"] * 0.30), 500)
        time.sleep(1)


def main():
    q.OUT.mkdir(parents=True, exist_ok=True)
    lokal = q.OUT / "ktp_uji.png"
    lokal.write_bytes(g.png_bytes())
    for nm in ("ktp_uji", "sim_uji", "stnk_depan_uji", "stnk_belakang_uji", "skck_uji", "selfie_uji"):
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
        for langkah in range(1, 5):
            xml = q.save(d, f"langkah_{langkah}_awal")
            if q.re.search(r"(?i)kirim|submit|selesaikan|ajukan", " ".join(q.semua_label(xml))):
                catat("layar akhir (Kirim/Submit) terdeteksi: BERHENTI, tidak ditekan")
                break
            q.isi_kolom(d)
            q.pilih_dropdown(d, langkah)
            for el in d.find_elements("xpath", "//android.widget.Button[@content-desc='Tidak' or @text='Tidak']")[:1]:
                el.click()
                time.sleep(1)
                catat("opsi 'Tidak' (ECGO Driver) dipilih")
            q.save(d, f"langkah_{langkah}_terisi")
            unggah_semua_terlihat(d)
            xml = q.save(d, f"langkah_{langkah}_setelah_unggah")
            # kembali ke puncak untuk melihat tombol Lanjutkan di bawah layar
            lanjut = d.find_elements("xpath", BTN_LANJUT)
            catat(f"langkah {langkah}: tombol Lanjutkan={len(lanjut)} enabled={lanjut[0].get_attribute('enabled') if lanjut else '-'}")
            if lanjut:
                lanjut[0].click()
                time.sleep(4)
                q.save(d, f"langkah_{langkah}_setelah_lanjutkan")
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
