"""
Peta layar aplikasi asli: login, lalu buka tiap menu yang terlihat dan simpan struktur layar (XML) + screenshot.

Dipakai untuk memperbaiki locator Page Object berdasarkan layar sungguhan, bukan tebakan.
Jalankan saat Appium + emulator aktif:
    python scripts/dump_screens.py user      # aplikasi User
    python scripts/dump_screens.py driver    # aplikasi Driver
Hasil: reports/screen_map/<app>/NN_<nama>.xml dan .png, plus index.txt (daftar layar dan teks utamanya).

Aman untuk staging: tombol yang bisa membuat transaksi atau mengubah akun tidak pernah diketuk.
"""
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature")]

from core.driver_factory import DriverFactory  # noqa: E402
from config import config  # noqa: E402

# Kata pada tombol yang TIDAK boleh diketuk (transaksi, hapus data, keluar akun, kirim data)
BERBAHAYA = re.compile(r"(?i)keluar|logout|log out|hapus|delete|batalkan|cancel|pesan sekarang|pesan evmoto|bayar|"
                       r"tarik|withdraw|transfer|top ?up|kirim|simpan|daftar|offline|online|terima|tolak|panggil|"
                       r"hubungi|whatsapp|telepon|call|sos|darurat|putuskan|tautkan|link")
OUT = ROOT / "reports" / "screen_map"


def texts(xml):
    return [t for t in re.findall(r'(?:content-desc|text)="([^"]{2,60})"', xml) if t.strip() and t not in ("true", "false")]


def save(driver, folder, idx, name, index):
    xml = driver.page_source
    safe = re.sub(r"[^A-Za-z0-9]+", "_", name)[:40]
    (folder / f"{idx:02d}_{safe}.xml").write_text(xml, encoding="utf-8")
    try:
        driver.save_screenshot(str(folder / f"{idx:02d}_{safe}.png"))
    except Exception:
        pass
    index.append(f"{idx:02d}_{safe}: " + " | ".join(texts(xml)[:12]))


def tappable(driver):
    """Label elemen yang bisa diketuk di layar saat ini (Button, tab, atau view dengan content-desc pendek)."""
    labels = []
    for el in driver.find_elements("xpath", "//*[@content-desc!='' and (@clickable='true' or contains(@class,'Button'))]"):
        label = (el.get_attribute("content-desc") or "").split("\n")[0].strip()
        if 1 < len(label) <= 30 and not BERBAHAYA.search(label) and label not in labels:
            labels.append(label)
    return labels


def login(app, driver):
    if app == "user":
        from Pages.login_page import LoginPage
        page = LoginPage(driver)
        if page.is_login_screen_displayed(timeout=20):
            page.login(config.DEV_PHONE, config.DEV_OTP)
    else:
        from Pages.drv_login_page import DrvLoginPage
        DrvLoginPage(driver).login_as_driver()
    time.sleep(6)


def main(app):
    folder = OUT / app
    folder.mkdir(parents=True, exist_ok=True)
    driver = DriverFactory.create_driver(is_driver_app=(app == "driver"))
    index, idx = [], 0
    try:
        login(app, driver)
        save(driver, folder, idx, "beranda", index)
        home_labels = tappable(driver)
        index.append("  tombol di beranda: " + ", ".join(home_labels))
        for label in home_labels[:25]:
            idx += 1
            try:
                driver.find_element("xpath", f"//*[starts-with(@content-desc, \"{label}\")]").click()
                time.sleep(3)
                save(driver, folder, idx, label, index)
                index.append("    tombol di layar ini: " + ", ".join(tappable(driver)[:20]))
            except Exception as e:
                index.append(f"{idx:02d}_{label}: gagal dibuka ({type(e).__name__})")
            driver.back()
            time.sleep(2)
            if not texts(driver.page_source):
                driver.activate_app(config.DRIVER_PACKAGE if app == "driver" else config.APP_PACKAGE)
                time.sleep(3)
    finally:
        (folder / "index.txt").write_text("\n".join(index), encoding="utf-8")
        driver.quit()
    print(f"{idx + 1} layar disimpan di {folder}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "user")
