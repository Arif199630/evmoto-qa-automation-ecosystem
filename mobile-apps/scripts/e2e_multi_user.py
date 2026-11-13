"""
E2E multi-pengguna dengan dua emulator (CI suite skrip2), staging, metode bayar Cash:
  emulator-5558: aplikasi Driver (akun driver uji), sendirian dan selalu di depan.
  emulator-5554: aplikasi User A (akun QA pool E2E_USER_A_INDEX, default 12).
  emulator-5556: aplikasi User B (akun QA pool E2E_USER_B_INDEX, default 14).
Run 43195711401 membuktikan Driver harus di perangkat sendiri: User di perangkat yang sama dengan aplikasi Driver
(di belakang) melihat 'Belum ada driver yang tersedia', User di perangkat lain melihat 'Driver terdekat 0 m'.

Skenario:
  1. Race condition: Driver Online; User A dan User B memesan hampir bersamaan dari titik yang sama ke tujuan yang
     sama. Diharapkan: satu pesanan diterima driver, pesanan lain TIDAK di-assign ke driver yang sama.
  2. Driver sibuk: selama driver mengantar pesanan pertama, pesanan user lain tidak ditawarkan ke driver itu.
Bukti (dump ringan + screenshot) dari ketiga layar di setiap langkah. Di akhir, pesanan dibatalkan dan driver Offline.
Hasil: reports/repro/e2e_multi_user/NN_<perangkat>_<langkah>.xml|.png dan ringkasan.txt
"""
import os
import re
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

OUT = ROOT / "reports" / "repro" / "e2e_multi_user"
ringkasan = []
step = 0


def akun_pool(idx):
    prefix = os.getenv("TEST_USER_POOL_PREFIX", "")
    return f"{prefix}{idx:02d}" if prefix and idx >= 2 else os.getenv("DEV_PHONE", "")


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from config import config
    from core.driver_factory import DriverFactory
    from core.screen_dump import dump as dump_ringan
    from Pages.login_page import LoginPage
    from Pages.drv_login_page import DrvLoginPage
    from Pages.booking_page import BookingPage
    from _diag_util import izinkan_lokasi, log, pindah_app, pesan_order

    user_pkg, driver_pkg = config.APP_PACKAGE, getattr(config, "DRIVER_PACKAGE", "com.evmoto.driver.app")
    tujuan = os.getenv("E2E_TUJUAN", "Senayan City")
    phone_a = akun_pool(int(os.getenv("E2E_USER_A_INDEX", "12")))
    phone_b = akun_pool(int(os.getenv("E2E_USER_B_INDEX", "14")))
    OUT.mkdir(parents=True, exist_ok=True)

    def teks(xml):
        return [t for t in re.findall(r'(?:content-desc|text|hint)="([^"]{1,70})"', xml)
                if t.strip() and t not in ("true", "false") and not t.startswith(("Ping", "PlatformException"))]

    def save(d, dev, nama):
        global step
        step += 1
        izinkan_lokasi(d)
        xml = dump_ringan(d)
        base = OUT / f"{step:02d}_{dev}_{nama}"
        base.with_suffix(".xml").write_text(xml, encoding="utf-8")
        d.save_screenshot(str(base.with_suffix(".png")))
        line = f"{step:02d} [{dev}] {nama}: " + " | ".join(teks(xml)[:20]).replace("&#10;", "/")
        ringkasan.append(re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", line))
        log(ringkasan[-1][:150])
        return xml

    def ke(d, pkg):
        return pindah_app(d, pkg, udid="emulator-5554", system_port=8200)

    def ketuk(d, xpath, tunggu=2.0):
        els = d.find_elements("xpath", xpath)
        if els:
            els[0].click()
            time.sleep(tunggu)
            return True
        return False

    def login_user(d, phone):
        lp = LoginPage(d)
        if lp.is_login_screen_displayed(timeout=15):
            lp.input_phone_number(phone)
            lp.click_submit_login()
            lp.input_otp_dev(config.ACTIVE_OTP)
            time.sleep(5)
        ketuk(d, "//*[@content-desc='Lanjutkan']", 1.5)

    def pesan(d, dev):
        BookingPage(d).open_place_order(tujuan)
        save(d, dev, "place_order")
        ok = ketuk(d, "//android.widget.Button[@content-desc='Pesan EVMoto' or @text='Pesan EVMoto']", 3)
        save(d, dev, "setelah_pesan")
        return ok

    def batalkan(d, dev):
        for label in ("Batalkan", "Batalkan Pesanan", "Ya, Batalkan", "Ya"):
            ketuk(d, f"//*[contains(@content-desc, '{label}') or contains(@text, '{label}')]", 2)
        save(d, dev, "pembersihan_batal")

    dv = da = db = None
    diterima_global = {}
    pesanan = {"A": False, "B": False}
    try:
        dv = DriverFactory.create_driver(is_driver_app=True, udid="emulator-5558", system_port=8202)
        da = DriverFactory.create_driver(udid="emulator-5554", system_port=8200)
        db = DriverFactory.create_driver(udid="emulator-5556", system_port=8201)
        ringkasan.append("Driver: emulator-5558 | User A: emulator-5554 | User B: emulator-5556 (akun QA pool); metode bayar: Cash")
        # Driver Online di perangkat A
        DrvLoginPage(dv).login_as_driver()
        time.sleep(4)
        ketuk(dv, "//*[@content-desc='Lanjutkan' or @text='Lanjutkan']", 1.5)
        ketuk(dv, "//*[@content-desc='Offline' or @text='Offline']", 3)
        save(dv, "driver", "status_online")
        # User A dan User B login, lalu memesan hampir bersamaan
        login_user(da, phone_a)
        login_user(db, phone_b)
        save(da, "A-user", "beranda")
        save(db, "B-user", "beranda")
        for nama, d_ in (("A", da), ("B", db)):
            BookingPage(d_).open_place_order(tujuan)
            if not d_.find_elements("xpath", "//android.widget.Button[@content-desc='Pesan EVMoto']"):
                # run 43348861484: User B tertahan di form rute; ulangi dari Beranda sekali
                ringkasan.append(f"   User {nama}: Place Order belum tampil, diulang")
                d_.terminate_app(user_pkg)
                d_.activate_app(user_pkg)
                time.sleep(5)
                ketuk(d_, "//*[@content-desc='Lanjutkan' or @text='Lanjutkan']", 1.5)
                BookingPage(d_).open_place_order(tujuan)
        t0 = time.time()
        pesanan["A"] = pesan_order(da)
        pesanan["B"] = pesan_order(db)
        ringkasan.append(f"   pesanan A={pesanan['A']} B={pesanan['B']}, selisih {time.time() - t0:.1f} dtk")
        save(da, "A-user", "setelah_pesan")
        save(db, "B-user", "setelah_pesan")
        # Driver menerima satu pesanan
        diterima = None
        for _ in range(20):
            xml = save(dv, "driver", "cek_order_masuk")
            if re.search(r"Swipe|Geser|Terima|Orderan Baru|Pesanan Baru", xml):
                els = dv.find_elements("xpath", "//*[contains(@content-desc,'Swipe') or contains(@content-desc,'Geser') or contains(@text,'Geser') or contains(@content-desc,'Terima')]")
                if els:
                    r = els[-1].rect
                    y = r["y"] + r["height"] // 2
                    dv.swipe(r["x"] + 15, y, r["x"] + r["width"] - 10, y, 900)
                    time.sleep(4)
                    diterima = save(dv, "driver", "setelah_terima")
                break
            time.sleep(6)
        diterima_global["ya"] = bool(diterima)
        ringkasan.append("   driver menerima pesanan" if diterima else "   tidak ada pesanan masuk ke driver dalam ±2 menit")
        # Status kedua user setelah driver menerima: hanya satu yang boleh mendapat driver
        xa = save(da, "A-user", "status_setelah_driver_terima")
        xb = save(db, "B-user", "status_setelah_driver_terima")
        dapat = [n for n, x in (("A", xa), ("B", xb)) if re.search(r"B 9099|testdr|Driver menuju|sedang menuju|dalam perjalanan", x)]
        diterima_global["dapat"] = dapat
        if not (pesanan["A"] and pesanan["B"]):
            ringkasan.append(f"HASIL race condition: TIDAK VALID, order terkirim A={pesanan['A']} B={pesanan['B']} "
                             f"(butuh dua order aktif bersamaan); user yang mendapat driver = {dapat or 'tidak ada'}")
        else:
            ringkasan.append(f"HASIL race condition: user yang mendapat driver = {dapat or 'tidak ada'} "
                             f"({'BENAR: hanya satu' if len(dapat) == 1 else 'PERLU DICEK' if not dapat else 'SALAH: lebih dari satu user mendapat driver yang sama'})")
        # Driver sibuk: selama 60 dtk, pesanan user lain tidak boleh ditawarkan ke driver ini
        tawaran = 0
        for _ in range(6):
            xml = save(dv, "driver", "selama_mengantar")
            tawaran += 1 if re.search(r"Orderan Baru|Pesanan Baru|Swipe untuk mendapatkan", xml) else 0
            time.sleep(10)
        if diterima:
            ringkasan.append(f"HASIL driver sibuk: tawaran pesanan baru selama mengantar = {tawaran} kali "
                             f"({'BENAR' if tawaran == 0 else 'PERLU DICEK'})")
        else:
            ringkasan.append("HASIL driver sibuk: tidak bisa dinilai (driver tidak memegang order)")
    except Exception as e:
        traceback.print_exc()
        ringkasan.append(f"langkah gagal: {type(e).__name__}: {str(e)[:220]}")
    finally:
        if diterima_global.get("ya"):
            try:
                import e2e_dua_perangkat as ep
                ep.e.OUT = OUT
                try:
                    dv.find_elements("xpath", "//*")
                except Exception:
                    dv = DriverFactory.create_driver(no_reset=True, is_driver_app=True, udid="emulator-5558", system_port=8202)
                if ep.buka_order_driver(dv, ep.e) or ep.slider_driver(dv, 10) is not None:
                    pemenang = da if "A" in diterima_global.get("dapat", ["A"]) else db
                    ep.jalankan_tahap(dv, pemenang, ep.e, ringkasan, "bersih")
                    ringkasan.append("   pembersihan: order yang diterima diselesaikan lewat Driver (Cash)")
                    pesanan = {"A": False, "B": False} if len(diterima_global.get("dapat", [])) <= 1 else pesanan
            except Exception as ex:
                ringkasan.append(f"   pembersihan lewat Driver gagal: {type(ex).__name__}: {str(ex)[:120]}")
        for d, dev, key in ((da, "A-user", "A"), (db, "B-user", "B")):
            try:
                if d is not None and pesanan.get(key):
                    batalkan(d, dev)
            except Exception:
                pass
        try:
            if dv is not None:
                ketuk(dv, "//*[@content-desc='Online' or @text='Online']", 2)
                save(dv, "driver", "pembersihan_offline")
        except Exception:
            pass
        for d in (dv, da, db):
            try:
                if d is not None:
                    d.quit()
            except Exception:
                pass
        text = "\n".join(ringkasan)
        (OUT / "ringkasan.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
