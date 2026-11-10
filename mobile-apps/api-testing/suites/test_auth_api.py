"""
================================================================================
TEST SUITE: AUTHENTICATION & OTP ONBOARDING API
================================================================================
Target Sistem:
  - EvMoto Driver Auth API (/account/base/driver/driverLoginByOtp)
  - ECGO SuperApps Onboarding API (/v5/users/onboarding/verifyOtp)
Cakupan Pengujian:
  - Positive Test: Login sukses dengan kredensial bypass dev
  - Negative Test: Penolakan PIN / OTP keliru
  - Boundary Test: Validasi nomor telepon kosong atau tidak terdaftar
  - Contract Test: JSON Schema validation pada auth payload
================================================================================
"""
import pytest
import jsonschema
from config.api_config import ApiConfig
from client.api_client import ApiClient
from schemas.api_schemas import (
    DRIVER_LOGIN_SUCCESS_SCHEMA,
    DRIVER_LOGIN_ERROR_SCHEMA,
    ECGO_GENERATE_OTP_SCHEMA,
    ECGO_VERIFY_OTP_SUCCESS_SCHEMA
)


class TestDriverAuthenticationApi:
    """Pengujian API Autentikasi Mitra Pengemudi EvMoto."""

    def test_tc_api_auth_01_driver_login_valid_credentials(self, evmoto_client: ApiClient):
        """TC-API-AUTH-01: Verifikasi login mitra driver sukses dengan kredensial valid."""
        # 1. Trigger query captcha
        evmoto_client.post(ApiConfig.EP_DRIVER_QUERY_CAPTCHA, json_data={"phone": ApiConfig.DRIVER_PHONE})

        # 2. Kirim kredensial login
        payload = {
            "phone": ApiConfig.DRIVER_PHONE,
            "code": ApiConfig.DRIVER_PIN
        }
        resp = evmoto_client.post(ApiConfig.EP_DRIVER_LOGIN_OTP, json_data=payload)

        # 3. Status Code Assertion
        assert resp.status_code == 200, f"Ekspektasi HTTP 200, respon: {resp.status_code} - {resp.data}"

        # 4. Contract Schema Validation
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=DRIVER_LOGIN_SUCCESS_SCHEMA)

        # 5. Data Integrity Assertion
        auth_data = res_json.get("data", {})
        assert auth_data.get("token") is not None, "Token JWT tidak boleh None"
        assert len(auth_data.get("token")) > 10, "Panjang token JWT tidak memadai"
        assert auth_data.get("id") is not None, "Driver ID wajib terisi"

    def test_tc_api_auth_02_driver_login_invalid_pin(self, evmoto_client: ApiClient):
        """TC-API-AUTH-02: Verifikasi penolakan login mitra driver dengan PIN keliru."""
        payload = {
            "phone": ApiConfig.DRIVER_PHONE,
            "code": "9999"  # PIN salah
        }
        resp = evmoto_client.post(ApiConfig.EP_DRIVER_LOGIN_OTP, json_data=payload)

        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=DRIVER_LOGIN_ERROR_SCHEMA)
        # Server Golang merespons dengan code != 200 (misal 500) dan pesan kegagalan verifikasi
        assert res_json.get("code") != 200, "Login dengan PIN salah tidak boleh menghasilkan code 200"
        assert "invalid" in str(res_json.get("msg", "")).lower()

    def test_tc_api_auth_03_driver_login_empty_phone(self, evmoto_client: ApiClient):
        """TC-API-AUTH-03: Boundary Test - Login dengan field nomor handphone kosong."""
        payload = {
            "phone": "",
            "code": ApiConfig.DRIVER_PIN
        }
        resp = evmoto_client.post(ApiConfig.EP_DRIVER_LOGIN_OTP, json_data=payload)

        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=DRIVER_LOGIN_ERROR_SCHEMA)
        assert res_json.get("code") != 200, "Nomor handphone kosong wajib ditolak sistem"


class TestEcgoSuperAppsAuthenticationApi:
    """Pengujian API Autentikasi Pengguna & Driver di ECGO SuperApps."""

    def test_tc_api_auth_04_ecgo_generate_otp_sms(self, ecgo_client: ApiClient):
        """TC-API-AUTH-04: Verifikasi permintaan kirim kode OTP via SMS."""
        payload = {"phoneNumber": ApiConfig.ECGO_PHONE}
        resp = ecgo_client.post(ApiConfig.EP_ECGO_GENERATE_OTP, json_data=payload)

        assert resp.status_code == 200, f"Gagal request OTP: {resp.status_code} - {resp.data}"
        res_json = resp.json()
        if res_json.get("message") == "still have active otp, please wait":
            # Cooldown aktif dari pengujian sebelumnya - respons rate limit valid dari server
            assert True
        else:
            jsonschema.validate(instance=res_json, schema=ECGO_GENERATE_OTP_SCHEMA)
            assert res_json.get("message") == "success"

    def test_tc_api_auth_05_ecgo_verify_otp_valid(self, ecgo_client: ApiClient):
        """TC-API-AUTH-05: Verifikasi validasi kode OTP benar dan penerbitan token sesi."""
        # 1. Pastikan OTP aktif digenerate terlebih dahulu
        ecgo_client.post(ApiConfig.EP_ECGO_GENERATE_OTP, json_data={"phoneNumber": ApiConfig.ECGO_PHONE})

        # 2. Verifikasi OTP
        payload = {
            "phoneNumber": ApiConfig.ECGO_PHONE,
            "code": ApiConfig.ECGO_OTP
        }
        resp = ecgo_client.post(ApiConfig.EP_ECGO_VERIFY_OTP, json_data=payload)

        assert resp.status_code == 200, f"Gagal verifikasi OTP: {resp.status_code} - {resp.data}"
        res_json = resp.json()
        jsonschema.validate(instance=res_json, schema=ECGO_VERIFY_OTP_SUCCESS_SCHEMA)
        assert res_json.get("token") is not None
        assert res_json.get("status") == "verified"

    def test_tc_api_auth_06_ecgo_verify_otp_invalid_code(self, ecgo_client: ApiClient):
        """TC-API-AUTH-06: Verifikasi penolakan kode OTP keliru."""
        payload = {
            "phoneNumber": ApiConfig.ECGO_PHONE,
            "code": "000000"  # Kode OTP salah
        }
        resp = ecgo_client.post(ApiConfig.EP_ECGO_VERIFY_OTP, json_data=payload)

        assert resp.status_code in (400, 403, 404), f"Ekspektasi HTTP 4xx untuk OTP salah, didapat: {resp.status_code}"
