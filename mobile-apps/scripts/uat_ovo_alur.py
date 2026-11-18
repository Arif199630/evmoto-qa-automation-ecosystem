"""Peta alur menautkan OVO di aplikasi User (build UAT) untuk persiapan eksekusi TC UAT OVO.

Hanya MEMBACA dan membuka layar: Akun -> Pengaturan Pembayaran -> 'Tambahkan Metode Lainnya' -> pilihan OVO -> layar tautan.
Tidak mengetik nomor OVO, OTP, atau PIN, dan tidak menekan tombol yang menyelesaikan penautan atau pembayaran.
Akun: UAT_POOL_INDEX (default 15 = akun QA pool, OVO belum tertaut; 0 = akun utama).
Hasil: reports/repro/uat_ovo_alur/NN_<layar>.xml|.png dan index.txt (teks layar + daftar label yang bisa diketuk)."""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("UAT_POOL_INDEX", "15")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "uat_ovo_alur"
index = []
step = 0
# Tombol yang menyelesaikan penautan/pembayaran TIDAK boleh diketuk oleh skrip pemetaan ini
DILARANG = re.compile(r"(?i)^(tautkan|hubungkan|link|lanjut|lanjutkan|konfirmasi|kirim|verifikasi|masuk|bayar|isi ulang sekarang|simpan|ya)\b")


def semua_label(xml):
    labels = re.findall(r'(?:content-desc|text|hint)="([^"]{1,90})"', xml)
    return [t.replace("&#10;", "/") for t in dict.fromkeys(labels)
            if t.strip() and t not in ("true", "false") and not t.startswith(("Ping", "PlatformException"))]


def save(d, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(semua_label(xml)[:45]))
    log(index[-1][:160])
    return xml


def tap(d, xpath, nama, tunggu=3, idx=0):
    els = d.find_elements("xpath", xpath)
    if len(els) <= idx:
        index.append(f"   tidak ditemukan: {nama}")
        return False
    label = (els[idx].get_attribute("content-desc") or els[idx].get_attribute("text") or "").strip()
    if DILARANG.search(label):
        index.append(f"   DILEWATI (tombol penyelesaian): {nama} '{label[:40]}'")
        return False
    els[idx].click()
    time.sleep(tunggu)
    save(d, nama)
    return True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(5)
        for el in d.find_elements("xpath", "//*[@content-desc='Lanjutkan']")[:1]:  # popup sambutan, bukan tombol penautan
            el.click()
            time.sleep(2)
            save(d, "tutup_popup")
        PENGATURAN = "//*[@content-desc='Pengaturan Pembayaran' or @text='Pengaturan Pembayaran']"
        akun_terbuka = False
        for percobaan in range(1, 5):  # ketukan pertama tepat setelah login sering diabaikan (bukti run 18 Nov 2026)
            tap(d, "//android.widget.ImageView[starts-with(@content-desc, 'Akun')]", f"akun_{percobaan}", 3)
            if d.find_elements("xpath", PENGATURAN):
                akun_terbuka = True
                break
            time.sleep(2)
        if akun_terbuka:
            if tap(d, PENGATURAN, "pengaturan_pembayaran", 4):
                save(d, "pengaturan_pembayaran_penuh")
                if tap(d, "//*[contains(@content-desc,'Tambahkan Metode Lainnya') or contains(@text,'Tambahkan Metode Lainnya')]",
                       "tambah_metode", 4):
                    # Buka entri OVO (bila ada) tanpa melanjutkan penautan
                    if tap(d, "//*[contains(@content-desc,'OVO') or contains(@text,'OVO')]", "pilih_ovo", 4):
                        save(d, "layar_tautan_ovo")
                        d.back()
                        time.sleep(2)
                    # Entri GoPay (sekadar dilihat, untuk peta cakupan)
                    if tap(d, "//*[contains(@content-desc,'GoPay') or contains(@text,'GoPay')]", "pilih_gopay", 4):
                        d.back()
                        time.sleep(2)
                    d.back()
                    time.sleep(2)
                # Entri OVO yang sudah tertaut (akun utama): buka detailnya bila ada
                tap(d, "//*[starts-with(@content-desc,'OVO')]", "detail_ovo_tertaut", 4)
    except Exception as e:
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(d, "saat_error")
        except Exception:
            pass
    finally:
        try:
            d.quit()
        except Exception:
            pass
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(index))
        (OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
