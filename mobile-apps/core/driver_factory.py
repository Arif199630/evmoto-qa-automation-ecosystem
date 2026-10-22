"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - DRIVER FACTORY
================================================================================
Bertanggung jawab atas inisialisasi, manajemen sesi, dan teardown
Appium WebDriver secara terisolasi dan aman.
================================================================================
"""
from appium import webdriver
from config import config
from config.capabilities import get_capabilities
from utils.logger import get_logger

logger = get_logger("DriverFactory")

class DriverFactory:
    """Factory class untuk pembuatan instance Appium WebDriver."""

    @staticmethod
    def create_driver(no_reset: bool = False, full_reset: bool = False, is_driver_app: bool = False) -> webdriver.Remote:
        """Membuat instance driver baru yang terhubung ke Appium Server."""
        logger.info(f"Menghubungkan ke Appium Server: {config.APPIUM_SERVER_URL}")
        options = get_capabilities(no_reset=no_reset, full_reset=full_reset, is_driver_app=is_driver_app)
        
        driver = webdriver.Remote(
            command_executor=config.APPIUM_SERVER_URL,
            options=options
        )
        target_pkg = getattr(config, "DRIVER_PACKAGE", "com.evmoto.driver.app") if is_driver_app else config.APP_PACKAGE
        logger.info(f"Driver berhasil diinisialisasi untuk package '{target_pkg}' pada '{config.DEVICE_NAME}'.")
        return driver

