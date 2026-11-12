"""
E2E multi-pengguna dengan dua emulator (CI suite skrip2), staging, metode bayar Cash:
  Emulator A (emulator-5554): aplikasi Driver (akun driver uji) + aplikasi User A (akun utama), berpindah aplikasi.
  Emulator B (emulator-5556): aplikasi User B (akun QA Auto indeks E2E_USER_B_INDEX, default 14).

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
    from _diag_util import izinkan_lokasi, log

    user_pkg, driver_pkg = config.APP_PACKAGE, getattr(config, "DRIVER_PACKAGE", "com.evmoto.driver.app")
    tujuan = os.getenv("E2E_TUJUAN", "Senayan City")
    phone_a = akun_pool(0)
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
        d.activate_app(pkg)
        time.sleep(3)
        izinkan_lokasi(d)

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

    da = db = None
    pesanan = {"A": False, "B": False}
    try:
        da = DriverFactory.create_driver(is_driver_app=True, udid="emulator-5554", system_port=8200)
        db = DriverFactory.create_driver(udid="emulator-5556", system_port=8201)
        ringkasan.append("perangkat A: emulator-5554 (Driver + User A), perangkat B: emulator-5556 (User B); metode bayar: Cash")
        # Driver Online di perangkat A
        DrvLoginPage(da).login_as_driver()
        time.sleep(4)
        ketuk(da, "//*[@content-desc='Lanjutkan' or @text='Lanjutkan']", 1.5)
        ketuk(da, "//*[@content-desc='Offline' or @text='Offline']", 3)
        save(da, "A-driver", "status_online")
        # User A dan User B login, lalu memesan hampir bersamaan
        ke(da, user_pkg)
        login_user(da, phone_a)
        login_user(db, phone_b)
        save(da, "A-user", "beranda")
        save(db, "B-user", "beranda")
        BookingPage(da).open_place_order(tujuan)
        BookingPage(db).open_place_order(tujuan)
        t0 = time.time()
        pesanan["A"] = ketuk(da, "//android.widget.Button[@content-desc='Pesan EVMoto' or @text='Pesan EVMoto']", 0.5)
        pesanan["B"] = ketuk(db, "//android.widget.Button[@content-desc='Pesan EVMoto' or @text='Pesan EVMoto']", 0.5)
        ringkasan.append(f"   pesanan A={pesanan['A']} B={pesanan['B']}, selisih {time.time() - t0:.1f} dtk")
        save(da, "A-user", "setelah_pesan")
        save(db, "B-user", "setelah_pesan")
        # Driver menerima satu pesanan
        ke(da, driver_pkg)
        diterima = None
        for _ in range(20):
            xml = save(da, "A-driver", "cek_order_masuk")
            if re.search(r"Swipe|Geser|Terima|Orderan Baru|Pesanan Baru", xml):
                els = da.find_elements("xpath", "//*[contains(@content-desc,'Swipe') or contains(@content-desc,'Geser') or contains(@text,'Geser') or contains(@content-desc,'Terima')]")
                if els:
                    r = els[-1].rect
                    y = r["y"] + r["height"] // 2
                    da.swipe(r["x"] + 15, y, r["x"] + r["width"] - 10, y, 900)
                    time.sleep(4)
                    diterima = save(da, "A-driver", "setelah_terima")
                break
            time.sleep(6)
        ringkasan.append("   driver menerima pesanan" if diterima else "   tidak ada pesanan masuk ke driver dalam ±2 menit")
        # Status kedua user setelah driver menerima: hanya satu yang boleh mendapat driver
        ke(da, user_pkg)
        xa = save(da, "A-user", "status_setelah_driver_terima")
        xb = save(db, "B-user", "status_setelah_driver_terima")
        dapat = [n for n, x in (("A", xa), ("B", xb)) if re.search(r"B 9099|testdr|Driver menuju|sedang menuju|dalam perjalanan", x)]
        ringkasan.append(f"HASIL race condition: user yang mendapat driver = {dapat or 'tidak ada'} "
                         f"({'BENAR: hanya satu' if len(dapat) == 1 else 'PERLU DICEK' if not dapat else 'SALAH: lebih dari satu user mendapat driver yang sama'})")
        # Driver sibuk: selama 60 dtk, pesanan user lain tidak boleh ditawarkan ke driver ini
        ke(da, driver_pkg)
        tawaran = 0
        for _ in range(6):
            xml = save(da, "A-driver", "selama_mengantar")
            tawaran += 1 if re.search(r"Orderan Baru|Pesanan Baru|Swipe untuk mendapatkan", xml) else 0
            time.sleep(10)
        ringkasan.append(f"HASIL driver sibuk: tawaran pesanan baru selama mengantar = {tawaran} kali "
                         f"({'BENAR' if tawaran == 0 else 'PERLU DICEK'})")
    except Exception as e:
        ringkasan.append(f"langkah gagal: {type(e).__name__}: {str(e)[:220]}")
    finally:
        for d, dev, key in ((da, "A-user", "A"), (db, "B-user", "B")):
            try:
                if d is not None and pesanan.get(key):
                    if dev.startswith("A"):
                        ke(d, user_pkg)
                    batalkan(d, dev)
            except Exception:
                pass
        try:
            if da is not None:
                ke(da, driver_pkg)
                ketuk(da, "//*[@content-desc='Online' or @text='Online']", 2)
                save(da, "A-driver", "pembersihan_offline")
        except Exception:
            pass
        for d in (da, db):
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
