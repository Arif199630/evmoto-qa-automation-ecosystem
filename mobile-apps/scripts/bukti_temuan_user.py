"""Bagian User dari bukti_temuan_beranda.py dijalankan terpisah dari bagian Driver."""
import re

import bukti_temuan_beranda as b

if __name__ == "__main__":
    b.OUT.mkdir(parents=True, exist_ok=True)
    try:
        b.bagian_user()
    except Exception as e:  # noqa: BLE001
        b.catatan.append(f"bagian_user gagal: {type(e).__name__}: {str(e)[:200]}")
    teks = re.sub(r"(8\d{3})\d{4,}(\d{2})", r"\1****\2", "\n".join(b.catatan))
    (b.OUT / "index_user.txt").write_text(teks, encoding="utf-8")
    print(teks)
