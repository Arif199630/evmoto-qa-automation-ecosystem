"""
================================================================================
EVMOTO USER MOBILE AUTOMATION - BASE PAGE OBJECT
================================================================================
Kelas induk Page Object Model (POM).
Menyediakan method wrapper standar untuk explicit wait, interaksi elemen,
pemberian log, scrolling, pengambilan screenshot, dan human-like pacing.
================================================================================
"""
import re
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
            element = WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located(locator)
            )
            return self._best_match(locator, element)
        except TimeoutException:
            self.check_for_server_errors()
            logger.error(f"Elemen dengan locator {locator} tidak ditemukan dalam {t} detik.")
            raise

    def find_element(self, locator: Tuple[str, str], timeout: int = None):
        """Alias untuk self.find() demi kompatibilitas POM."""
        return self.find(locator, timeout)

    def find_all(self, locator: Tuple[str, str], timeout: int = 5) -> List:
        """Menemukan seluruh elemen yang cocok dengan locator."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def _best_match(self, locator: Tuple[str, str], fallback):
        """Pilih elemen yang tepat bila locator 'contains(...)' cocok dengan beberapa elemen.

        Contoh: contains(@content-desc,'Masuk') juga cocok dengan label 'Masukkan nomor handphone'.
        Urutan pilihan: teks/content-desc yang PERSIS sama dengan kata kunci, lalu elemen Button,
        lalu elemen pertama seperti sebelumnya.
        """
        if not isinstance(locator[1], str) or "contains(" not in locator[1]:
            return fallback
        try:
            candidates = self.driver.find_elements(*locator)
        except Exception:
            return fallback
        if len(candidates) <= 1:
            return fallback
        keywords = set(re.findall(r"contains\(@(?:content-desc|text),\s*'([^']+)'\)", locator[1]))

        def label_of(el):
            return ((el.get_attribute("content-desc") or el.get_attribute("text") or "").strip())

        exact = [el for el in candidates if label_of(el) in keywords]
        if exact:
            return exact[0]
        buttons = [el for el in candidates if (el.get_attribute("class") or "").endswith("Button")]
        return buttons[0] if buttons else fallback

    def click(self, locator: Tuple[str, str], label: str = "", use_human_pacing: bool = True):
        """Menunggu elemen clickable kemudian melakukan klik."""
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element = self._best_match(locator, element)
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

    # Pembatalan order sisa (peta layar CI 18 Nov 2026, peta_batal_order): panel 'Sedang mencari driver' terpotong di layar 320x640;
    # setelah digeser ke atas muncul Button 'Batalkan'. Diketuk -> dialog 'Apakah Anda yakin ingin membatalkan pesanan?' dengan
    # Button 'Tutup' dan 'Batalkan' (konfirmasi, elemen 'Batalkan' terakhir di pohon).
    _XP_MENCARI_DRIVER = "//*[contains(@content-desc,'Sedang mencari driver terdekat') or contains(@text,'Sedang mencari driver terdekat')]"
    _XP_BATALKAN = "//android.widget.Button[@content-desc='Batalkan' or @text='Batalkan']"
    _XP_DIALOG_YAKIN = "//*[starts-with(@content-desc, 'Apakah Anda yakin ingin membatalkan pesanan')]"

    def batalkan_order_sisa_jika_ada(self) -> bool:
        """Batalkan order yang tertinggal di status 'Sedang mencari driver' (sisa test sebelumnya) agar akun kembali bersih.

        Satu akun QA dipakai berurutan oleh banyak test; satu order sisa membuat semua test berikutnya gagal karena Beranda tidak
        punya kolom pencarian (24 kegagalan di run 18 Nov 2026). True bila ada order sisa yang berhasil dibatalkan.
        """
        if not self.is_displayed(("xpath", self._XP_MENCARI_DRIVER), timeout=2):
            return False
        logger.info("Order sisa 'Sedang mencari driver' terdeteksi, membatalkan...")
        for percobaan in range(1, 4):
            size = self.driver.get_window_size()
            x = size["width"] // 2
            try:
                self.driver.swipe(x, int(size["height"] * 0.93), x, int(size["height"] * 0.55), 600)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(1.5)
            tombol = self.driver.find_elements("xpath", self._XP_BATALKAN)
            if not tombol:
                continue
            tombol[0].click()
            time.sleep(1.5)
            if self.driver.find_elements("xpath", self._XP_DIALOG_YAKIN):
                self.driver.find_elements("xpath", self._XP_BATALKAN)[-1].click()
                time.sleep(3)
            if not self.driver.find_elements("xpath", self._XP_MENCARI_DRIVER):
                logger.info(f"Order sisa dibatalkan (percobaan {percobaan})")
                return True
        logger.warning("Order sisa tidak berhasil dibatalkan setelah 3 percobaan")
        return False

    def tutup_popup_lanjutkan(self) -> bool:
        """Tutup popup 'Pemberitahuan Jam Operasional' (Button 'Lanjutkan') bila sedang tampil. True bila ditutup.

        Popup ini muncul beberapa detik setelah login dan menutupi layar; ketukan pertama pada tab bawah hanya mengenai
        latar popup sehingga layar tidak berpindah (bukti run 18 Nov 2026: test Aktivitas dan peta alur OVO). Hanya
        dipanggil dari fungsi navigasi tab utama, tempat 'Lanjutkan' tidak mungkin tombol alur lain.
        """
        try:
            els = self.driver.find_elements("xpath", "//android.widget.Button[@content-desc='Lanjutkan' or @text='Lanjutkan']")
            if not els:
                return False
            logger.info("Popup 'Lanjutkan' (Pemberitahuan Jam Operasional) tampil, menutup popup...")
            els[0].click()
            time.sleep(1.0)
            return True
        except Exception:
            return False

    def scroll_until_displayed(self, locator: Tuple[str, str], max_swipes: int = 5) -> bool:
        """Geser layar ke atas sampai elemen tampil (ListView Flutter hanya menampilkan item yang terlihat).

        Emulator CI berukuran 320x640, sehingga banyak menu/tombol berada di bawah lipatan layar dan
        TimeoutException bila langsung diklik tanpa menggeser layar (bukti run 18 Nov 2026: menu Kontak Darurat dkk).
        """
        if self.is_displayed(locator, timeout=2):
            return True
        size = self.driver.get_window_size()
        x = size["width"] // 2
        for _ in range(max_swipes):
            try:
                self.swipe(x, int(size["height"] * 0.75), x, int(size["height"] * 0.35), 500)
            except Exception as e:
                logger.warning(f"Gagal menggeser layar: {e}")
                break
            time.sleep(0.6)
            if self.is_displayed(locator, timeout=1):
                return True
        return False

    def click_with_scroll(self, locator: Tuple[str, str], label: str = "", max_swipes: int = 5):
        """Klik elemen; bila belum terlihat, geser layar dulu sampai tampil."""
        self.scroll_until_displayed(locator, max_swipes=max_swipes)
        return self.click(locator, label=label)

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

    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """Nama lain is_displayed(), dipakai Page Object Driver App."""
        return self.is_displayed(locator, timeout=timeout)

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 400):
        """Geser layar dari titik awal ke titik akhir (koordinat piksel, durasi milidetik)."""
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)

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
