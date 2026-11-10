# EvMoto User App - Mobile QA Automation Framework 📱

Framework pengujian otomatisasi mobile berstandar industri (*Enterprise Mobile QA Automation*) untuk menguji **Aplikasi Pengguna / Penumpang Ojek Online EvMoto** (`com.evmoto.user.app`).

Framework ini mengadopsi arsitektur **Page Object Model (POM)** terpusat anti-hardcode, **BDD (Given - When - Then)**, metodologi **4 Pilar QA**, dan simulasi **Human-like Pacing**.

---

## 🎯 Konsep Arsitektur Proyek (Page Object Model Ringkas & Efisien)

1. **Folder Pages (`Frontend/Feature/Pages/`)**:
   - **Pusat berkumpulnya data XPath dan Elemen ID** aplikasi (Login, Register, Home, Booking, Tracking, Profile, Splash).
   - Setiap layar cukup didefinisikan dalam **1 file Page Object** utuh di dalam folder `Pages/`, memuat langsung seluruh elemen XPath / ID beserta metode interaksinya tanpa perlu membuat subfolder terpisah `locators/`.

2. **Folder Test Data (`Frontend/Feature/Data/`)**:
   - Menyimpan seluruh data multi-user dan payload pengujian (Dev User, Penumpang Aktif, Penumpang Korporat, User Baru/Unregistered, Akun Invalid, SQLi/XSS).

3. **Folder Step Definition (`Frontend/Feature/Step_Definition/`)**:
   - Berisi seluruh skenario pengujian dengan metodologi **4 Pilar QA** dan alur interaksi **Given - When - Then** (BDD).

---

## 📂 Struktur Direktori Proyek

```text
evmoto-user-mobile-automation/
│
├── config/                       # Konfigurasi Appium & Desired Capabilities
├── core/                         # BasePage & Appium Driver Factory
│
├── Frontend/
│   └── Feature/
│       ├── Pages/                # 📁 PUSAT ELEMEN ID / XPATH & PAGE OBJECT (1 FILE PER LAYAR)
│       │   ├── __init__.py       # Exporter seluruh Page Object & Locator alias
│       │   ├── login_page.py     # Layar Login & OTP (memuat AppiumBy XPath + aksi)
│       │   ├── register_page.py  # Form registrasi akun baru (memuat AppiumBy XPath + aksi)
│       │   ├── home_page.py      # Beranda & navigasi bawah (memuat AppiumBy XPath + aksi)
│       │   ├── booking_page.py   # Rute, promo, & checkout (memuat AppiumBy XPath + aksi)
│       │   ├── profile_page.py   # Profil, pengaturan, & logout (memuat AppiumBy XPath + aksi)
│       │   ├── splash_page.py    # Splash & onboarding (memuat AppiumBy XPath + aksi)
│       │   └── tracking_page.py  # Live trip tracking & status driver (XPath + aksi)
│       │
│       ├── Data/                 # 📁 PUSAT TEST DATA MULTI-USER & AUTH (1 FILE UTUH)
│       │   ├── users.json        # Database JSON multiple user
│       │   └── user_data.py      # Provider multi-user & dataset 4 pilar lengkap
│       │
│       └── Step_Definition/      # 📁 PUSAT TEST SCENARIO & STEP DEFINITIONS (4 PILAR QA)
│           ├── test_login.py     # Suite Login 4 Pilar
│           ├── test_register.py  # Suite Register 4 Pilar
│           ├── test_profile.py   # Suite Profil & Akun Pengguna 4 Pilar
│           └── test_e2e_live_demo.py # Live Demo End-to-End
│
└── utils/                        # 📁 UTILITIES
    ├── bdd_helper.py             # Helper BDD (given, when, then, and_step)
    ├── human_pacing.py           # Simulasi touch & typing natural
    ├── logger.py                 # Logger otomasi
    └── video_recorder.py         # Perekam video otomatis layar emulator
```

---

## 🚀 Contoh Penerapan BDD (Given - When - Then) di Mobile Test Case

```python
from pages.login_page import LoginPage
from pages.home_page import HomePage
from test_data.user_data import MobileUserDataProvider
from utils.bdd_helper import given, when, then, and_step

def test_login_mobile_berhasil(driver):
    login_page = LoginPage(driver)
    home_page = HomePage(driver)
    phone, otp = MobileUserDataProvider.get_credentials("dev_user")

    # GIVEN: Kondisi awal
    given("Aplikasi EVMoto terbuka dan menampilkan layar Login awal")
    login_page.is_login_screen_displayed(timeout=15)

    # WHEN: Aksi pengguna
    when(f"Pengguna menginput nomor telepon terdaftar '{phone}' dan menekan tombol Log In")
    login_page.input_phone_number(phone)
    login_page.click_submit_login()

    and_step(f"Pengguna memasukkan kode verifikasi OTP dev '{otp}'")
    login_page.input_otp_dev(otp, fast_transition=True)
    login_page.handle_location_prompt_if_present()

    # THEN: Ekspektasi hasil
    then("Sistem berhasil mengautentikasi dan mengarahkan pengguna ke Beranda utama EVMoto")
    assert home_page.is_home_screen_displayed(timeout=20)
```
