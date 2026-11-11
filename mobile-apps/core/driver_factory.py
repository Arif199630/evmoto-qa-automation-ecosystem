"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - DRIVER FACTORY
================================================================================
Bertanggung jawab atas inisialisasi, manajemen sesi, dan teardown
Appium WebDriver secara terisolasi dan aman.
Mendukung fallback otomatis ke Headless Mobile Driver Simulator saat
Appium Server tidak aktif / lingkungan pengujian headless tanpa GUI.
================================================================================
"""
import os
import socket
from appium import webdriver
from config import config
from config.capabilities import get_capabilities
from utils.logger import get_logger
from core.headless_mobile_driver import HeadlessMobileDriver

logger = get_logger("DriverFactory")


class DriverFactory:
    """Factory class untuk pembuatan instance Appium WebDriver."""

    @staticmethod
    def _is_appium_listening(url: str, timeout: float = 0.8) -> bool:
        """Memeriksa secara cepat apakah port Appium aktif sebelum membuka sesi urllib3."""
        try:
            # url biasanya http://127.0.0.1:4723
            clean_url = url.replace("http://", "").replace("https://", "").split("/")[0]
            host, port = clean_url.split(":")
            with socket.create_connection((host, int(port)), timeout=timeout):
                return True
        except Exception:
            return False

    @staticmethod
    def create_driver(no_reset: bool = False, full_reset: bool = False, is_driver_app: bool = False):
        """
        Membuat instance driver baru.

        - HEADLESS_MOBILE=1 -> HeadlessMobileDriver (simulator). Hanya untuk mengecek kode test dan
          Page Object; hasilnya BUKAN bukti aplikasi berjalan benar.
        - Selain itu -> wajib terhubung ke Appium (emulator headless atau device). Bila Appium
          tidak aktif, test gagal dengan pesan jelas. Tidak ada lagi pindah diam-diam ke simulator,
          karena itu membuat test terlihat lulus tanpa aplikasi.
        """
        target_pkg = getattr(config, "DRIVER_PACKAGE", "com.evmoto.driver.app") if is_driver_app else config.APP_PACKAGE

        if os.getenv("HEADLESS_MOBILE", "0") == "1":
            logger.info(f"[SIMULATOR] HEADLESS_MOBILE=1, memakai HeadlessMobileDriver untuk '{target_pkg}'.")
            return HeadlessMobileDriver(is_driver_app=is_driver_app)

        server_url = getattr(config, "APPIUM_SERVER_URL", "http://127.0.0.1:4723")
        if not DriverFactory._is_appium_listening(server_url):
            raise RuntimeError(
                f"Appium tidak aktif di {server_url}. Jalankan emulator headless dan Appium "
                "(lihat scripts/start_headless_emulator.ps1), atau set HEADLESS_MOBILE=1 untuk mode simulator."
            )

        logger.info(f"Menghubungkan ke Appium Server: {server_url}")
        options = get_capabilities(no_reset=no_reset, full_reset=full_reset, is_driver_app=is_driver_app)
        driver = webdriver.Remote(command_executor=server_url, options=options)
        # Beranda User berisi peta (Google Maps) yang terus beranimasi; UiAutomator2 bawaan menunggu layar
        # "diam" sebelum mencari elemen / membaca page source sehingga bisa timeout (bukti CI: 240 detik).
        try:
            driver.update_settings({"waitForIdleTimeout": int(os.getenv("APPIUM_WAIT_FOR_IDLE_MS", "100"))})
        except Exception as e:
            logger.warning(f"Gagal mengatur waitForIdleTimeout: {e}")
        logger.info(f"Driver berhasil diinisialisasi untuk package '{target_pkg}' pada '{config.DEVICE_NAME}'.")
        return driver
