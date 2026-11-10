"""
Base Page: Kelas Induk untuk Seluruh Page Object
Automation Project EvMoto
"""

import time
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Config


class BasePage:
    """Kelas dasar yang membungkus fungsi-fungsi umum WebDriver dan WebDriverWait."""

    def __init__(self, driver, wait_timeout=12):
        self.driver = driver
        self.wait_timeout = wait_timeout
        self.wait = WebDriverWait(self.driver, self.wait_timeout)

    def open(self, url_or_path=None):
        """
        Buka URL tertentu atau relative path secara dinamis.
        - None                       : Membuka BASE_URL aktif dari Config.
        - 'http://...' / 'https://...': Membuka full URL langsung.
        - '/path' atau 'path'        : Membuka relative path yang digabung secara dinamis dengan BASE_URL aktif.
        """
        if url_or_path is None:
            target_url = Config.get_base_url()
        elif str(url_or_path).startswith("http://") or str(url_or_path).startswith("https://"):
            target_url = str(url_or_path)
        else:
            target_url = Config.get_url(str(url_or_path))
        self.driver.get(target_url)

    def get_url(self, path=""):
        """Mendapatkan full URL dinamis untuk path tertentu berdasarkan konfigurasi aktif."""
        return Config.get_url(path)

    def open_path(self, path):
        """Helper untuk membuka relative path langsung."""
        self.open(path)

    def get_current_url(self):
        """Mendapatkan URL browser saat ini."""
        return self.driver.current_url

    def get_title(self):
        """Mendapatkan judul halaman (title tag)."""
        return self.driver.title

    def get_page_source(self):
        """Mendapatkan seluruh HTML page source."""
        return self.driver.page_source

    def find(self, locator, timeout=None):
        """Mencari satu elemen dengan explicit wait sampai muncul di DOM."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator, timeout=None):
        """Mencari satu elemen sampai terlihat (visible) di layar."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        """Mencari seluruh elemen yang cocok dengan locator (list)."""
        return self.driver.find_elements(*locator)

    def get_first_row_value(self, header_keyword):
        """Teks sel pada baris pertama tabel, di kolom yang judulnya memuat header_keyword.

        Dipakai test pencarian agar kata kunci diambil dari data yang benar-benar ada di
        environment aktif (dev/staging), bukan nilai tetap dari production.
        Mengembalikan "" bila tabel kosong atau kolom tidak ditemukan.
        """
        headers = [h.text.strip().upper() for h in self.driver.find_elements("css selector", "table thead th")]
        index = next((i for i, h in enumerate(headers) if header_keyword.upper() in h), None)
        rows = self.driver.find_elements("css selector", "table tbody tr")
        if index is None or not rows:
            return ""
        cells = rows[0].find_elements("css selector", "td")
        return cells[index].text.strip() if index < len(cells) else ""

    def click(self, locator, timeout=None):
        """Menunggu elemen clickable lalu melakukan klik standar."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return element

    def click_js(self, locator_or_element):
        """Klik elemen menggunakan JavaScript (andal untuk tombol terhalang/tersembunyi)."""
        if isinstance(locator_or_element, tuple):
            element = self.find(locator_or_element)
        else:
            element = locator_or_element
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def type_text(self, locator, text, clear_first=True):
        """Mengetik teks pada field input setelah elemen terlihat."""
        element = self.find_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        return element

    def set_value_js(self, locator_or_element, value):
        """Mengatur nilai input field menggunakan JavaScript (berguna untuk input date/hidden)."""
        if isinstance(locator_or_element, tuple):
            element = self.find(locator_or_element)
        else:
            element = locator_or_element
        self.driver.execute_script(f"arguments[0].value = '{value}';", element)
        return element

    def dispatch_event(self, locator_or_element, event_name="change"):
        """Memicu browser event (change/input) via JavaScript."""
        if isinstance(locator_or_element, tuple):
            element = self.find(locator_or_element)
        else:
            element = locator_or_element
        self.driver.execute_script(f"arguments[0].dispatchEvent(new Event('{event_name}', {{bubbles: true}}));", element)
        return element

    def get_text(self, locator, timeout=None):
        """Mengambil teks dari elemen."""
        element = self.find_visible(locator, timeout=timeout)
        return element.text.strip()

    def get_attribute(self, locator, attr_name, timeout=None):
        """Mengambil nilai atribut dari elemen."""
        element = self.find(locator, timeout=timeout)
        return element.get_attribute(attr_name)

    def is_displayed(self, locator, timeout=3):
        """Memeriksa apakah elemen terlihat di halaman."""
        try:
            return self.find_visible(locator, timeout=timeout).is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def is_enabled(self, locator, timeout=3):
        """Memeriksa apakah elemen dalam status enabled (aktif)."""
        try:
            return self.find(locator, timeout=timeout).is_enabled()
        except (TimeoutException, NoSuchElementException):
            return False

    def select_dropdown_by_value(self, locator, value):
        """Memilih opsi dropdown select berdasarkan value."""
        element = self.find_visible(locator)
        select = Select(element)
        select.select_by_value(str(value))
        return select

    def wait_for_url_contains(self, fragment, timeout=None):
        """Menunggu sampai URL browser memuat fragmen string tertentu."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.url_contains(fragment))

    def wait_for_title_contains(self, fragment, timeout=None):
        """Menunggu sampai title browser memuat string tertentu."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.title_contains(fragment))

    def get_cookies(self):
        """Mengambil seluruh cookies sesi browser saat ini."""
        return self.driver.get_cookies()

    def set_window_size(self, width, height):
        """Mengatur ukuran viewport jendela browser (responsivitas)."""
        self.driver.set_window_size(width, height)

    def refresh_page(self):
        """Me-refresh / reload halaman browser saat ini."""
        self.driver.refresh()

    def navigate_back(self):
        """Melakukan simulasi klik tombol Back pada browser."""
        self.driver.back()

    # =========================================================================
    # NAVIGASI & INTERAKSI PROFIL DROPDOWN (GLOBAL TOP NAVIGATION BAR)
    # =========================================================================

    def is_profile_trigger_present(self):
        """Memeriksa kehadiran tombol profil di pojok kanan atas."""
        try:
            from selenium.webdriver.common.by import By
            elems = self.find_all((By.CSS_SELECTOR, "[data-profile-trigger], .profile-trigger"))
            return len(elems) > 0
        except Exception:
            return False

    def open_profile_dropdown(self):
        """Membuka dropdown menu profil di pojok kanan atas."""
        from selenium.webdriver.common.by import By
        trigger = self.find((By.CSS_SELECTOR, "[data-profile-trigger], .profile-trigger"), timeout=5)
        self.driver.execute_script("arguments[0].click();", trigger)
        time.sleep(0.4)

    def close_profile_dropdown(self):
        """Menutup dropdown menu profil."""
        from selenium.webdriver.common.by import By
        try:
            dropdown = self.find((By.CSS_SELECTOR, "[data-profile-dropdown], .profile-dropdown"), timeout=2)
            if dropdown.get_attribute("hidden") is None:
                trigger = self.find((By.CSS_SELECTOR, "[data-profile-trigger], .profile-trigger"), timeout=2)
                self.driver.execute_script("arguments[0].click();", trigger)
                time.sleep(0.3)
        except Exception:
            pass

    def is_profile_dropdown_open(self):
        """Memeriksa apakah dropdown profil dalam kondisi terbuka."""
        from selenium.webdriver.common.by import By
        try:
            dropdown = self.find((By.CSS_SELECTOR, "[data-profile-dropdown], .profile-dropdown"), timeout=2)
            hidden_attr = dropdown.get_attribute("hidden")
            return hidden_attr is None or hidden_attr is False or str(hidden_attr).lower() == "false"
        except Exception:
            return False

    def get_profile_header_text(self):
        """Mengambil teks header profil (Nama dan Role)."""
        from selenium.webdriver.common.by import By
        try:
            header = self.find((By.CSS_SELECTOR, ".profile-dropdown__header"), timeout=3)
            return header.text.strip()
        except Exception:
            return ""

    def click_edit_profile(self):
        """Klik menu Edit Profil pada dropdown profil."""
        from selenium.webdriver.common.by import By
        if not self.is_profile_dropdown_open():
            self.open_profile_dropdown()
        btn = self.find((By.CSS_SELECTOR, "[data-profile-edit], .profile-dropdown__item:nth-of-type(1)"), timeout=3)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.4)

    def click_edit_password(self):
        """Klik menu Edit Password pada dropdown profil."""
        from selenium.webdriver.common.by import By
        if not self.is_profile_dropdown_open():
            self.open_profile_dropdown()
        btn = self.find((By.CSS_SELECTOR, "[data-password-edit], .profile-dropdown__item:nth-of-type(2)"), timeout=3)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.4)

    def click_logout(self):
        """Klik menu Keluar (Logout) pada dropdown profil."""
        from selenium.webdriver.common.by import By
        if not self.is_profile_dropdown_open():
            self.open_profile_dropdown()
        btn = self.find((By.CSS_SELECTOR, ".profile-dropdown__item.is-danger, form[action='/logout'] button"), timeout=3)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

    def get_toast_message(self):
        """Mengambil pesan notifikasi toast yang muncul di antarmuka."""
        from selenium.webdriver.common.by import By
        try:
            toast = self.find((By.CSS_SELECTOR, "[data-toast]"), timeout=3)
            return toast.text.strip()
        except Exception:
            return ""

