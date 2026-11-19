"""Diagnosa pembatalan order sisa: akun pool 3 menyimpan order 'Sedang mencari driver'. Mencoba beberapa cara membuka panel (ketuk banner, geser dengan
titik awal/akhir berbeda, drag lambat dengan W3C actions, tarik pegangan panel) dan mencatat apakah tombol 'Batalkan' muncul. Verifikasi run 44488041916:
Batalkan tidak ditemukan setelah 4 geser. Tidak mengonfirmasi pembatalan (hanya mencatat); bila tombol muncul, hanya dicatat. MAP_POOL default 3."""
import os
import re
import sys
import time
from pathlib import Path

os.environ["TEST_USER_POOL_INDEX"] = os.getenv("MAP_POOL", "3")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import peta_sedang_berjalan as p  # noqa: E402
from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from selenium.webdriver.common.actions import interaction  # noqa: E402
from selenium.webdriver.common.actions.action_builder import ActionBuilder  # noqa: E402
from selenium.webdriver.common.actions.pointer_input import PointerInput  # noqa: E402
from _diag_util import izinkan_lokasi  # noqa: E402

p.OUT = ROOT / "reports" / "repro" / "diag_batal_sisa"
XP_BATAL = "//*[contains(@content-desc,'Batalkan') or contains(@text,'Batalkan')]"


def drag(d, x, y1, y2, ms):
    """Seret dengan W3C actions: tekan, tahan sebentar, gerak perlahan, lepas."""
    pointer = PointerInput(interaction.POINTER_TOUCH, "finger")
    ab = ActionBuilder(d, mouse=pointer)
    ab.pointer_action.move_to_location(x, y1)
    ab.pointer_action.pointer_down()
    ab.pointer_action.pause(0.3)
    ab.pointer_action.move_to_location(x, y2, duration=ms)
    ab.pointer_action.release()
    ab.perform()


def cek(d, nama):
    time.sleep(1.5)
    xml = p.save(d, nama)
    batal = d.find_elements("xpath", XP_BATAL)
    info = [(e.get_attribute("class").split(".")[-1], e.get_attribute("content-desc") or e.get_attribute("text"), e.rect) for e in batal]
    p.index.append(f"   >> {nama}: elemen Batalkan={len(batal)} {info[:3]}; label={p.labels(xml)[:8]}")
    return bool(batal)


def main():
    p.OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver()
    try:
        izinkan_lokasi(d)
        login = LoginPage(d)
        if login.is_login_screen_displayed(timeout=20):
            login.input_phone_number(config.ACTIVE_PHONE)
            login.click_submit_login()
            login.input_otp_dev(config.ACTIVE_OTP)
        time.sleep(6)
        p.tutup_popup(d)
        time.sleep(2)
        cek(d, "awal")
        d.tap([(160, 520)], 150)
        if cek(d, "setelah_tap_banner"):
            return
        ukuran = d.get_window_size()
        w, h = ukuran["width"], ukuran["height"]
        x = w // 2
        varian = [
            ("swipe_86_25", lambda: d.swipe(x, int(h * 0.86), x, int(h * 0.25), 600)),
            ("swipe_93_55", lambda: d.swipe(x, int(h * 0.93), x, int(h * 0.55), 600)),
            ("swipe_82_30_lambat", lambda: d.swipe(x, int(h * 0.82), x, int(h * 0.30), 1500)),
            ("drag_w3c_82_30", lambda: drag(d, x, int(h * 0.82), int(h * 0.30), 800)),
            ("drag_w3c_85_40", lambda: drag(d, x, int(h * 0.85), int(h * 0.40), 1200)),
            ("gesture_scroll", lambda: d.execute_script("mobile: dragGesture", {"startX": x, "startY": int(h * 0.82), "endX": x, "endY": int(h * 0.30), "speed": 600})),
        ]
        for nama, aksi in varian:
            try:
                aksi()
            except Exception as ex:  # noqa: BLE001
                p.index.append(f"   {nama} gagal: {type(ex).__name__}: {str(ex)[:100]}")
            if cek(d, nama):
                p.index.append(f"   BERHASIL membuka panel dengan: {nama}")
                break
    except Exception as e:  # noqa: BLE001
        p.index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        teks = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(p.index))
        (p.OUT / "index.txt").write_text(teks, encoding="utf-8")
        print(teks)


if __name__ == "__main__":
    main()
