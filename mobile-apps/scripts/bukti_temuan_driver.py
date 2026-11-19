"""Bagian Driver dari bukti_temuan_beranda.py dijalankan terpisah (sesi User dan Driver dalam satu run memicu kegagalan adb di emulator, run 44482702844)."""
import re

import bukti_temuan_beranda as b

if __name__ == "__main__":
    b.OUT.mkdir(parents=True, exist_ok=True)
    try:
        b.bagian_driver()
    except Exception as e:  # noqa: BLE001
        b.catatan.append(f"bagian_driver gagal: {type(e).__name__}: {str(e)[:200]}")
    teks = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(b.catatan))
    (b.OUT / "index_driver.txt").write_text(teks, encoding="utf-8")
    print(teks)
