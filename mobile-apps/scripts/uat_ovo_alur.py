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
HANYA_LIHAT = os.getenv("UAT_HANYA_LIHAT", "") == "1"  # akun sudah tertaut OVO: hanya baca layar, jangan ketuk baris OVO/GoPay
AKUN_VAR = os.getenv("UAT_AKUN_VAR", "")  # nama variabel .env berisi nomor login UAT (mis. UAT_OVO_NOMOR1); kosong = akun pool
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
    if not AKUN_VAR:  # dengan nomor UAT tidak ada gambar: repo publik, nomor bisa terbaca
        d.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    try:
        jejak = f" [{d.current_package}/{(d.current_activity or '').split('.')[-1]}]"
    except Exception:
        jejak = ""
    index.append(f"{step:02d}_{nama}{jejak}: " + " | ".join(semua_label(xml)[:45]))
    log(index[-1][:160])
    return xml


def tutup_popup(d):
    """Popup 'Pemberitahuan Jam Operasional' (Button 'Lanjutkan') menelan ketukan; tutup bila ada. Hanya di fase navigasi awal."""
    for el in d.find_elements("xpath", "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")[:1]:
        el.click()
        time.sleep(1.5)
        return True
    return False


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


def judul_metode_lainnya(d):
    return bool(d.find_elements("xpath", "//*[@content-desc='Metode Lainnya']"))


def ketuk_baris(d, xpath, nama):
    """Ketuk baris dengan tiga cara bergantian (element.click, lalu clickGesture di tengah baris, lalu sekali lagi dengan tunggu 8 dtk).
    Layar dicatat 1 detik setelah tiap ketukan agar pesan sementara (snackbar/dialog) ikut terbaca. True bila layar berganti."""
    els = d.find_elements("xpath", xpath)
    if not els:
        index.append(f"   tidak ditemukan: {nama}")
        return False
    label = (els[0].get_attribute("content-desc") or "").strip()
    if DILARANG.search(label):
        index.append(f"   DILEWATI (tombol penyelesaian): {nama} '{label[:40]}'")
        return False
    rc = els[0].rect
    x, y = rc["x"] + rc["width"] // 2, rc["y"] + rc["height"] // 2
    for cara in ("click", "gesture", "gesture_tunggu_lama"):
        if cara == "click":
            els[0].click()
        else:
            d.execute_script("mobile: clickGesture", {"x": x, "y": y})
        time.sleep(1)
        save(d, f"{nama}_{cara}_1dtk")
        time.sleep(8 if cara == "gesture_tunggu_lama" else 3)
        if not judul_metode_lainnya(d):
            save(d, f"{nama}_layar_baru")
            return True
    index.append(f"   layar tidak berganti setelah tiga cara ketuk: {nama}")
    return False


def gulir_dan_catat_pengaturan(d):
    """Mode hanya-lihat: catat layar Pengaturan Pembayaran di tiap posisi gulir (tanpa mengetuk apa pun)."""
    size = d.get_window_size()
    x = size["width"] // 2
    for i in range(3):
        d.swipe(x, int(size["height"] * 0.75), x, int(size["height"] * 0.35), 500)
        time.sleep(1.0)
        save(d, f"pengaturan_pembayaran_gulir_{i + 1}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number((os.getenv(AKUN_VAR, "") if AKUN_VAR else "") or config.ACTIVE_PHONE)
            save(d, "login_nomor_diisi")
            login.click_submit_login()
            for detik in (1, 3, 6):  # pesan penolakan/validasi bisa hilang dalam ±3 detik, jadi dicatat bertahap
                time.sleep(detik if detik == 1 else 2 if detik == 3 else 3)
                save(d, f"login_setelah_masuk_{detik}dtk")
            if d.find_elements(*login.TITLE_OTP):
                login.input_otp_dev(config.ACTIVE_OTP)
            else:
                index.append("   layar OTP tidak muncul setelah 'Masuk': eksekusi dihentikan (tidak ada pendaftaran akun otomatis)")
                return
        time.sleep(5)
        for el in d.find_elements("xpath", "//*[@content-desc='Lanjutkan']")[:1]:  # popup sambutan, bukan tombol penautan
            el.click()
            time.sleep(2)
            save(d, "tutup_popup")
        PENGATURAN = "//*[@content-desc='Pengaturan Pembayaran' or @text='Pengaturan Pembayaran']"
        akun_terbuka = False
        for percobaan in range(1, 5):  # ketukan pertama tepat setelah login sering diabaikan (bukti run 18 Nov 2026)
            tutup_popup(d)
            tap(d, "//android.widget.ImageView[starts-with(@content-desc, 'Akun')]", f"akun_{percobaan}", 3)
            if d.find_elements("xpath", PENGATURAN):
                akun_terbuka = True
                break
            time.sleep(2)
        if akun_terbuka:
            tutup_popup(d)
            if tap(d, PENGATURAN, "pengaturan_pembayaran", 4):
                save(d, "pengaturan_pembayaran_penuh")
                if HANYA_LIHAT:
                    gulir_dan_catat_pengaturan(d)
                elif tap(d, "//*[contains(@content-desc,'Tambahkan Metode Lainnya') or contains(@text,'Tambahkan Metode Lainnya')]",
                         "tambah_metode", 4):
                    # Peta 18 Nov 2026: 'Metode Lainnya' berisi baris View clickable 'GoPay / <nomor akun>' dan 'OVO / <nomor akun>'
                    # (nomor OVO = nomor login akun). Ketuk baris OVO berulang sampai layar berganti, tanpa melanjutkan penautan.
                    for nama_baris in ("OVO", "GoPay"):
                        baris = f"//android.view.View[@clickable='true' and starts-with(@content-desc,'{nama_baris}')]"
                        if ketuk_baris(d, baris, f"baris_{nama_baris.lower()}") and not judul_metode_lainnya(d):
                            d.back()
                            time.sleep(2)
                    d.back()
                    time.sleep(2)
                # Entri OVO yang sudah tertaut (akun utama): buka detailnya bila ada
                if tap(d, "//*[starts-with(@content-desc,'OVO')]", "detail_ovo_tertaut", 4) and os.getenv("UAT_BUKA_DETAIL") == "1":
                    # Mode lihat: buka 'Lihat riwayat pembayaran' dan 'Pengaturan' (hanya dibaca, tidak ada toggle/tombol aksi yang diketuk)
                    for nama, xp in (("riwayat_pembayaran", "//*[starts-with(@content-desc,'Lihat riwayat pembayaran')]"),
                                     ("pengaturan_ovo", "//*[@content-desc='Pengaturan' or @text='Pengaturan']")):
                        if tap(d, xp, nama, 4):
                            gulir_dan_catat_pengaturan(d)
                            d.back()
                            time.sleep(2)
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
