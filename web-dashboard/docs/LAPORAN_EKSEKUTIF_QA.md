# Laporan Eksekutif Otomatisasi Pengujian (Executive QA Automation Report)

| Informasi Proyek | Keterangan |
|---|---|
| **Aplikasi Target** | eVMOTO Admin Management Web Service |
| **URL Aplikasi** | `https://dashboard.evmotoid.com` |
| **Pola Arsitektur** | **Page Object Model (POM)** |
| **Teknologi Utama** | Python 3.12, Selenium WebDriver, Unittest Framework |
| **Total Cakupan Pengujian** | **104 Test Cases** (Positif, Negatif, & Validasi Keamanan) |
| **Status Keseluruhan** | **100% Siap Digunakan & Terstruktur Rapi** |

---

## 1. Latar Belakang & Tujuan Rekayasa

Pengujian manual terhadap sistem administrasi eVMOTO yang memiliki banyak modul dan formulir kompleks membutuhkan waktu berjam-jam setiap kali ada pembaruan kode (*deployment*).

Tujuan penerapan proyek otomatisasi ini adalah:
1. **Memastikan Stabilitas Sistem (Regression Testing)**: Mencegah bug lama muncul kembali setelah adanya rilis fitur baru.
2. **Efisiensi Waktu & Biaya (ROI Tinggi)**: Pengujian manual yang memakan waktu > 4 jam kini dapat dijalankan secara otomatis dalam hitungan menit.
3. **Standarisasi Kualitas Perusahaan**: Memastikan setiap alur kerja penting (autentikasi, perizinan role, persetujuan driver, kemitraan kota) tervalidasi secara konsisten.

---

## 2. Mengapa Memilih Arsitektur Page Object Model (POM)?

Bagi manajemen, pemilihan arsitektur ini memberikan manfaat langsung terhadap biaya pemeliharaan (*maintenance cost*):

```
+-------------------------------------------------------------+
|                      KEUNTUNGAN BISNIS                      |
+-------------------------------------------------------------+
| 1. Keterbacaan Tinggi  : Bahasa skrip pengujian mencerminkan |
|                          logika bisnis nyata.               |
| 2. Perawatan Mudah     : Locator HTML terpusat di pages/.   |
| 3. Tidak Ada Redundansi: Helper login digunakan bersama     |
|                          oleh seluruh modul.                |
| 4. Onboarding Cepat    : QA engineer baru langsung paham    |
|                          struktur kode dalam hitungan hari. |
+-------------------------------------------------------------+
```

---

## 3. Matriks Hasil Cakupan Pengujian (104 Tests)

Berikut adalah rekapitulasi lengkap pengujian per modul:

| No | Modul Sistem | File Test Script | Page Object | Jumlah Test | Cakupan Skenario |
|:---:|---|---|---|:---:|---|
| 1 | **Halaman Login** | `tests/test_01_login.py` | `LoginPage` | 6 Tests | Kredensial valid, invalid password, invalid username, form required validation. |
| 2 | **Dashboard / Beranda** | `tests/test_02_home.py` | `HomePage` | 6 Tests | 3 Widget metrik operasional, filter tanggal, Dark/Light mode toggle, profil & logout. |
| 3 | **Account Cancellation** | `tests/test_03_account_cancellation.py` | `AccountCancellationPage` | 7 Tests | Filter status cleared, pencarian nama customer, aktivasi tombol aksi, proteksi akun tertutup. |
| 4 | **System Management** | `tests/test_04_system_management.py` | `SystemManagementPage` | 13 Tests | Platform Admin (`/mgr`), Role (`/role`), Menu (`/menu`), dan Departemen (`/dept`). |
| 5 | **Enterprise Management** | `tests/test_05_enterprise_management.py` | `EnterprisePage` | 9 Tests | Profil perusahaan, interaktivitas kota mitra & badge counter, tabel antrean audit mitra. |
| 6 | **User Management** | `tests/test_06_user_management.py` | `UserManagementPage` | 7 Tests | Tabel customer, pencarian no telepon & nickname, aktivasi tombol rincian/saldo, modal kode promo. |
| 7 | **Agreement Management** | `tests/test_07_agreement_management.py` | `AgreementPage` | 18 Tests | Multi-bahasa (CN/EN/ID), Rich Text Editor, 9 toolbar formatting, 6 sub-halaman legalitas. |
| 8 | **Urban Management** | `tests/test_08_urban_management.py` | `UrbanPage` | 15 Tests | Kota operasional, Hot Address (pencarian lokasi strategis), tautan service area di sidebar. |
| 9 | **Driver Management** | `tests/test_09_driver_management.py` | `DriverPage` | 23 Tests | Audit driver baru, pergantian kendaraan armada, daftar driver aktif, rincian potongan withholding. |
| **TOTAL** | **9 Modul Utama** | | | **104 Tests** | **Cakupan Menyeluruh** |

---

## 4. Struktur Repositori Siap-GitHub

Struktur folder ini dirancang mengikuti standar baku industri agar siap ditinjau (*peer review*) oleh atasan maupun tim engineering:

```text
📁 Automation_Project_EvMoto/
│
├── 📄 .gitignore                 -> Standar ignore file cache Python & OS
├── 📄 requirements.txt           -> Daftar dependensi library resmi
├── 📄 config.py                  -> Konfigurasi global terpusat
├── 📄 main_runner.py             -> Eksekutor utama seluruh rangkaian 104 pengujian
├── 📄 README.md                  -> Dokumentasi resmi proyek untuk publik & tim
│
├── 📁 pages/                     -> LAPISAN OBJECT HALAMAN (Web Model)
│   ├── base_page.py              -> Wrapper reusable helper Selenium
│   ├── login_page.py             -> Model Halaman Login
│   ├── home_page.py              -> Model Dashboard
│   ├── account_cancellation_page.py
│   ├── system_management_page.py
│   ├── enterprise_page.py
│   ├── user_management_page.py
│   ├── agreement_page.py
│   ├── urban_page.py
│   └── driver_page.py
│
├── 📁 tests/                     -> LAPISAN KASUS PENGUJIAN (Test Scripts)
│   ├── test_01_login.py
│   ├── test_02_home.py
│   ├── test_03_account_cancellation.py
│   ├── test_04_system_management.py
│   ├── test_05_enterprise_management.py
│   ├── test_06_user_management.py
│   ├── test_07_agreement_management.py
│   ├── test_08_urban_management.py
│   └── test_09_driver_management.py
│
└── 📁 docs/                      -> DOKUMENTASI MANAJERIAL & MAINTENANCE
    ├── LAPORAN_EKSEKUTIF_QA.md   -> Laporan formal untuk atasan/manajemen
    └── PANDUAN_MAINTENANCE_POM.md -> Petunjuk teknis pemeliharaan kode
```

---

## 5. Kesimpulan & Rekomendasi Selanjutnya

1. **Siap Diintegrasikan ke CI/CD**: Proyek ini dapat langsung dipasang ke dalam pipeline GitHub Actions atau Jenkins untuk pengujian otomatis setiap kali ada pull request dari developer.
2. **Mudah Diperluas**: Jika ada modul baru di masa mendatang (seperti *Vehicle Management* atau *Order Management*), tim QA cukup membuat 1 file baru di `pages/` dan 1 file baru di `tests/` tanpa mengganggu modul yang sudah ada.
