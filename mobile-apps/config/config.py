"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - CENTRAL CONFIGURATION
================================================================================
Menyimpan seluruh konfigurasi global environment, URL Appium server, target APK,
kemampuan perangkat (Desired Capabilities), dan direktori output laporan.
================================================================================
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
VIDEOS_DIR = REPORTS_DIR / "videos"

# Load Environment Variables from .env file
load_dotenv(PROJECT_ROOT / ".env")

# Akun User per emulator (CI paralel): aplikasi hanya mengizinkan 1 perangkat login per akun, jadi emulator
# yang memakai akun sama saling memutus sesi ("Anda sedang Login di perangkat lain").
# TEST_USER_POOL_PREFIX + nomor emulator (2 digit) = nomor akun QA Auto yang didaftarkan di staging.
_pool_prefix = os.getenv("TEST_USER_POOL_PREFIX", "")
_pool_index = int(os.getenv("TEST_USER_POOL_INDEX", "-1") or -1)
if _pool_prefix and _pool_index >= 2:
    _pool_phone = f"{_pool_prefix}{_pool_index:02d}"
    for _key in ("TEST_USER_PHONE", "DEV_PHONE", "ACTIVE_PHONE", "EVMOTO_DEV_PHONE"):
        os.environ[_key] = _pool_phone

# Ensure directories exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Import Backend Endpoints (Java & Golang)
from .endpoints import BackendEndpoints, get_backend_url


# Lark Suite Notifier Configuration
LARK_WEBHOOK_URL = os.getenv("LARK_WEBHOOK_URL", "")

# Appium Server Configuration
APPIUM_HOST = os.getenv("APPIUM_HOST", "127.0.0.1")
APPIUM_PORT = int(os.getenv("APPIUM_PORT", "4723"))
APPIUM_SERVER_URL = f"http://{APPIUM_HOST}:{APPIUM_PORT}"

# Active Environment (dev | production / prod)
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev").strip().lower()

# Target Mobile App Presets (Dev vs Production)
_user_apk_default = PROJECT_ROOT.parent / "apps" / "UserApps.apk"
_user_apk_legacy = PROJECT_ROOT.parent / "apps" / "evmoto-user-1.2.33-env-dev_golang-20261020-v8a.apk"
_user_apk_resolved = str(_user_apk_default if _user_apk_default.exists() else _user_apk_legacy)

DEV_EVMOTO_USER_APK = os.getenv("DEV_EVMOTO_USER_APK", _user_apk_resolved)
PROD_EVMOTO_USER_APK = os.getenv("PROD_EVMOTO_USER_APK", _user_apk_resolved)

# Resolusi APK Aktif Dinamis
if os.getenv("EVMOTO_USER_APK"):
    APK_PATH = os.getenv("EVMOTO_USER_APK")
elif ENVIRONMENT in ("prod", "production"):
    APK_PATH = PROD_EVMOTO_USER_APK
else:
    APK_PATH = DEV_EVMOTO_USER_APK

APP_PACKAGE = "com.evmoto.user.app"
APP_ACTIVITY = "com.evmoto.user.app.MainActivity"
APP_WAIT_ACTIVITY = "*"

# Konfigurasi Driver Mobile App
DRIVER_VERSION = "latest"
_driver_apk_latest = PROJECT_ROOT.parent / "apps" / "DriverApps.apk"
_driver_apk_legacy = PROJECT_ROOT.parent / "apps" / "evmoto-driver-1.9.27-env-dev_golang-20261020-v7a.apk"
_driver_apk_resolved = str(_driver_apk_latest if _driver_apk_latest.exists() else _driver_apk_legacy)

DEV_EVMOTO_DRIVER_APK = os.getenv("DEV_EVMOTO_DRIVER_APK", _driver_apk_resolved)
PROD_EVMOTO_DRIVER_APK = os.getenv("PROD_EVMOTO_DRIVER_APK", _driver_apk_resolved)

if os.getenv("EVMOTO_DRIVER_APK"):
    DRIVER_APK_PATH = os.getenv("EVMOTO_DRIVER_APK")
elif ENVIRONMENT in ("prod", "production"):
    DRIVER_APK_PATH = PROD_EVMOTO_DRIVER_APK
else:
    DRIVER_APK_PATH = DEV_EVMOTO_DRIVER_APK

DRIVER_PACKAGE = "com.evmoto.driver.app"
DRIVER_ACTIVITY = "com.evmoto.driver.app.MainActivity"
DRIVER_ACTIVE_PHONE = os.getenv("EVMOTO_DRIVER_PHONE", "")
DRIVER_ACTIVE_PIN = os.getenv("EVMOTO_DRIVER_PIN", os.environ.get("EVMOTO_OTP_BYPASS", ""))

# Kredensial Pengujian (Phone & OTP) Dev vs Production
DEV_PHONE = os.getenv("DEV_PHONE", os.getenv("EVMOTO_DEV_PHONE", ""))
DEV_OTP = os.getenv("DEV_OTP", os.getenv("EVMOTO_DEV_OTP", os.environ.get("EVMOTO_OTP_BYPASS", "")))

PROD_PHONE = os.getenv("PROD_PHONE", os.getenv("EVMOTO_PROD_PHONE", ""))
PROD_OTP = os.getenv("PROD_OTP", os.getenv("EVMOTO_PROD_OTP", os.environ.get("EVMOTO_OTP_BYPASS", "")))

if ENVIRONMENT in ("prod", "production"):
    ACTIVE_PHONE = os.getenv("ACTIVE_PHONE", PROD_PHONE)
    ACTIVE_OTP = os.getenv("ACTIVE_OTP", PROD_OTP)
else:
    ACTIVE_PHONE = os.getenv("ACTIVE_PHONE", DEV_PHONE)
    ACTIVE_OTP = os.getenv("ACTIVE_OTP", DEV_OTP)

# Target Device Configuration (Android Emulator Samsung Galaxy S25)
DEVICE_NAME = os.getenv("DEVICE_NAME", "Samsung_Galaxy_S25")
DEVICE_UDID = os.getenv("DEVICE_UDID", "")
PLATFORM_NAME = "Android"
AUTOMATION_NAME = "UiAutomator2"
EMULATOR_AVD = "Samsung_Galaxy_S25"

# Timeouts (dalam detik)
DEFAULT_TIMEOUT = 25
SPLASH_WAIT_DURATION = 25000  # milidetik untuk UiAutomator2 appWaitDuration
HUMAN_PACING_MIN = 3.0
HUMAN_PACING_MAX = 3.0


class Config:
    """Wrapper Class untuk kompatibilitas import OOP Config."""
    PROJECT_ROOT = PROJECT_ROOT
    REPORTS_DIR = REPORTS_DIR
    SCREENSHOTS_DIR = SCREENSHOTS_DIR
    VIDEOS_DIR = VIDEOS_DIR
    ENVIRONMENT = ENVIRONMENT
    APK_PATH = APK_PATH
    DEV_EVMOTO_USER_APK = DEV_EVMOTO_USER_APK
    PROD_EVMOTO_USER_APK = PROD_EVMOTO_USER_APK
    APP_PACKAGE = APP_PACKAGE
    APP_ACTIVITY = APP_ACTIVITY
    APP_WAIT_ACTIVITY = APP_WAIT_ACTIVITY
    DRIVER_APK_PATH = DRIVER_APK_PATH
    DRIVER_PACKAGE = DRIVER_PACKAGE
    DRIVER_ACTIVITY = DRIVER_ACTIVITY
    DRIVER_ACTIVE_PHONE = DRIVER_ACTIVE_PHONE
    DRIVER_ACTIVE_PIN = DRIVER_ACTIVE_PIN
    ACTIVE_PHONE = ACTIVE_PHONE
    ACTIVE_OTP = ACTIVE_OTP
    DEV_PHONE = DEV_PHONE
    DEV_OTP = DEV_OTP
    PROD_PHONE = PROD_PHONE
    PROD_OTP = PROD_OTP
    DEVICE_NAME = DEVICE_NAME
    APPIUM_SERVER_URL = APPIUM_SERVER_URL
    DEFAULT_TIMEOUT = DEFAULT_TIMEOUT
    SPLASH_WAIT_DURATION = SPLASH_WAIT_DURATION
    HUMAN_PACING_MIN = HUMAN_PACING_MIN
    HUMAN_PACING_MAX = HUMAN_PACING_MAX

    # Backend Endpoints
    JAVA_DEV_API_URL = BackendEndpoints.JAVA_DEV
    JAVA_PROD_API_URL = BackendEndpoints.JAVA_PROD
    GOLANG_DEV_API_IP = BackendEndpoints.GOLANG_DEV_IP
    GOLANG_DEV_API_DOMAIN = BackendEndpoints.GOLANG_DEV_DOMAIN
    GOLANG_DEV_API_URL = BackendEndpoints.GOLANG_DEV
    GOLANG_PROD_API_URL = BackendEndpoints.GOLANG_PROD
    BackendEndpoints = BackendEndpoints
    get_backend_url = staticmethod(get_backend_url)

