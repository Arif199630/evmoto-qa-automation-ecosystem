"""
================================================================================
EVMOTO ADMIN DASHBOARD - DISPATCH BATCH HELPER & ACTOR
================================================================================
Target URL   : https://evmotoadmin.justkidding.app/dispatchBatch
Fungsi       : Mengelola konfigurasi penyebaran orderan batch ke driver,
               pengaturan jarak (radius bands) untuk Order Biasa (Ordinary)
               dan Advance Booking, serta validasi 4 Pilar QA.
Keamanan     : Kredensial via Environment Variable (.env)
Mode         : Headless Web & REST/Form API Layer
================================================================================
"""
import os
import re
import requests
import urllib3
from typing import Dict, List, Tuple, Optional, Any
from utils.logger import get_logger

urllib3.disable_warnings()
logger = get_logger("AdminDispatchBatchHelper")


class AdminDispatchBatchHelper:
    """Helper & Actor untuk menguji fitur Dispatch Batch pada Admin Dashboard."""

    DEFAULT_ADMIN_URL = os.getenv("ADMIN_DEV_URL", "https://evmotoadmin.justkidding.app")
    DEFAULT_ADMIN_USER = os.getenv("ADMIN_DEV_USER", "admin_temp")
    DEFAULT_ADMIN_PASS = os.getenv("ADMIN_DEV_PASS", "123456")

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or self.DEFAULT_ADMIN_URL).rstrip("/")
        self.session = requests.Session()
        self.session.verify = False

        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.is_authenticated = False

    def login(self, username: Optional[str] = None, password: Optional[str] = None, max_attempts: int = 3) -> bool:
        """Melakukan otentikasi login ke Admin Dashboard dengan proteksi retry koneksi."""
        user = username or self.DEFAULT_ADMIN_USER
        pwd = password or self.DEFAULT_ADMIN_PASS
        login_url = f"{self.base_url}/login"

        for attempt in range(1, max_attempts + 1):
            logger.info(f"Otentikasi Admin Dashboard ke: {login_url} (User: {user}) - Percobaan {attempt}/{max_attempts}")
            try:
                # 1. GET login page untuk inisialisasi session cookie
                r_get = self.session.get(login_url, headers=self.headers, timeout=10)
                if r_get.status_code != 200:
                    logger.warning(f"Gagal membuka halaman login: HTTP {r_get.status_code}")
                    import time
                    time.sleep(1.5)
                    continue

                # 2. POST kredensial
                payload = {"username": user, "password": pwd}
                r_post = self.session.post(
                    login_url,
                    data=payload,
                    headers={"Referer": login_url, **self.headers},
                    timeout=10,
                    allow_redirects=True
                )

                # Cek cookie session
                session_cookie = self.session.cookies.get("evmoto_admin_session")
                if session_cookie or (r_post.status_code == 200 and "/login" not in r_post.url):
                    self.is_authenticated = True
                    logger.info("Login Admin Dashboard BERHASIL. Session aktif terpasang.")
                    return True
                else:
                    logger.warning(f"Login ditolak atau gagal. URL akhir: {r_post.url}")
            except Exception as e:
                logger.warning(f"Transient connection glitch saat login (attempt {attempt}): {e}")
                import time
                time.sleep(2.0)

        logger.error("Gagal login setelah seluruh percobaan habis.")
        return False

    def get_dispatch_batch_page(self) -> Tuple[int, str]:
        """Mengambil halaman /dispatchBatch dan mengembalikan status code beserta HTML."""
        url = f"{self.base_url}/dispatchBatch"
        logger.info(f"Mengakses halaman Dispatch Batch: {url}")
        r = self.session.get(url, headers=self.headers, timeout=10)
        return r.status_code, r.text

    def parse_dispatch_batch_settings(self, html: Optional[str] = None) -> Dict[str, Any]:
        """Mem-parsing elemen-elemen form konfigurasi Dispatch Batch dari HTML."""
        if html is None:
            status, html = self.get_dispatch_batch_page()
            if status != 200:
                raise RuntimeError(f"Gagal mengambil halaman /dispatchBatch: HTTP {status}")

        settings: Dict[str, Any] = {
            "enabled": False,
            "size": 0,
            "delay": 0,
            "duration": 0,
            "concurrent": 5,  # Baseline default kuota order konkuren per driver
            "rescans": 0,
            "ordinary_bands": [],
            "advance_bands": [],
            "raw_html_length": len(html),
        }

        # Checkbox Enabled
        chk_match = re.search(r'<input[^>]+name=["\']enabled["\'][^>]*>', html)
        if chk_match and "checked" in chk_match.group(0):
            settings["enabled"] = True

        # Input numeric fields
        for field in ["size", "delay", "duration", "concurrent", "rescans"]:
            m = re.search(rf'<input[^>]+name=["\']{field}["\'][^>]+value=["\']([^"\']*)["\']', html)
            if not m:
                # Coba format terbalik (value sebelum name)
                m = re.search(rf'<input[^>]+value=["\']([^"\']*)["\'][^>]+name=["\']{field}["\']', html)
            if m:
                try:
                    settings[field] = int(m.group(1)) if m.group(1).isdigit() else m.group(1)
                except ValueError:
                    settings[field] = m.group(1)

        # Parsing Ordinary Bands
        ordinary_starts = re.findall(r'<input[^>]+name=["\']ordinaryStart["\'][^>]+value=["\']([^"\']*)["\']', html)
        ordinary_ends = re.findall(r'<input[^>]+name=["\']ordinaryEnd["\'][^>]+value=["\']([^"\']*)["\']', html)
        for s, e in zip(ordinary_starts, ordinary_ends):
            if s != "" and e != "":
                settings["ordinary_bands"].append((s, e))

        # Parsing Advance Booking Bands
        advance_starts = re.findall(r'<input[^>]+name=["\']advanceStart["\'][^>]+value=["\']([^"\']*)["\']', html)
        advance_ends = re.findall(r'<input[^>]+name=["\']advanceEnd["\'][^>]+value=["\']([^"\']*)["\']', html)
        for s, e in zip(advance_starts, advance_ends):
            if s != "" and e != "":
                settings["advance_bands"].append((s, e))

        return settings

    def verify_ui_components(self, html: Optional[str] = None) -> Dict[str, bool]:
        """
        Validasi mendalam keberadaan seluruh komponen UI:
        - Checkbox switch Jalur Batch
        - Input numerik (size, delay, duration, concurrent, rescans)
        - Section Band Order Biasa (+ Tambah & Hapus)
        - Section Band Advance Booking (+ Tambah & Hapus)
        - Tombol Simpan
        """
        if html is None:
            _, html = self.get_dispatch_batch_page()

        results = {
            "has_batch_switch_checkbox": bool(re.search(r'name=["\']enabled["\']', html)),
            "has_input_batch_size": bool(re.search(r'name=["\']size["\']', html)),
            "has_input_delay": bool(re.search(r'name=["\']delay["\']', html)),
            "has_input_duration": bool(re.search(r'name=["\']duration["\']', html)),
            "has_input_concurrent": bool(re.search(r'name=["\']concurrent["\']', html)),
            "has_input_rescans": bool(re.search(r'name=["\']rescans["\']', html)),
            "has_ordinary_bands_section": "Band order biasa" in html,
            "has_btn_add_ordinary_band": 'data-band-add="ordinary"' in html,
            "has_advance_bands_section": "Band advance booking" in html,
            "has_btn_add_advance_band": 'data-band-add="advance"' in html,
            "has_btn_remove_row": 'data-row-remove' in html,
            "has_submit_button": bool(re.search(r'<button[^>]+type=["\']submit["\'][^>]*>[\s\S]*?Simpan[\s\S]*?</button>', html)),
        }
        return results

    def submit_dispatch_batch(
        self,
        enabled: bool = True,
        size: Any = 5,
        delay: Any = 10,
        duration: Any = 0,
        concurrent: Any = 5,
        rescans: Any = 2,
        ordinary_bands: Optional[List[Tuple[Any, Any]]] = None,
        advance_bands: Optional[List[Tuple[Any, Any]]] = None,
    ) -> requests.Response:
        """Mengirimkan form konfigurasi POST /dispatchBatch."""
        url = f"{self.base_url}/dispatchBatch"
        payload: List[Tuple[str, str]] = []

        if enabled:
            payload.append(("enabled", "1"))
        payload.append(("size", str(size)))
        payload.append(("delay", str(delay)))
        payload.append(("duration", str(duration)))
        payload.append(("concurrent", str(concurrent)))
        payload.append(("rescans", str(rescans)))

        # Default ordinary bands jika None
        if ordinary_bands is None:
            ordinary_bands = [("0", "1"), ("1", "2"), ("2", "3"), ("3", "4"), ("4", "5")]

        for s, e in ordinary_bands:
            payload.append(("ordinaryStart", str(s)))
            payload.append(("ordinaryEnd", str(e)))

        # Default advance bands jika None
        payload.append(("advanceEditable", "1"))
        if advance_bands is None:
            advance_bands = [("0", "1"), ("1", "2"), ("2", "5"), ("5", "15")]

        for s, e in advance_bands:
            payload.append(("advanceStart", str(s)))
            payload.append(("advanceEnd", str(e)))

        logger.info(f"Submitting POST /dispatchBatch: size={size}, delay={delay}, duration={duration}, concurrent={concurrent}")
        import time
        time.sleep(0.6)
        resp = self.session.post(
            url,
            data=payload,
            headers={"Referer": url, **self.headers},
            timeout=10,
            allow_redirects=True
        )
        return resp

    def extract_alert_message(self, html: str) -> Optional[str]:
        """Mengekstrak pesan error role='alert' jika ada."""
        m = re.search(r'<div[^>]*role=["\']alert["\'][^>]*>([\s\S]*?)</div>', html)
        if m:
            clean = re.sub(r'<[^>]+>', ' ', m.group(1))
            return re.sub(r'\s+', ' ', clean).strip()
        return None

    def is_saved_successfully(self, resp: requests.Response) -> bool:
        """Memeriksa apakah pengiriman berhasil disimpan ('saved=1' atau teks 'Pengaturan tersimpan')."""
        return "saved=1" in resp.url or "Pengaturan tersimpan." in resp.text
