"""Diagnosa OTP pendaftaran Driver: apakah verifikasi OTP bisa diulang DALAM SATU sesi Appium?
Hasil sebelumnya: antar sesi baru hanya sesi pertama per emulator yang lolos (clearApp, ganti android_id, jeda 5 menit, kirim ulang kode tidak membantu).
Skrip ini membuka satu sesi, lolos OTP (pembanding), lalu ulang tiga kali: tekan Kembali sampai langkah nomor handphone, isi nomor acak baru, OTP, catat hasil.
Tidak menekan Kirim. Keluaran: reports/repro/diag_otp_satu_sesi/index.txt."""
from _diag_otp import ROOT, alur_otp, labels, sesi_baru, time, tulis, tutup

OUT = ROOT / "reports" / "repro" / "diag_otp_satu_sesi"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hasil = []
    d, reg = sesi_baru()
    try:
        hasil.append(f"putaran 0 (login > formulir): {alur_otp(reg)}")
        for i in range(1, 4):
            for _ in range(3):
                if reg.is_phone_step_displayed():
                    break
                try:
                    reg.click_back()
                except Exception:  # noqa: BLE001
                    d.back()
                time.sleep(2)
            hasil.append(f"putaran {i}: setelah Kembali, langkah nomor tampil={reg.is_phone_step_displayed()}; layar={labels(d, 6)}")
            try:
                reg.lewati_verifikasi_nomor()
                hasil.append(f"putaran {i}: formulir TAMPIL")
            except Exception as e:  # noqa: BLE001
                hasil.append(f"putaran {i}: formulir TIDAK tampil ({type(e).__name__}: {str(e)[:60]}); layar={labels(d, 8)}")
    finally:
        tutup(d, OUT, "akhir")
    tulis(OUT, hasil)


if __name__ == "__main__":
    main()
