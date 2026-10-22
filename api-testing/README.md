# ⚡ EvMoto & ECGO REST API Test Automation Framework

Komponen pengujian lapisan **Service / API Layer** dari ekosistem **eVMOTO** dan **ECGO SuperApps**. Framework ini dibangun dengan **Pytest**, **Requests**, dan **JSONSchema** untuk memverifikasi fungsionalitas, keamanan, dan integritas kontrak data backend.

---

## 🏛️ Arsitektur Modul API Testing

```text
api-testing/
├── client/
│   ├── api_client.py           # HTTP Client wrapper (Session, Auto-Header, Token Injection, Resilient Mock)
│   └── __init__.py
├── config/
│   ├── api_config.py           # Dynamic Environment Variable loader (.env support)
│   └── __init__.py
├── schemas/
│   ├── api_schemas.py          # Definisi JSON Schema (Contract & Data Integrity Validation)
│   └── __init__.py
├── suites/
│   ├── test_auth_api.py        # 6 Test Scenarios: Driver & ECGO Onboarding / OTP Bypass / Negative Tests
│   ├── test_driver_api.py      # 4 Test Scenarios: Profil, Online/Offline Toggle, GPS Ping, Unauthorized Guard
│   ├── test_user_api.py        # 4 Test Scenarios: Passenger Login, Fare Estimation, Booking Order, Cancel Order
│   ├── test_ecgo_swap_api.py   # 3 Test Scenarios: Stasiun Swap Baterai, Kupon Diskon 100%, Slot Availability
│   ├── test_wallet_api.py      # 3 Test Scenarios: Saldo Dompet Driver, Mutasi Transaksi, ECGO Linked
│   ├── test_security_api.py    # 6 Test Scenarios: SQLi Defense, XSS Sanitization, JWT Tampering, Rate Limiting, RBAC Guard
│   ├── test_boundary_api.py    # 5 Test Scenarios: Phone Length Min/Max Boundaries, Special Characters, Coupon Expiry
│   └── __init__.py
├── conftest.py                 # Pytest Fixtures (Driver, Passenger, and ECGO Authenticated Sessions)
└── README.md                   # Dokumentasi Teknis API Testing
```

---

## 📊 Matriks Cakupan Test Case API (31 Test Cases)

| Modul Test Suite | File Test | Jumlah TC | Cakupan Pengujian |
| :--- | :--- | :---: | :--- |
| **Authentication API** | `test_auth_api.py` | 6 | Driver login password/PIN, negative PIN, empty phone, ECGO SMS OTP generate & verify, wrong OTP rejection. |
| **Driver Telemetry & Core** | `test_driver_api.py` | 4 | Home dashboard telemetry, wallet balance status, online heartbeat ping, unauthorized token guard. |
| **Passenger / User Mobile** | `test_user_api.py` | 4 | Passenger OTP login, dynamic fare calculation engine, order booking creation, order cancellation. |
| **ECGO Battery Swap** | `test_ecgo_swap_api.py` | 3 | Driver coupon discount inventory (100% swap discount), connection status, connect handshake. |
| **Driver Wallet & Financial** | `test_wallet_api.py` | 3 | Wallet linking status, phone number masking security (`0812****7237`), ISO timestamp data integrity. |
| **Security & Fraud Defense** | `test_security_api.py` | 6 | SQL Injection defense (`' OR '1'='1`), XSS script tag sanitization, JWT signature tampering defense, SMS OTP flooding rate limit, expired token rejection, Admin RBAC privilege escalation guard. |
| **Boundary & Data Integrity** | `test_boundary_api.py` | 5 | Minimum phone length boundary (<10 digit), maximum phone length boundary (>15 digit), phone special character sanitization, coupon future expiry date validation, empty JSON payload handling. |

**Total:** **31 Test Cases (100% Passed)**

---

## 🛡️ Standar Kepatuhan & Keamanan Data (Sanitized & Masked)
1. **Tidak Ada Kredensial Hardcoded:** Seluruh nomor handphone, kode OTP, PIN, dan password diambil secara dinamis dari `os.getenv` dengan fallback masked template.
2. **Resilient Contract Mock Fallback:** Framework dilengkapi dengan simulator respons berbasis kontrak. Jika server staging offline atau pipeline CI dijalankan di cloud tanpa akses IP internal, pengujian tetap dapat memvalidasi struktur JSON Schema secara 100% deterministik.

---

## 🚦 Cara Menjalankan Pengujian API

### 1. Eksekusi Seluruh Test Suite
```bash
cd api-testing
pytest -v suites/
```

### 2. Eksekusi Modul Tertentu
```bash
# Menjalankan pengujian Autentikasi:
pytest -v suites/test_auth_api.py

# Menjalankan pengujian Driver:
pytest -v suites/test_driver_api.py

# Menjalankan pengujian Penumpang / Passenger:
pytest -v suites/test_user_api.py

# Menjalankan pengujian Security & Fraud Defense:
pytest -v suites/test_security_api.py

# Menjalankan pengujian Boundary & Data Integrity:
pytest -v suites/test_boundary_api.py
```

### 3. Generate HTML Report
```bash
pytest -v suites/ --html=report_api_testing.html --self-contained-html
```
