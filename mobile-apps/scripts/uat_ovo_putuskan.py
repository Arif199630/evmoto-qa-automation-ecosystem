"""UAT OVO A4.0: unlink akun OVO TANPA PIN challenge dari aplikasi User, memakai akun UAT A (nomor dari secret DRIVER_KANDIDAT, kandidat 4).

Alur: login -> Akun -> Pengaturan Pembayaran -> detail OVO -> 'Putuskan' -> catat dialog.
  - Bila dialog meminta PIN/password/OTP (kolom isian atau kata 'PIN'/'Kata Sandi'/'Password'/'OTP'): BERHENTI dan mencatat 'MINTA_KREDENSIAL'. Skrip tidak pernah mengetik PIN.
  - Bila hanya konfirmasi (tombol 'Putuskan'/'Ya'): ketuk konfirmasi, lalu catat hasil (OVO tidak lagi 'Terhubung', baris OVO kembali muncul di 'Metode Lainnya').
Hasil: reports/repro/uat_ovo_putuskan/index.txt (tanpa nomor, tanpa screenshot). Nama berkas huruf kecil (pola langkah 'skrip')."""
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.getenv("DRIVER_KANDIDAT_4"):
    raise SystemExit("DRIVER_KANDIDAT_4 belum ada di .env (secret DRIVER_KANDIDAT)")
os.environ["UAT_AKUN_VAR"] = "DRIVER_KANDIDAT_4"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import uat_ovo_alur as a  # noqa: E402  (helper save/tutup_popup; main() tidak dijalankan saat diimpor)
from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402

a.OUT = ROOT / "reports" / "repro" / "uat_ovo_putuskan"
KREDENSIAL = re.compile(r"(?i)\bpin\b|kata sandi|password|\botp\b|kode verifikasi|masukkan (pin|kode)")
ketemu_kredensial = False


def main():
    global ketemu_kredensial
    a.OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    try:
        a.izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(os.getenv("DRIVER_KANDIDAT_4") or config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(5)
        a.tutup_popup(d)
        akun = "//android.widget.ImageView[starts-with(@content-desc, 'Akun')]"
        pengaturan = "//*[@content-desc='Pengaturan Pembayaran' or @text='Pengaturan Pembayaran']"
        for percobaan in range(1, 5):
            a.tutup_popup(d)
            a.tap(d, akun, f"akun_{percobaan}", 3)
            if d.find_elements("xpath", pengaturan):
                break
        a.tutup_popup(d)
        if not a.tap(d, pengaturan, "pengaturan_pembayaran", 4):
            a.index.append("   GAGAL: layar Pengaturan Pembayaran tidak terbuka")
            return
        a.save(d, "sebelum_putuskan")
        if not a.tap(d, "//*[starts-with(@content-desc,'OVO')]", "detail_ovo", 4):
            a.index.append("   GAGAL: baris OVO tidak ditemukan di Pengaturan Pembayaran")
            return
        # 'Putuskan' = tombol/aksi unlink di detail OVO (aksi UAT A4.0, bukan tombol pembayaran)
        els = d.find_elements("xpath", "//*[@content-desc='Putuskan' or @text='Putuskan' or starts-with(@content-desc,'Putuskan')]")
        if not els:
            a.index.append("   GAGAL: tombol 'Putuskan' tidak ditemukan")
            return
        els[0].click()
        for detik in (1, 3):
            time.sleep(detik)
            xml = a.save(d, f"setelah_ketuk_putuskan_{detik}dtk")
            if KREDENSIAL.search(" ".join(a.semua_label(xml))) or d.find_elements("xpath", "//android.widget.EditText"):
                ketemu_kredensial = True
        if ketemu_kredensial:
            a.index.append("   HASIL: MINTA_KREDENSIAL (dialog meminta PIN/kata sandi/OTP). Skrip berhenti; tidak ada yang diketik.")
            return
        # Konfirmasi saja: ketuk tombol konfirmasi di dialog (bukan 'Batal'/'Tutup')
        konfirmasi = d.find_elements("xpath", "//android.widget.Button[contains(@content-desc,'Putuskan') or contains(@content-desc,'Ya') "
                                              "or contains(@text,'Putuskan') or contains(@text,'Ya')]")
        if konfirmasi:
            a.index.append(f"   konfirmasi unlink diketuk ({len(konfirmasi)} kandidat tombol, memakai yang terakhir)")
            konfirmasi[-1].click()
            time.sleep(1)
            a.save(d, "setelah_konfirmasi_1dtk")
            time.sleep(4)
            a.save(d, "setelah_konfirmasi_5dtk")
        else:
            a.index.append("   tidak ada tombol konfirmasi terdeteksi; layar dicatat apa adanya")
        # Periksa hasil: kembali ke Pengaturan Pembayaran
        for _ in range(3):
            d.back()
            time.sleep(2)
            if d.find_elements("xpath", pengaturan) or d.find_elements("xpath", "//*[@content-desc='Pilih Metode']"):
                break
        xml = a.save(d, "pengaturan_setelah_putuskan")
        masih = bool(re.search(r"OVO/Saldo|OVO/.*Terhubung", xml.replace("&#10;", "/")))
        a.index.append(f"   HASIL: OVO masih terlihat 'Terhubung' di Pengaturan Pembayaran = {masih}")
    except Exception as e:  # noqa: BLE001
        a.index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
    finally:
        try:
            d.quit()
        except Exception:
            pass
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(a.index))
        (a.OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
