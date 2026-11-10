# Automation Project EvMoto 🚀 (Page Object Model & BDD Architecture)

Framework Otomatisasi Pengujian Web Admin eVMOTO menggunakan Python, Selenium WebDriver, dan arsitektur **Page Object Model (POM)** berbasis **4 Pilar Testing** serta **BDD (Given - When - Then)**.

- **Website Target**: [https://dashboard.evmotoid.com](https://dashboard.evmotoid.com)
- **Multi-User Data**: Tersimpan terpusat di `test_data/users.json` via `UserDataProvider`

---

## 🎯 Konsep Arsitektur Proyek (Page Object Model Ringkas & Efisien)

Proyek ini telah direstrukturisasi agar rapi, modular, dan bersih:

1. **Folder Pages (`Frontend/Feature/Pages/`)**:
   - **Pusat berkumpulnya seluruh data XPath, Elemen ID, dan CSS Selector** dashboard admin EvMoto.
   - Setiap modul web cukup didefinisikan dalam **1 file Page Object** di dalam folder `Pages/`, memuat langsung seluruh locator elemen bersama metode interaksinya tanpa perlu membuat subfolder terpisah `locators/`.
   - Jika UI website berubah, cukup perbarui locator di file modul terkait di dalam folder `Pages/`.

2. **Folder Test Data (`Frontend/Feature/Data/`)**:
   - Menyimpan seluruh data multi-user (`users.json`) seperti `super_admin`, `branch_manager`, `driver_auditor`, `finance_officer`, akun invalid, payload SQLi, dan XSS.
   - Diakses melalui helper `UserDataProvider.get_credentials("super_admin")`.

3. **Folder Step Definition (`Frontend/Feature/Step_Definition/`)**:
   - Berisi skrip skenario pengujian bisnis yang menerapkan metodologi **4 Pilar QA** dan logika **Given - When - Then** (BDD).

---

## 📂 Struktur Direktori Proyek

```text
Automation_Project_EvMoto/
│
├── config.py                     # Konfigurasi global (Base URL, Driver Chrome & Environment)
├── main_runner.py                # Runner pengujian otomatis 19 modul lengkap
│
├── Frontend/
│   └── Feature/
│       ├── Pages/                # 📁 PUSAT ELEMEN ID / XPATH & PAGE OBJECT (1 FILE PER MODUL)
│       │   ├── __init__.py       # Package exporter semua page class
│       │   ├── page_base.py      # Class Induk Selenium (Explicit wait, click, type)
│       │   ├── page_visual_pacer.py # Visual pacer helper
│       │   ├── page_00_login.py  # POM Login Page (ID, CSS & aksi)
│       │   ├── page_01_account_cancellation.py # POM Pembatalan Akun (Menu #1)
│       │   ├── page_02_home.py   # POM Beranda & Widget Dashboard (Menu #2)
│       │   ├── page_03_system_management.py # POM Manajemen Sistem (Menu #3)
│       │   ├── page_04_user_management.py   # POM Manajemen Pengguna (Menu #4)
│       │   └── ... (Modul 05 hingga 24)
│       │
│       ├── Data/                 # 📁 PUSAT TEST DATA MULTI-USER & KREDENSIAL
│       │   ├── users.json        # Database kredensial user (Admin, Manager, Auditor, Attacker)
│       │   └── user_data.py      # Provider Python untuk query user dinamis & env overrides
│       │
│       └── Step_Definition/      # 📁 PUSAT TEST SCENARIO & STEP DEFINITIONS (4 PILAR QA)
│           ├── test_00_login.py  # Test suite Login 4 Pilar
│           ├── test_01_account_cancellation.py # Test suite Pembatalan Akun
│           ├── test_02_home.py   # Test suite Beranda & Dashboard
│           └── ... (Test suite modul 03 hingga 24)
│
└── utils/                        # 📁 HELPER & UTILITIES
    ├── bdd_helper.py             # Helper BDD (given, when, then, and_step)
    ├── bug_tracker.py            # Pencatat otomatis bug & anomali
    └── test_interceptor.py       # Interceptor eksekusi pengujian
```

---

## 🚀 Contoh Penerapan BDD (Given - When - Then) di Test Case

```python
from pages.login_page import LoginPage
from test_data.user_data import UserDataProvider
from utils.bdd_helper import given, when, then, and_step

def test_login_berhasil(self):
    user, pwd = UserDataProvider.get_credentials("super_admin")

    # GIVEN: Kondisi awal
    given("Pengguna membuka halaman Login EvMoto Dashboard")
    self.login_page.navigate()

    # WHEN: Aksi pengguna
    when(f"Pengguna menginput username '{user}' dan password valid lalu menekan Submit")
    self.login_page.login(user, pwd)

    # THEN: Ekspektasi hasil
    then("Sistem mengarahkan pengguna ke halaman Dashboard (/blackboard)")
    self.login_page.wait_for_url_contains("/blackboard")
    
    and_step("Dashboard shell utama berhasil ditampilkan di layar")
    self.assertTrue(self.login_page.is_dashboard_displayed())
```
