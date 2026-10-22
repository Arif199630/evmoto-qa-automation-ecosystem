"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - PYTEST FIXTURES & HOOKS
================================================================================
Menyediakan fixtures untuk inisialisasi Appium Driver, otomatisasi perekaman
video layar (Live Demo MP4), dan auto-screenshot saat kegagalan pengujian.
================================================================================
"""
import os
import sys
import ssl
import types
import importlib.util
import urllib.request
import urllib.error
from pathlib import Path
import pytest

# Pastikan path modul terdaftar secara absolut di PYTHONPATH
CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parent
while not (ROOT_DIR / 'core').exists() and not (ROOT_DIR / 'pytest.ini').exists() and ROOT_DIR.parent != ROOT_DIR:
    ROOT_DIR = ROOT_DIR.parent

FRONTEND_DIR = ROOT_DIR / 'Frontend'
FEATURE_DIR = FRONTEND_DIR / 'Feature'
PAGES_DIR = FEATURE_DIR / 'Pages'
DATA_DIR = FEATURE_DIR / 'Data'
STEP_DEF_DIR = FEATURE_DIR / 'Step_Definition'

for p in [str(ROOT_DIR), str(FRONTEND_DIR), str(FEATURE_DIR), str(PAGES_DIR), str(DATA_DIR), str(STEP_DEF_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

for mod_name, mod_dir in [
    ('pages', PAGES_DIR),
    ('Step_Definition', STEP_DEF_DIR)
]:
    if (mod_dir / '__init__.py').exists():
        spec = importlib.util.spec_from_file_location(mod_name, str(mod_dir / '__init__.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)

# Registrasi terpadu test_data & user_data (1 File dalam folder Data)
if 'test_data' not in sys.modules:
    import types
    _td_mod = types.ModuleType('test_data')
    _td_mod.__path__ = [str(DATA_DIR)]
    sys.modules['test_data'] = _td_mod

if (DATA_DIR / 'user_data.py').exists():
    spec = importlib.util.spec_from_file_location('test_data.user_data', str(DATA_DIR / 'user_data.py'))
    ud_mod = importlib.util.module_from_spec(spec)
    sys.modules['test_data.user_data'] = ud_mod
    sys.modules['test_data.auth_data'] = ud_mod
    sys.modules['test_data.profile_data'] = ud_mod
    sys.modules['user_data'] = ud_mod
    spec.loader.exec_module(ud_mod)
    for attr in dir(ud_mod):
        if not attr.startswith('__'):
            setattr(sys.modules['test_data'], attr, getattr(ud_mod, attr))

from core.driver_factory import DriverFactory
from utils.video_recorder import start_screen_recording, stop_and_save_recording
from utils.logger import get_logger
from config import config

logger = get_logger("Conftest")

def check_backend_server_status() -> tuple:
    """
    Memeriksa status kesehatan server development backend (api-dev.evmoto.internal).
    Returns (status_code, status_message).
    0 = OK / Online
    500 = Server mati / Internal Server Error
    502 = Server sedang restart / Bad Gateway
    503/504 = Service Unavailable / Gateway Timeout
    """
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        target_host = os.getenv("BACKEND_API_URL", "https://api-dev.evmoto.internal")
        req = urllib.request.Request(target_host, headers={"User-Agent": "Dart/3.5"})
        urllib.request.urlopen(req, context=ctx, timeout=3)
        return (200, "Online")
    except urllib.error.HTTPError as e:
        if e.code == 500:
            return (500, "Server mati / Internal Server Error (HTTP 500)")
        elif e.code == 502:
            return (502, "Server sedang restart / Bad Gateway (HTTP 502)")
        elif e.code in (503, 504):
            return (e.code, f"Server tidak tersedia / Gateway Timeout (HTTP {e.code})")
        return (e.code, f"HTTP Error {e.code}")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return (500, f"Koneksi server terputus / Server mati ({e})")
    except Exception as e:
        return (0, str(e))

@pytest.fixture(scope="function")
def driver(request):
    """
    Fixture utama untuk inisialisasi sesi Appium WebDriver pada setiap skenario test.
    Mendukung auto screen recording dan teardown yang bersih.
    Mendeteksi jika server mati (Error 500) dan memberikan warning langsung ke user.
    Membatalkan pengujian otomatis jika terdeteksi backend sedang restart (Error 502).
    """
    logger.info(f"=== [START TEST] {request.node.name} ===")

    # 1. Cek kesehatan server backend sebelum memulai pengujian
    status_code, status_msg = check_backend_server_status()
    
    if status_code == 500:
        warning_msg = (
            "\n" + "=" * 78 + "\n"
            "[PERINGATAN KRITIKAL: SERVER MATI (ERROR 500)]\n"
            "Server backend 'api-dev.evmoto.internal' MATI atau mengalami Internal Server Error!\n"
            "Automasi testing langsung dihentikan untuk menghindari kegagalan uji palsu.\n"
            "Silakan periksa atau hubungi tim Backend untuk menyalakan/memperbaiki server.\n"
            + "=" * 78
        )
        print(warning_msg)
        logger.error(warning_msg)
        try:
            from utils.lark_notifier import send_server_alert_to_lark
            send_server_alert_to_lark(500, status_msg)
        except Exception:
            pass
        pytest.skip(f"[WARNING: SERVER MATI] Terjadi Error 500 ({status_msg}). Automasi dibatalkan.")

    elif status_code == 502:
        logger.warning("[SERVER 502] Server development api-dev.evmoto.internal sedang direstart oleh developer.")
        try:
            from utils.lark_notifier import send_server_alert_to_lark
            send_server_alert_to_lark(502, status_msg)
        except Exception:
            pass
        pytest.skip("Developer sedang restart server (HTTP 502 Bad Gateway). Automasi testing dibatalkan sesuai instruksi.")

    elif status_code in (503, 504):
        logger.warning(f"[SERVER {status_code}] {status_msg}")
        try:
            from utils.lark_notifier import send_server_alert_to_lark
            send_server_alert_to_lark(status_code, status_msg)
        except Exception:
            pass
        pytest.skip(f"Server backend tidak responsif ({status_msg}). Automasi dibatalkan.")
    
    # Periksa apakah test meminta no_reset
    no_reset = "no_reset" in request.keywords
    driver_instance = DriverFactory.create_driver(no_reset=no_reset)
    
    # Simpan instance driver ke node agar dapat diakses oleh hook makereport
    request.node.driver = driver_instance

    # Mulai perekaman video hanya jika terdapat marker eksplisit 'record_video'
    is_video_enabled = "record_video" in request.keywords
    if is_video_enabled:
        start_screen_recording(driver_instance, time_limit=180)

    yield driver_instance

    # Teardown: Simpan video jika diaktifkan
    if is_video_enabled:
        video_filename = f"{request.node.name}.mp4"
        stop_and_save_recording(driver_instance, file_name=video_filename)

    logger.info(f"=== [TEARDOWN] Menutup sesi driver untuk {request.node.name} ===")
    try:
        driver_instance.quit()
    except Exception as e:
        logger.warning(f"Peringatan saat menutup driver: {e}")

@pytest.fixture(scope="function")
def driver_app(request):
    """
    Fixture khusus untuk inisialisasi sesi Appium WebDriver pada aplikasi EvMoto Driver
    (package: com.evmoto.driver.app, activity: com.evmoto.driver.app.MainActivity).
    """
    logger.info(f"=== [START DRIVER APP TEST] {request.node.name} ===")
    no_reset = "no_reset" in request.keywords
    driver_instance = DriverFactory.create_driver(no_reset=no_reset, is_driver_app=True)
    request.node.driver = driver_instance

    is_video_enabled = "record_video" in request.keywords
    if is_video_enabled:
        start_screen_recording(driver_instance, time_limit=180)

    yield driver_instance

    if is_video_enabled:
        video_filename = f"{request.node.name}.mp4"
        stop_and_save_recording(driver_instance, file_name=video_filename)

    logger.info(f"=== [TEARDOWN DRIVER APP] Menutup sesi driver untuk {request.node.name} ===")
    try:
        driver_instance.quit()
    except Exception as e:
        logger.warning(f"Peringatan saat menutup driver: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook bawaan Pytest:
    Secara otomatis mengambil tangkapan layar dan mengirimkan notifikasi Lark
    jika ada skenario yang GAGAL (FAILED).
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_instance = getattr(item, "driver", None)
        screenshot_path = None
        if driver_instance:
            target_dir = getattr(config, "SCREENSHOTS_DIR", getattr(config, "SCREENSHOTSDIR", None))
            screenshot_path = target_dir / f"{item.name}_FAILED.png" if target_dir else None
            try:
                if screenshot_path:
                    driver_instance.save_screenshot(str(screenshot_path))
                    logger.error(f"[TEST FAILED] Bukti screenshot otomatis disimpan di: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Gagal mengambil screenshot otomatis: {e}")

        # Sinkronisasi Otomatis ke Lark Group Chat
        try:
            from utils.lark_notifier import send_test_failure_to_lark
            docstring = getattr(item.function, "__doc__", "") or ""
            error_msg = str(call.excinfo.value) if call.excinfo else "Test Assertion Failure"
            send_test_failure_to_lark(
                test_name=item.name,
                docstring=docstring,
                error_message=error_msg,
                screenshot_path=str(screenshot_path) if screenshot_path else None
            )
        except Exception as e:
            logger.warning(f"[LarkAutoSync] Gagal memicu notifikasi Lark: {e}")