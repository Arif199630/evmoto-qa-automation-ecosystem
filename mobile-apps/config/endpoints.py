"""
================================================================================
EVMOTO BACKEND API ENDPOINTS CONFIGURATION (JAVA & GOLANG)
================================================================================
Menyimpan konfigurasi URL dan alamat IP server backend EvMoto:
Dimuat secara dinamis via Environment Variable (.env) untuk keamanan kredensial.
================================================================================
"""
import os
from enum import Enum
from typing import Dict, Optional


class BackendType(str, Enum):
    JAVA = "java"
    GOLANG = "golang"


class EnvironmentType(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class BackendEndpoints:
    """Konstanta Endpoint Backend API Resmi EvMoto."""

    # Java Backend Endpoints
    JAVA_DEV = os.getenv("JAVA_DEV_API_URL", "https://dev-api.evmoto.internal")
    JAVA_PROD = os.getenv("JAVA_PROD_API_URL", "https://api.evmoto.internal")

    # Golang Backend Endpoints
    GOLANG_DEV_IP = os.getenv("GOLANG_DEV_API_IP", "http://10.0.0.10")
    GOLANG_DEV_DOMAIN = os.getenv("EVMOTO_API_BASE_URL", "https://api-dev.evmoto.internal")
    GOLANG_DEV = GOLANG_DEV_DOMAIN
    GOLANG_PROD = os.getenv("GOLANG_PROD_API_URL", "https://new-api.evmoto.internal")

    # Mapping Komprehensif
    ALL_ENDPOINTS: Dict[str, Dict[str, str]] = {
        "java": {
            "dev": JAVA_DEV,
            "development": JAVA_DEV,
            "prod": JAVA_PROD,
            "production": JAVA_PROD,
        },
        "golang": {
            "dev": GOLANG_DEV,
            "development": GOLANG_DEV,
            "dev_ip": GOLANG_DEV_IP,
            "dev_domain": GOLANG_DEV_DOMAIN,
            "prod": GOLANG_PROD,
            "production": GOLANG_PROD,
        }
    }

    # Alias Flat Dictionary untuk kemudahan akses cepat
    ENDPOINTS_MAP = {
        "java_dev": JAVA_DEV,
        "dev_java": JAVA_DEV,
        "java_prod": JAVA_PROD,
        "prod_java": JAVA_PROD,
        "golang_dev": GOLANG_DEV,
        "dev_golang": GOLANG_DEV,
        "golang_dev_ip": GOLANG_DEV_IP,
        "golang_prod": GOLANG_PROD,
        "prod_golang": GOLANG_PROD,
    }


def get_backend_url(
    backend: Optional[str] = None,
    environment: Optional[str] = None,
    use_ip_for_golang_dev: bool = False
) -> str:
    """
    Mengambil Base URL API backend berdasarkan tipe backend (java/golang)
    dan environment (dev/prod). Jika tidak dispesifikasikan, membaca dari
    Environment Variables sistem / .env.
    """
    backend_val = (backend or os.getenv("BACKEND_TYPE", "golang")).strip().lower()
    env_val = (environment or os.getenv("ENVIRONMENT", "dev")).strip().lower()

    # Normalisasi nama environment
    if env_val in ("production", "live"):
        env_key = "prod"
    else:
        env_key = "dev"

    if backend_val == "java":
        return BackendEndpoints.JAVA_PROD if env_key == "prod" else BackendEndpoints.JAVA_DEV
    elif backend_val == "golang":
        if env_key == "prod":
            return BackendEndpoints.GOLANG_PROD
        return BackendEndpoints.GOLANG_DEV_IP if use_ip_for_golang_dev else BackendEndpoints.GOLANG_DEV_DOMAIN

    # Fallback ke override environment variable langsung
    return os.getenv("BACKEND_API_URL", BackendEndpoints.GOLANG_PROD)
