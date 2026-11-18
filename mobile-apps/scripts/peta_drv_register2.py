"""Peta LANJUTAN pendaftaran Driver baru: mengisi data pribadi (nama, jenis kelamin, provinsi, kota, KTP, pengalaman) dan mengamati
langkah berikutnya (unggah foto, data kendaraan). Berhenti sebelum tombol akhir (Kirim/Submit/Selesai); TIDAK menyelesaikan pendaftaran.
Pemetaan sebelumnya: nomor handphone > OTP > Data Informasi Personal.

(Ringkasan pemetaan awal) Peta alur pendaftaran Driver baru (aplikasi Driver, staging): langkah SETELAH 'Daftar sebagai Driver baru'.

Latar belakang (18 Nov 2026): 21 test test_drv_register gagal di enter_plate_number karena layar pendaftaran kini dimulai dengan langkah
'Nomor Handphone' + tombol 'Lanjutkan', bukan langsung pilihan ECGO dan plat. Skrip ini mengikuti langkah itu dan mencatat layar demi layar
sampai formulir muncul. Tidak mengunggah berkas dan TIDAK menekan 'Kirim': tidak ada pendaftaran yang diselesaikan.
Nomor yang diketik acak (awalan 899) dan tidak terhubung ke orang; OTP memakai kode bypass dev.
Hasil: reports/repro/peta_drv_register/NN_<layar>.xml|.png dan index.txt."""
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402
from _diag_util import log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "peta_drv_register2"
index = []
step = 0


def semua_label(xml):
    isi = re.findall(r'(?:content-desc|text|hint)="([^"]{1,80})"', xml)
    return [t.replace("&#10;", "/") for t in dict.fromkeys(isi) if t.strip() and t not in ("true", "false") and not t.startswith("Ping")]


def bisa_diketuk(xml):
    hasil = []
    for m in re.finditer(r'<(\S+)\s([^>]*?)/?>', xml):
        a = m.group(2)
        if 'clickable="true"' not in a and "EditText" not in m.group(1):
            continue
        d = re.search(r'content-desc="([^"]*)"', a) or re.search(r'text="([^"]*)"', a) or re.search(r'hint="([^"]*)"', a)
        b = re.search(r'bounds="([^"]+)"', a)
        lab = (d.group(1) if d else "(tanpa label)").replace("&#10;", "/")[:40]
        if not lab.startswith("Ping"):
            hasil.append(f"{m.group(1).split('.')[-1]} {b.group(1) if b else ''} '{lab}'")
    return hasil


def save(d, nama):
    global step
    step += 1
    xml = dump_ringan(d)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(semua_label(xml)[:32]))
    index.append("      bisa diketuk/diisi: " + " ; ".join(bisa_diketuk(xml)[:12]))
    log(index[-2][:150])
    return xml


def nilai_untuk(petunjuk):
    p = petunjuk.lower()
    if "nama" in p:
        return "Uji Otomasi Mitra"
    if "ktp" in p or "1023" in p:
        return "3171012345670001"
    if "20" in p and "-" in p:   # 'Misalnya 2025-11-29'
        return "2024-01-15"
    if "plat" in p or "b1234" in p:
        return "B 1234 EVM"
    return "12345"


def isi_kolom(d):
    for el in d.find_elements("xpath", "//android.widget.EditText"):
        try:
            petunjuk = el.get_attribute("hint") or el.get_attribute("content-desc") or el.get_attribute("text") or ""
            if (el.get_attribute("text") or "").strip() and (el.get_attribute("text") or "") != petunjuk:
                continue  # sudah terisi
            el.click()
            time.sleep(0.3)
            el.send_keys(nilai_untuk(petunjuk))
            time.sleep(0.4)
        except Exception:  # noqa: BLE001
            pass
    try:
        if d.is_keyboard_shown():
            d.hide_keyboard()
    except Exception:  # noqa: BLE001
        pass


def pilih_dropdown(d, langkah):
    """Buka tiap Button 'Pilih ...' dan pilih opsi pertama yang tampil (hanya mengamati hasilnya)."""
    hasil = []
    for k in range(4):
        tombol = d.find_elements("xpath", "//android.widget.Button[starts-with(@content-desc,'Pilih ') or starts-with(@text,'Pilih ')]")
        if not tombol:
            break
        try:
            tombol[0].click()
            time.sleep(2)
            xml = save(d, f"langkah_{langkah}_dropdown_{k + 1}")
            kandidat = [e for e in d.find_elements("xpath", "//*[@clickable='true']")
                        if (e.get_attribute("content-desc") or "").strip() and not (e.get_attribute("content-desc") or "").startswith(("Kembali", "Ping", "Pilih"))]
            if kandidat:
                kandidat[0].click()
                time.sleep(1.5)
            hasil.append(len(kandidat))
        except Exception as ex:  # noqa: BLE001
            index.append(f"   dropdown gagal: {type(ex).__name__}")
            break
    return hasil


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver(is_driver_app=True)
    nomor = "899" + "".join(str(random.randint(0, 9)) for _ in range(8))
    try:
        login = DrvLoginPage(d)
        reg = DrvRegisterPage(d)
        login.handle_system_permissions()
        if not login.is_login_screen_displayed():
            index.append("   layar login Driver tidak tampil")
            save(d, "bukan_layar_login")
            return
        save(d, "layar_login")
        reg.click_daftar_driver_baru()
        time.sleep(2)
        save(d, "setelah_daftar_driver_baru")
        field = d.find_elements("xpath", "//android.widget.EditText")
        if not field:
            index.append("   tidak ada kolom isian di layar pendaftaran")
            return
        field[0].click()
        time.sleep(0.5)
        field[0].send_keys(nomor)
        time.sleep(1)
        save(d, "nomor_diisi")
        try:
            if d.is_keyboard_shown():
                d.hide_keyboard()
        except Exception:  # noqa: BLE001
            pass
        tombol = d.find_elements("xpath", "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")
        index.append(f"   tombol 'Lanjutkan' ditemukan: {len(tombol)}; enabled={tombol[0].get_attribute('enabled') if tombol else '-'}")
        if tombol:
            tombol[0].click()
        for detik in (1, 3, 8):
            time.sleep(detik if detik == 1 else 2 if detik == 3 else 5)
            xml = save(d, f"setelah_lanjutkan_{detik}dtk")
        # Layar OTP? Masukkan kode bypass dev lalu catat layar berikutnya (formulir)
        if re.search(r"(?i)OTP|verifikasi|kode", " ".join(semua_label(xml))):
            index.append("   layar OTP/verifikasi terdeteksi; memasukkan kode bypass dev")
            kolom = d.find_elements("xpath", "//android.widget.EditText")
            if kolom:
                kolom[0].click()
                time.sleep(0.3)
            for ch in str(Config.DRIVER_ACTIVE_PIN):
                try:
                    d.press_keycode(7 + int(ch))
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(0.2)
            time.sleep(2)
            save(d, "otp_diisi")
            lanjut = d.find_elements("xpath", "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")
            if lanjut:
                lanjut[0].click()
            for detik in (2, 6):
                time.sleep(detik)
                save(d, f"setelah_otp_{detik}dtk")
        # Isi formulir bertahap: setiap layar, isi kolom teks kosong, buka dropdown 'Pilih ...' dan pilih opsi pertama, amati tombol foto, lalu 'Lanjutkan'
        for langkah in range(1, 8):
            xml = save(d, f"langkah_{langkah}_awal")
            teks = " ".join(semua_label(xml))
            if re.search(r"(?i)kirim|submit|selesaikan|ajukan", teks):
                index.append("   layar akhir (Kirim/Submit) terdeteksi: BERHENTI, tidak ditekan")
                break
            isi_kolom(d)
            for dd in pilih_dropdown(d, langkah):
                pass
            save(d, f"langkah_{langkah}_terisi")
            for nama in ("Foto ID KTP", "Foto SIM", "Foto STNK Depan", "Foto STNK Belakang", "Foto SKCK", "Foto Selfie"):
                el = d.find_elements("xpath", f"//*[contains(@content-desc,'{nama}') or contains(@text,'{nama}')]")
                if el:
                    try:
                        sebelum = d.current_package
                        el[0].click()
                        time.sleep(2)
                        save(d, f"langkah_{langkah}_{nama.replace(' ', '_')}")
                        index.append(f"   ketuk '{nama}': paket sebelum={sebelum}, sesudah={d.current_package}")
                        d.back()
                        time.sleep(2)
                    except Exception as ex:  # noqa: BLE001
                        index.append(f"   ketuk '{nama}' gagal: {type(ex).__name__}")
            lanjut = d.find_elements("xpath", "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")
            if not lanjut:
                index.append("   tombol 'Lanjutkan' tidak ada; berhenti")
                break
            index.append(f"   'Lanjutkan' enabled={lanjut[0].get_attribute('enabled')}")
            lanjut[0].click()
            time.sleep(3)
            save(d, f"langkah_{langkah}_setelah_lanjutkan")
    except Exception as e:  # noqa: BLE001
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(d, "saat_error")
        except Exception:  # noqa: BLE001
            pass
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        text = "\n".join(index).replace(nomor, "899********")
        (OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
