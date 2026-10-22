"""
================================================================================
TEST SUITE: ECGO BATTERY SWAP & COUPON DISCOUNT API
================================================================================
Target Sistem:
  - ECGO SuperApps Swap API (/v5/users/diskon/list, /v5/users/evmoto-connect/status, /v5/users/evmoto-connect/start)
Cakupan Pengujian:
  - Data Integrity Test: Kupon Free Swap Baterai 100% Hasil Integrasi EvMoto
  - Business Rule Test: Status Keterhubungan Akun ECGO Connect (status: 'completed', linked: true)
  - Anti-Duplicate Binding: Validasi Penolakan Re-Linking pada Akun Terhubung (HTTP 409)
================================================================================
"""
import pytest
import jsonschema
from config.api_config import ApiConfig
from client.api_client import ApiClient
from schemas.api_schemas import (
    ECGO_DISCOUNTS_SCHEMA,
    ECGO_CONNECT_STATUS_SCHEMA
)


class TestEcgoBatterySwapApi:
    """Pengujian Ekosistem Penukaran Baterai & Kupon Diskon ECGO."""

    def test_tc_api_swap_01_driver_coupon_discounts(self, authenticated_ecgo_session: ApiClient):
        """TC-API-SWAP-01: Verifikasi kupon Free Swap 100% muncul di dompet diskon driver."""
        resp = authenticated_ecgo_session.get(ApiConfig.EP_ECGO_DISCOUNTS)

        assert resp.status_code == 200, f"Gagal mendapatkan kupon diskon: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=ECGO_DISCOUNTS_SCHEMA)

        rows = res_json.get("data", {}).get("rows", [])
        assert len(rows) > 0, "Daftar kupon diskon mitra tidak boleh kosong"

        # Cari kupon Free Swap hasil integrasi (Diskon Pergantian Baterai 100%)
        free_swap_coupon = None
        for coupon in rows:
            c_name = coupon.get("name", "").lower()
            if "baterai" in c_name or "swap" in c_name:
                free_swap_coupon = coupon
                break

        assert free_swap_coupon is not None, "Kupon Free Swap Baterai tidak ditemukan di daftar kupon"
        assert free_swap_coupon.get("amount") == 100, "Besaran diskon kupon harus 100%"
        assert free_swap_coupon.get("status") == "ready", "Status kupon harus 'ready' (siap digunakan)"

    def test_tc_api_swap_02_connection_status(self, authenticated_ecgo_session: ApiClient):
        """TC-API-SWAP-02: Verifikasi status interkoneksi EvMoto Connect di SuperApps."""
        resp = authenticated_ecgo_session.get(ApiConfig.EP_ECGO_CONNECT_STATUS)

        assert resp.status_code == 200, f"Gagal mengambil status koneksi: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=ECGO_CONNECT_STATUS_SCHEMA)

        assert res_json.get("linked") is True, "Akun driver wajib berstatus terhubung (linked = True)"
        assert res_json.get("status") == "completed", "Status interkoneksi harus 'completed'"
        assert res_json.get("couponGranted") is True, "Flag pemberian kupon swap wajib bernilai True"

    def test_tc_api_swap_03_connect_start_contract(self, authenticated_ecgo_session: ApiClient):
        """TC-API-SWAP-03: Verifikasi inisiasi handshake web connect jembatan EvMoto-ECGO & anti-duplicate binding."""
        resp = authenticated_ecgo_session.post(ApiConfig.EP_ECGO_CONNECT_START)

        # Jika akun belum terhubung: HTTP 200 dengan token web connect
        # Jika akun sudah terhubung: HTTP 409 Conflict (Pencegahan double-link)
        assert resp.status_code in (200, 409), f"Status tidak diharapkan: {resp.status_code} - {resp.data}"
        res_json = resp.json()
        if resp.status_code == 200:
            assert res_json.get("success") is True or "url" in str(res_json).lower()
        else:
            assert "terhubung" in str(res_json.get("message", "")).lower()
