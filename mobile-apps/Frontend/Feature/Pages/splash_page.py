"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - SPLASH & ONBOARDING PAGE
================================================================================
"""
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage

class SplashPage(BasePage):
    """Page Object untuk Splash Screen & Layar Onboarding Awal EvMoto."""

    # Locators Elemen ID / XPath untuk Splash Screen & Onboarding
    SPLASH_LOGO = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Evmoto') or contains(@text, 'Evmoto')]")
    BTN_GET_STARTED = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Mulai') or contains(@content-desc, 'Get Started') or contains(@text, 'Mulai')]")
    BTN_SKIP = (AppiumBy.XPATH, "//*[contains(@content-desc, 'Lewati') or contains(@content-desc, 'Skip')]")

    def wait_until_loaded(self):
        """Menunggu splash screen selesai memuat."""
        self.pause(2.0, 3.0, "Memuat splash screen EvMoto")
        return self.is_displayed(self.SPLASH_LOGO, timeout=15)

    def click_get_started(self):
        """Menekan tombol Mulai / Get Started."""
        return self.click(self.BTN_GET_STARTED, label="Tombol Mulai / Get Started")


# Backward compatibility alias
SplashLocators = SplashPage


