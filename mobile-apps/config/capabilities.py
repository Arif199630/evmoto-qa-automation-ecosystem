"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - DESIRED CAPABILITIES BUILDER
================================================================================
Membangun spesifikasi kemampuan perangkat (UiAutomator2Options) khusus
untuk aplikasi Flutter/Android EvMoto pada emulator Samsung Galaxy S25.
================================================================================
"""
from appium.options.android import UiAutomator2Options
from config import config

def get_capabilities(no_reset: bool = False, full_reset: bool = False, is_driver_app: bool = False) -> UiAutomator2Options:
    """
    Menghasilkan objek UiAutomator2Options siap pakai untuk Appium Driver (User App atau Driver App).
    
    :param no_reset: Jika True, mempertahankan cache dan sesi login aplikasi.
    :param full_reset: Jika True, menghapus instalasi dan menginstal ulang APK.
    :param is_driver_app: Jika True, menargetkan aplikasi EvMoto Driver (com.evmoto.driver.app).
    :return: Objek UiAutomator2Options
    """
    options = UiAutomator2Options()
    options.platform_name = config.PLATFORM_NAME
    options.automation_name = config.AUTOMATION_NAME
    options.device_name = config.DEVICE_NAME
    if hasattr(config, "DEVICE_UDID") and config.DEVICE_UDID:
        options.udid = config.DEVICE_UDID

    # Target Activity pada Device (User App vs Driver App)
    if is_driver_app:
        options.app_package = getattr(config, "DRIVER_PACKAGE", "com.evmoto.driver.app")
        options.app_activity = getattr(config, "DRIVER_ACTIVITY", "com.evmoto.driver.app.MainActivity")
    else:
        options.app_package = config.APP_PACKAGE
        options.app_activity = config.APP_ACTIVITY
    options.app_wait_activity = config.APP_WAIT_ACTIVITY
    options.app_wait_duration = config.SPLASH_WAIT_DURATION

    # Otomatis izinkan permission lokasi, notifikasi, dll
    options.auto_grant_permissions = True

    # Biarkan Appium menginstal UiAutomator2 Server yang kompatibel secara otomatis
    options.skip_server_installation = False

    # Reset strategy
    options.no_reset = no_reset
    options.full_reset = full_reset

    # Stabilitas & Optimasi Performa UiAutomator2 (Bebas Lag)
    options.new_command_timeout = 300
    options.adb_exec_timeout = 60000
    options.uiautomator2_server_launch_timeout = 60000
    options.uiautomator2_server_install_timeout = 60000
    options.disable_window_animation = True
    options.ignore_unimportant_views = True

    return options
