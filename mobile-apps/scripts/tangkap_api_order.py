"""
Tangkap request API yang dipakai aplikasi User saat memesan dan membatalkan order (staging), dari database Chucker
(HTTP inspector di build dev) lewat adb root di emulator CI. Hasilnya dipakai untuk uji race condition
'2 emulator + API' (User B memesan lewat API pada detik yang sama dengan User A di aplikasi).

Akun: User dengan GoPay tertaut (GOPAY_TEST_PHONE), karena akun QA pool dan akun utama dipakai job regression.
Metode bayar diganti ke Cash sebelum memesan. Order dibatalkan dari aplikasi sebelum ada driver yang menerima.
Repo CI ini public: detail request (transaksi.json) dienkripsi dengan sertifikat qa-tools/artifact_cert.pem
(kunci privat hanya di laptop QA) menjadi transaksi.json.enc; file terbuka dihapus. Log dan ringkasan.txt hanya
memuat jumlah transaksi. Token dan nomor tetap disensor sebelum dienkripsi.
"""
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")
from config import config  # noqa: E402
from core.driver_factory import DriverFactory  # noqa: E402
from core.screen_dump import dump as dump_ringan  # noqa: E402
from Pages.login_page import LoginPage  # noqa: E402
from Pages.booking_page import BookingPage  # noqa: E402
from _diag_util import izinkan_lokasi, log, pesan_order  # noqa: E402

OUT = ROOT / "reports" / "repro" / "tangkap_api_order"
PKG = config.APP_PACKAGE
SENSOR_KUNCI = re.compile(r"(?i)token|authorization|password|secret|otp|pin|captcha|signature|cookie|session")
ringkasan = []
step = 0


def sensor(v):
    """Sensor nomor telepon dan nilai yang terlihat seperti token."""
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    s = re.sub(r"(?<!\d)(\+?62|0)?8\d{8,12}(?!\d)", "8***", s)
    s = re.sub(r"[A-Za-z0-9_\-]{24,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "<jwt>", s)
    s = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._\-]+", r"\1<token>", s)
    return s


def bersihkan_json(teks):
    try:
        obj = json.loads(teks)
    except Exception:
        return sensor(teks or "")[:600]

    def jalan(o):
        if isinstance(o, dict):
            return {k: ("<disensor>" if SENSOR_KUNCI.search(k) else jalan(v)) for k, v in o.items()}
        if isinstance(o, list):
            return [jalan(x) for x in o[:20]]
        return o
    return json.loads(sensor(jalan(obj)))


def save(d, nama):
    global step
    step += 1
    izinkan_lokasi(d)
    xml = dump_ringan(d)
    (OUT / f"{step:02d}_{nama}.xml").write_text(xml, encoding="utf-8")
    d.save_screenshot(str(OUT / f"{step:02d}_{nama}.png"))
    teks = [t for t in re.findall(r'content-desc="([^"]{1,70})"', xml) if not t.startswith(("Ping", "PlatformException"))]
    ringkasan.append(f"{step:02d} {nama}: " + " | ".join(teks[:14]).replace("&#10;", "/"))
    log(ringkasan[-1][:150])
    return xml


def adb(*args, binary=False):
    r = subprocess.run(["adb", "-s", os.getenv("ANDROID_SERIAL", "emulator-5554"), *args], capture_output=True, timeout=60)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def ambil_chucker():
    """Salin database Chucker aplikasi User lewat adb root, kembalikan daftar transaksi HTTP (sudah disensor)."""
    adb("root")
    time.sleep(3)
    files = adb("shell", f"ls /data/data/{PKG}/databases/").split()
    ringkasan.append("database aplikasi: " + ", ".join(files))
    kandidat = [f for f in files if "chucker" in f.lower() and f.endswith(".db")] or [f for f in files if "chucker" in f.lower()]
    if not kandidat:
        return []
    lokal = OUT / "chucker.db"
    for suffix in ("", "-wal", "-shm"):
        data = adb("exec-out", "cat", f"/data/data/{PKG}/databases/{kandidat[0]}{suffix}", binary=True)
        if data:
            Path(str(lokal) + suffix).write_bytes(data)
    con = sqlite3.connect(str(lokal))
    tabel = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
    ringkasan.append("tabel chucker: " + ", ".join(tabel))
    t = "transactions" if "transactions" in tabel else next((x for x in tabel if "trans" in x.lower()), None)
    if not t:
        return []
    kolom = [r[1] for r in con.execute(f"pragma table_info({t})")]
    pilih = [c for c in ("requestDate", "method", "host", "path", "url", "responseCode", "requestBody", "responseBody",
                         "requestContentType") if c in kolom]
    hasil = []
    for row in con.execute(f"select {', '.join(pilih)} from {t} order by requestDate"):
        rec = dict(zip(pilih, row))
        for k in ("requestBody", "responseBody"):
            if rec.get(k):
                rec[k] = bersihkan_json(rec[k])
        if rec.get("url"):
            rec["url"] = sensor(re.sub(r"(?i)([?&](token|access_token|sign)[^=]*=)[^&]+", r"\1<disensor>", rec["url"]))
        hasil.append(rec)
    con.close()
    for suffix in ("", "-wal", "-shm"):
        try:
            Path(str(lokal) + suffix).unlink()
        except FileNotFoundError:
            pass
    return hasil


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    phone = os.getenv("GOPAY_TEST_PHONE", "")
    if not phone:
        raise SystemExit("GOPAY_TEST_PHONE belum ada di Secret ENV_MOBILE_APPS")
    d = DriverFactory.create_driver(no_reset=True)
    try:
        lp = LoginPage(d)
        if lp.is_login_screen_displayed(timeout=20):
            lp.input_phone_number(phone)
            lp.click_submit_login()
            lp.input_otp_dev(config.ACTIVE_OTP)
            time.sleep(5)
        for _ in range(2):
            els = d.find_elements("xpath", "//*[@content-desc='Lanjutkan']")
            if els:
                els[0].click()
                time.sleep(1.5)
        save(d, "beranda")
        bp = BookingPage(d)
        bp.open_place_order(os.getenv("E2E_TUJUAN", "Senayan City"))
        save(d, "place_order")
        try:
            bp.select_payment_method("cash")
            time.sleep(2)
        except Exception as ex:
            ringkasan.append(f"ganti ke Cash gagal: {type(ex).__name__}")
        xml = save(d, "metode_cash")
        if "content-desc=\"Cash\"" not in xml:
            ringkasan.append("metode bayar bukan Cash: order TIDAK dibuat")
        elif pesan_order(d):
            save(d, "menunggu_driver")
            time.sleep(5)
            for label in ("Batalkan", "Batalkan Pesanan", "Batal"):
                els = d.find_elements("xpath", f"//*[contains(@content-desc,'{label}') or contains(@text,'{label}')]")
                if els:
                    els[0].click()
                    time.sleep(3)
                    save(d, f"ketuk_{label.replace(' ', '_')}")
                    for konfirm in ("Ya, Batalkan", "Ya", "Batalkan Pesanan", "Konfirmasi"):
                        els = d.find_elements("xpath", f"//*[@content-desc='{konfirm}' or @text='{konfirm}']")
                        if els:
                            els[0].click()
                            time.sleep(3)
                            save(d, f"konfirmasi_{konfirm.replace(' ', '_').replace(',', '')}")
                            break
                    break
            save(d, "setelah_batal")
        else:
            ringkasan.append("'Pesan EVMoto' tidak terkirim")
    except Exception as ex:
        traceback.print_exc()
        ringkasan.append(f"langkah gagal: {type(ex).__name__}: {str(ex)[:200]}")
    finally:
        try:
            d.quit()
        except Exception:
            pass
        try:
            trx = ambil_chucker()
            polos = OUT / "transaksi.json"
            polos.write_text(json.dumps(trx, ensure_ascii=False, indent=1), encoding="utf-8")
            cert = ROOT.parent / "qa-tools" / "artifact_cert.pem"
            r = subprocess.run(["openssl", "smime", "-encrypt", "-aes256", "-binary", "-outform", "DER",
                                "-in", str(polos), "-out", str(OUT / "transaksi.json.enc"), str(cert)], capture_output=True)
            polos.unlink()
            ringkasan.append(f"transaksi HTTP tercatat: {len(trx)}; terenkripsi: {r.returncode == 0}; "
                             f"terkait order: {sum(1 for t in trx if re.search(r'(?i)order', str(t.get('path') or t.get('url'))))}")
        except Exception as ex:
            traceback.print_exc()
            ringkasan.append(f"ambil Chucker gagal: {type(ex).__name__}: {str(ex)[:200]}")
        for f in list(OUT.glob("chucker.db*")) + list(OUT.glob("transaksi.json")):
            f.unlink()  # database mentah dan file terbuka tidak boleh ikut artifact (repo public)
        text = sensor("\n".join(ringkasan))
        (OUT / "ringkasan.txt").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
