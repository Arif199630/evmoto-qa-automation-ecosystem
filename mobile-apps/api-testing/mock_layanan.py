"""
Sambungan ke mock server lokal (evmoto-qa-tools/mock_services) untuk layanan yang belum ada di staging.

Hanya aktif bila USE_MOCK_SERVICES=1. Tanpa variabel itu, file ini tidak mengubah apa pun.
Saat aktif:
  - ECGO_API_BASE_URL (bila kosong di .env) dan CONNECT_BRIDGE_URL (bila tidak diisi) diarahkan ke mock.
  - Endpoint EvMoto yang belum ada di staging (ApiConfig.MOCK_ROUTED_ENDPOINTS) dikirim ke mock;
    endpoint EvMoto lain tetap ke staging sungguhan.
  - Test karantina di KARANTINA_DENGAN_MOCK dijalankan terhadap mock, tidak di-skip.
  - Test yang benar-benar memanggil mock diberi properti JUnit mock=true.

File ini sengaja TIDAK berada di package config/, karena env harus diisi sebelum config/api_config.py dibaca.
"""
import json
import os
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

MOCK_AKTIF = os.getenv("USE_MOCK_SERVICES", "0") == "1"
MOCK_URL = os.getenv("MOCK_SERVICES_URL", "http://127.0.0.1:8790").rstrip("/")

# Akun ECGO palsu. Harus sama dengan fixtures/ecgo_superapps.json -> data.akun_uji.
ECGO_PHONE_MOCK = "080000000001"
ECGO_OTP_MOCK = "246810"

# Test karantina yang alasannya "endpoint belum ada di staging / kontrak dari mock".
# Nama class atau nama fungsi test. Hapus dari sini setelah endpoint-nya ada di staging.
KARANTINA_DENGAN_MOCK = {
    "TestFitur2OnlineFreeSwapApi",
    "TestFitur3UserOnboardingVouchersApi",
    "TestFitur5RushHourSubsidyApi",
    "test_tc_api_usr_02_fare_estimation",
    "test_tc_api_usr_03_create_booking_order",
    "test_tc_api_usr_04_cancel_booking_order",
}

HOST_LOKAL = {"127.0.0.1", "localhost", "::1"}


def terapkan_env():
    """Isi env yang menunjuk ke mock. Dipanggil conftest sebelum ApiConfig dibaca."""
    if not MOCK_AKTIF:
        return
    if (urlparse(MOCK_URL).hostname or "") not in HOST_LOKAL:
        raise RuntimeError(f"MOCK_SERVICES_URL harus di mesin lokal (127.0.0.1/localhost), bukan {MOCK_URL}")
    env_file = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_file if env_file.exists() else None)
    if not os.getenv("ECGO_API_BASE_URL"):
        os.environ["ECGO_API_BASE_URL"] = MOCK_URL
        os.environ["TEST_ECGO_PHONE"] = ECGO_PHONE_MOCK
        os.environ["TEST_ECGO_OTP"] = ECGO_OTP_MOCK
    if not os.getenv("CONNECT_BRIDGE_URL"):
        os.environ["CONNECT_BRIDGE_URL"] = MOCK_URL


def _panggil(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(MOCK_URL + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read())


def siapkan_sesi():
    """Pastikan mock hidup, lalu kosongkan state-nya supaya tiap sesi pytest mulai dari data fixture."""
    try:
        _panggil("/__health")
    except OSError as e:
        raise RuntimeError(
            f"USE_MOCK_SERVICES=1 tetapi mock server tidak bisa dihubungi di {MOCK_URL} ({e}).\n"
            "Jalankan dulu: python ../../evmoto-qa-tools/mock_services/mock_server.py"
        ) from e
    _panggil("/__reset", method="POST", body={})


def jumlah_hit():
    """Jumlah request ke rute mock sejak reset terakhir."""
    return _panggil("/__stats")["hits"]
