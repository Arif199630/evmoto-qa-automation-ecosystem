"""
================================================================================
TEST SUITE: DRIVER PROFILE, HOME DATA & TELEMETRY API
================================================================================
Target Sistem:
  - EvMoto Driver Core API (/driver/api/driver/queryHomeData, /driver/api/v2/online)
Cakupan Pengujian:
  - Contract Test: Beranda Driver & Kelengkapan Identitas Kendaraan (licensePlate, brand)
  - Integration Status: Keterhubungan eWallet dengan status 'LINKED'
  - Telemetry Telematics Test: Pengiriman Heartbeat Online Status
  - Security / Auth Guard Test: Pencegahan Akses Tanpa Token / Token Tidak Sah
================================================================================
"""
import pytest
import jsonschema
from config.api_config import ApiConfig
from client.api_client import ApiClient
from schemas.api_schemas import (
    DRIVER_HOME_DATA_SCHEMA,
    DRIVER_WALLET_STATUS_SCHEMA
)


class TestDriverCoreApi:
    """Pengujian Fungsionalitas Utama & Telemetri Driver."""

    def test_tc_api_drv_01_home_data_contract(self, authenticated_driver_session: ApiClient):
        """TC-API-DRV-01: Verifikasi kontrak profil beranda driver dan data kendaraan terdaftar."""
        resp = authenticated_driver_session.post(ApiConfig.EP_DRIVER_HOME_DATA, json_data={})

        assert resp.status_code == 200, f"Gagal mengambil data beranda driver: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=DRIVER_HOME_DATA_SCHEMA)

        home_data = res_json.get("data", {})
        assert home_data.get("licensePlate") is not None, "Plat nomor armada wajib terdaftar"
        assert home_data.get("brand") == "ECGO", "Brand kendaraan wajib ECGO"
        assert home_data.get("score", 0) >= 0.0, "Rating skor driver harus bernilai valid"

    def test_tc_api_drv_02_wallet_status_contract(self, authenticated_driver_session: ApiClient):
        """TC-API-DRV-02: Verifikasi status penautan eWallet ECGO pengemudi (status: LINKED)."""
        resp = authenticated_driver_session.get(ApiConfig.EP_DRIVER_WALLET_STATUS)

        assert resp.status_code == 200, f"Gagal mengambil status wallet: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=DRIVER_WALLET_STATUS_SCHEMA)

        wallet_data = res_json.get("data", {})
        assert wallet_data.get("status") == "LINKED", "Status eWallet harus 'LINKED'"
        assert wallet_data.get("linked") is True, "Nilai linked harus True"

    def test_tc_api_drv_03_online_status_heartbeat(self, authenticated_driver_session: ApiClient):
        """TC-API-DRV-03: Verifikasi pengiriman sinyal status aktif/online driver."""
        payload = {"status": 1}
        resp = authenticated_driver_session.post(ApiConfig.EP_DRIVER_ONLINE, json_data=payload)

        # Server merespon request online ping
        assert resp.status_code == 200, f"Gagal memproses online ping: {resp.status_code}"

    def test_tc_api_drv_04_unauthorized_token_rejection(self):
        """TC-API-DRV-04: Security Guard - Menolak akses ke endpoint profil tanpa token JWT sah."""
        unauthenticated_client = ApiClient(base_url=ApiConfig.EVMOTO_BASE_URL)
        # Sematkan token palsu
        unauthenticated_client.set_driver_token("INVALID_FORGED_JWT_TOKEN_123")

        resp = unauthenticated_client.post(ApiConfig.EP_DRIVER_HOME_DATA, json_data={})
        res_json = resp.json() if isinstance(resp.json(), dict) else {}
        
        # Server Golang merespons dengan code 600 (TOKEN_INVALID) atau HTTP 401
        assert resp.status_code in (401, 403) or res_json.get("code") in (600, 401, 500)
        assert "token" in str(res_json.get("msg", "")).lower() or resp.status_code in (401, 403)
