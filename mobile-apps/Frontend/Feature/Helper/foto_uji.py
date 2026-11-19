"""Foto uji untuk unggah berkas di aplikasi (pendaftaran Driver): membuat PNG kecil, mengirimnya ke galeri emulator lewat adb, dan memindai media
agar tampil di pemilih foto Android. Dipakai suite Driver di emulator CI (adb ada di runner); di mesin tanpa adb fungsi mengembalikan False."""
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("FotoUji")
NAMA_BERKAS = "foto_uji_evmoto.png"


def buat_png(lebar: int = 200, tinggi: int = 120) -> bytes:
    mentah = b"".join(b"\x00" + b"".join(bytes([(x * 2) % 256, (y * 2) % 256, 160]) for x in range(lebar)) for y in range(tinggi))

    def potongan(tag: bytes, data: bytes) -> bytes:
        isi = struct.pack(">I", len(data)) + tag + data
        return isi + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + potongan(b"IHDR", struct.pack(">IIBBBBB", lebar, tinggi, 8, 2, 0, 0, 0))
            + potongan(b"IDAT", zlib.compress(mentah)) + potongan(b"IEND", b""))


def siapkan_foto_uji() -> bool:
    """Kirim foto uji ke /sdcard/Pictures emulator dan pindai media. True bila berhasil."""
    adb = shutil.which("adb")
    if not adb:
        logger.warning("adb tidak ditemukan; foto uji tidak disiapkan")
        return False
    lokal = Path(tempfile.gettempdir()) / NAMA_BERKAS
    lokal.write_bytes(buat_png())
    perintah = [
        [adb, "shell", "mkdir", "-p", "/sdcard/Pictures"],
        [adb, "push", str(lokal), f"/sdcard/Pictures/{NAMA_BERKAS}"],
        [adb, "shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file:///sdcard/Pictures/{NAMA_BERKAS}"],
    ]
    for cmd in perintah:
        hasil = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if hasil.returncode != 0:
            logger.warning(f"adb gagal ({' '.join(cmd[1:3])}): {(hasil.stdout + hasil.stderr).strip()[:150]}")
            return False
    logger.info("Foto uji disiapkan di galeri emulator")
    return True
