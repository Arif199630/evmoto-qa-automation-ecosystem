# Panduan Konfigurasi Backend API Resmi EvMoto (Mobile Apps & Dashboard)

Dokumen ini memuat daftar alamat server backend API resmi EvMoto yang digunakan bersama oleh pengujian otomatisasi **Mobile Apps** (`evmoto-user-mobile-automation`) dan **Web Dashboard** (`Automation_Project_EvMoto`).

---

## 🌐 Daftar Endpoint Server Resmi

| Backend Stack | Environment | Base URL / Host | Catatan Khusus |
| :--- | :--- | :--- | :--- |
| **Java** | **Development** | `https://dev-api.evmotoid.com` | Server staging & integrasi Java |
| **Java** | **Production** | `https://api.evmotoid.com` | Server production Java (live) |
| **Golang** | **Development** | `https://evmotodev.justkidding.app` | IP Server langsung: `http://139.162.60.46` |
| **Golang** | **Production** | `https://new-api.evmotoid.com` | Server production Golang (live) |

---

## 🛠️ Cara Penggunaan di Automation Dashboard (`Automation_Project_EvMoto`)

### 1. Mengakses lewat `Config` Class:
```python
from config import Config

# Akses konstanta URL langsung
print(Config.JAVA_DEV_API_URL)        # https://dev-api.evmotoid.com
print(Config.JAVA_PROD_API_URL)       # https://api.evmotoid.com
print(Config.GOLANG_DEV_API_IP)       # http://139.162.60.46
print(Config.GOLANG_DEV_API_URL)      # https://evmotodev.justkidding.app
print(Config.GOLANG_PROD_API_URL)     # https://new-api.evmotoid.com

# Akses dinamis via method helper
active_api = Config.get_backend_api_url(backend="golang", env="dev")
```

### 2. Konfigurasi via file `.env`:
```env
JAVA_DEV_API_URL=https://dev-api.evmotoid.com
JAVA_PROD_API_URL=https://api.evmotoid.com
GOLANG_DEV_API_IP=http://139.162.60.46
GOLANG_DEV_API_URL=https://evmotodev.justkidding.app
GOLANG_PROD_API_URL=https://new-api.evmotoid.com

BACKEND_TYPE=golang
BACKEND_API_URL=https://evmotodev.justkidding.app   # automation hanya boleh ke staging
```

---

## 📱 Cara Penggunaan di Mobile Automation (`evmoto-user-mobile-automation`)

### 1. Mengakses lewat `config` package:
```python
from config import Config, BackendEndpoints, get_backend_url

# Akses via BackendEndpoints
print(BackendEndpoints.JAVA_DEV)       # https://dev-api.evmotoid.com
print(BackendEndpoints.JAVA_PROD)      # https://api.evmotoid.com
print(BackendEndpoints.GOLANG_DEV)     # https://evmotodev.justkidding.app
print(BackendEndpoints.GOLANG_DEV_IP)  # http://139.162.60.46
print(BackendEndpoints.GOLANG_PROD)    # https://new-api.evmotoid.com

# Akses via Config
print(Config.GOLANG_PROD_API_URL)
```
