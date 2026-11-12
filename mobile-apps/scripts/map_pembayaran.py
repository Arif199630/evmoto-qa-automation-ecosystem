"""
Peta layar metode pembayaran aplikasi User: Pengaturan Pembayaran, tombol 'Aktifkan' GoPay/OVO, dan Isi Ulang saldo
EVMoto. Hanya membuka layar lalu kembali: TIDAK mengetik nomor e-wallet, tidak menekan 'Isi Ulang Sekarang', tidak
membayar. Tujuannya mengetahui apa yang dibutuhkan untuk menautkan GoPay/OVO dan mengisi saldo (OTP, PIN, VA, dll.).
Hasil: reports/repro/map_pembayaran/NN_<layar>.xml|.png dan index.txt
"""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL_INDEX", "15")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "map_pembayaran"
index = []
step = 0
DILARANG = re.compile(r"(?i)isi ulang sekarang|bayar|konfirmasi|kirim|lanjutkan pembayaran|tautkan sekarang|hubungkan sekarang")


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text|hint)="([^"]{1,70})"', xml)
            if t.strip() and t not in ("true", "false") and not t.startswith(("Ping", "PlatformException"))]


def save(d, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(teks(xml)[:26]).replace("&#10;", "/"))
    log(index[-1][:150])


def tap(d, xpath, nama, tunggu=3, idx=0):
    els = d.find_elements("xpath", xpath)
    if len(els) <= idx:
        index.append(f"   tidak ditemukan: {nama}")
        return False
    label = els[idx].get_attribute("content-desc") or els[idx].get_attribute("text") or ""
    if DILARANG.search(label):
        index.append(f"   DILEWATI (tombol transaksi): {nama} '{label}'")
        return False
    els[idx].click()
    time.sleep(tunggu)
    save(d, nama)
    return True


def back(d, n=1):
    for _ in range(n):
        d.back()
        time.sleep(2)


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
        tap(d, "//*[@content-desc='Lanjutkan']", "tutup_popup", 2)
        # Akun -> Pengaturan Pembayaran
        if tap(d, "//android.widget.ImageView[starts-with(@content-desc, 'Akun')]", "akun", 3):
            if tap(d, "//*[@content-desc='Pengaturan Pembayaran' or @text='Pengaturan Pembayaran']", "pengaturan_pembayaran", 4):
                for i in range(2):  # tombol Aktifkan pertama (GoPay?) dan kedua (OVO?)
                    if tap(d, "//*[@content-desc='Aktifkan' or @text='Aktifkan']", f"aktifkan_{i + 1}", 5, idx=i):
                        save(d, f"aktifkan_{i + 1}_5dtk")
                        back(d)
                        save(d, f"kembali_dari_aktifkan_{i + 1}")
                back(d)
            back(d)
        # Isi Ulang saldo: pilih nominal lalu lihat pilihan cara bayar, tanpa membayar
        tap(d, "//android.widget.ImageView[starts-with(@content-desc, 'Beranda')]", "beranda", 3)
        if tap(d, "//*[@content-desc='Isi Ulang']", "isi_ulang", 3):
            tap(d, "//*[@content-desc='Rp50.000' or @text='Rp50.000']", "pilih_50rb", 2)
            save(d, "setelah_pilih_nominal")
            back(d)
        # Place Order -> Metode Pembayaran (lihat tampilan GoPay/OVO saat belum tertaut)
        from Pages.booking_page import BookingPage
        bp = BookingPage(d)
        bp.open_place_order("Senayan City")
        save(d, "place_order")
        if tap(d, "//android.widget.ImageView[@content-desc='Cash']", "metode_pembayaran", 3):
            size = d.get_window_size()
            d.swipe(size["width"] // 2, int(size["height"] * 0.8), size["width"] // 2, int(size["height"] * 0.3), 600)
            time.sleep(1.5)
            save(d, "metode_pembayaran_gulir")
            back(d)
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
