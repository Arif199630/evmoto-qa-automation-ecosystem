"""
Peta layar lengkap aplikasi Driver (termasuk bagian yang perlu digulir dan tab ketiga), untuk memperbaiki locator
test_drv_menu / test_drv_activity berdasarkan layar asli.

Hanya membuka layar lalu kembali: tidak Online, tidak logout, tidak menghapus akun, tidak mengirim masukan.
Di dalam Kelola Akun / Pengaturan Lainnya layar hanya digulir dan disimpan; tidak ada item yang diketuk.
'Cara Penggunaan Aplikasi' dibuka paling akhir karena emulator CI mati saat layar itu terbuka (run 43134989584).
Hasil: reports/repro/map_driver/NN_<layar>.xml|.png dan index.txt
"""
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_home_page import DrvHomePage  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "map_driver"
index = []
step = 0


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text)="([^"]{1,60})"', xml) if t.strip() and t not in ("true", "false")]


def save(driver, nama):
    global step
    step += 1
    log(f"simpan layar {step:02d}_{nama}")
    xml = driver.page_source
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    driver.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(teks(xml)[:24]).replace("&#10;", "\\n"))


def tap(driver, xpath, nama, tunggu=3):
    log(f"ketuk {nama}")
    izinkan_lokasi(driver)
    els = driver.find_elements("xpath", xpath)
    if not els:
        index.append(f"   tidak ditemukan: {nama} ({xpath})")
        return False
    els[0].click()
    time.sleep(tunggu)
    save(driver, nama)
    return True


def gulir(driver, nama, kali=3):
    size = driver.get_window_size()
    for i in range(kali):
        driver.swipe(size["width"] // 2, int(size["height"] * 0.75), size["width"] // 2, int(size["height"] * 0.3), 600)
        time.sleep(1.5)
        save(driver, f"{nama}_gulir_{i + 1}")


def back(driver):
    driver.back()
    time.sleep(2)


# Penanda layar Menu: header 'Total Orderan' tetap tampil saat daftar menu digulir (peta 12 Nov 2026: 04-07)
PENANDA_MENU = "//*[@content-desc='Total Orderan']"


def kembali_ke_driver(driver):
    """Bila layar lain (mis. WhatsApp / pemilih aplikasi dari 'Hubungi Customer Service') di depan, tekan Back
    lalu bawa aplikasi Driver ke depan lagi."""
    if driver.current_package != Config.DRIVER_PACKAGE:
        log(f"layar di depan milik {driver.current_package}, kembali ke aplikasi Driver")
        back(driver)
        if driver.current_package != Config.DRIVER_PACKAGE:
            driver.activate_app(Config.DRIVER_PACKAGE)
            time.sleep(3)


def pastikan_di_menu(driver):
    """Buka tab Menu bila layar Menu belum tampil."""
    if not driver.find_elements("xpath", PENANDA_MENU):
        els = driver.find_elements("xpath", "//*[@content-desc='Menu']")
        if els:
            els[0].click()
            time.sleep(3)


def cari_di_menu(driver, label):
    """Cari item Menu berlabel persis; gulir ke bawah lalu ke atas bila belum terlihat. Kembalikan elemen atau None."""
    xpath = f"//*[@content-desc='{label}']"
    size = driver.get_window_size()
    x = size["width"] // 2
    for arah in ("bawah", "atas"):
        for _ in range(4):
            els = driver.find_elements("xpath", xpath)
            if els:
                return els[0]
            if arah == "bawah":
                driver.swipe(x, int(size["height"] * 0.75), x, int(size["height"] * 0.35), 600)
            else:
                driver.swipe(x, int(size["height"] * 0.35), x, int(size["height"] * 0.75), 600)
            time.sleep(1.5)
    return None


def buka_dari_menu(driver, label, nama, kali_gulir=0, tunggu=4):
    """Buka satu item Menu, simpan layarnya (dan gulirannya), lalu kembali ke Menu. Tidak mengetuk apa pun di dalam."""
    pastikan_di_menu(driver)
    izinkan_lokasi(driver)
    el = cari_di_menu(driver, label)
    if el is None:
        index.append(f"   tidak ditemukan di Menu: {label}")
        return False
    log(f"ketuk menu {label}")
    el.click()
    time.sleep(tunggu)
    save(driver, nama)
    if kali_gulir and driver.current_package == Config.DRIVER_PACKAGE:
        gulir(driver, nama, kali_gulir)
    back(driver)
    kembali_ke_driver(driver)
    save(driver, f"setelah_{nama}")
    return True


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    driver = DriverFactory.create_driver(is_driver_app=True)
    try:
        log("login driver")
        DrvLoginPage(driver).login_as_driver()
        time.sleep(5)
        izinkan_lokasi(driver)
        try:
            DrvHomePage(driver).dismiss_operational_popup()
        except Exception:
            pass
        save(driver, "beranda")
        gulir(driver, "beranda", 2)
        # Menu (bagian bawah biasanya berisi bahasa, logout, hapus akun)
        if tap(driver, "//*[starts-with(@content-desc, 'Menu')]", "menu", 3):
            gulir(driver, "menu", 3)
        tap(driver, "//*[starts-with(@content-desc, 'Beranda')]", "kembali_beranda", 3)
        # Aktivitas Saya: tiga tab (tab ketiga di luar layar, perlu digeser)
        if tap(driver, "//*[@content-desc='Aktivitas Saya']", "aktivitas_saya", 4):
            tap(driver, "//*[starts-with(@content-desc, 'Coupon Income')]", "tab_coupon_income", 3)
            size = driver.get_window_size()
            driver.swipe(int(size["width"] * 0.85), 110, int(size["width"] * 0.15), 110, 500)  # geser baris tab
            time.sleep(1)
            save(driver, "tab_digeser")
            tap(driver, "//*[contains(@content-desc, 'Tab 3 dari 3') or contains(@content-desc, 'Tab 3 of 3')]", "tab_ketiga", 3)
            back(driver)
        if tap(driver, "//*[@content-desc='Order Saya']", "order_saya", 4):
            tap(driver, "//*[starts-with(@content-desc, 'Normal Order')]", "tab_normal_order", 3)
            tap(driver, "//*[starts-with(@content-desc, 'Advance Booking')]", "tab_advance_booking", 3)
            # Rincian satu order selesai (kartu 'Reguler\nSelesai\nLokasi Tujuan...'); hanya dibuka lalu kembali
            tap(driver, "//*[starts-with(@content-desc, 'Semua')]", "tab_semua", 3)
            if tap(driver, "(//*[contains(@content-desc, 'Lokasi Tujuan')])[1]", "detail_order", 4):
                gulir(driver, "detail_order", 2)
                back(driver)
            back(driver)
        # eWallet lewat kartu 'Saldo Kamu' di Beranda; bagian bawah ('Aktivitas Anda') perlu digulir
        if tap(driver, "//*[starts-with(@content-desc, 'Saldo Kamu')]", "saldo_kamu_ewallet", 4):
            gulir(driver, "saldo_kamu_ewallet", 2)
            back(driver)
            save(driver, "setelah_saldo_kamu")
        if tap(driver, "//*[starts-with(@content-desc, 'Menu')]", "menu_lagi", 3):
            if tap(driver, "//*[@content-desc='Kirim Masukan']", "kirim_masukan", 3):
                back(driver)
            if tap(driver, "//*[@content-desc='Evaluasi Saya']", "evaluasi_saya", 3):
                back(driver)
            # Item Menu lain yang belum terpetakan (open-and-back saja; di dalamnya tidak ada yang diketuk)
            buka_dari_menu(driver, "Izinkan Order di Layar Utama", "izinkan_order_layar_utama")
            buka_dari_menu(driver, "Pilih Jenis Layanan", "pilih_jenis_layanan", kali_gulir=1)
            buka_dari_menu(driver, "Ubah Kendaraan", "ubah_kendaraan", kali_gulir=1)
            buka_dari_menu(driver, "Rekomendasi Kepada Teman", "rekomendasi_kepada_teman", kali_gulir=1)
            # Bisa membuka WhatsApp / pemilih aplikasi: disimpan lalu Back ke aplikasi Driver
            buka_dari_menu(driver, "Hubungi Customer Service", "hubungi_customer_service")
            # Bahasa, bersihkan cache, Tentang Kami diduga ada di sini: hanya digulir, tidak diketuk
            buka_dari_menu(driver, "Pengaturan Lainnya", "pengaturan_lainnya", kali_gulir=2)
            # Logout / Hapus Akun diduga ada di sini: hanya digulir, tombolnya TIDAK diketuk
            buka_dari_menu(driver, "Kelola Akun", "kelola_akun", kali_gulir=2)
            pastikan_di_menu(driver)
            cari_di_menu(driver, "Cara Penggunaan Aplikasi")
            if tap(driver, "//*[@content-desc='Cara Penggunaan Aplikasi']", "cara_penggunaan_5dtk", 5):
                gulir(driver, "cara_penggunaan", 3)
                back(driver)
                save(driver, "setelah_cara_penggunaan")
    except Exception as e:
        index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(driver, "saat_error")
        except Exception:
            pass
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        text = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(index))
        (OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
