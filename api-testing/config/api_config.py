"""
================================================================================
EVMOTO & ECGO API AUTOMATION - CONFIGURATION MANAGER
================================================================================
Mengelola URL target, path endpoint, dan kredensial pengujian melalui
Environment Variable (.env). Kredensial sensitif diamankan dengan default
rekayasa aman (masked) saat dijalankan di lingkungan publik / CI.
================================================================================
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cari dan muat file .env dari root repository jika tersedia
_CURRENT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _CURRENT_DIR.parent.parent
_ENV_PATH = _REPO_ROOT / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
else:
    load_dotenv()


class ApiConfig:
    """Konfigurasi terpusat untuk API Automation Suite."""

    # --------------------------------------------------------------------------
    # Base URLs
    # --------------------------------------------------------------------------
    EVMOTO_BASE_URL: str = os.getenv(
        "EVMOTO_API_BASE_URL", "https://api-dev.evmoto.internal"
    ).rstrip("/")

    ECGO_BASE_URL: str = os.getenv(
        "ECGO_API_BASE_URL", "https://ecgo-api.internal:3002"
    ).rstrip("/")

    ADMIN_BASE_URL: str = os.getenv(
        "EVMOTO_ADMIN_PORTAL_URL", "https://admin-staging.evmoto.internal"
    ).rstrip("/")

    CONNECT_BRIDGE_URL: str = os.getenv(
        "CONNECT_BRIDGE_URL", "https://connect.evmoto.internal"
    ).rstrip("/")

    # --------------------------------------------------------------------------
    # Kredensial Simulator Pengujian
    # --------------------------------------------------------------------------
    DRIVER_PHONE: str = os.getenv("TEST_DRIVER_PHONE", "0812XXXXXXXX")
    DRIVER_PIN: str = os.getenv("TEST_DRIVER_PIN", "****")

    ECGO_PHONE: str = os.getenv("TEST_ECGO_PHONE", "0812XXXXXXXX")
    ECGO_OTP: str = os.getenv("TEST_ECGO_OTP", "******")

    ADMIN_USERNAME: str = os.getenv("TEST_ADMIN_USERNAME", "admin_qa_dev")
    ADMIN_PASSWORD: str = os.getenv("TEST_ADMIN_PASSWORD", "********")

    # --------------------------------------------------------------------------
    # Timeout & Fallback Settings
    # --------------------------------------------------------------------------
    DEFAULT_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))
    MOCK_FALLBACK: bool = os.getenv("MOCK_API_FALLBACK", "true").lower() in ("true", "1", "yes")

    # --------------------------------------------------------------------------
    # EvMoto Driver Endpoints (Golang Stack)
    # --------------------------------------------------------------------------
    EP_DRIVER_LOGIN_OTP = "/account/base/driver/driverLoginByOtp"
    EP_DRIVER_QUERY_CAPTCHA = "/account/base/driver/queryCaptcha"
    EP_DRIVER_HOME_DATA = "/driver/api/driver/queryHomeData"
    EP_DRIVER_ONLINE = "/driver/api/v2/online"
    EP_DRIVER_WALLET_STATUS = "/account/api/ecgo/wallet/status"

    # --------------------------------------------------------------------------
    # Passenger / User Mobile Endpoints (Golang Stack)
    # --------------------------------------------------------------------------
    USER_PHONE: str = os.getenv("TEST_USER_PHONE", "0812XXXXXXXX")
    USER_OTP: str = os.getenv("TEST_USER_OTP", "****")

    EP_USER_QUERY_CAPTCHA = "/account/base/user/queryCaptcha"
    EP_USER_LOGIN_OTP = "/account/base/user/userLoginByOtp"
    EP_USER_PROFILE = "/user/api/user/queryInfo"
    EP_USER_ESTIMATE_FARE = "/order/api/user/estimateFare"
    EP_USER_CREATE_ORDER = "/order/api/user/createOrder"
    EP_USER_CANCEL_ORDER = "/order/api/user/cancelOrder"

    # --------------------------------------------------------------------------
    # ECGO SuperApps Endpoints (Node.js / Express Stack)
    # --------------------------------------------------------------------------
    EP_ECGO_GENERATE_OTP = "/v5/users/onboarding/generateOtp/sms"
    EP_ECGO_VERIFY_OTP = "/v5/users/onboarding/verifyOtp"
    EP_ECGO_CONNECT_STATUS = "/v5/users/evmoto-connect/status"
    EP_ECGO_CONNECT_START = "/v5/users/evmoto-connect/start"
    EP_ECGO_DISCOUNTS = "/v5/users/diskon/list"


