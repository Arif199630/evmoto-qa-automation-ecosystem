"""
Peta layar alur pemesanan + Beranda + Akun aplikasi User (akun QA Auto), untuk memperbaiki locator test_home,
test_booking_order, test_profil, test_gopay/ovo berdasarkan layar asli.

Hanya membuka layar lalu kembali: TIDAK menekan 'Pesan EVMoto', tidak top up, tidak tarik dana, tidak menyimpan alamat,
tidak logout. Hasil: reports/repro/map_booking/NN_<layar>.xml|.png dan index.txt
"""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL_INDEX", "13")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from _diag_util import izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "map_booking"
index = []
step = 0
DILARANG = re.compile(r"(?i)pesan evmoto|pesan sekarang|isi ulang sekarang|tarik dana sekarang|simpan|keluar|logout|hapus")


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text|hint)="([^"]{1,60})"', xml) if t.strip() and t not in ("true", "false")]


def tutup_dialog_sistem(driver):
    """Dialog izin Android (lokasi / notifikasi) menutupi layar aplikasi: ketuk izinkan."""
    izinkan_lokasi(driver)
    for label in ("Izinkan", "Allow"):
        els = driver.find_elements("xpath", f"//*[@text='{label}' and contains(@resource-id, 'permission')]")
        if els:
            els[0].click()
            time.sleep(1)


def save(driver, nama):
    global step
    step += 1
    log(f"simpan layar {step:02d}_{nama}")
    tutup_dialog_sistem(driver)
    xml = dump_ringan(driver)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    driver.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    index.append(f"{step:02d}_{nama}: " + " | ".join(teks(xml)[:26]).replace("&#10;", "\\n"))


def tap(driver, xpath, nama, tunggu=3):
    tutup_dialog_sistem(driver)
    els = driver.find_elements("xpath", xpath)
    if not els:
        index.append(f"   tidak ditemukan: {nama} ({xpath})")
        return False
    label = (els[0].get_attribute("content-desc") or els[0].get_attribute("text") or "")
    if DILARANG.search(label):
        index.append(f"   DILEWATI (tombol transaksi): {nama} '{label}'")
        return False
    els[0].click()
    time.sleep(tunggu)
    save(driver, nama)
    return True


def back(driver, kali=1):
    for _ in range(kali):
        driver.back()
        time.sleep(2)


def gulir(driver, nama, kali=2):
    size = driver.get_window_size()
    for i in range(kali):
        driver.swipe(size["width"] // 2, int(size["height"] * 0.8), size["width"] // 2, int(size["height"] * 0.35), 600)
        time.sleep(1.5)
        save(driver, f"{nama}_gulir_{i + 1}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    driver = DriverFactory.create_driver()
    try:
        tutup_dialog_sistem(driver)
        login = LoginPage(driver)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(6)
        save(driver, "beranda")  # tanpa menggulir: gulir menutup panel tujuan (peta CI 12 Nov 2026)
        # Popup 'Pemberitahuan Jam Operasional' (tombol Lanjutkan) menutupi Beranda saat dibuka
        tap(driver, "//*[@content-desc='Lanjutkan']", "tutup_popup_jam_operasional", 2)
        # Alur pemesanan: ketukan pertama pada kolom tujuan hanya menaikkan panel (peta CI 12 Nov 2026), ketuk lagi
        kolom = "//*[contains(@hint, 'mau kemana') or contains(@text, 'mau kemana') or contains(@content-desc, 'mau kemana')]"
        tap(driver, kolom, "panel_naik", 2)
        if not driver.find_elements("xpath", "//android.widget.EditText"):
            tap(driver, kolom, "form_tujuan_ketuk_kedua", 3)
        # Elemen kolom tujuan adalah wadah panel (kolom + chip Rumah/Kantor/Lainnya): element.click() mengetuk tengah
        # wadah, bukan kolomnya. Coba ketuk koordinat kolom (bagian atas wadah).
        for percobaan in range(2):
            if driver.find_elements("xpath", "//android.widget.EditText"):
                break
            els = driver.find_elements("xpath", kolom)
            if not els:
                break
            r = els[0].rect
            x, y = r["x"] + r["width"] // 2, r["y"] + 20
            index.append(f"   ketuk koordinat kolom tujuan ({x},{y}) dari wadah {r}")
            driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
            time.sleep(3)
            save(driver, f"form_tujuan_koordinat_{percobaan + 1}")
        if driver.find_elements("xpath", "//android.widget.EditText"):
            fields = driver.find_elements("xpath", "//android.widget.EditText")
            index.append(f"   kolom di form tujuan: {[(f.get_attribute('hint') or f.get_attribute('text')) for f in fields]}")
            if fields:
                fields[-1].click()
                fields[-1].send_keys("Senayan City")
                time.sleep(4)
                save(driver, "saran_tujuan")
                index.append("   lokasi jemput di form: " + " | ".join(
                    (e.get_attribute("content-desc") or e.get_attribute("text") or "")[:50]
                    for e in driver.find_elements("xpath", "//*[contains(@class,'View') and string-length(@content-desc) > 3]")[:6]))
                tap(driver, "(//*[contains(@content-desc, 'Senayan') or contains(@text, 'Senayan')])[last()]", "pilih_saran", 6)
                # Layar konfirmasi 'Lokasi Penjemputan' / tujuan: tombol 'Pilih Lokasi' (bukan transaksi), bisa dua kali
                for k in range(3):
                    if not tap(driver, "//*[@content-desc='Pilih Lokasi' or @text='Pilih Lokasi']", f"konfirmasi_lokasi_{k + 1}", 5):
                        break
                tap(driver, "//*[@content-desc='Lanjutkan']", "tutup_popup_place_order", 2)
                gulir(driver, "place_order", 1)
                tap(driver, "//*[contains(@content-desc, 'Tunai') or contains(@content-desc, 'Pembayaran') or contains(@content-desc, 'Cash')]",
                    "pilih_pembayaran", 3)
                back(driver)
                save(driver, "kembali_ke_place_order")
            back(driver, 3)
        save(driver, "kembali_beranda")
        if tap(driver, "//*[starts-with(@content-desc, 'Rumah')]", "alamat_rumah", 3):
            back(driver)
        if tap(driver, "//*[@content-desc='Isi Ulang']", "isi_ulang", 3):
            back(driver)
        if tap(driver, "//*[@content-desc='Riwayat']", "riwayat_saldo", 3):
            back(driver)
        if tap(driver, "//*[starts-with(@content-desc, 'Akun')]", "akun", 3):
            gulir(driver, "akun", 3)
        tap(driver, "//*[starts-with(@content-desc, 'Aktivitas')]", "aktivitas_akun_qa", 3)
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
