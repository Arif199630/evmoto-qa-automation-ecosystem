"""Diagnosa 2 pembatalan order sisa (APK UAT). Run 44694217442: ±27 test User gagal karena order tertinggal di layar pelacakan 'Sedang Menunggu Konfirmasi
Driver...' / 'Sedang mencari driver'; pohon layar tidak memuat tombol 'Batalkan' (panel belum terbuka) dan geser/dragGesture dari Beranda tidak membukanya.
Skrip ini menjalankan satu proses per akun pool (3, 12, 14) dan mencoba: tombol Kembali (panah) dan Back sistem pada layar pelacakan, ketuk judul panel,
dragGesture/swipeGesture dari judul panel, serta tab Aktivitas > Reguler > kartu pesanan berjalan. Mencatat layar/dialog dan apakah 'Batalkan' muncul.
Tidak mengonfirmasi pembatalan. Keluaran: reports/repro/diag_batal_sisa2/<pool>/index.txt."""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOLS = ("3", "12", "14")
XP_BATAL = "//*[contains(@content-desc,'Batalkan') or contains(@text,'Batalkan')]"
XP_SISA = "//*[contains(@content-desc,'Menunggu Konfirmasi Driver') or contains(@content-desc,'Sedang mencari driver') or contains(@content-desc,'Sedang berjalan')]"


def anak(pool: str):
    os.environ["TEST_USER_POOL_INDEX"] = pool
    sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]
    import peta_sedang_berjalan as p
    from config import config
    from core.driver_factory import DriverFactory
    from Pages.login_page import LoginPage
    from _diag_util import izinkan_lokasi

    p.OUT = ROOT / "reports" / "repro" / "diag_batal_sisa2" / pool
    p.OUT.mkdir(parents=True, exist_ok=True)

    def cek(d, nama):
        time.sleep(1.5)
        xml = p.save(d, nama)
        batal = d.find_elements("xpath", XP_BATAL)
        p.index.append(f"   >> {nama}: Batalkan={len(batal)} {[(e.get_attribute('content-desc') or e.get_attribute('text'), e.rect) for e in batal][:2]}; label={p.labels(xml)[:9]}")
        return bool(batal)

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
        if not d.find_elements("xpath", XP_SISA):
            p.index.append("   akun ini TIDAK punya order sisa; diagnosa dihentikan")
            return
        ukuran = d.get_window_size()
        w, h = ukuran["width"], ukuran["height"]
        x = w // 2
        # Bila masih di Beranda dengan banner 'Sedang berjalan', buka layar pelacakan dengan mengetuk banner
        banner = d.find_elements("xpath", "//*[contains(@content-desc,'Sedang berjalan')]")
        if banner:
            banner[0].click()
            cek(d, "setelah_ketuk_banner")
        varian = [
            ("ketuk_judul_panel", lambda: d.tap([(x, int(h * 0.86))], 150)),
            ("dragGesture_dari_judul_pelan", lambda: d.execute_script("mobile: dragGesture", {"startX": x, "startY": int(h * 0.86), "endX": x, "endY": int(h * 0.30), "speed": 250})),
            ("swipeGesture_atas_90", lambda: d.execute_script("mobile: swipeGesture", {"left": 40, "top": int(h * 0.80), "width": w - 80, "height": int(h * 0.15), "direction": "up", "percent": 0.9, "speed": 300})),
            ("panah_kembali", lambda: d.tap([(28, 68)], 150)),
            ("back_sistem", lambda: d.back()),
        ]
        for nama, aksi in varian:
            try:
                aksi()
            except Exception as ex:  # noqa: BLE001
                p.index.append(f"   {nama} gagal: {type(ex).__name__}: {str(ex)[:100]}")
            if cek(d, nama):
                p.index.append(f"   BERHASIL memunculkan Batalkan dengan: {nama}")
                return
        # Jalur Aktivitas
        try:
            tab = d.find_elements("xpath", "//*[@content-desc='Aktivitas' or @text='Aktivitas']")
            if tab:
                tab[0].click()
                time.sleep(2)
                cek(d, "tab_aktivitas")
                kartu = d.find_elements("xpath", "//*[contains(@content-desc,'Sedang') or contains(@content-desc,'Menunggu') or contains(@content-desc,'Mencari')]")
                p.index.append(f"   kartu pesanan berjalan di Aktivitas: {len(kartu)}")
                if kartu:
                    kartu[0].click()
                    cek(d, "detail_kartu_berjalan")
        except Exception as ex:  # noqa: BLE001
            p.index.append(f"   jalur Aktivitas gagal: {type(ex).__name__}: {str(ex)[:100]}")
    except Exception as e:  # noqa: BLE001
        p.index.append(f"langkah gagal: {type(e).__name__}: {str(e)[:200]}")
    finally:
        try:
            d.quit()
        except Exception:  # noqa: BLE001
            pass
        teks = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(p.index))
        (p.OUT / "index.txt").write_text(teks, encoding="utf-8")
        print(f"=== pool {pool}\n{teks}", flush=True)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--pool":
        anak(sys.argv[2])
        return
    for pool in POOLS:
        subprocess.run([sys.executable, str(Path(__file__).resolve()), "--pool", pool], timeout=900, check=False)


if __name__ == "__main__":
    main()
