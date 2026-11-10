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

import mock_layanan

mock_layanan.terapkan_env()  # hanya berpengaruh bila USE_MOCK_SERVICES=1; harus sebelum ApiConfig dibaca

from config.api_config import ApiConfig
from client.api_client import ApiClient
from config.staging_guard import ensure_not_production


def pytest_configure(config):
    config.addinivalue_line("markers", "mock_services: test karantina yang dijalankan terhadap mock lokal (USE_MOCK_SERVICES=1)")


def pytest_sessionstart(session):
    """Batalkan run bila URL API mengarah ke production (hanya dev/staging yang diizinkan)."""
    ensure_not_production(extra_urls=[ApiConfig.EVMOTO_BASE_URL, ApiConfig.ECGO_BASE_URL, ApiConfig.ADMIN_BASE_URL,
                                      ApiConfig.CONNECT_BRIDGE_URL])
    if mock_layanan.MOCK_AKTIF:
        mock_layanan.siapkan_sesi()


_TEST_MOCK = []


@pytest.fixture(autouse=True)
def _tandai_test_mock(request):
    """Bila USE_MOCK_SERVICES=1: test yang memanggil mock diberi properti JUnit mock=true.

    Dihitung dari jumlah request ke mock sebelum dan sesudah test, jadi hanya test yang benar-benar
    memanggil mock yang ditandai. Test yang tetap ke staging sungguhan tidak ditandai.
    """
    if not mock_layanan.MOCK_AKTIF:
        yield
        return
    sebelum = mock_layanan.jumlah_hit()
    yield
    if mock_layanan.jumlah_hit() > sebelum:
        request.node.user_properties.append(("mock", "true"))
        _TEST_MOCK.append(request.node.nodeid)


def pytest_terminal_summary(terminalreporter):
    if mock_layanan.MOCK_AKTIF:
        terminalreporter.write_line(
            f"MOCK: {len(_TEST_MOCK)} test memanggil mock lokal ({mock_layanan.MOCK_URL}). "
            "Hasilnya memvalidasi alur automation terhadap kontrak tiruan, BUKAN backend sungguhan.")


@pytest.fixture(scope="session")
def evmoto_client() -> ApiClient:
    """Fixture instance API client untuk backend EvMoto."""
    client = ApiClient(base_url=ApiConfig.EVMOTO_BASE_URL)
    return client


@pytest.fixture(scope="session")
def ecgo_client() -> ApiClient:
    """Fixture instance API client untuk backend ECGO SuperApps."""
    if not ApiConfig.ECGO_BASE_URL:
        pytest.skip("ECGO_API_BASE_URL belum diisi di .env: URL staging ECGO belum tersedia, test ECGO dilewati.")
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


def pytest_collection_modifyitems(config, items):
    """Test bertanda @pytest.mark.quarantine dilewati dengan alasan jelas, kecuali RUN_QUARANTINE=1.

    Karantina dipakai untuk test yang belum bisa divalidasi terhadap staging (endpoint belum ada,
    kontrak belum dikonfirmasi). Test ini tidak dihitung lulus maupun gagal, dan wajib punya alasan.
    Dengan USE_MOCK_SERVICES=1, test di mock_layanan.KARANTINA_DENGAN_MOCK dijalankan terhadap mock lokal.
    """
    import os
    if os.getenv("RUN_QUARANTINE", "0") == "1":
        return
    for item in items:
        marker = item.get_closest_marker("quarantine")
        nama = {item.originalname, item.cls.__name__ if item.cls else ""}
        if marker and mock_layanan.MOCK_AKTIF and nama & mock_layanan.KARANTINA_DENGAN_MOCK:
            item.add_marker(pytest.mark.mock_services)
            continue
        if marker:
            reason = marker.kwargs.get("reason", "tanpa alasan")
            item.add_marker(pytest.mark.skip(reason=f"KARANTINA: {reason}"))
