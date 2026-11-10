"""
Pytest hook untuk Admin Dashboard EvMoto.

Satu-satunya tugasnya: membatalkan run bila target mengarah ke production.
Fixture browser tetap dibuat di masing-masing test class (unittest).
"""
from config import Config
from utils.staging_guard import ensure_not_production


def pytest_sessionstart(session):
    """Batalkan run bila target mengarah ke production (hanya dev/staging yang diizinkan)."""
    ensure_not_production(extra_urls=[Config.get_base_url(), Config.get_backend_api_url()])
