"""
================================================================================
TEST SUITE: BOUNDARY, EXTREME INPUT & DATA INTEGRITY API TESTING (PILAR 4 QA)
================================================================================
Target Sistem:
  - EvMoto Backend API & ECGO SuperApps Discount Engine
Cakupan Pengujian:
  - Panjang Nomor Handphone Ekstrem (< 8 Digit, > 20 Digit)
  - Input Karakter Spesial & Non-Numerik
  - Verifikasi Waktu Kedaluwarsa Kupon di Masa Depan (No Expired Active Coupons)
  - Robustness Test: Penanganan Empty JSON Body & Malformed Content
================================================================================
"""
from datetime import datetime, timezone
import pytest
from config.api_config import ApiConfig
from client.api_client import ApiClient


class TestBoundaryAndDataIntegrityApi:
    """Pengujian Batas Nilai Ekstrem dan Robustness Input."""

    def test_tc_api_bnd_01_phone_too_short(self, evmoto_client: ApiClient):
        """TC-API-BND-01: Boundary Test - Input nomor handphone terlalu pendek (7 digit: '8123456')."""
        resp = evmoto_client.post(
            ApiConfig.EP_DRIVER_LOGIN_OTP,
            json_data={"phone": "8123456", "code": "1234"}
        )
        assert resp.status_code in (200, 400, 422)
        if resp.status_code == 200:
            assert resp.json().get("code") != 200, "Nomor HP 7 digit harus ditolak oleh validasi server"

    def test_tc_api_bnd_02_phone_too_long(self, evmoto_client: ApiClient):
        """TC-API-BND-02: Boundary Test - Input nomor handphone terlalu panjang (25 digit)."""
        long_phone = "8228373723712345678901234"
        resp = evmoto_client.post(
            ApiConfig.EP_DRIVER_LOGIN_OTP,
            json_data={"phone": long_phone, "code": "1234"}
        )
        assert resp.status_code in (200, 400, 422)
        if resp.status_code == 200:
            assert resp.json().get("code") != 200, "Nomor HP 25 digit harus ditolak oleh server"

    def test_tc_api_bnd_03_phone_with_special_characters(self, evmoto_client: ApiClient):
        """TC-API-BND-03: Input Sanitization - Nomor handphone memuat simbol (@, #, $, !)."""
        resp = evmoto_client.post(
            ApiConfig.EP_DRIVER_LOGIN_OTP,
            json_data={"phone": "0812@#$!-7237", "code": "1234"}
        )
        assert resp.status_code in (200, 400, 422)
        if resp.status_code == 200:
            assert resp.json().get("code") != 200, "Nomor HP dengan karakter spesial harus ditolak"

    def test_tc_api_bnd_04_coupon_future_expiry_date(self, authenticated_ecgo_session: ApiClient):
        """TC-API-BND-04: Data Integrity - Memastikan seluruh kupon aktif ('ready') memiliki masa berlaku valid di masa depan."""
        resp = authenticated_ecgo_session.get(ApiConfig.EP_ECGO_DISCOUNTS)
        assert resp.status_code == 200
        rows = resp.json().get("data", {}).get("rows", [])

        now = datetime.now(timezone.utc)
        for coupon in rows:
            if coupon.get("status") == "ready" and coupon.get("expiredAt"):
                exp_str = coupon.get("expiredAt")
                try:
                    # Parse ISO format UTC (contoh: 2027-01-30T06:33:06.000Z)
                    exp_dt = datetime.fromisoformat(exp_str.replace("Z", "+00:00"))
                    assert exp_dt > now, f"Kupon {coupon.get('name')} berstatus 'ready' tetapi sudah kedaluwarsa ({exp_str})!"
                except ValueError:
                    pass

    def test_tc_api_bnd_05_empty_payload_post(self, evmoto_client: ApiClient):
        """TC-API-BND-05: Robustness Test - Mengirim empty JSON object {} pada endpoint login."""
        resp = evmoto_client.post(ApiConfig.EP_DRIVER_LOGIN_OTP, json_data={})

        # Server tidak boleh crash (HTTP 502 / 504), harus mengembalikan respons validasi tertangani
        assert resp.status_code in (200, 400, 422)
        if resp.status_code == 200:
            assert resp.json().get("code") != 200, "Payload kosong tidak boleh menghasilkan code 200"
