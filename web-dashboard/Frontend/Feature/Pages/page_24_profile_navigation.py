"""
Page Object: Profile & Top Navigation Component
Automation Project EvMoto
Target: Komponen Dropdown Profil di Pojok Kanan Atas Seluruh Halaman Dashboard
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.page_base import BasePage


class ProfilePage(BasePage):
    """
    Page Object yang merepresentasikan komponen Profil di pojok kanan atas
    navbar aplikasi EvMoto Dashboard (tersedia secara global di seluruh modul).
    """

    # --- Locators Utama Navbar & Profil ---
    PROFILE_MENU         = (By.CSS_SELECTOR, "[data-profile-menu]")
    PROFILE_TRIGGER      = (By.CSS_SELECTOR, "[data-profile-trigger]")
    PROFILE_AVATAR       = (By.CSS_SELECTOR, "[data-profile-trigger] img")
    PROFILE_COPY         = (By.CSS_SELECTOR, ".profile-trigger__copy")
    PROFILE_COPY_NAME    = (By.CSS_SELECTOR, ".profile-trigger__copy strong")
    PROFILE_COPY_ROLE    = (By.CSS_SELECTOR, ".profile-trigger__copy small")
    PROFILE_CHEVRON      = (By.CSS_SELECTOR, ".profile-chevron")

    # --- Locators Menu Dropdown ---
    PROFILE_DROPDOWN     = (By.CSS_SELECTOR, "[data-profile-dropdown]")
    PROFILE_HEADER       = (By.CSS_SELECTOR, ".profile-dropdown__header")
    PROFILE_HEADER_NAME  = (By.CSS_SELECTOR, ".profile-dropdown__header strong")
    PROFILE_HEADER_ROLE  = (By.CSS_SELECTOR, ".profile-dropdown__header small")
    PROFILE_DIVIDER      = (By.CSS_SELECTOR, ".profile-dropdown__divider")
    BTN_EDIT_PROFILE     = (By.CSS_SELECTOR, "[data-profile-edit]")
    BTN_EDIT_PASSWORD    = (By.CSS_SELECTOR, "[data-password-edit]")
    BTN_LOGOUT           = (By.CSS_SELECTOR, ".profile-dropdown__item.is-danger")
    LOGOUT_FORM          = (By.CSS_SELECTOR, "form[action='/logout']")
    TOAST                = (By.CSS_SELECTOR, "[data-toast]")
    BODY                 = (By.TAG_NAME, "body")

    def __init__(self, driver):
        super().__init__(driver)

    # --- Verifikasi Kehadiran Elemen ---
    def is_profile_trigger_visible(self):
        """Memverifikasi tombol trigger profil terlihat di pojok kanan atas."""
        return self.is_displayed(self.PROFILE_TRIGGER)

    def is_avatar_present(self):
        """Memverifikasi foto/ikon avatar profil hadir di navbar."""
        try:
            elem = self.find(self.PROFILE_AVATAR, timeout=4)
            return elem is not None
        except (TimeoutException, NoSuchElementException):
            return False

    def get_trigger_user_name(self):
        """Mengambil nama pengguna yang tertera pada trigger profil."""
        try:
            return self.get_text(self.PROFILE_COPY_NAME, timeout=3)
        except Exception:
            return ""

    def get_trigger_user_role(self):
        """Mengambil role pengguna yang tertera pada trigger profil."""
        try:
            return self.get_text(self.PROFILE_COPY_ROLE, timeout=3)
        except Exception:
            return ""

    # --- Interaksi Buka / Tutup Dropdown ---
    def click_profile_trigger(self):
        """Melakukan klik pada tombol trigger profil untuk toggle dropdown."""
        trigger = self.find(self.PROFILE_TRIGGER, timeout=5)
        self.driver.execute_script("arguments[0].click();", trigger)
        time.sleep(0.4)

    def is_dropdown_open(self):
        """Memeriksa apakah menu dropdown profil sedang terbuka (hidden=False/None)."""
        try:
            dropdown = self.find(self.PROFILE_DROPDOWN, timeout=3)
            hidden_attr = dropdown.get_attribute("hidden")
            return hidden_attr is None or hidden_attr is False or str(hidden_attr).lower() == "false"
        except (TimeoutException, NoSuchElementException):
            return False

    def get_trigger_aria_expanded(self):
        """Mengambil nilai atribut aria-expanded pada trigger profil."""
        try:
            return self.get_attribute(self.PROFILE_TRIGGER, "aria-expanded", timeout=3)
        except Exception:
            return "false"

    def get_dropdown_items_count(self):
        """Menghitung jumlah item tombol aksi yang ada di dalam dropdown profil."""
        items = self.find_all((By.CSS_SELECTOR, ".profile-dropdown__item"))
        return len(items)

    def get_dropdown_header_name(self):
        """Mengambil nama pengguna yang tertera di header dropdown."""
        try:
            return self.get_text(self.PROFILE_HEADER_NAME, timeout=3)
        except Exception:
            return ""

    def get_dropdown_header_role(self):
        """Mengambil role pengguna yang tertera di header dropdown."""
        try:
            return self.get_text(self.PROFILE_HEADER_ROLE, timeout=3)
        except Exception:
            return ""

    # --- Interaksi Tombol di Dalam Dropdown ---
    def click_edit_profile_btn(self):
        """Klik tombol 'Edit Profil' di dalam menu dropdown."""
        if not self.is_dropdown_open():
            self.click_profile_trigger()
        btn = self.find(self.BTN_EDIT_PROFILE, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.4)

    def click_edit_password_btn(self):
        """Klik tombol 'Edit Password' di dalam menu dropdown."""
        if not self.is_dropdown_open():
            self.click_profile_trigger()
        btn = self.find(self.BTN_EDIT_PASSWORD, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.4)

    def click_logout_btn(self):
        """Klik tombol 'Keluar' (Logout) di dalam menu dropdown."""
        if not self.is_dropdown_open():
            self.click_profile_trigger()
        btn = self.find(self.BTN_LOGOUT, timeout=4)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

    def get_toast_content(self):
        """Mengambil teks pesan toast yang muncul di antarmuka."""
        try:
            toast = self.find(self.TOAST, timeout=3)
            return toast.text.strip()
        except Exception:
            return ""

    def click_outside(self):
        """Melakukan klik di luar menu dropdown (misal pada tag body) untuk menutup menu."""
        try:
            body = self.find(self.BODY, timeout=3)
            self.driver.execute_script("document.body.click();")
            time.sleep(0.3)
        except Exception:
            pass

    def press_escape_key(self):
        """Mengirimkan tombol keyboard Escape untuk menutup dropdown profil."""
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.3)
        except Exception:
            pass
