"""
================================================================================
EVMOTO & ECGO API TESTING - PYTEST CONFTEST FIXTURES
================================================================================
Menyediakan fixtures sesi pengujian otomatis, autentikasi otomatis,
dan manajemen siklus pengujian API.
================================================================================
"""
import pytest
import sys
from pathlib import Path

# Daftarkan modul api-testing ke sys.path
_API_DIR = Path(__file__).resolve().parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

from config.api_config import ApiConfig
from client.api_client import ApiClient


@pytest.fixture(scope="session")
def evmoto_client() -> ApiClient:
    """Fixture instance API client untuk backend EvMoto."""
    client = ApiClient(base_url=ApiConfig.EVMOTO_BASE_URL)
    return client


@pytest.fixture(scope="session")
def ecgo_client() -> ApiClient:
    """Fixture instance API client untuk backend ECGO SuperApps."""
    client = ApiClient(base_url=ApiConfig.ECGO_BASE_URL)
    return client


@pytest.fixture(scope="module")
def authenticated_driver_session(evmoto_client) -> ApiClient:
    """Fixture sesi Driver yang sudah terautentikasi dengan token aktif."""
    # 1. Query captcha terlebih dahulu
    evmoto_client.post(ApiConfig.EP_DRIVER_QUERY_CAPTCHA, json_data={"phone": ApiConfig.DRIVER_PHONE})

    # 2. Login via OTP / PIN bypass
    payload = {
        "phone": ApiConfig.DRIVER_PHONE,
        "code": ApiConfig.DRIVER_PIN
    }
    resp = evmoto_client.post(ApiConfig.EP_DRIVER_LOGIN_OTP, json_data=payload)
    if resp.status_code == 200:
        token = resp.json().get("data", {}).get("token")
        if token:
            evmoto_client.set_driver_token(token)
    return evmoto_client


@pytest.fixture(scope="module")
def authenticated_ecgo_session(ecgo_client) -> ApiClient:
    """Fixture sesi ECGO SuperApps yang sudah terautentikasi dengan token aktif."""
    # 1. Trigger generate OTP SMS
    ecgo_client.post(
        ApiConfig.EP_ECGO_GENERATE_OTP,
        json_data={"phoneNumber": ApiConfig.ECGO_PHONE}
    )
    # 2. Verifikasi OTP
    resp = ecgo_client.post(
        ApiConfig.EP_ECGO_VERIFY_OTP,
        json_data={"phoneNumber": ApiConfig.ECGO_PHONE, "code": ApiConfig.ECGO_OTP}
    )
    if resp.status_code == 200:
        token = resp.json().get("token")
        if token:
            ecgo_client.set_ecgo_token(token)
    return ecgo_client


@pytest.fixture(scope="module")
def authenticated_user_session() -> ApiClient:
    """Fixture sesi Penumpang (User Mobile) yang sudah terautentikasi."""
    user_client = ApiClient(base_url=ApiConfig.EVMOTO_BASE_URL)
    user_client.post(ApiConfig.EP_USER_QUERY_CAPTCHA, json_data={"phone": ApiConfig.USER_PHONE})
    
    payload = {
        "phone": ApiConfig.USER_PHONE,
        "code": ApiConfig.USER_OTP
    }
    resp = user_client.post(ApiConfig.EP_USER_LOGIN_OTP, json_data=payload)
    if resp.status_code == 200:
        token = resp.json().get("data", {}).get("token")
        if token:
            user_client.set_user_token(token)
    return user_client

