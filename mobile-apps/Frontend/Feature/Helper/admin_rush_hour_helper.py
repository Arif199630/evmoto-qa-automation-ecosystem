"""
================================================================================
EVMOTO ADMIN DASHBOARD - RUSH HOUR SUBSIDY HELPER & ACTOR
================================================================================
Target URL   : https://evmotoadmin.justkidding.app/rushHour/settings
               https://evmotoadmin.justkidding.app/rushHour/history
Fitur        : Halaman Pengaturan Subsidi Jam Sibuk & Riwayat Subsidi
Keamanan     : Kredensial via Environment Variable (.env)
Mode         : Headless Web & REST/Form API Layer dengan Snapshot Teardown Restoration
================================================================================
"""
import os
import re
import requests
import urllib3
from typing import Dict, List, Tuple, Optional, Any
from utils.logger import get_logger

urllib3.disable_warnings()
logger = get_logger("AdminRushHourHelper")


class AdminRushHourHelper:
    """Helper & Actor untuk menguji fitur Subsidi Jam Sibuk pada Admin Dashboard."""

    DEFAULT_ADMIN_URL = os.getenv("ADMIN_DEV_URL", "https://evmotoadmin.justkidding.app")
    DEFAULT_ADMIN_USER = os.getenv("ADMIN_DEV_USER", "")
    DEFAULT_ADMIN_PASS = os.getenv("ADMIN_DEV_PASS", "")

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
        """Melakukan otentikasi login ke Admin Dashboard."""
        user = username or self.DEFAULT_ADMIN_USER
        pwd = password or self.DEFAULT_ADMIN_PASS
        login_url = f"{self.base_url}/login"

        for attempt in range(1, max_attempts + 1):
            try:
                r_get = self.session.get(login_url, headers=self.headers, timeout=10)
                payload = {"username": user, "password": pwd}
                r_post = self.session.post(
                    login_url,
                    data=payload,
                    headers={"Referer": login_url, **self.headers},
                    timeout=10,
                    allow_redirects=True
                )
                session_cookie = self.session.cookies.get("evmoto_admin_session")
                if session_cookie or (r_post.status_code == 200 and "/login" not in r_post.url):
                    self.is_authenticated = True
                    logger.info("Login Admin Dashboard BERHASIL.")
                    return True
            except Exception as e:
                logger.warning(f"Percobaan login {attempt} gagal: {e}")
                import time
                time.sleep(1.5)

        logger.error("Gagal login ke Admin Dashboard.")
        return False

    def get_settings_page(self) -> Tuple[int, str]:
        """Mengambil halaman /rushHour/settings."""
        url = f"{self.base_url}/rushHour/settings"
        logger.info(f"Mengakses halaman Subsidi Jam Sibuk: {url}")
        r = self.session.get(url, headers=self.headers, timeout=10)
        return r.status_code, r.text

    def get_history_page(self) -> Tuple[int, str]:
        """Mengambil halaman /rushHour/history."""
        url = f"{self.base_url}/rushHour/history"
        logger.info(f"Mengakses halaman Riwayat Subsidi Jam Sibuk: {url}")
        r = self.session.get(url, headers=self.headers, timeout=10)
        return r.status_code, r.text

    def parse_settings(self, html: Optional[str] = None) -> Dict[str, Any]:
        """Mem-parsing elemen-elemen form konfigurasi Subsidi Jam Sibuk dari HTML."""
        if html is None:
            status, html = self.get_settings_page()
            if status != 200:
                raise RuntimeError(f"Gagal mengambil halaman /rushHour/settings: HTTP {status}")

        settings: Dict[str, Any] = {
            "enabled": False,
            "windows": [],
            "tiers": [],
            "daily_budget": "",
        }

        # Checkbox enabled: abaikan input hidden (value=false) yang mendahului checkbox.
        # Sebelumnya input hidden terbaca lebih dulu sehingga snapshot selalu enabled=False
        # dan teardown mematikan subsidi jam sibuk di staging.
        boxes = [t for t in re.findall(r'<input[^>]+name=["\']enabled["\'][^>]*>', html) if 'type="checkbox"' in t]
        settings["enabled"] = bool(boxes) and bool(re.search(r"\bchecked\b", boxes[0]))

        # Windows
        w_starts = re.findall(r'name=["\']windowStart["\'][^>]+value=["\']([^"\']*)["\']', html)
        w_ends = re.findall(r'name=["\']windowEnd["\'][^>]+value=["\']([^"\']*)["\']', html)
        for s, e in zip(w_starts, w_ends):
            if s.strip() or e.strip():
                settings["windows"].append((s.strip(), e.strip()))

        # Tiers
        t_subsidies = re.findall(r'name=["\']tierSubsidy["\'][^>]+value=["\']([^"\']*)["\']', html)
        t_maxes = re.findall(r'name=["\']tierMax["\'][^>]+value=["\']([^"\']*)["\']', html)
        for sub, mx in zip(t_subsidies, t_maxes):
            if sub.strip() or mx.strip():
                settings["tiers"].append((sub.strip(), mx.strip()))

        # Daily Budget
        b_match = re.search(r'name=["\']dailyBudget["\'][^>]+value=["\']([^"\']*)["\']', html)
        if b_match:
            settings["daily_budget"] = b_match.group(1).strip()

        return settings

    def verify_ui_components(self, html: Optional[str] = None) -> Dict[str, bool]:
        """Validasi keberadaan komponen UI halaman Subsidi Jam Sibuk."""
        if html is None:
            _, html = self.get_settings_page()

        results = {
            "has_title_subsidi_jam_sibuk": "Subsidi jam sibuk" in html,
            "has_switch_enabled": bool(re.search(r'name=["\']enabled["\']', html)),
            "has_input_window_start": bool(re.search(r'name=["\']windowStart["\']', html)),
            "has_input_window_end": bool(re.search(r'name=["\']windowEnd["\']', html)),
            "has_input_tier_subsidy": bool(re.search(r'name=["\']tierSubsidy["\']', html)),
            "has_input_tier_max": bool(re.search(r'name=["\']tierMax["\']', html)),
            "has_input_daily_budget": bool(re.search(r'name=["\']dailyBudget["\']', html)),
            "has_submit_button": bool(re.search(r'<button[^>]+type=["\']submit["\'][^>]*>[\s\S]*?Simpan[\s\S]*?</button>', html)),
        }
        return results

    def submit_settings(
        self,
        enabled: bool = True,
        windows: Optional[List[Tuple[str, str]]] = None,
        tiers: Optional[List[Tuple[str, str]]] = None,
        daily_budget: str = "",
    ) -> requests.Response:
        """Mengirimkan form konfigurasi POST /rushHour/settings."""
        url = f"{self.base_url}/rushHour/settings"
        payload: List[Tuple[str, str]] = []

        payload.append(("enabled", "false"))
        if enabled:
            payload.append(("enabled", "true"))

        if windows is None:
            windows = [("06:45", "08:45"), ("10:45", "18:45")]

        for s, e in windows:
            payload.append(("windowStart", s))
            payload.append(("windowEnd", e))

        if tiers is None:
            tiers = [("3000", "10000"), ("4000", "20000"), ("5000", "")]

        for idx, (sub, mx) in enumerate(tiers):
            payload.append(("tierSubsidy", str(sub)))
            payload.append(("tierMax", str(mx)))
            if str(mx).strip() == "":
                payload.append(("tierUnlimited", str(idx)))

        payload.append(("dailyBudget", str(daily_budget)))

        logger.info(f"Submitting POST /rushHour/settings: enabled={enabled}, windows={len(windows)}, tiers={len(tiers)}")
        import time
        time.sleep(0.5)
        resp = self.session.post(
            url,
            data=payload,
            headers={"Referer": url, **self.headers},
            timeout=10,
            allow_redirects=True
        )
        return resp

    def restore_settings(self, original_settings: Dict[str, Any]) -> requests.Response:
        """Mengembalikan konfigurasi form /rushHour/settings ke snapshot data semula (Teardown Cleanup)."""
        logger.info(f"Mengembalikan pengaturan Subsidi Jam Sibuk ke snapshot semula: {original_settings}")
        return self.submit_settings(
            enabled=original_settings.get("enabled", True),
            windows=original_settings.get("windows"),
            tiers=[(sub, mx) for sub, mx in original_settings.get("tiers", [])],
            daily_budget=original_settings.get("daily_budget", ""),
        )

    def is_saved_successfully(self, resp: requests.Response) -> bool:
        """Memeriksa apakah pengiriman berhasil disimpan."""
        return "saved=1" in resp.url or "Pengaturan tersimpan." in resp.text or resp.status_code == 200

