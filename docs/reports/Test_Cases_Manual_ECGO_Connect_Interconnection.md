# Test Case Manual: Interkoneksi Terpadu ECGO Connect (Dashboard Admin, ECGO SuperApps, & EvMoto Driver)

## 📌 Informasi Pengujian
* **Proyek:** Interkoneksi 3-Sisi Layanan ECGO Connect & Kupon Free Swap Baterai
* **Environment:** Staging / Development (Golang Base)
* **Target Sistem:**
  1. **Web Admin Dashboard:** `https://admin-staging.evmoto.internal` (User: `admin_qa_temp` / PIN: `******`)
  2. **ECGO SuperApps (API Backend):** `https://ecgo-api.internal:3002` (HP: `0812-XXXX-7237` / OTP Bypass: `******`)
  3. **EvMoto Driver App:** `https://api-dev.evmoto.internal` (HP: `0812-XXXX-7237` / PIN Bypass: `1234`)
  4. **Web Connect Bridge:** `https://connect.evmoto.internal/connect`
* **Metodologi Pengujian:** Multi-Role Actor Pattern (Role Admin, Role Driver SuperApps, Role Driver EvMoto)
* **Status Eksekusi:** **100% PASSED (Automated Headless & Protocol Verified)**

---

## 📋 Matriks Test Case Manual Terintegrasi (End-to-End)

| No | TC ID | Peran / Aktor | Modul / Halaman | Deskripsi Pengujian | Pre-kondisi | Langkah Pengujian | Data Uji | Hasil yang Diharapkan | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | `TC-MAN-ECGO-01` | **Admin Dashboard** | `/login` & `/blackboard` | Login Superadmin menggunakan kredensial akun dev `admin_qa_temp` | Layar login terbuka di browser | 1. Input username `admin_qa_temp`<br>2. Input password `******`<br>3. Pilih bahasa English<br>4. Klik tombol Login | User: `admin_qa_temp`<br>Pass: `******` | Berhasil autentikasi dan dialihkan (*redirect*) ke halaman `/blackboard` dengan status HTTP 200 | **PASS** |
| 2 | `TC-MAN-ECGO-02` | **Admin Dashboard** | `/ecgoConnect` | Validasi fungsionalitas formulir dan parameter halaman Pengaturan ECGO Connect | Superadmin sudah login | 1. Klik menu Pengaturan ECGO Connect<br>2. Periksa blok konfigurasi armada, diskon, dan model | URL: `/ecgoConnect` | Seluruh form kontrol tampil normal (`section`: car, discount, color, model) tanpa error layout | **PASS** |
| 3 | `TC-MAN-ECGO-03` | **Admin Dashboard** | `/freeSwap` | Verifikasi konfigurasi aturan harian kupon Free Swap Baterai (Target 5 Menit) | Superadmin sudah login | 1. Buka halaman Free Swap Baterai<br>2. Periksa input Target Online Menit<br>3. Periksa besaran diskon dan kuota | URL: `/freeSwap`<br>Target: 5 menit<br>Amount: 100% | Formulir memuat target 5 menit, kuota harian 1, dan besaran diskon 100% secara presisi | **PASS** |
| 4 | `TC-MAN-ECGO-04` | **Driver SuperApps** | Onboarding / Auth | Autentikasi akun mitra pada ECGO SuperApps dengan bypass OTP SMS | Nomor HP terdaftar di server dev | 1. Masukkan nomor HP `0812-XXXX-7237`<br>2. Request OTP via SMS<br>3. Masukkan kode bypass `******` | HP: `0812-XXXX-7237`<br>OTP: `******` | Login berhasil, server menerbitkan JWT auth token dengan status `verified` | **PASS** |
| 5 | `TC-MAN-ECGO-05` | **Driver EvMoto** | Driver Auth | Autentikasi mitra pengemudi pada EvMoto Driver Apps dengan PIN bypass | Akun driver terdaftar di EvMoto | 1. Kirim permintaan captcha/PIN<br>2. Submit nomor HP dan PIN `1234`<br>3. Verifikasi token driver | HP: `0812-XXXX-7237`<br>PIN: `1234` | Login sukses, memperoleh Driver ID `546` dan token sesi aktif | **PASS** |
| 6 | `TC-MAN-ECGO-06` | **Driver SuperApps** | ECGO Connect | Inisiasi penautan akun dari ECGO SuperApps ke jembatan web connect | Driver telah login di SuperApps | 1. Buka menu integrasi EvMoto Connect<br>2. Tekan tombol Hubungkan Akun<br>3. Ambil URL handshake web connect | Endpoint: `/v5/users/evmoto-connect/start` | Sistem merespon sukses dengan URL `https://connect.evmoto.internal/connect` beserta token sesi | **PASS** |
| 7 | `TC-MAN-ECGO-07` | **Driver SuperApps** | Web Bridge | Konfirmasi One-Way Linking pada portal web connect jembatan EvMoto-ECGO | Token web bridge aktif | 1. Buka URL web connect<br>2. Verifikasi data armada B9001DEV<br>3. Klik tombol "Hubungkan Akun"<br>4. Ikuti alur redirect return | POST `/connect/link`<br>Redirect URL valid | Handshake linking sukses (One-Way), status berubah menjadi `completed` & `linked: true` | **PASS** |
| 8 | `TC-MAN-ECGO-08` | **Driver EvMoto** | Sesi Kerja (5 Menit) | Verifikasi sesi kerja aktif driver 5 menit untuk memenuhi syarat Free Swap | Driver EvMoto online | 1. Nyalakan status kerja Online<br>2. Pertahankan sesi aktif selama minimal 5 menit (`targetMinutes = 5`)<br>3. Periksa status eWallet | Durasi: 5 Menit<br>Armada: B9001DEV (ECGO 3) | Sesi online tercatat, status eWallet ECGO driver berubah menjadi `LINKED` secara realtime | **PASS** |
| 9 | `TC-MAN-ECGO-09` | **Admin Dashboard** | `/ecgoConnect/drivers` | Verifikasi data Driver Terhubung muncul pada tabel data Dashboard Admin | Akun driver telah terhubung | 1. Masuk ke halaman Driver Terhubung<br>2. Cari nomor telepon `0812-XXXX-7237`<br>3. Amati isi tabel baris driver | URL: `/ecgoConnect/drivers` | Data driver muncul presisi: Nama `Local Dev User`, ID `546`, Plat `B9001DEV`, Kupon `Diskon Pergantian Baterai`, Kuota `1` | **PASS** |
| 10 | `TC-MAN-ECGO-10` | **Driver SuperApps** | `/v5/users/diskon/list` | Verifikasi kupon Free Swap Baterai terbit dan tersimpan di dompet kupon mitra | Driver memenuhi syarat 5 menit | 1. Buka menu Kupon & Diskon di SuperApps<br>2. Periksa daftar kupon swap aktif<br>3. Verifikasi nominal diskon | Kupon ID: `207457`<br>Diskon: `100%`<br>Status: `ready` | Kupon "Diskon Pergantian Baterai" 100% tampil dengan status siap pakai (`usedQuota: 0`, `quota: 1`) | **PASS** |

---

## 🔍 Ringkasan Hasil Integrasi Lintas Platform (Live Evidence)
* **Data Driver di Dashboard Admin (`https://admin-staging.evmoto.internal/ecgoConnect/drivers`):**
  * **Driver:** `Local Dev User` (ID 546)
  * **Telepon:** `62812XXXX7237`
  * **User ID ECGO:** `15361`
  * **Kendaraan:** `B9001DEV` (ECGO ECGO 3 Model)
  * **Waktu Terhubung:** `2026-10-22 11:46:00`
  * **Kupon Terbit:** `Diskon Pergantian Baterai` (discount swap)
  * **Kuota Kupon:** `1`
  * **Status Penggunaan:** `0 / Belum dipakai`
* **Data Kupon di ECGO SuperApps (`https://ecgo-api.internal:3002/v5/users/diskon/list`):**
  * **Kupon:** `Diskon Pergantian Baterai`
  * **Tipe Diskon:** `Percentage (100%)` -> **Free Swap Baterai**
  * **Status:** `ready`
  * **Status Integrasi:** `linked: true`, `couponGranted: true`
* **Data Sesi di EvMoto Driver Apps (`https://api-dev.evmoto.internal`):**
  * **Status eWallet ECGO:** `LINKED`
  * **Armada Aktif:** `B9001DEV` (Brand ECGO)
  * **Kelayakan Kupon:** Terpenuhi (Target 5 Menit Login Driver Selesai)
