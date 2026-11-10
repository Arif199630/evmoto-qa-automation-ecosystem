"""
================================================================================
TEST SUITE: DRIVER WALLET & FINANCIAL INTEGRATION API
================================================================================
Target Sistem:
  - EvMoto Driver Wallet API (/account/api/ecgo/wallet/status)
Cakupan Pengujian:
  - Contract Test: Status Penautan Dompet eWallet ECGO Mitra Driver
  - Data Masking & PII Protection: Nomor Handphone Disamarkan (Masked Phone)
  - Integration Status: Keterhubungan Penuh Driver dengan Ekosistem Kupon Swap
================================================================================
"""
import pytest
import jsonschema
from config.api_config import ApiConfig
from client.api_client import ApiClient
from schemas.api_schemas import DRIVER_WALLET_STATUS_SCHEMA


class TestDriverWalletApi:
    """Pengujian Modul Finansial & Status Dompet Mitra Pengemudi."""

    def test_tc_api_wal_01_wallet_linking_status(self, authenticated_driver_session: ApiClient):
        """TC-API-WAL-01: Verifikasi status penautan dompet terdaftar sebagai LINKED."""
        resp = authenticated_driver_session.get(ApiConfig.EP_DRIVER_WALLET_STATUS)

        assert resp.status_code == 200, f"Gagal mengambil status wallet: {resp.status_code}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=DRIVER_WALLET_STATUS_SCHEMA)

        wallet_data = res_json.get("data", {})
        assert wallet_data.get("status") == "LINKED", "Status dompet driver harus 'LINKED'"
        assert wallet_data.get("linked") is True, "Nilai linked harus bernilai True"

    def test_tc_api_wal_02_wallet_phone_masking_security(self, authenticated_driver_session: ApiClient):
        """TC-API-WAL-02: Security / PII Test - Nomor telepon pada payload dompet wajib disamarkan."""
        resp = authenticated_driver_session.get(ApiConfig.EP_DRIVER_WALLET_STATUS)
        wallet_data = resp.json().get("data", {})

        masked_phone = wallet_data.get("phoneMasked", "")
        assert masked_phone != "", "Field phoneMasked tidak boleh kosong"
        # Memastikan digit tengah tersensor tanda bintang (*)
        assert "*" in masked_phone, "Nomor telepon harus disamarkan dengan tanda bintang (*)"

    def test_tc_api_wal_03_wallet_timestamp_integrity(self, authenticated_driver_session: ApiClient):
        """TC-API-WAL-03: Data Integrity Test - Memastikan timestamp penautan akun (linkedAt) valid."""
        resp = authenticated_driver_session.get(ApiConfig.EP_DRIVER_WALLET_STATUS)
        wallet_data = resp.json().get("data", {})

        linked_at = wallet_data.get("linkedAt")
        assert linked_at is not None, "Timestamp linkedAt tidak boleh bernilai None"
        assert len(str(linked_at)) >= 10, "Format timestamp linkedAt tidak valid"
