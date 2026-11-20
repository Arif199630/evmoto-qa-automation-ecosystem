"""Diagnosa OTP pendaftaran Driver: apakah pembatasan OTP berbasis waktu yang lebih panjang dari 5 menit?
Sesi pertama lolos (pembanding), lalu sesi baru setelah jeda 10 dan 25 menit (dua sesi tambahan per jeda tidak dilakukan agar run tidak terlalu lama).
Tidak menekan Kirim. Keluaran: reports/repro/diag_otp_tunggu/index.txt."""
from _diag_otp import ROOT, alur_otp, labels, sesi_baru, time, tulis, tutup

OUT = ROOT / "reports" / "repro" / "diag_otp_tunggu"


def satu(nama, hasil):
    d, reg = sesi_baru()
    try:
        status = alur_otp(reg)
        hasil.append(f"{nama} ({time.strftime('%H:%M:%S')} jam runner): {status}" + ("" if status.startswith("formulir TAMPIL") else f"; layar={labels(d, 8)}"))
    finally:
        tutup(d, OUT, nama)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hasil = []
    satu("T0_sesi_pertama", hasil)
    time.sleep(600)
    satu("T1_setelah_10_menit", hasil)
    time.sleep(900)
    satu("T2_setelah_25_menit_lagi", hasil)
    tulis(OUT, hasil)


if __name__ == "__main__":
    main()
