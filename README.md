# 🚀 EVMOTO & ECGO End-to-End QA Automation Ecosystem

[![CI/CD Pipeline](https://github.com/Arif199630/evmoto-qa-automation-ecosystem/actions/workflows/ci.yml/badge.svg)](https://github.com/Arif199630/evmoto-qa-automation-ecosystem/actions)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Test Automation](https://img.shields.io/badge/Total%20Test%20Cases-1%2C180%2B%20TC-success.svg?logo=pytest&logoColor=white)](docs/reports/)
[![Architecture](https://img.shields.io/badge/Framework-POM%20%7C%20BDD%20%7C%20API%20Contract%20%7C%204--Pillar%20QA-orange.svg)]()
[![Platform](https://img.shields.io/badge/Target-Web%20Dashboard%20%7C%20Mobile%20Android%20%7C%20REST%20API-lightgrey.svg)]()

> **QA Engineering Portfolio** oleh **Bhagus Arif Prayogo** ([@Arif199630](https://github.com/Arif199630))  
> Proyek pengujian otomasi komprehensif skala *enterprise* untuk platform transportasi listrik pintar (**eVMOTO**) dan ekosistem *battery swap* (**ECGO**), mencakup **REST API Testing**, **Web Admin Console**, **Driver Mobile App**, **Passenger Mobile App**, dan **SuperApps Interconnection**.

---

## 🌟 Executive Summary & Key Achievements

* 📊 **1.180+ Test Cases Terotomasi & Terdokumentasi Lengkap:**
  * ⚡ **API Automation Suite:** **31 Test Scenarios** (Autentikasi OTP/Bypass, Driver Telemetry & Order, Passenger Lifecycle & Fare, Security & Fraud Defense, Boundary Tests, ECGO Swap, Dompet Digital).
  * 🌐 **Web Admin Console:** **608 Test Cases** (25 modul administrasi, penetapan tarif, manajemen armada & driver, verifikasi order).
  * 🛵 **Driver Mobile App:** **299 Test Cases** (Autentikasi, alur order, pendapatan jaminan GI, dompet eWallet, sewa motor & cicilan ECGO).
  * 👤 **Passenger Mobile App:** **237 Test Cases** (Booking, live dispatch, multi-payment, riwayat perjalanan, profil).
* 🔄 **Interkoneksi 3-Sisi (ECGO Connect & Free Swap Kupon):**
  * Handshake penautan akun *One-Way Binding* antara **ECGO SuperApps** $\leftrightarrow$ **EvMoto Driver App** $\leftrightarrow$ **Dashboard Admin**.
  * Otomasi evaluasi sesi online 5 menit untuk penerbitan kupon diskon 100% swap baterai secara realtime.
* ⚡ **CI/CD Pipeline Terpadu (GitHub Actions):**
  * Terintegrasi dengan **GitHub Actions** untuk validasi sintaks, contract testing, kompilasi kode, dan eksekusi pengujian integrasi *headless* tanpa membebani GUI emulator.
* 🛡️ **Keamanan & Manajemen Lingkungan (.env Architecture):**
  * Seluruh endpoint internal, kredensial pengujian, dan token autentikasi diproteksi melalui arsitektur Environment Variable terisolasi (`.env.example` template) demi standar kepatuhan keamanan *open-source*.

---

## 🏛️ Arsitektur Repository (Monorepo Clean Architecture)

Struktur direktori dirancang dengan prinsip modularitas tinggi agar mudah dipahami oleh tim rekrutmen (*HRD / Lead QA*):

```text
├── .github/
│   └── workflows/
│       └── ci.yml                     # Pipeline GitHub Actions (API & Headless Integration CI)
├── api-testing/                       # [MODUL API AUTOMATION SUITE]
│   ├── client/                        # Reusable HTTP API Client & Session Manager
│   ├── config/                        # Dynamic Environment Loader & Endpoints
│   ├── schemas/                       # JSON Schema & Contract Validation (jsonschema)
│   ├── suites/                        # Pytest Test Suites (Auth, Driver, User, ECGO, Wallet, Security, Boundary)
│   ├── conftest.py                    # Session Fixtures & Mock Fallback Handler
│   └── README.md                      # Dokumentasi Teknis API Testing
├── mobile-apps/                       # Kerangka Otomasi Mobile (Appium + Pytest)
│   ├── config/                        # Endpoints API, Capabilities, Multi-Environment
│   ├── core/                          # BasePage POM, DriverFactory, Appium Custom Wrappers
│   ├── Frontend/Feature/
│   │   ├── Pages/                     # Page Object Model (User & Driver Screens)
│   │   ├── Step_Definition/           # Test Suites BDD (test_drv_*.py & test_*.py)
│   │   └── Data/                      # Dataset Pengujian 4 Pilar QA (drv_data.py)
│   └── pytest.ini                     # Konfigurasi Test Runner & Marker
├── web-dashboard/                     # Otomasi Web Admin Console (Selenium / Headless HTTP)
│   ├── config.py                      # Konfigurasi Environment Dashboard (Dev & Prod)
│   └── record_dashboard_price_bug.py  # Automation Script Verifikasi Form Tarif
├── integration-ecosystem/             # Pengujian Interkoneksi Terpadu 3-Sisi
│   └── test_ecgo_connect_integrated_suite.py # Multi-Role Actor Test Suite (100% Headless)
├── apps/                              # Spesifikasi & Metadata Build APK
│   └── README.md                      # Metadata Versi APK, Package, Checksum & Release Links
├── docs/                              # Dokumentasi Resmi & Laporan QA
│   └── reports/                       # Matriks Excel (.xlsx) & Laporan Manual (.md)
├── .env.example                       # Template Konfigurasi Environment (Sanitized / Rekayasa)
├── .gitignore                         # Mengabaikan cache, log, credentials, dan binary 100MB+
├── requirements.txt                   # Dependensi Python
└── README.md                          # Dokumentasi Utama Portofolio
```

---

## 📱 Ruang Lingkup Aplikasi & Endpoint Teruji

| Komponen Sistem | Target Aplikasi / Endpoint | Lingkungan | Platform & Tools |
| :--- | :--- | :---: | :--- |
| **REST API Services** | `https://api-dev.evmoto.internal` *(Masked)* | Staging / Dev | Pytest, Requests, JSONSchema, Contract Testing |
| **Web Admin Console** | `https://admin-staging.evmoto.internal` *(Masked)* | Staging / Dev | Selenium, Headless Chrome, Requests |
| **Driver Mobile App** | `evmoto-driver-1.9.27-env-dev_golang-20261020-v7a.apk` | Golang Dev | Appium, UiAutomator2, Pytest BDD |
| **Passenger App** | `evmoto-user-1.2.33-env-dev_golang-20261020-v8a.apk` | Golang Dev | Appium, UiAutomator2, Pytest BDD |
| **ECGO SuperApps** | `ECGO SuperApps.apk` (`https://ecgo-api.internal:3002`) | Dev API | Headless Protocol, Web Bridge Handshake |

> *Catatan Keamanan:* Semua domain internal, IP server staging, nomor telepon uji coba, dan kredensial dalam dokumentasi publik direkayasa atau dimuat via environment variable demi menjaga kerahasiaan data internal.

---

## 🚦 Menjalankan Pengujian Lokal (Quick Start)

### 1. Kloning Repositori & Persiapan Environment
```bash
git clone https://github.com/Arif199630/evmoto-qa-automation-ecosystem.git
cd evmoto-qa-automation-ecosystem

# Buat virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependensi
pip install -r requirements.txt

# Siapkan file environment lokal dari template
cp .env.example .env
```

### 2. Menjalankan Suite API Automation
```bash
cd api-testing
pytest -v suites/
```

### 3. Menjalankan Suite Integrasi 3-Sisi (Headless - Cepat & Ringan)
Suite ini mengeksekusi peran Superadmin, Driver SuperApps, dan Driver EvMoto secara simultan tanpa memerlukan emulator:
```bash
cd integration-ecosystem
pytest -v test_ecgo_connect_integrated_suite.py
```

### 4. Menjalankan Suite Otomasi Mobile (Appium)
```bash
cd mobile-apps
# Jalankan pengujian modul driver tertentu:
pytest -v Frontend/Feature/Step_Definition/test_drv_home.py
# Atau jalankan seluruh suite sewa & cicilan motor:
pytest -v Frontend/Feature/Step_Definition/test_drv_rental_installment.py
```

---

## 📊 Matriks & Laporan Pengujian Resmi

Dokumentasi lengkap test cases dapat diakses pada folder [docs/reports/](docs/reports/):
* 📗 **[Test_Cases_EvMoto_Mobile.xlsx](docs/reports/Test_Cases_EvMoto_Mobile.xlsx):** Matriks 536 Test Cases Mobile Apps (Bahasa Indonesia).
* 📘 **[Test_Cases_EvMoto_Mobile_EN.xlsx](docs/reports/Test_Cases_EvMoto_Mobile_EN.xlsx):** Matriks 536 Test Cases Mobile Apps (Bahasa Inggris).
* 📙 **[Test_Cases_Manual_ECGO_Connect_Interconnection.xlsx](docs/reports/Test_Cases_Manual_ECGO_Connect_Interconnection.xlsx):** Matriks Pengujian Manual Interkoneksi 3-Sisi.
* 📝 **[Test_Cases_Manual_ECGO_Connect_Interconnection.md](docs/reports/Test_Cases_Manual_ECGO_Connect_Interconnection.md):** Panduan Langkah Pengujian Step-by-Step QA.

---

## 👨‍💻 Profil Author & QA Engineer

* **Nama:** Bhagus Arif Prayogo
* **GitHub:** [@Arif199630](https://github.com/Arif199630)
* **Keahlian:** Mobile & Web Test Automation, API Testing & Contract Validation, Performance Testing, CI/CD Pipeline Design, QA Strategy & 4 Pillars Methodology.
