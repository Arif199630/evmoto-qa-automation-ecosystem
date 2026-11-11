# Panduan QA Automation Junior: Mobile EvMoto (User App & Driver App)

Dokumen ini menjelaskan cara menjalankan dan menambah test untuk aplikasi EvMoto User (penumpang) dan Driver (mitra), termasuk test yang terhubung ke web admin. Baca sekali dari atas, lalu jadikan rujukan.

## 1. Tiga mode menjalankan test

| Mode | Kapan | Yang benar-benar diuji |
|---|---|---|
| **Device / emulator + Appium** | Uji aplikasi sungguhan | Layar, tombol, dan alur aplikasi APK |
| **Headless** (`HEADLESS_MOBILE=1`) | Tanpa emulator, misalnya di CI | Alur test dan Page Object terhadap **simulator** `HeadlessMobileDriver`, bukan aplikasi |
| **API** (`api-testing/`) | Uji backend | Endpoint backend staging lewat HTTP |

Penting: hasil mode headless **bukan** bukti aplikasi berjalan benar. Simulator hanya meniru sebagian layar. Di akhir run, pytest menulis berapa sesi yang memakai simulator, supaya hasilnya tidak disalahartikan.

## 2. Akun dan environment staging

| Item | Nilai |
|---|---|
| Backend API | `https://evmotodev.justkidding.app` |
| Web admin | `https://evmotoadmin.justkidding.app` |
| Akun User | `<TEST_USER_PHONE>`, OTP bypass `<EVMOTO_OTP_BYPASS>` |
| Akun Driver | `<TEST_DRIVER_PHONE>`, OTP bypass `<EVMOTO_OTP_BYPASS>` |

Semua nilai ini ada di `.env`. Jangan menulis nomor, OTP, atau password langsung di file test; ambil dari `config` atau `Frontend/Feature/Data/`.

## 3. Struktur folder

```text
evmoto-user-mobile-automation/
├── conftest.py                Satu-satunya conftest: fixture driver, screenshot saat gagal
├── config/                    URL, akun, capability Appium
├── core/
│   ├── base_page.py           Induk semua Page Object (tunggu, klik, ketik)
│   ├── driver_factory.py      Memilih Appium atau simulator headless
│   └── headless_mobile_driver.py   Simulator untuk mode headless
├── Frontend/Feature/
│   ├── Pages/                 Satu file per layar: locator + aksi
│   ├── Data/                  Data test
│   ├── Helper/                Helper lintas aplikasi (admin dispatch, rush hour, tarif, simulator driver)
│   └── Step_Definition/       Skenario test
└── api-testing/               Test REST API backend
```

Penamaan file test:

| Awalan | Isi |
|---|---|
| `test_login`, `test_home`, `test_booking_order`, `test_activity`, `test_profil`, `test_register`, `test_gopay_payment`, `test_ovo_payment` | User App |
| `test_drv_*` | Driver App |
| `test_admin_*`, `test_dispatch_*`, `test_drv_batch_*`, `test_drv_order_hall_*`, `test_e2e_*` | Lintas aplikasi: Admin, Driver, dan User |

## 4. Cara menjalankan

```bash
pip install -r requirements.txt
```

Semua test mobile tanpa emulator:

```bash
HEADLESS_MOBILE=1 HEADLESS_FAST=1 ENVIRONMENT=dev python -m pytest -q -o addopts=""
```

Hanya Driver App, 4 proses paralel:

```bash
HEADLESS_MOBILE=1 HEADLESS_FAST=1 ENVIRONMENT=dev python -m pytest Frontend/Feature/Step_Definition -k "drv" -n 4 -q -o addopts=""
```

API ke backend staging:

```bash
cd api-testing
EVMOTO_API_BASE_URL=https://evmotodev.justkidding.app python -m pytest -q -o addopts=""
```

`MOCK_API_FALLBACK` sekarang default `false`. Bila dinyalakan, test API bisa lulus tanpa server, jadi hasilnya bukan uji backend.

## 5. Aturan menulis test

1. **Assertion harus bisa gagal.** Jangan menulis `assert True` atau `assert x or True`. Keduanya selalu lulus, sehingga bug tidak pernah tertangkap.

   ```python
   # Salah: selalu lulus
   assert home_page.is_home_screen_displayed() or True

   # Benar
   assert home_page.is_home_screen_displayed(), "Beranda harus tampil setelah login"
   ```

2. **Panggil hanya method yang ada di Page Object.** Sebelum memakai `login_page.xxx()`, cek dulu method itu ada di `Pages/login_page.py`. Bila belum ada, buat dulu di Page Object, jangan di file test.
3. **Jangan menelan error.** Hindari `try: ... except Exception: pass` di setup. Bila login gagal, test harus berhenti dengan pesan jelas, bukan lanjut diam-diam.
4. **Satu conftest saja**, di root. Menyalin `conftest.py` ke subfolder membuat fixture dan hook terdaftar berulang kali.
5. **Locator di Page Object, assertion di Step_Definition.**

## 6. Perapian 9 November 2026

| Perubahan | Alasan |
|---|---|
| `Frontend/conftest.py` dan `Step_Definition/conftest.py` dipindah ke `_archive/` | Salinan dari `conftest.py` root, sehingga hook laporan kegagalan terdaftar tiga kali |
| `LoginPage.login(phone, otp)` ditambahkan | Dipanggil `test_activity.py` dan `test_e2e_master_flow.py` tetapi belum ada, sehingga 35 test error saat setup |
| 12 pemanggilan method yang tidak ada diganti ke method yang ada | Contoh: `is_home_displayed` menjadi `is_home_screen_displayed`, `login_with_pin` menjadi `login_as_driver` |
| 33 `assert ... or True` diubah menjadi assertion biasa | Sebelumnya tidak pernah bisa gagal |
| 126 `assert True` diberi penanda `TODO(QA)` | Belum memverifikasi apa pun; perlu diganti assertion nyata |
| Ringkasan sesi simulator di akhir run | Agar jelas kapan hasil berasal dari simulator |
| `MOCK_API_FALLBACK` default `false` | Agar test API tidak lulus tanpa server |
| Script coba-coba dan screenshot lepas di root dipindah ke `_archive/` | Root folder lebih mudah dibaca |

Pekerjaan yang masih terbuka:
- `test_e2e_master_flow.py` memanggil sekitar 27 method yang belum ada di Page Object. Suite ini perlu ditulis ulang mengikuti method yang tersedia.
- `AdminDashboardFareCalculator` belum punya `calculate_waiting_fee`, `calculate_all_in_one`, dan `calculate_cancellation_fase_c`. Aturan tarifnya perlu diambil dari PRD harga, jangan ditebak.
- `DrvMenuPage.scroll_down` belum ada.
- `run_ecosystem_regression_1258_tc.py` menulis angka PASS tetap di PDF tanpa menjalankan test. Jangan dipakai sebagai bukti hasil test.

Backup sebelum perapian: folder `evmoto-user-mobile-automation_backup_2026-11-09` di samping folder ini.

## 7. Cara kerja baru (10 November 2026)

- **Satu perintah untuk regression:** `python ../evmoto-qa-tools/run_all.py --suite all`. Urutannya quality gate, pengaman staging, test per file, lalu laporan PDF di `../evmoto-qa-tools/runs/`. Panduan lengkap ada di `../evmoto-qa-tools/README.md`.
- **Hanya dev/staging.** `staging_guard.py` membatalkan run bila `ENVIRONMENT` bukan dev/staging, atau bila URL mengarah ke `dashboard.evmotoid.com`, `api.evmotoid.com`, `new-api.evmotoid.com`.
- **Quality gate menolak pelanggaran baru:** method yang tidak ada, `assert True` atau `assert x or True`, domain production di file test, file test duplikat. Jalankan `python ../evmoto-qa-tools/quality_gate.py admin` atau `mobile` sebelum commit.
- **Fitur baru:** mulai dari `templates/template_test_fitur_baru.py`.
- **Skip selalu beralasan:** pakai `self.skipTest("alasan")` (Admin) atau `pytest.skip("alasan")` / `@pytest.mark.quarantine(reason="...")` (Mobile/API). Jangan menulis assertion yang selalu lulus.

## 8. Sumber angka bisnis (11 November 2026)

- **Tarif dan subsidi jam sibuk diambil dari Admin Dashboard environment aktif**, bukan angka yang ditulis di test. Pembacanya: `core/admin_config_reader.py` (hanya membaca halaman, tidak menyimpan apa pun).
  - Tarif: Price control > Motorcycle Price Settings (`/tSystemPrice/special`), baris Driver dan User.
  - Jam sibuk: Subsidi jam sibuk > Pengaturan (`/rushHour/settings`).
- Membandingkan tarif di layar aplikasi: pakai `AdminDashboardFareCalculator.from_admin("User")`. Konstanta bawaan kalkulator adalah angka dokumen production dan hanya untuk unit test rumus.
- Biaya e-wallet memakai rumus gross-up: `ceil(subtotal x 100 / (100 - rate))`, GoPay 2%, OVO 1,665%.
- `api-testing/suites/test_admin_config_api.py` memeriksa konfigurasi itu sendiri (tarif Driver = User, window jam sibuk valid, tier naik). Kegagalan di sana adalah temuan konfigurasi, bukan bug kode aplikasi.
