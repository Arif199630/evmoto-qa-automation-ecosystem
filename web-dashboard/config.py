"""
Global Configuration & Dynamic URL Manager & WebDriver Helper
Automation Project EvMoto
"""

import os
import sys
import types
import glob
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Dynamic path resolution & module mapping for unified Frontend architecture
_ROOT = Path(__file__).resolve().parent
_FRONTEND = _ROOT / "Frontend"
_FEATURE = _FRONTEND / "Feature"
_STEP_DEF = _FEATURE / "Step_Definition"
_PAGES = _FEATURE / "Pages"
_DATA = _FEATURE / "Data"

for _p in [str(_ROOT), str(_FRONTEND), str(_FEATURE), str(_STEP_DEF), str(_PAGES), str(_DATA)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

for _name, _p in [("pages", _PAGES), ("locators", _PAGES), ("test_data", _DATA), ("tests", _STEP_DEF), ("Step_Definition", _STEP_DEF)]:
    if _name not in sys.modules:
        _m = types.ModuleType(_name)
        _m.__path__ = [str(_p)]
        sys.modules[_name] = _m



def _load_env_file():
    """
    Membaca file .env jika tersedia di root folder project
    agar konfigurasi dinamis dapat dibaca tanpa third-party library tambahan.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_paths = [
        os.path.join(current_dir, ".env"),
        os.path.join(os.path.dirname(current_dir), ".env"),
    ]
    for env_path in env_paths:
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                                v = v[1:-1]
                            if k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass


_load_env_file()


class DynamicURL:
    """
    Descriptor yang mengembalikan URL lengkap secara dinamis berdasarkan
    BASE_URL aktif di Config saat runtime.
    """

    def __init__(self, path: str):
        self.path = path

    def __get__(self, instance, owner=None) -> str:
        target_cls = owner if owner is not None else (type(instance) if instance is not None else Config)
        return target_cls.get_url(self.path)


class ConfigMeta(type):
    """
    Metaclass untuk memungkinkan akses dan mutasi Config.BASE_URL, Config.VALID_USER,
    Config.VALID_PASS secara dinamis tanpa hardcode:
    - Membaca Config.BASE_URL akan selalu mengembalikan BASE_URL aktif saat ini.
    - Membaca Config.VALID_USER / Config.VALID_PASS mengembalikan kredensial sesuai environment aktif.
    """

    @property
    def BASE_URL(cls) -> str:
        return cls.get_base_url()

    @BASE_URL.setter
    def BASE_URL(cls, value: str):
        cls.set_base_url(value)

    @property
    def VALID_USER(cls) -> str:
        return cls.get_valid_user()

    @property
    def VALID_PASS(cls) -> str:
        return cls.get_valid_pass()

    @property
    def ENVIRONMENT(cls) -> str:
        return cls.get_environment()


class Config(metaclass=ConfigMeta):
    """
    Konfigurasi Global & Pengelola URL Dinamis EvMoto Automation.

    Fleksibilitas Pemanggilan Link Website & Kredensial:
    1. Melalui Environment Variable:
       - ENVIRONMENT=dev atau ENVIRONMENT=production
       - DEV_BASE_URL / DEV_USER / DEV_PASS
       - PROD_BASE_URL / PROD_USER / PROD_PASS
    2. Override Langsung (Prioritas Tertinggi):
       - BASE_URL / VALID_USER / VALID_PASS
    3. Melalui Runtime Python Method:
       - Config.set_base_url("http://localhost:3000")
       - Config.set_environment("dev")
    """

    DEFAULT_BASE_URL = os.getenv("EVMOTO_ADMIN_PORTAL_URL", "https://admin-staging.evmoto.internal")

    # Pemetaan URL default per Environment (Masked Internal Domains)
    ENV_BASE_URLS = {
        "production": "https://admin.evmoto.internal",
        "prod": "https://admin.evmoto.internal",
        "staging": "https://admin-staging.evmoto.internal",
        "dev": "https://admin-dev.evmoto.internal",
        "development": "https://admin-dev.evmoto.internal",
        "qa": "https://admin-qa.evmoto.internal",
        "local": "http://localhost:3000",
        "localhost": "http://localhost:3000",
    }

    _custom_base_url = None

    @classmethod
    def get_environment(cls) -> str:
        """Mendapatkan nama environment aktif (default: 'staging')."""
        return os.getenv("ENVIRONMENT", "staging").strip().lower()

    @classmethod
    def get_valid_user(cls) -> str:
        """Mendapatkan username login sesuai environment aktif tanpa hardcode."""
        explicit = os.getenv("VALID_USER")
        if explicit and explicit.strip():
            return explicit.strip()
        env_name = cls.get_environment()
        if env_name in ("dev", "development"):
            return os.getenv("DEV_USER", "admin_dev").strip()
        return os.getenv("PROD_USER", "admin_qa").strip()

    @classmethod
    def get_valid_pass(cls) -> str:
        """Mendapatkan password login sesuai environment aktif tanpa hardcode."""
        explicit = os.getenv("VALID_PASS")
        if explicit and explicit.strip():
            return explicit.strip()
        env_name = cls.get_environment()
        if env_name in ("dev", "development"):
            return os.getenv("DEV_PASS", "********").strip()
        return os.getenv("PROD_PASS", "********").strip()

    @classmethod
    def get_base_url(cls) -> str:
        """
        Mendapatkan BASE_URL aktif secara dinamis dengan urutan prioritas:
        1. Custom override runtime (Config.set_base_url)
        2. Environment variable: BASE_URL / EVMOTO_BASE_URL / APP_URL
        3. Environment variable per environment: DEV_BASE_URL (jika dev) / PROD_BASE_URL (jika prod)
        4. Environment preset: ENVIRONMENT (production, staging, dev, qa, local)
        5. Default: https://admin-staging.evmoto.internal
        """
        if cls._custom_base_url:
            return cls._custom_base_url.rstrip("/")

        explicit_base = os.getenv("BASE_URL") or os.getenv("EVMOTO_BASE_URL") or os.getenv("APP_URL")
        if explicit_base and explicit_base.strip():
            return explicit_base.strip().rstrip("/")

        env_name = cls.get_environment()
        if env_name in ("dev", "development"):
            dev_url = os.getenv("DEV_BASE_URL")
            if dev_url and dev_url.strip():
                return dev_url.strip().rstrip("/")
        elif env_name in ("prod", "production"):
            prod_url = os.getenv("PROD_BASE_URL")
            if prod_url and prod_url.strip():
                return prod_url.strip().rstrip("/")

        if env_name in cls.ENV_BASE_URLS:
            return cls.ENV_BASE_URLS[env_name].rstrip("/")

        return cls.DEFAULT_BASE_URL.rstrip("/")

    @classmethod
    def set_base_url(cls, url: str):
        """Mengatur BASE_URL secara dinamis saat runtime."""
        if url:
            cls._custom_base_url = str(url).strip().rstrip("/")
        else:
            cls._custom_base_url = None

    @classmethod
    def set_environment(cls, env_name: str):
        """Mengalihkan environment target secara instan (cth: 'dev', 'production')."""
        env_key = str(env_name).strip().lower()
        if env_key in cls.ENV_BASE_URLS:
            cls.set_base_url(cls.ENV_BASE_URLS[env_key])
        else:
            raise ValueError(f"Environment '{env_name}' tidak dikenal. Pilihan: {list(cls.ENV_BASE_URLS.keys())}")

    @classmethod
    def reset_base_url(cls):
        """Mereset override base URL kembali ke setting default / env var."""
        cls._custom_base_url = None

    @classmethod
    def get_url(cls, path: str = "") -> str:
        """
        Membangun URL lengkap dari path atau URL relatif secara dinamis.
        Contoh:
          Config.get_url("/login") -> "https://admin-staging.evmoto.internal/login"
          Config.get_url("https://example.com/custom") -> "https://example.com/custom"
        """
        if not path:
            return cls.get_base_url()

        path_str = str(path).strip()
        if path_str.startswith("http://") or path_str.startswith("https://"):
            return path_str

        if not path_str.startswith("/"):
            path_str = "/" + path_str

        return f"{cls.get_base_url()}{path_str}"

    # =========================================================================
    # BACKEND API ENDPOINTS (JAVA & GOLANG)
    # =========================================================================
    JAVA_DEV_API_URL        = os.getenv("JAVA_DEV_API_URL", "https://dev-api.evmoto.internal")
    JAVA_PROD_API_URL       = os.getenv("JAVA_PROD_API_URL", "https://api.evmoto.internal")
    GOLANG_DEV_API_IP       = os.getenv("GOLANG_DEV_API_IP", "http://10.0.0.10")
    GOLANG_DEV_API_DOMAIN   = os.getenv("EVMOTO_API_BASE_URL", "https://api-dev.evmoto.internal")
    GOLANG_DEV_API_URL      = os.getenv("EVMOTO_API_BASE_URL", "https://api-dev.evmoto.internal")
    GOLANG_PROD_API_URL     = os.getenv("GOLANG_PROD_API_URL", "https://new-api.evmoto.internal")

    BACKEND_API_MAP = {
        "java_dev": JAVA_DEV_API_URL,
        "dev_java": JAVA_DEV_API_URL,
        "java_prod": JAVA_PROD_API_URL,
        "prod_java": JAVA_PROD_API_URL,
        "golang_dev": GOLANG_DEV_API_URL,
        "dev_golang": GOLANG_DEV_API_URL,
        "golang_dev_ip": GOLANG_DEV_API_IP,
        "golang_prod": GOLANG_PROD_API_URL,
        "prod_golang": GOLANG_PROD_API_URL,
    }

    @classmethod
    def get_backend_api_url(cls, backend: str = "golang", env: str = None) -> str:
        """
        Mendapatkan endpoint URL API backend (Java / Golang) untuk kebutuhan integrasi
        atau verifikasi API dashboard.
        """
        env_val = (env or cls.get_environment()).strip().lower()
        backend_val = str(backend).strip().lower()
        if env_val in ("prod", "production"):
            return cls.GOLANG_PROD_API_URL if backend_val == "golang" else cls.JAVA_PROD_API_URL
        else:
            return cls.GOLANG_DEV_API_URL if backend_val == "golang" else cls.JAVA_DEV_API_URL

    # =========================================================================
    # URL DEFINITIONS (Dinamis terhubung dengan Config.BASE_URL)
    # =========================================================================
    LOGIN_URL               = DynamicURL("/login")
    HOME_URL                = DynamicURL("/blackboard")
    USER_EXIT_URL           = DynamicURL("/userExit")

    # System Management URLs
    MGR_URL                 = DynamicURL("/mgr")                   # Platform Administrator
    ROLE_URL                = DynamicURL("/role")                  # Role Management
    MENU_URL                = DynamicURL("/menu")                  # Menu Management
    DEPT_URL                = DynamicURL("/dept")                  # Divisional Management

    # Enterprise URLs
    COMPANY_INFO_URL        = DynamicURL("/tCompany/admin_update") # Enterprise Information
    COMPANY_AUDIT_URL       = DynamicURL("/tCompany/auditPage")    # Enterprise Audit List

    # User Management URL
    USER_MGMT_URL           = DynamicURL("/tUser")                 # User Management

    # Basic Information / Agreement URLs
    AGREEMENT_BASE_URL      = DynamicURL("/tAgreement")
    LOGISTICS_URL           = DynamicURL("/tAgreement/showSmallPieceLogistics")
    ORDER_AGREEMENT_URL     = DynamicURL("/tAgreement/order")
    USER_GUIDE_URL          = DynamicURL("/tAgreement/user")
    LAW_URL                 = DynamicURL("/tAgreement/law")
    ABOUT_URL               = DynamicURL("/tAgreement/me")

    # Opening Up Urban Management URLs
    OPEN_CITY_URL           = DynamicURL("/tOpenCity")             # Urban Management
    HOT_ADDRESS_URL         = DynamicURL("/THotAddress")           # City Search Address Settings
    SERVICE_AREA_URL        = DynamicURL("/service-area")          # Service Area (Link in sidebar)

    # Driver Management URLs
    DRIVER_WITHHOLDING_URL  = DynamicURL("/tDriver/without")       # Driver Withholding Details
    DRIVER_AUDIT_URL        = DynamicURL("/tDriver")               # Driver Audit List
    DRIVER_VERIFY_URL       = DynamicURL("/tDriverVerify")         # Driver Replacement Vehicle Audit List
    DRIVER_LIST_URL         = DynamicURL("/tDriver/yesDriver")     # Drivers' List

    # Vehicle Management URLs
    CAR_BRAND_URL           = DynamicURL("/tCarBrand")             # Vehicle Brand Management
    CAR_MODEL_URL           = DynamicURL("/tCarModel")             # Vehicle Type Management
    CAR_LIST_URL            = DynamicURL("/tCar")                  # Vehicle Management
    MOTOR_MODEL_URL         = DynamicURL("/tMotorModel")           # Motorcycle Model Setting
    MOTOR_MODEL_ADD_URL     = DynamicURL("/tMotorModel/tMotorModel_add") # Add Motorcycle Model Sub-Page

    # Branch & Franchisee Management URLs
    BRANCH_URL              = DynamicURL("/tCompany")              # Branch Management
    FRANCHISEE_URL          = DynamicURL("/tCompany/franchisee")   # Franchisee Management

    # Travel Order Management URLs
    ORDER_MOTORCYCLE_URL    = DynamicURL("/tOrderPrivateCar")      # Motorcycle Orders
    ORDER_LOGISTICS_URL     = DynamicURL("/tOrderLogistics")       # City Express Orders

    # App Management URLs
    CHAT_SET_URL            = DynamicURL("/TChatSet")              # Chat Message Preset Settings
    ICON_MGMT_URL           = DynamicURL("/tbBanner")              # Icon Management
    VOICE_BROADCAST_URL     = DynamicURL("/TVoice")                # Voice Broadcast Management

    # Withdrawal Management URLs
    PUB_WITHDRAWAL_URL      = DynamicURL("/tPubWithdrawal")        # Withdrawal List
    WITHDRAWAL_CONFIG_URL   = DynamicURL("/withdrawalConfig")      # Withdrawal Configuration

    # Comment Management URL
    COMMENT_URL             = DynamicURL("/tOrderEvaluate")        # Comment List Management

    # System Setup URLs
    SYS_REFORMIST_URL       = DynamicURL("/tSysReformist")         # System Setup (Points, Cancellation Fee, Hotline, Dispatch)
    USER_DEBT_UNBLOCK_URL   = DynamicURL("/userDebtUnblock")       # Unblock Cancellation Debt

    # Complaint Management URL
    COMPLAINT_URL           = DynamicURL("/tComplaint")            # Complaint List Management

    # Sensitive Word Management URLs
    SENSITIVE_WORDS_URL     = DynamicURL("/tSysSensitiveWords")    # Sensitive Word Management
    SENSITIVE_WORDS_ADD_URL = DynamicURL("/tSysSensitiveWords/tSysSensitiveWords_add") # Add Sensitive Word Sub-Page

    # Feedback Management URLs
    FEEDBACK_DRIVER_URL     = DynamicURL("/tFeedback")             # Driver Feedback Management
    FEEDBACK_USER_URL       = DynamicURL("/tFeedback/userFeedback") # User Feedback Management
    FEEDBACK_DETAIL_URL     = DynamicURL("/tFeedback/lookDetail/81/1") # Feedback Detail View Sub-Page

    # Version Management URLs
    VERSION_MGMT_URL        = DynamicURL("/tVersionManagement")    # Version Management
    VERSION_ADD_URL         = DynamicURL("/tVersionManagement/tVersionManagement_add") # Add Version Sub-Page
    VERSION_UPDATE_URL      = DynamicURL("/tVersionManagement/tVersionManagement_update/43") # Edit Version Sub-Page

    # Activity Management URLs
    ACTIVITY_DRIVER_URL      = DynamicURL("/driverActivity")
    ACTIVITY_DRIVER_ADD_URL  = DynamicURL("/driverActivity/driverActivity_add")
    ACTIVITY_GIFT_URL        = DynamicURL("/sysCouponActivity")
    ACTIVITY_GIFT_ADD_URL    = DynamicURL("/sysCouponActivity/sysCouponActivity_add")
    ACTIVITY_USER_URL        = DynamicURL("/userActivity")
    ACTIVITY_USER_ADD_URL    = DynamicURL("/userActivity/userActivity_add")
    ACTIVITY_LARGE_URL       = DynamicURL("/tUserLarge")
    ACTIVITY_LARGE_ADD_URL   = DynamicURL("/tUserLarge/tUserLarge_add")
    ACTIVITY_INCOME_RULE_URL = DynamicURL("/tEnsureIncomeRule")
    ACTIVITY_INCOME_ADD_URL  = DynamicURL("/tEnsureIncomeRule/tEnsureIncomeRule_add")
    ACTIVITY_DISTRIB_URL     = DynamicURL("/couponDistribution")
    ACTIVITY_DISTRIB_ADD_URL = DynamicURL("/couponDistribution/couponDistribution_add")
    ACTIVITY_USAGE_URL       = DynamicURL("/couponUsage")
    ACTIVITY_RECORD_URL      = DynamicURL("/sysCouponRecord")
    ACTIVITY_RECORD_ADD_URL  = DynamicURL("/sysCouponRecord/sysCouponRecord_add")

    # Price Control URLs
    PRICE_SPECIAL_URL       = DynamicURL("/tSystemPrice/special")
    PRICE_SMALL_URL         = DynamicURL("/tSystemPrice/small")
    PRICE_CHECK_URL         = DynamicURL("/tSystemPrice/check")
    PRICE_SPECIAL_ADD_URL   = DynamicURL("/tSystemPrice/tSystemPrice_add")

    # Execution Flags & Platform
    HEADLESS    = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")
    PLATFORM    = os.getenv("PLATFORM", "Website (Desktop)")

    active_driver = None

    @classmethod
    def get_driver(cls, headless: bool = None):
        """
        Membuat instance WebDriver Chrome.
        - headless=True  : Mode background tanpa tampilan jendela browser.
        - headless=False : Mode visual GUI (Chrome terbuka di layar dengan human pacing).
        """
        options = Options()
        use_headless = cls.HEADLESS if headless is None else headless
        if use_headless:
            options.add_argument("--headless=new")
        else:
            options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Cari chromedriver yang sudah di-cache lokal untuk menghindari eksekusi selenium-manager.exe
        driver_pattern = os.path.expanduser(r"~/.cache/selenium/chromedriver/win64/*/chromedriver.exe")
        cached_drivers = glob.glob(driver_pattern)
        if cached_drivers:
            service = Service(executable_path=sorted(cached_drivers)[-1])
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(3)
        cls.active_driver = driver
        return driver


# Pasang hook otomatis pencatatan bug saat konfigurasi diimpor
try:
    from utils.test_interceptor import install_bug_tracker_hook
    install_bug_tracker_hook()
except Exception:
    pass
