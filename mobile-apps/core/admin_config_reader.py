"""
Membaca konfigurasi bisnis langsung dari Admin Dashboard environment aktif (read-only).

Sumber kebenaran angka tarif dan subsidi jam sibuk adalah halaman Admin, bukan angka yang
ditulis tetap di kode test (keputusan 11 Nov 2026):
  - Tarif     : Price control > Motorcycle Price Settings (/tSystemPrice/special), baris Driver dan User
  - Jam sibuk : Subsidi jam sibuk > Pengaturan (/rushHour/settings)

Modul ini hanya melakukan GET halaman; tidak pernah mengirim form simpan.
Kredensial admin dibaca dari env: ADMIN_DEV_URL, ADMIN_DEV_USER, ADMIN_DEV_PASS.
"""
import html
import os
import re
from functools import lru_cache

import requests

PRICE_FIELDS = ("startPrice", "startKm", "mileageFee", "durationFee", "waitMinutes", "waitFee",
                "farFrom1", "farTo1", "farFee1", "farFrom2", "farTo2", "farFee2", "farFrom3", "farFee3",
                "peakTime", "peakStart", "peakMileage", "nightTime", "nightStart", "nightMileage")


class AdminConfigError(RuntimeError):
    """Konfigurasi tidak bisa dibaca dari Admin (login gagal, halaman berubah, atau data kosong)."""


def _inputs(page_html):
    """Daftar (name, value) semua <input>/<select> sesuai urutan di halaman."""
    pairs = []
    for tag in re.findall(r"<(?:input|select)\b[^>]*>", page_html, re.I):
        name = re.search(r'\bname="([^"]*)"', tag)
        if not name:
            continue
        typ = re.search(r'\btype="([^"]*)"', tag)
        if typ and typ.group(1).lower() in ("hidden", "password"):
            continue
        value = re.search(r'\bvalue="([^"]*)"', tag)
        if typ and typ.group(1).lower() == "checkbox":
            pairs.append((name.group(1), "true" if re.search(r"\bchecked\b", tag) else "false"))
        else:
            pairs.append((name.group(1), html.unescape(value.group(1)) if value else ""))
    return pairs


@lru_cache(maxsize=1)
def _session():
    base = os.getenv("ADMIN_DEV_URL", "").rstrip("/")
    user, password = os.getenv("ADMIN_DEV_USER", ""), os.getenv("ADMIN_DEV_PASS", "")
    if not (base and user and password):
        raise AdminConfigError("ADMIN_DEV_URL / ADMIN_DEV_USER / ADMIN_DEV_PASS belum diisi di .env")
    s = requests.Session()
    s.get(f"{base}/login", timeout=15)
    resp = s.post(f"{base}/login", data={"username": user, "password": password, "language": "2"}, timeout=15)
    if "/blackboard" not in resp.url:
        raise AdminConfigError("Login Admin gagal; cek ADMIN_DEV_USER / ADMIN_DEV_PASS")
    return base, s


def _get(path):
    base, s = _session()
    resp = s.get(base + path, timeout=15)
    resp.raise_for_status()
    return resp.text


@lru_cache(maxsize=None)
def read_price_config(billing_object: str = "User") -> dict:
    """Parameter tarif motor untuk 'User' atau 'Driver' (angka sudah berupa float, jam berupa teks)."""
    listing = _get("/tSystemPrice/special")
    rows = re.findall(r"<tr\b.*?</tr>", listing, re.S | re.I)
    price_id = None
    for row in rows:
        text = re.sub(r"<[^>]+>", " ", row)
        found = re.search(r'name="selected-price"[^>]*value="(\d+)"|value="(\d+)"[^>]*name="selected-price"', row)
        if found and re.search(rf"\b{billing_object}\b", text):
            price_id = found.group(1) or found.group(2)
            break
    if not price_id:
        raise AdminConfigError(f"Baris tarif '{billing_object}' tidak ditemukan di /tSystemPrice/special")
    values = {}
    for name, value in _inputs(_get(f"/tSystemPrice/tSystemPrice_update/{price_id}")):
        values.setdefault(name, value)  # nama far* muncul dua kali (bagian tarif malam); pakai yang pertama
    config = {"price_id": price_id, "billing_object": billing_object}
    for field in PRICE_FIELDS:
        raw = values.get(field, "")
        try:
            config[field] = float(raw)
        except ValueError:
            config[field] = raw
    if not isinstance(config.get("startPrice"), float):
        raise AdminConfigError(f"startPrice tidak terbaca untuk tarif {billing_object} (ID {price_id})")
    return config


@lru_cache(maxsize=1)
def read_rush_hour_config() -> dict:
    """Aturan subsidi jam sibuk: aktif/tidak, daftar window (HH:MM), dan tier tarif berurutan."""
    pairs = _inputs(_get("/rushHour/settings"))
    enabled = next((v for k, v in pairs if k == "enabled"), "false") == "true"
    starts = [v for k, v in pairs if k == "windowStart"]
    ends = [v for k, v in pairs if k == "windowEnd"]
    windows = [(a, b) for a, b in zip(starts, ends) if a and b]
    maxes = [v for k, v in pairs if k == "tierMax"]
    subsidies = [v for k, v in pairs if k == "tierSubsidy"]
    tiers = []
    for upper, subsidy in zip(maxes, subsidies):
        if not subsidy:
            continue
        tiers.append({"max_fare": float(upper) if upper else None, "subsidy": float(subsidy)})
    daily_budget = next((v for k, v in pairs if k == "dailyBudget"), "")
    return {"enabled": enabled, "windows": windows, "tiers": tiers,
            "daily_budget": float(daily_budget) if daily_budget else None}
