"""
================================================================================
EVMOTO & ECGO PERFORMANCE TESTING - CONFIGURATION MANAGER
================================================================================
Mengelola konfigurasi target staging/dev server, kredensial load test, 
ambang batas SLA (Latency & Failure Rate), serta parameter profil beban.
================================================================================
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Muat environment variable dari .env root atau lokal
_CURRENT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _CURRENT_DIR.parent.parent
_ENV_PATH = _REPO_ROOT / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
else:
    load_dotenv()


class PerfConfig:
    """Konfigurasi terpusat untuk skenario Locust Performance Testing."""

    # --------------------------------------------------------------------------
    # Base URLs (Staging / Dev Server)
    # --------------------------------------------------------------------------
    EVMOTO_BASE_URL: str = os.getenv(
        "EVMOTO_API_BASE_URL", "https://evmotodev.justkidding.app"
    ).rstrip("/")

    ECGO_BASE_URL: str = os.getenv(
        "ECGO_API_BASE_URL", "http://139.162.60.46:3002"
    ).rstrip("/")

    ADMIN_BASE_URL: str = os.getenv(
        "EVMOTO_ADMIN_PORTAL_URL", "https://evmotoadmin.justkidding.app"
    ).rstrip("/")

    # --------------------------------------------------------------------------
    # Kredensial Pengujian Akun Staging
    # --------------------------------------------------------------------------
    DRIVER_PHONE: str = os.getenv("TEST_DRIVER_PHONE", "082283737237")
    DRIVER_PIN: str = os.getenv("TEST_DRIVER_PIN", "1234")

    USER_PHONE: str = os.getenv("TEST_USER_PHONE", "082283737237")
    USER_OTP: str = os.getenv("TEST_USER_OTP", "1234")

    ECGO_PHONE: str = os.getenv("TEST_ECGO_PHONE", "082283737237")
    ECGO_OTP: str = os.getenv("TEST_ECGO_OTP", "777777")

    # --------------------------------------------------------------------------
    # Driver Endpoints (Golang Backend)
    # --------------------------------------------------------------------------
    EP_DRIVER_QUERY_CAPTCHA = "/account/base/driver/queryCaptcha"
    EP_DRIVER_LOGIN_OTP = "/account/base/driver/driverLoginByOtp"
    EP_DRIVER_HOME_DATA = "/driver/api/driver/queryHomeData"
    EP_DRIVER_ONLINE = "/driver/api/v2/online"
    EP_DRIVER_WALLET_STATUS = "/account/api/ecgo/wallet/status"

    # --------------------------------------------------------------------------
    # Passenger / User Endpoints (Golang Backend)
    # --------------------------------------------------------------------------
    EP_USER_QUERY_CAPTCHA = "/account/base/user/queryCaptcha"
    EP_USER_LOGIN_OTP = "/account/base/user/userLoginByOtp"
    EP_USER_PROFILE = "/user/api/user/queryInfo"
    EP_USER_ESTIMATE_FARE = "/order/api/user/estimateFare"
    EP_USER_CREATE_ORDER = "/order/api/user/createOrder"
    EP_USER_CANCEL_ORDER = "/order/api/user/cancelOrder"

    # --------------------------------------------------------------------------
    # ECGO SuperApps Endpoints (Node.js Backend)
    # --------------------------------------------------------------------------
    EP_ECGO_GENERATE_OTP = "/v5/users/onboarding/generateOtp/sms"
    EP_ECGO_VERIFY_OTP = "/v5/users/onboarding/verifyOtp"
    EP_ECGO_DISCOUNTS = "/v5/users/diskon/list"
    EP_ECGO_CONNECT_STATUS = "/v5/users/evmoto-connect/status"
    EP_ECGO_CONNECT_START = "/v5/users/evmoto-connect/start"

    # --------------------------------------------------------------------------
    # SLA & Thresholds
    # --------------------------------------------------------------------------
    SLA_MAX_P95_MS: int = int(os.getenv("PERF_SLA_MAX_P95_MS", "800"))
    SLA_MAX_FAILURE_RATE: float = float(os.getenv("PERF_SLA_MAX_FAIL_RATE", "2.0"))  # Persentase max 2%
    REQUEST_TIMEOUT: int = int(os.getenv("PERF_REQUEST_TIMEOUT", "10"))
