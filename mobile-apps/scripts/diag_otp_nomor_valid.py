"""Diagnosa OTP pendaftaran Driver dengan NOMOR VALID. Koreksi pemilik produk (20 Nov 2026): bypass 1234 berlaku untuk semua nomor, tetapi layar OTP
muncul untuk nomor yang valid; diagnosa sebelumnya memakai nomor buatan sendiri (+62 899 + 8 angka acak) dan tidak pernah menguji nomor valid.
Tiap tahap = satu sesi Appium baru di emulator yang sama (satu siklus nomor > OTP, tanpa pengulangan), tidak menekan Kirim:
  N1, N2: nomor acak berformat valid (awalan operator seluler Indonesia nyata, 11-12 digit setelah +62).
  N3: nomor akun Driver uji yang sudah ada (dari Secret; hanya dicek sampai formulir, tidak dikirim).
  N4: nomor akun User uji yang sudah ada (dari Secret; sama).
  N5: nomor acak berformat valid lagi.
Nomor tidak pernah dicetak (hanya 4 digit pertama dan panjangnya). Keluaran: reports/repro/diag_otp_nomor_valid/index.txt."""
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "Frontend" / "Feature"), str(ROOT / "scripts")]

from config.config import Config  # noqa: E402
from _diag_otp import labels, sesi_baru, tutup  # noqa: E402

OUT = ROOT / "reports" / "repro" / "diag_otp_nomor_valid"
AWALAN = ("812", "813", "821", "822", "852", "857", "878", "877", "896", "815")


def acak_valid():
    return random.choice(AWALAN) + "".join(str(random.randint(0, 9)) for _ in range(random.choice((7, 8))))


def normal(nomor: str) -> str:
    """Ambil bagian lokal tanpa +62 / 62 / 0 di depan."""
    digit = re.sub(r"\D", "", nomor or "")
    if digit.startswith("62"):
        digit = digit[2:]
    return digit.lstrip("0")


def satu(nama, nomor, hasil, rahasia=False):
    """rahasia=True untuk nomor akun uji asli: tanpa screenshot dan tanpa isi layar (repo publik; nomor hanya boleh lewat Secret)."""
    if not nomor:
        hasil.append(f"{nama}: dilewati (nomor tidak tersedia di Secret)")
        return
    d, reg = sesi_baru()
    samar = "***" if rahasia else f"{nomor[:4]}***({len(nomor)} digit)"
    try:
        reg.MAKS_SIKLUS_OTP = 1
        reg.click_daftar_driver_baru()
        assert reg.is_phone_step_displayed(), "langkah nomor tidak tampil"
        try:
            reg.lewati_verifikasi_nomor(nomor)
            hasil.append(f"{nama} {samar}: formulir TAMPIL")
        except AssertionError as e:
            hasil.append(f"{nama} {samar}: formulir TIDAK tampil ({str(e)[:70]})" + ("" if rahasia else f"; layar={labels(d, 8)}"))
    except Exception as e:  # noqa: BLE001
        hasil.append(f"{nama} {samar}: GAGAL {type(e).__name__}: {str(e)[:80]}")
    finally:
        if rahasia:
            try:
                d.quit()
            except Exception:  # noqa: BLE001
                pass
        else:
            tutup(d, OUT, nama)
        time.sleep(2)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hasil = []
    satu("N1_valid_acak", acak_valid(), hasil)
    satu("N2_valid_acak", acak_valid(), hasil)
    satu("N3_akun_driver_ada", normal(Config.DRIVER_ACTIVE_PHONE), hasil, rahasia=True)
    satu("N4_akun_user_ada", normal(Config.ACTIVE_PHONE), hasil, rahasia=True)
    satu("N5_valid_acak", acak_valid(), hasil)
    teks = "\n".join(hasil)
    (OUT / "index.txt").write_text(teks, encoding="utf-8")
    print(teks)


if __name__ == "__main__":
    main()
