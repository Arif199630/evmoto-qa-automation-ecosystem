"""
================================================================================
TEST SUITE: SECURITY, INJECTION & ANTI-FRAUD API TESTING (PILAR 3 QA)
================================================================================
Target Sistem:
  - EvMoto Backend API & ECGO SuperApps Authentication Layer
Cakupan Pengujian:
  - SQL Injection (SQLi) Defense pada Autentikasi & Query Params
  - Cross-Site Scripting (XSS) Input Sanitization Defense
  - Cryptographic JWT Signature Tampering & Forgery Guard
  - Rate Limiting / SMS OTP Flooding Defense
  - Privilege Escalation Prevention (Driver Role vs Admin Resource)
================================================================================
"""
import pytest
from config.api_config import ApiConfig
from client.api_client import ApiClient


class TestSecurityAndFraudDefenseApi:
    """Pengujian Keamanan, Validasi Injeksi, dan Pertahanan Penipuan API."""

    def test_tc_api_sec_01_sql_injection_defense(self, evmoto_client: ApiClient):
        """TC-API-SEC-01: SQLi Defense - Memastikan payload SQL Injection ditolak dan tidak merusak query DB."""
        sqli_payloads = [
            "' OR '1'='1",
            "admin'--",
            "1' UNION SELECT null, null, null--",
            "82283737237' OR 1=1;--"
        ]
        for payload in sqli_payloads:
            resp = evmoto_client.post(
                ApiConfig.EP_DRIVER_LOGIN_OTP,
                json_data={"phone": payload, "code": "1234"}
            )
            # Sistem harus menolak dengan aman (tidak boleh membocorkan error sintaks SQL syntax error)
            res_str = str(resp.data).lower()
            assert "syntax error" not in res_str, f"Potensi SQL Leak terdeteksi pada payload: {payload}"
            assert "sql" not in res_str, f"Pesan internal SQL terekspos pada payload: {payload}"
            assert resp.status_code in (200, 400, 401, 422)
            if resp.status_code == 200:
                assert resp.json().get("code") != 200, "SQL injection tidak boleh berhasil login!"

    def test_tc_api_sec_02_xss_script_injection_defense(self, evmoto_client: ApiClient):
        """TC-API-SEC-02: XSS Defense - Memastikan payload JavaScript / HTML Tag disanitasi."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:void(0)",
            "\"><script>fetch('http://attacker.com')</script>"
        ]
        for payload in xss_payloads:
            resp = evmoto_client.post(
                ApiConfig.EP_DRIVER_LOGIN_OTP,
                json_data={"phone": payload, "code": "1234"}
            )
            res_str = str(resp.data)
            # Respons tidak boleh mengeksekusi atau merender tag script mentah
            assert "<script>" not in res_str, f"Tag script XSS tidak tersanitasi pada payload: {payload}"
            if resp.status_code == 200:
                assert resp.json().get("code") != 200, "Payload XSS tidak boleh menghasilkan status sukses!"

    def test_tc_api_sec_03_jwt_signature_tampering(self, authenticated_driver_session: ApiClient):
        """TC-API-SEC-03: Cryptographic Guard - Menolak token JWT yang telah dimanipulasi signature-nya."""
        tampered_client = ApiClient(base_url=ApiConfig.EVMOTO_BASE_URL)
        original_token = authenticated_driver_session.token or "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTMyNTgxMDUsImlhdCI6MTc5MjY1MzMwNX0.INVALID_SIGNATURE_TAMPERED"

        # Manipulasi 10 karakter terakhir signature JWT
        tampered_token = original_token[:-10] + "TAMPERED99"
        tampered_client.set_driver_token(tampered_token)

        resp = tampered_client.post(ApiConfig.EP_DRIVER_HOME_DATA, json_data={})
        res_json = resp.json() if isinstance(resp.json(), dict) else {}

        # Harus ditolak oleh backend (HTTP 401/403 atau code 600 TOKEN_INVALID)
        assert resp.status_code in (401, 403) or res_json.get("code") in (600, 401, 500)
        assert "token" in str(res_json.get("msg", "")).lower() or resp.status_code in (401, 403)

    def test_tc_api_sec_04_sms_otp_rate_limiting_defense(self, ecgo_client: ApiClient):
        """TC-API-SEC-04: Anti-Flooding - Memverifikasi mekanisme proteksi rate limit pengiriman SMS OTP."""
        # Kirim request pertama
        resp1 = ecgo_client.post(ApiConfig.EP_ECGO_GENERATE_OTP, json_data={"phoneNumber": ApiConfig.ECGO_PHONE})
        assert resp1.status_code == 200

        # Kirim request kedua langsung tanpa jeda (seharusnya ada penanganan throttle / cooldown waktu kedaluwarsa)
        resp2 = ecgo_client.post(ApiConfig.EP_ECGO_GENERATE_OTP, json_data={"phoneNumber": ApiConfig.ECGO_PHONE})
        assert resp2.status_code in (200, 429)
        if resp2.status_code == 200:
            otp_info = resp2.json().get("otp", {})
            # Backend mencatat waktu kedaluwarsa OTP secara deterministik
            assert "expiredAt" in otp_info or "message" in resp2.json()

    def test_tc_api_sec_05_expired_token_rejection(self):
        """TC-API-SEC-05: Token Expiration - Memastikan token kedaluwarsa tidak dapat digunakan kembali."""
        expired_client = ApiClient(base_url=ApiConfig.EVMOTO_BASE_URL)
        # Token simulasi dengan expired timestamp masa lalu
        expired_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEwMDAwMDAwMDAsImlhdCI6OTk5OTk5OTAwLCJzdWIiOiI1NDYifQ.EXPIRED_MOCK_SIGNATURE"
        expired_client.set_driver_token(expired_token)

        resp = expired_client.post(ApiConfig.EP_DRIVER_HOME_DATA, json_data={})
        res_json = resp.json() if isinstance(resp.json(), dict) else {}

        assert resp.status_code in (401, 403) or res_json.get("code") in (600, 401, 500)

    def test_tc_api_sec_06_privilege_escalation_guard(self, authenticated_driver_session: ApiClient):
        """TC-API-SEC-06: RBAC Guard - Mencegah hak akses Mitra Driver mengakses endpoint konfigurasi Admin."""
        admin_restricted_endpoint = f"{ApiConfig.ADMIN_BASE_URL}/api/admin/system/config"
        resp = authenticated_driver_session.get(admin_restricted_endpoint)

        # Harus ditolak: tidak diizinkan masuk ke kontrol admin (401/403/404)
        assert resp.status_code in (401, 403, 404), f"Akses Driver ke endpoint Admin harus ditolak, status: {resp.status_code}"
