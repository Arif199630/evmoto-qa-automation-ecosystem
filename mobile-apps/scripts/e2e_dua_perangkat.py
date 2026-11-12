"""
E2E User + Driver di DUA perangkat (CI suite skrip2), staging, metode bayar Cash:
  emulator-5556: aplikasi Driver (akun driver uji), tetap di depan selama test (lokasi driver terus terkirim).
  emulator-5554: aplikasi User (akun QA pool E2E_USER_POOL_INDEX, default 13).
Alasan: run 43193330852 (satu perangkat, pindah aplikasi) menampilkan 'Belum ada driver yang tersedia' dan driver
tidak mendapat tawaran; saat aplikasi Driver di belakang, lokasi driver mungkin tidak terkirim. Dua perangkat
meniru kondisi nyata.
Alur: driver Online -> user pesan (Cash) -> driver geser terima -> tahap perjalanan -> layar akhir kedua aplikasi.
Pembersihan: pesanan yang belum selesai dibatalkan dari User, driver Offline.
Hasil: reports/repro/e2e_dua_perangkat/NN_<app>_<langkah>.xml|.png dan ringkasan.txt
"""
import os
import sys
import time
import traceback
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("E2E_USER_POOL_INDEX", "13")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import e2e_dua_aplikasi as e  # noqa: E402  (helper save/ketuk/geser/tunggu_label)
from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.booking_page import BookingPage  # noqa: E402
from _diag_util import pesan_order  # noqa: E402

e.OUT = ROOT / "reports" / "repro" / "e2e_dua_perangkat"
PESAN = "//android.widget.Button[@content-desc='Pesan EVMoto' or @text='Pesan EVMoto']"


def main():
    e.OUT.mkdir(parents=True, exist_ok=True)
    r = e.ringkasan
    dd = du = None
    order_dibuat = False
    try:
        dd = DriverFactory.create_driver(is_driver_app=True, udid="emulator-5556", system_port=8201)
        du = DriverFactory.create_driver(udid="emulator-5554", system_port=8200)
        r.append("Driver: emulator-5556 | User: emulator-5554 (akun QA pool) | metode bayar: Cash")
        DrvLoginPage(dd).login_as_driver()
        time.sleep(4)
        e.tutup_popup(dd)
        xml = e.save(dd, "driver", "beranda")
        if "content-desc=\"Offline\"" in xml:
            e.ketuk(dd, "//*[@content-desc='Offline' or @text='Offline']", 3)
        xml = e.save(dd, "driver", "status")
        r.append(f"   status driver: {'Online' if 'content-desc=\"Online\"' in xml else 'TIDAK Online'}")

        lp = LoginPage(du)
        if lp.is_login_screen_displayed(timeout=20):
            lp.input_phone_number(config.ACTIVE_PHONE)
            lp.click_submit_login()
            lp.input_otp_dev(config.ACTIVE_OTP)
            time.sleep(5)
        e.tutup_popup(du)
        e.save(du, "user", "beranda")
        BookingPage(du).open_place_order(e.TUJUAN)
        e.save(du, "user", "place_order")
        if pesan_order(du):
            order_dibuat = True
            for i in range(3):
                e.save(du, "user", f"setelah_pesan_{i + 1}")
                time.sleep(8)
        else:
            r.append("   'Pesan EVMoto' sudah diketuk 3x tetapi layar Place Order tidak berubah")
            e.save(du, "user", "pesan_tidak_terkirim")

        if e.tunggu_label(dd, ["Swipe", "Geser", "Terima", "Orderan Baru", "Pesanan Baru"], 150, 5, "driver", "order_masuk"):
            e.save(dd, "driver", "order_masuk")
            r.append(f"   geser terima: {e.geser(dd, ['Swipe', 'Geser', 'Terima'])}")
            e.save(dd, "driver", "setelah_terima")
            e.save(du, "user", "driver_ditemukan")
            for tahap in range(6):
                lbl = e.geser(dd, ["Geser", "Swipe", "Tiba", "Mulai", "Selesai", "Berangkat", "Antar"])
                if not lbl:
                    break
                r.append(f"   tahap {tahap + 1}: geser '{lbl}'")
                e.save(dd, "driver", f"tahap_{tahap + 1}")
                e.save(du, "user", f"tahap_{tahap + 1}")
            for label in ("Sudah Diterima", "Terima Pembayaran", "Selesai", "OK"):
                if e.ketuk(dd, f"//*[@content-desc='{label}' or @text='{label}']", 3):
                    e.save(dd, "driver", f"ketuk_{label.replace(' ', '_')}")
            e.save(dd, "driver", "akhir")
            xml = e.save(du, "user", "akhir")
            if any(k in xml for k in ("Penilaian", "penilaian", "Selesai", "Perjalanan selesai")):
                order_dibuat = False
    except Exception as ex:
        traceback.print_exc()
        r.append(f"langkah gagal: {type(ex).__name__}: {str(ex)[:200]}")
    finally:
        try:
            if order_dibuat and du is not None:
                for label in ("Batalkan", "Batalkan Pesanan", "Ya, Batalkan", "Ya"):
                    e.ketuk(du, f"//*[contains(@content-desc, '{label}') or contains(@text, '{label}')]", 2)
                e.save(du, "user", "pembersihan_batal")
            if dd is not None:
                e.ketuk(dd, "//*[@content-desc='Online' or @text='Online']", 2)
                e.save(dd, "driver", "pembersihan_offline")
        except Exception as ex:
            r.append(f"pembersihan gagal: {type(ex).__name__}")
        for d in (dd, du):
            try:
                if d is not None:
                    d.quit()
            except Exception:
                pass
        text = "\n".join(r)
        (e.OUT / "ringkasan.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
