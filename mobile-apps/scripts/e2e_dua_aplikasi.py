"""
E2E dua aplikasi di satu emulator (staging): Driver Online -> User memesan (Cash) -> Driver menerima, tiba, mulai,
selesai -> cek layar kedua aplikasi. Bukti (dump ringan + screenshot) di setiap langkah.

Satu sesi Appium, berpindah aplikasi dengan activate_app. Lokasi GPS emulator = area layanan Jakarta (CI), sehingga
driver dan penumpang berada di titik yang sama. Pesanan staging sungguhan (Cash); bila alur berhenti di tengah,
pesanan dibatalkan dari aplikasi User dan driver dikembalikan Offline.
Hasil: reports/repro/e2e_dua_aplikasi/NN_<app>_<langkah>.xml|.png dan ringkasan.txt
"""
import os
import re
import sys
import time
import traceback
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("E2E_USER_POOL_INDEX", "13")  # akun QA pool 13 (Cash); akun utama dipakai tarif_metode_bayar.py di run paralel
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from _diag_util import pindah_app, izinkan_lokasi, log  # noqa: E402

OUT = ROOT / "reports" / "repro" / "e2e_dua_aplikasi"
USER_PKG = config.APP_PACKAGE
DRIVER_PKG = getattr(config, "DRIVER_PACKAGE", "com.evmoto.driver.app")
TUJUAN = os.getenv("E2E_TUJUAN", "Senayan City")
ringkasan = []
step = 0


def teks(xml):
    return [t for t in re.findall(r'(?:content-desc|text|hint)="([^"]{1,70})"', xml)
            if t.strip() and t not in ("true", "false") and not t.startswith(("Ping", "PlatformException"))]


def save(d, app, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    base = OUT / f"{step:02d}_{app}_{nama}"
    base.with_suffix(".xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(base.with_suffix(".png")))
    line = f"{step:02d} [{app}] {nama}: " + " | ".join(teks(xml)[:22]).replace("&#10;", "/")
    ringkasan.append(re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", line))
    log(ringkasan[-1][:160])
    return xml


def ke(d, pkg):
    return pindah_app(d, pkg)


def ketuk(d, xpath, tunggu=2.0):
    els = d.find_elements("xpath", xpath)
    if not els:
        return False
    els[0].click()
    time.sleep(tunggu)
    return True


def tutup_popup(d):
    ketuk(d, "//*[@content-desc='Lanjutkan' or @text='Lanjutkan']", 1.5)


def geser(d, kata):
    """Geser (slide) tombol berlabel kata tertentu dari kiri ke kanan."""
    q = " or ".join(f"contains(@content-desc, '{k}') or contains(@text, '{k}')" for k in kata)
    els = d.find_elements("xpath", f"//*[{q}]")
    if not els:
        return None
    r = els[-1].rect
    y = r["y"] + r["height"] // 2
    label = (els[-1].get_attribute("content-desc") or els[-1].get_attribute("text") or "")[:50]
    d.swipe(r["x"] + 15, y, r["x"] + r["width"] - 10, y, 900)
    time.sleep(3)
    return label


def tunggu_label(d, kata, detik=90, interval=6, app="driver", nama="tunggu"):
    q = " or ".join(f"contains(@content-desc, '{k}') or contains(@text, '{k}')" for k in kata)
    mulai = time.time()
    while time.time() - mulai < detik:
        if d.find_elements("xpath", f"//*[{q}]"):
            ringkasan.append(f"   '{'/'.join(kata)}' muncul setelah {time.time() - mulai:.0f} dtk")
            return True
        time.sleep(interval)
    save(d, app, f"{nama}_habis_waktu")
    ringkasan.append(f"   '{'/'.join(kata)}' tidak muncul dalam {detik} dtk")
    return False


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver(is_driver_app=True)
    order_dibuat = False
    try:
        # 1. Driver login dan Online
        log("driver login")
        DrvLoginPage(d).login_as_driver()
        time.sleep(4)
        tutup_popup(d)
        save(d, "driver", "beranda")
        ketuk(d, "//*[@content-desc='Offline' or @text='Offline']", 3)
        save(d, "driver", "setelah_ketuk_offline")
        for label in ("Online", "Ya", "Aktifkan", "Lanjutkan", "Mulai"):
            if ketuk(d, f"//android.widget.Button[@content-desc='{label}' or @text='{label}']", 2):
                save(d, "driver", f"konfirmasi_{label}")
        save(d, "driver", "status_online")

        # 2. User memesan (Cash) dari titik yang sama
        d = ke(d, USER_PKG)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=15):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
            time.sleep(5)
        tutup_popup(d)
        save(d, "user", "beranda")
        from Pages.booking_page import BookingPage
        bp = BookingPage(d)
        bp.open_place_order(TUJUAN)
        save(d, "user", "place_order")
        if ketuk(d, "//android.widget.Button[@content-desc='Pesan EVMoto' or @text='Pesan EVMoto']", 5):
            order_dibuat = True
            save(d, "user", "setelah_pesan")
        else:
            ringkasan.append("   tombol 'Pesan EVMoto' tidak ditemukan")

        # 3. Driver menerima order
        d = ke(d, DRIVER_PKG)
        save(d, "driver", "menunggu_order")
        if tunggu_label(d, ["Swipe", "Geser", "Terima", "Orderan Baru", "Pesanan Baru"], 120, 6, "driver", "order_masuk"):
            save(d, "driver", "order_masuk")
            ringkasan.append(f"   geser terima: {geser(d, ['Swipe', 'Geser', 'Terima'])}")
            save(d, "driver", "setelah_terima")
            d = ke(d, USER_PKG)
            save(d, "user", "driver_ditemukan")
            d = ke(d, DRIVER_PKG)
            # 4. Tahap perjalanan driver: berangkat/tiba/mulai/selesai (label slider dibaca dari layar)
            for tahap in range(6):
                lbl = geser(d, ["Geser", "Swipe", "Tiba", "Mulai", "Selesai", "Berangkat", "Antar"])
                if not lbl:
                    break
                save(d, "driver", f"tahap_{tahap + 1}")
                ringkasan.append(f"   tahap {tahap + 1}: geser '{lbl}'")
                d = ke(d, USER_PKG)
                save(d, "user", f"tahap_{tahap + 1}")
                d = ke(d, DRIVER_PKG)
            save(d, "driver", "akhir_perjalanan")
            for label in ("Sudah Diterima", "Terima Pembayaran", "Selesai", "OK"):
                if ketuk(d, f"//*[@content-desc='{label}' or @text='{label}']", 3):
                    save(d, "driver", f"ketuk_{label.replace(' ', '_')}")
            d = ke(d, USER_PKG)
            save(d, "user", "akhir_perjalanan")
            order_dibuat = False if any("Selesai" in r or "Penilaian" in r for r in ringkasan[-3:]) else order_dibuat
    except Exception as e:
        traceback.print_exc()
        ringkasan.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            save(d, "x", "saat_error")
        except Exception:
            pass
    finally:
        try:
            if order_dibuat:
                d = ke(d, USER_PKG)
                for label in ("Batalkan", "Batalkan Pesanan", "Ya, Batalkan", "Ya"):
                    ketuk(d, f"//*[contains(@content-desc, '{label}') or contains(@text, '{label}')]", 2)
                save(d, "user", "pembersihan_batal")
            d = ke(d, DRIVER_PKG)
            ketuk(d, "//*[@content-desc='Online' or @text='Online']", 2)
            save(d, "driver", "pembersihan_offline")
        except Exception as e:
            ringkasan.append(f"pembersihan gagal: {type(e).__name__}")
        try:
            d.quit()
        except Exception:
            pass
        text = "\n".join(ringkasan)
        (OUT / "ringkasan.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
