"""Peta lanjutan pendaftaran Driver: pengunggahan Foto ID KTP di layar 'Data Informasi Personal' (langkah 2 dari 3).
Temuan run 44282149182: mengetuk label 'Foto ID KTP' tidak membuka apa pun dan 'Lanjutkan' tanpa foto mengembalikan formulir kosong. Di sini kotak foto
diketuk di koordinatnya, lalu dicatat dialog/pemilih yang muncul (paket, activity, label) dan pilihan sumber foto diketuk satu per satu.
Tidak mengisi nomor sungguhan (acak awalan 899), tidak menekan 'Kirim'. Hasil: reports/repro/peta_drv_register3/NN_<layar>.xml|.png dan index.txt."""
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

import peta_drv_register as p  # noqa: E402
from config.config import Config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from Pages.drv_login_page import DrvLoginPage  # noqa: E402
from Pages.drv_register_page import DrvRegisterPage  # noqa: E402

p.OUT = ROOT / "reports" / "repro" / "peta_drv_register3"
BTN_LANJUT = "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']"


def catat(d, teks):
    try:
        teks += f" [paket={d.current_package} activity={d.current_activity}]"
    except Exception:  # noqa: BLE001
        pass
    p.index.append("   " + teks)


def main():
    p.OUT.mkdir(parents=True, exist_ok=True)
    d = DriverFactory.create_driver(is_driver_app=True)
    nomor = "899" + "".join(str(random.randint(0, 9)) for _ in range(8))
    try:
        login = DrvLoginPage(d)
        login.handle_system_permissions()
        DrvRegisterPage(d).click_daftar_driver_baru()
        time.sleep(2)
        kolom = d.find_elements("xpath", "//android.widget.EditText")[0]
        kolom.click()
        time.sleep(0.5)
        kolom.send_keys(nomor)
        time.sleep(1)
        try:
            if d.is_keyboard_shown():
                d.hide_keyboard()
        except Exception:  # noqa: BLE001
            pass
        d.find_elements("xpath", BTN_LANJUT)[0].click()
        time.sleep(3)
        d.find_elements("xpath", "//android.widget.EditText")[0].click()
        for ch in str(Config.DRIVER_ACTIVE_PIN):
            d.press_keycode(7 + int(ch))
            time.sleep(0.2)
        time.sleep(1)
        d.find_elements("xpath", BTN_LANJUT)[0].click()
        time.sleep(6)
        p.save(d, "data_informasi_personal")
        catat(d, "layar awal Data Informasi Personal")
        # Ketuk kotak foto (di layar 320x640 kotak berada sekitar y=245..425 saat formulir di puncak)
        d.tap([(160, 335)], 200)
        time.sleep(3)
        p.save(d, "setelah_ketuk_kotak_foto")
        catat(d, "setelah ketuk kotak foto")
        labels = p.semua_label(d.page_source)
        for kata in ("Kamera", "Galeri", "Gallery", "Camera", "Ambil Foto", "Pilih Foto", "Pilih dari", "File", "Izinkan", "Allow", "While using"):
            for el in d.find_elements("xpath", f"//*[contains(@text,'{kata}') or contains(@content-desc,'{kata}')]")[:1]:
                catat(d, f"elemen '{kata}' ada: {(el.get_attribute('text') or el.get_attribute('content-desc') or '')[:40]}")
        index_pilihan = [l for l in labels if re.search(r"(?i)kamera|galeri|gallery|camera|ambil|pilih|file|izin|allow", l)]
        catat(d, f"label terkait: {index_pilihan[:10]}")
    except Exception as e:  # noqa: BLE001
        p.index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
        try:
            p.save(d, "saat_error")
        except Exception:  # noqa: BLE001
            pass
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        text = "\n".join(p.index).replace(nomor, "899********")
        (p.OUT / "index.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
