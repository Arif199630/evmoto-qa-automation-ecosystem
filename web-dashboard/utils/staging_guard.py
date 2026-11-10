"""
Pengaman environment: automation EvMoto hanya boleh berjalan di dev/staging.

Dipanggil sekali di awal setiap run pytest (lihat pytest_sessionstart di conftest.py).
Bila ENVIRONMENT atau salah satu URL target mengarah ke production, run dibatalkan
sebelum test pertama berjalan, supaya tidak ada data production yang tersentuh.
"""
import os
from urllib.parse import urlparse

ALLOWED_ENVIRONMENTS = {"dev", "staging", "qa", "local"}

# Host production EvMoto. Tambahkan di sini bila ada domain production baru.
PRODUCTION_HOSTS = {
    "dashboard.evmotoid.com",
    "api.evmotoid.com",
    "new-api.evmotoid.com",
}

# Variabel environment yang berisi URL target test.
URL_VARIABLES = (
    "BASE_URL", "EVMOTO_BASE_URL", "APP_URL", "DEV_BASE_URL",
    "BACKEND_API_URL", "GOLANG_DEV_API_URL", "JAVA_DEV_API_URL",
    "ADMIN_DEV_URL", "EVMOTO_API_BASE_URL", "ECGO_API_BASE_URL", "EVMOTO_ADMIN_PORTAL_URL",
)


class ProductionTargetError(RuntimeError):
    """Dilempar bila automation diarahkan ke production."""


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def find_production_targets(extra_urls=()) -> list:
    """Kembalikan daftar alasan (teks) bila ada target production. Kosong = aman."""
    problems = []
    env_name = os.getenv("ENVIRONMENT", "dev").strip().lower()
    if env_name not in ALLOWED_ENVIRONMENTS:
        problems.append(f"ENVIRONMENT={env_name} (hanya {', '.join(sorted(ALLOWED_ENVIRONMENTS))} yang diizinkan)")
    candidates = [(name, os.getenv(name, "")) for name in URL_VARIABLES]
    candidates += [("konfigurasi", url) for url in extra_urls]
    for name, url in candidates:
        if url and _host(url) in PRODUCTION_HOSTS:
            problems.append(f"{name}={url}")
    return problems


def ensure_not_production(extra_urls=()) -> None:
    """Hentikan run bila target mengarah ke production."""
    problems = find_production_targets(extra_urls)
    if problems:
        raise ProductionTargetError(
            "Automation dibatalkan: target mengarah ke PRODUCTION.\n  - "
            + "\n  - ".join(problems)
            + "\nAutomation EvMoto hanya boleh dijalankan di dev/staging. Perbaiki .env lalu jalankan ulang."
        )
