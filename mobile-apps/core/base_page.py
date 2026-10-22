"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - BASE PAGE OBJECT
================================================================================
Kelas induk Page Object Model (POM).
Menyediakan method wrapper standar untuk explicit wait, interaksi elemen,
pemberian log, scrolling, pengambilan screenshot, dan human-like pacing.
================================================================================
"""
import time
from typing import Tuple, List
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import config
from utils.logger import get_logger
from utils.human_pacing import human_click, human_type, human_pause

logger = get_logger("BasePage")

class BasePage:
    """Base class untuk seluruh halaman aplikasi EvMoto (POM Pattern)."""

    def __init__(self, driver, timeout: int = config.DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def find(self, locator: Tuple[str, str], timeout: int = None):
        """Menemukan satu elemen dengan Explicit Wait."""
        t = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            self.check_for_server_errors()
            logger.error(f"Elemen dengan locator {locator} tidak ditemukan dalam {t} detik.")
            raise

    def find_all(self, locator: Tuple[str, str], timeout: int = 5) -> List:
        """Menemukan seluruh elemen yang cocok dengan locator."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def click(self, locator: Tuple[str, str], label: str = "", use_human_pacing: bool = True):
        """Menunggu elemen clickable kemudian melakukan klik."""
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(locator)
            )
            if use_human_pacing:
                human_click(self.driver, element, label=label or str(locator[1]))
            else:
                logger.info(f"Klik: {label or locator[1]}")
                element.click()
            return element
        except Exception as e:
            self.check_for_server_errors()
            logger.error(f"Gagal melakukan klik pada {label or locator}: {e}")
            raise

    def type_text(self, locator: Tuple[str, str], text: str, label: str = "", use_human_pacing: bool = True):
        """Mengetik teks pada field input."""
        element = self.find(locator)
        if use_human_pacing:
            human_type(self.driver, element, text, label=label or str(locator[1]))
        else:
            logger.info(f"Input '{text}' ke: {label or locator[1]}")
            element.clear()
            element.send_keys(text)
        return element

    def get_text(self, locator: Tuple[str, str]) -> str:
        """Mengambil teks atau content-desc dari elemen."""
        element = self.find(locator)
        desc = element.get_attribute("content-desc")
        text = element.get_attribute("text")
        return desc or text or ""

    def is_displayed(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """Memeriksa apakah elemen tampil di layar."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def pause(self, min_sec: float = 3.0, max_sec: float = 3.0, message: str = ""):
        """Melakukan jeda deliberasi manusia (default 3 detik)."""
        human_pause(min_sec, max_sec, message)

    def take_screenshot(self, name: str) -> str:
        """Mengambil screenshot dan menyimpannya di folder reports/screenshots."""
        file_path = config.SCREENSHOTS_DIR / f"{name}.png"
        self.driver.save_screenshot(str(file_path))
        logger.info(f"Screenshot tersimpan: {file_path}")
        return str(file_path)

    def check_for_server_errors(self):
        """
        Memeriksa apakah layar aplikasi menampilkan pesan kesalahan server (500/502).
        Jika ditemukan, langsung memberikan warning tegas dan membatalkan pengujian.
        """
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            import pytest
            # Deteksi Error 500 / Server Mati
            err_500 = self.driver.find_elements(AppiumBy.XPATH, "//*[contains(@content-desc, '500') or contains(@content-desc, 'Internal Server') or contains(@text, '500')]")
            if err_500:
                warning_banner = (
                    "\n" + "=" * 78 + "\n"
                    "[PERINGATAN KRITIKAL: SERVER MATI (ERROR 500 DARI APLIKASI)]\n"
                    "Layar aplikasi mendeteksi Server Error 500 (Internal Server Error)!\n"
                    "Automasi testing langsung dihentikan karena server backend sedang mati / down.\n"
                    + "=" * 78
                )
                print(warning_banner)
                logger.error(warning_banner)
                pytest.skip("[WARNING: SERVER MATI] Terdeteksi Error 500 pada aplikasi. Testing dibatalkan.")

            # Deteksi Error 502 / Server Restart
            err_502 = self.driver.find_elements(AppiumBy.XPATH, "//*[contains(@content-desc, '502') or contains(@text, '502')]")
            if err_502:
                logger.warning("[SERVER 502] Layar aplikasi menampilkan 'Server error (502)'. Developer sedang restart server.")
                pytest.skip("Developer sedang restart server (HTTP 502 Bad Gateway terdeteksi di aplikasi). Testing dibatalkan.")
        except Exception:
            pass
