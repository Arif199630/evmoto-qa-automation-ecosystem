# ⚡ EVMOTO & ECGO Performance & Load Testing Suite

Modul pengujian performa, keandalan, dan kapasitas beban (*Performance, Load, Stress, and Spike Testing*) untuk ekosistem **eVMOTO Transportasi Listrik** dan **ECGO SuperApps Baterai**. Dibangun dengan **Locust 2.x**, framework ini mensimulasikan lalu lintas pengguna nyata (*Virtual Users*) ke server staging/development untuk mengukur latensi (*response time*), batas kejenuhan (*saturation threshold*), serta ketahanan sistem terhadap lonjakan trafik (*rush hour burst*).

---

## 🏛️ Arsitektur Direktori Performance Testing

```text
performance-testing/
├── config/
│   ├── perf_config.py              # Konfigurasi target URL, timeout, kredensial, & ambang SLA
│   └── __init__.py
├── locustfiles/
│   ├── passenger_locustfile.py     # Persona Penumpang: Estimasi tarif dinamis, booking, cancel order
│   ├── driver_locustfile.py        # Persona Driver: Telemetri GPS heartbeat, dashboard, eWallet
│   ├── ecgo_locustfile.py          # Persona ECGO: Verifikasi OTP SMS, kupon swap 100%, connect status
│   ├── unified_locustfile.py       # Simulasi terpadu (50% Passenger, 35% Driver, 15% ECGO)
│   └── __init__.py
├── shapes/
│   ├── load_test_shape.py          # Standard Load Profile (Ramp-up -> Steady State -> Cooldown)
│   ├── stress_test_shape.py        # Step-up Stress Profile (20 -> 50 -> 80 -> 120 Users)
│   ├── spike_test_shape.py         # Sudden Spike Profile (Baseline -> Instant 80 Users Surge -> Recovery)
│   └── __init__.py
├── reports/                        # Direktori penyimpanan otomatis HTML Report & file CSV metrik
├── run_performance.py              # CLI Runner otomatis, validator SLA, dan visualizer metrik
├── requirements.txt                # Dependensi (Locust, Requests, python-dotenv)
└── README.md                       # Dokumentasi Teknis Pengujian Performa
```

---

## 🎯 Cakupan Endpoint & Persona Beban

| Persona Pengguna | Endpoint Target | Method | Karakteristik Beban & Logika Bisnis |
| :--- | :--- | :---: | :--- |
| **Mitra Driver** | `/driver/api/v2/online` | `POST` | **Frekuensi Sangat Tinggi (High Frequency):** Pengiriman telemetri GPS, status ketersediaan (*heartbeat ping*). |
| **Mitra Driver** | `/driver/api/driver/queryHomeData` | `POST` | **Sedang:** Refresh ringkasan performa harian mitra (plat motor, order harian, rating). |
| **Mitra Driver** | `/account/api/ecgo/wallet/status` | `GET` | **Sedang:** Pengecekan saldo dompet e-wallet dan status akun ECGO. |
| **Passenger / User** | `/order/api/user/estimateFare` | `POST` | **High Compute / CPU Bound:** Kalkulasi tarif dinamis berdasarkan jarak koordinat jemput-antar. |
| **Passenger / User** | `/order/api/user/createOrder` | `POST` | **Stateful / Transactional:** Pembuatan tiket pesanan ojek listrik dan inisiasi antrean dispatch. |
| **Passenger / User** | `/order/api/user/cancelOrder` | `POST` | **Graceful Handling:** Pembatalan pesanan sebelum mitra tiba di titik jemput. |
| **Passenger / User** | `/user/api/user/queryInfo` | `GET` | **Read Heavy:** Akses profil pengguna dan saldo akun penumpang. |
| **ECGO SuperApps** | `/v5/users/diskon/list` | `GET` | **Read Heavy:** Pengecekan kupon diskon 100% pergantian baterai (*Free Swap Reward*). |
| **ECGO SuperApps** | `/v5/users/evmoto-connect/status` | `GET` | **Microservice Handshake:** Validasi status penautan akun *one-way binding* EvMoto $\leftrightarrow$ ECGO. |
| **ECGO SuperApps** | `/v5/users/evmoto-connect/start` | `POST` | **Auth Bridge:** Inisiasi sesi handshake penautan akun baru. |

### 📱 Versi Aplikasi Klien Teruji
* **Passenger / User Mobile App:** `v1.2.33` (`com.evmoto.user.app` | APK: `evmoto-user-1.2.33-env-dev_golang-20261020-v8a.apk`)
* **Mitra Driver Mobile App:** `v1.9.27` (`com.evmoto.driver.app` | APK: `evmoto-driver-1.9.27-env-dev_golang-20261020-v7a.apk`)
* **ECGO SuperApps:** `Latest` (`pk.krave.flutter_app` | `ECGO SuperApps.apk`)

---

## 📈 3 Tipe Pengujian Performa (Load Profiles)

### 1. 🟢 Standard Load Testing (`load`)
* **Tujuan:** Memvalidasi kestabilan sistem dan kepatuhan SLA pada kondisi operasional normal.
* **Profil Beban:** Ramp-up 0 $\rightarrow$ 30 pengguna virtual dalam 20 detik, bertahan (*steady-state*) pada 30 pengguna selama 30 detik, lalu diturunkan (*cooldown*).
* **Target SLA:**
  * **$P_{95}$ Latency:** $< 800\text{ ms}$
  * **Error / Failure Rate:** $< 1.0\%$

### 2. 🟡 Step-Up Stress Testing (`stress`)
* **Tujuan:** Menentukan *breaking point* (titik saturasi) server dan mendeteksi kurva degradasi respon saat kapasitas dinaikkan bertingkat.
* **Profil Beban:** 
  * Tahap 1: 20 pengguna (20 detik)
  * Tahap 2: 50 pengguna (20 detik)
  * Tahap 3: 80 pengguna (20 detik)
  * Tahap 4: 120 pengguna (25 detik)

### 3. 🔴 Sudden Surge Spike Testing (`spike`)
* **Tujuan:** Menguji elastisitas dan ketahanan sistem saat terjadi lonjakan trafik tiba-tiba (*flash traffic surge* seperti saat jam sibuk pulang kerja / hujan deras), serta mengevaluasi pemulihan sistem (*self-healing*).
* **Profil Beban:**
  * Fase 1: Baseline 5 pengguna (15 detik)
  * Fase 2: Lonjakan instan ke 80 pengguna dalam 5 detik (*spawn rate* 16 user/detik), dipertahankan selama 20 detik
  * Fase 3: Penurunan mendadak kembali ke baseline 5 pengguna (15 detik)

---

## 🚦 Cara Menjalankan Pengujian Performa

### 1. Eksekusi Headless Otomatis via `run_performance.py`

#### A. Standard Load Test (Unified Ecosystem: Passenger + Driver + ECGO)
```bash
python run_performance.py --target unified --type load
```

#### B. Stress Test Persona Driver
```bash
python run_performance.py --target driver --type stress
```

#### C. Spike Test Persona Passenger (Simulasi Rush Hour Pemesanan)
```bash
python run_performance.py --target passenger --type spike
```

#### D. Kustomisasi Manual (Jumlah User & Durasi Tertentu)
```bash
python run_performance.py --target unified --users 50 --spawn-rate 5 --run-time 1m
```

---

### 2. Mode Interaktif Web UI (Realtime Graph & Visual Monitoring)

Buka dashboard Locust di web browser dengan grafik realtime RPS, kegagalan, dan response time percentiles:
```bash
python run_performance.py --target unified --web
```
Kemudian buka browser pada alamat:
👉 **`http://localhost:8089`**

---

## 📊 Format Output Laporan & Metrik Hasil

Setiap pengujian otomatis di direktori `reports/` menghasilkan:
1. **Laporan Interaktif HTML (`perf_*.html`):** Berisi grafik interaktif *Total Requests per Second*, *Response Times (ms)*, *Number of Users*, serta rincian latensi $P_{50}, P_{66}, P_{75}, P_{80}, P_{90}, P_{95}, P_{98}, P_{99}, P_{99.9}$.
2. **File Statistik CSV (`perf_*_stats.csv`):** Ringkasan kuantitatif *Median*, *Average*, *Min/Max*, dan *Throughput RPS* per endpoint API.
3. **Failures CSV (`perf_*_failures.csv`):** Rincian pesan error dan kode status HTTP jika terjadi kegagalan.
4. **Validasi Kriteria SLA di Terminal:** Ringkasan status lulus/gagal (*PASSED / FAILED*) terhadap ambang batas $P_{95}$ dan *Failure Rate*.
