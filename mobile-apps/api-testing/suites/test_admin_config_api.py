"""
Konsistensi konfigurasi bisnis di Admin Dashboard environment aktif (read-only).

Sumber kebenaran tarif dan subsidi jam sibuk adalah halaman Admin (keputusan 11 Nov 2026).
Test ini memastikan konfigurasi itu sendiri masuk akal sebelum dipakai test lain:
  - Tarif Driver dan User harus sama (halaman Price control).
  - Window jam sibuk valid dan tidak tumpang tindih; tier subsidi naik berurutan.
Kegagalan di sini adalah temuan KONFIGURASI, bukan bug kode aplikasi.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # akses core/ di root mobile-apps
from core.admin_config_reader import AdminConfigError, read_price_config, read_rush_hour_config  # noqa: E402

COMPARED_FIELDS = ("startPrice", "startKm", "mileageFee", "durationFee", "waitMinutes", "waitFee",
                   "farFrom1", "farTo1", "farFee1", "farFrom2", "farTo2", "farFee2", "farFrom3", "farFee3",
                   "peakTime", "peakStart", "peakMileage", "nightTime", "nightStart", "nightMileage")


def _read(fn, *args):
    try:
        return fn(*args)
    except AdminConfigError as e:
        pytest.skip(f"Konfigurasi Admin tidak bisa dibaca: {e}")


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


class TestAdminPriceConfig:
    def test_tc_cfg_price_01_tarif_driver_dan_user_sama(self, record_property):
        """[Pilar 1] Semua parameter tarif motor di halaman Price untuk Driver dan User bernilai sama."""
        user, driver = _read(read_price_config, "User"), _read(read_price_config, "Driver")
        record_property("price_id_user", user["price_id"])
        record_property("price_id_driver", driver["price_id"])
        beda = {f: {"User": user.get(f), "Driver": driver.get(f)} for f in COMPARED_FIELDS if user.get(f) != driver.get(f)}
        assert not beda, f"Tarif Driver dan User berbeda di Admin (ID {driver['price_id']} vs {user['price_id']}): {beda}"

    def test_tc_cfg_price_02_tarif_lengkap_dan_berjenjang(self):
        """[Pilar 1] Tarif awal, tarif per km, dan batas jarak jauh terisi serta berurutan naik."""
        cfg = _read(read_price_config, "User")
        for field in ("startPrice", "startKm", "mileageFee", "farFrom1", "farTo1", "farFee1", "farTo2", "farFee2"):
            assert isinstance(cfg[field], float) and cfg[field] > 0, f"{field} kosong atau nol di Admin (ID {cfg['price_id']})"
        assert cfg["startKm"] < cfg["farFrom1"] < cfg["farTo1"] <= cfg["farFrom2"] < cfg["farTo2"], \
            "Batas jarak tarif harus berurutan: startKm < farFrom1 < farTo1 <= farFrom2 < farTo2"


class TestAdminRushHourConfig:
    def test_tc_cfg_rush_01_window_valid_dan_tidak_tumpang_tindih(self, record_property):
        """[Pilar 1] Setiap window jam sibuk punya jam mulai < jam selesai dan tidak saling tumpang tindih."""
        cfg = _read(read_rush_hour_config)
        record_property("rush_hour_aktif", cfg["enabled"])
        record_property("rush_hour_window", cfg["windows"])
        assert cfg["windows"], "Belum ada window jam sibuk di /rushHour/settings"
        spans = sorted((_minutes(a), _minutes(b)) for a, b in cfg["windows"])
        for start, end in spans:
            assert start < end, f"Window jam sibuk tidak valid: {cfg['windows']}"
        for (_, end1), (start2, _) in zip(spans, spans[1:]):
            assert end1 <= start2, f"Window jam sibuk tumpang tindih: {cfg['windows']}"

    def test_tc_cfg_rush_02_tier_subsidi_naik_berurutan(self):
        """[Pilar 1] Batas tarif tier naik berurutan, tier terakhir tanpa batas, dan subsidi tidak turun."""
        tiers = _read(read_rush_hour_config)["tiers"]
        assert tiers, "Belum ada tier subsidi di /rushHour/settings"
        limits = [t["max_fare"] for t in tiers[:-1]]
        assert all(limit is not None for limit in limits), "Hanya tier terakhir yang boleh tanpa batas tarif"
        assert limits == sorted(limits), f"Batas tarif tier harus naik: {limits}"
        assert tiers[-1]["max_fare"] is None, "Tier terakhir harus tanpa batas atas tarif"
        subsidies = [t["subsidy"] for t in tiers]
        assert subsidies == sorted(subsidies), f"Subsidi per tier tidak boleh turun: {subsidies}"
