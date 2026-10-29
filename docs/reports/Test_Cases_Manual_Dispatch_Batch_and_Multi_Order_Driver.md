# 📘 DOKUMEN TEST CASE MANUAL RESMI: 4 PILAR QA
## FITUR: PENGATURAN DISPATCH BATCH & MULTI-ORDER DRIVER MOBILE APPS
**Platform:** Admin Dashboard & Driver Mobile Apps (com.evmoto.driver.app)  
**Senior QA Engineer:** Bhagus Arif Prayogo  
**Jabatan:** Senior QA Engineer  
**Tanggal Rilis:** 29 Oktober 2026  
**Status Verifikasi:** 100% Terdokumentasi, Terverifikasi, & LULUS (40 Test Cases)  

---

## 🧭 1. Ringkasan Eksekutif & Filosofi 4 Pilar QA

Dokumen ini memuat seluruh rancangan dan hasil eksekusi pengujian manual untuk fitur baru **Dispatch Batch** 
pada Admin Dashboard (`https://evmotoadmin.justkidding.app/dispatchBatch`) dan **Multiple Orders** pada Driver Mobile Apps. 
Pengujian dirancang secara ketat menggunakan metodologi **4 Pilar QA** guna menjamin keandalan sistem, integritas data antrian, 
dan ketahanan terhadap volume tinggi (>5 orders simultan) serta matriks spektrum jarak lengkap (0–25 KM).

```
+---------------------------------------------------------------------------------+
|                         4 PILAR QA ARCHITECTURE MATRIX                          |
+---------------------------------------------------------------------------------+
| PILAR 1: POSITIVE TRUE             | PILAR 2: POSITIVE FALSE                    |
| - Happy path & workflow normal     | - Penolakan aman & fallback terkontrol     |
| - Terima order spesifik tanpa lag  | - Isolasi kapasitas 5 concurrent orders    |
+------------------------------------+--------------------------------------------+
| PILAR 3: NEGATIVE TRUE             | PILAR 4: NEGATIVE FALSE                    |
| - Validasi batas nilai (BVA)       | - Idempotensi submit & anti-duplikasi tap  |
| - Penolakan input ilegal (HTTP 422)| - Ketahanan siklus background/foreground   |
+---------------------------------------------------------------------------------+
```

---

## 📊 2. Matriks Distribusi Test Case (Total: 40 Test Cases)

| Modul Lingkup Pengujian | Pilar 1 (PT) | Pilar 2 (PF) | Pilar 3 (NT) | Pilar 4 (NF) | Total TC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Admin Dashboard (/dispatchBatch)** | 4 TC | 4 TC | 5 TC | 3 TC | **16 TC** | **100% PASSED** |
| **Driver Mobile Apps (Multiple Order)** | 4 TC | 3 TC | 4 TC | 3 TC | **14 TC** | **100% PASSED** |
| **High Volume (>5 Orders) & Distance Matrix** | 6 TC | 2 TC | 0 | 0 | **8 TC** | **100% PASSED** |
| **End-to-End Integration Synchronization** | 1 TC | 0 | 1 TC | 0 | **2 TC** | **100% PASSED** |
| **TOTAL KESELURUHAN** | **15 TC** | **9 TC** | **10 TC** | **6 TC** | **40 TC** | **100% PASSED** |

---

## 📋 3. Tabel Detail Skenario Test Case Manual (40 Test Cases)

| ID TC | Lingkup | Pilar QA | Prioritas | Judul Skenario | Prasyarat | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-DASH-PT-01** | Admin Dashboard | Pilar 1: Positive True | `P0 (Critical)` | Verifikasi 12 Elemen Kontrol UI Halaman Dispatch Batch | Admin terautentikasi login dan membuka https://evmotoadmin.justkidding.app/dispatchBatch | 1. Akses menu /dispatchBatch.<br>2. Verifikasi form Jalur Batch, checkbox, input size, delay, duration, concurrent, rescans.<br>3. Verifikasi tombol Tambah/Hapus Band & Simpan. | Seluruh 12 elemen UI ter-render sempurna tanpa elemen yang hilang atau freeze. | **PASSED** |
| **TC-DASH-PT-02** | Admin Dashboard | Pilar 1: Positive True | `P0 (Critical)` | Penyimpanan Konfigurasi Batch Valid dengan Pesan Sukses | Halaman /dispatchBatch terbuka, sesi login aktif | 1. Isi size=5, delay=10s, duration=0, concurrent=5, rescans=2.<br>2. Ketuk tombol Simpan Pengaturan.<br>3. Amati alert feedback. | HTTP 200 OK diterima, banner hijau 'Pengaturan tersimpan.' muncul di UI. | **PASSED** |
| **TC-DASH-PT-03** | Admin Dashboard | Pilar 1: Positive True | `P0 (Critical)` | Pemisahan Matriks Radius Band Order Biasa vs Advance Booking | Form konfigurasi radius band terbuka | 1. Atur Band Biasa: [0-1, 1-2, 2-3, 3-4, 4-5 KM].<br>2. Atur Band Advance: [0-1, 1-2, 2-5, 5-15 KM].<br>3. Submit simpan pengaturan. | Kedua daftar tersimpan secara terpisah dan independen tanpa kontaminasi silang nilai. | **PASSED** |
| **TC-DASH-PT-04** | Admin Dashboard | Pilar 1: Positive True | `P1 (High)` | Penyimpanan Mode Durasi 0 (Infinite Timer / Tanpa Batas) | Form konfigurasi batch terbuka | 1. Masukkan nilai duration=0 pada field durasi.<br>2. Set rescans=2 dan simpan form. | Nilai 0 tersimpan valid, menandakan tawaran batch tidak akan auto-expired. | **PASSED** |
| **TC-DASH-PF-01** | Admin Dashboard | Pilar 2: Positive False | `P1 (High)` | Penonaktifan Sakelar Jalur Batch (Mode Fallback Sekuensial) | Sakelar Jalur Batch aktif | 1. Uncheck checkbox Jalur Batch (enabled=0).<br>2. Simpan form pengaturan.<br>3. Verifikasi mode dispatch backend. | Sistem berhasil fallback aman ke mode sequential dispatch (1 driver per tawaran) tanpa error. | **PASSED** |
| **TC-DASH-PF-02** | Admin Dashboard | Pilar 2: Positive False | `P1 (High)` | Penggantian Daftar Band Advance Booking dengan Nilai Kustom Baru | Band Advance Booking lama telah tersimpan di sistem | 1. Masukkan daftar band baru [0-3, 3-12 KM].<br>2. Ketuk Simpan Pengaturan.<br>3. Muat ulang halaman. | Daftar band lama berhasil digantikan oleh konfigurasi baru sesuai aturan bisnis. | **PASSED** |
| **TC-DASH-PF-03** | Admin Dashboard | Pilar 2: Positive False | `P1 (High)` | Boundary Value Analysis (BVA): Batas Ukuran Batch Minimum 1 & Maksimum 50 | Form parameter batch terbuka | 1. Uji submit size=1 (minimum batas valid).<br>2. Uji submit size=50 (maksimum batas valid). | Kedua nilai batas ekstrem valid diterima sukses oleh server dengan HTTP 200. | **PASSED** |
| **TC-DASH-PF-04** | Admin Dashboard | Pilar 2: Positive False | `P2 (Medium)` | Validasi Input Angka Desimal pada Kolom Jarak Radius | Form radius band terbuka dengan inputmode='decimal' | 1. Masukkan nilai jarak 0.5 KM, 1.5 KM, 3.75 KM.<br>2. Simpan formulir pengaturan. | Nilai desimal diformat dan disimpan presisi tanpa pembulatan liar. | **PASSED** |
| **TC-DASH-NT-01** | Admin Dashboard | Pilar 3: Negative True | `P0 (Critical)` | Validasi Penolakan Nilai Ukuran Batch di Bawah Batas (size = -5) | Halaman form /dispatchBatch terbuka | 1. Masukkan nilai size=-5.<br>2. Submit simpan pengaturan. | Server menolak dengan HTTP 422: 'Ukuran batch harus bilangan bulat 1 sampai 50.' | **PASSED** |
| **TC-DASH-NT-02** | Admin Dashboard | Pilar 3: Negative True | `P0 (Critical)` | Validasi Penolakan Nilai Ukuran Batch Melampaui Batas (size = 51) | Halaman form /dispatchBatch terbuka | 1. Masukkan nilai size=51.<br>2. Submit simpan pengaturan. | Server menolak dengan HTTP 422: 'Ukuran batch harus bilangan bulat 1 sampai 50.' | **PASSED** |
| **TC-DASH-NT-03** | Admin Dashboard | Pilar 3: Negative True | `P1 (High)` | Validasi Penolakan Input Teks Alfanumerik pada Kolom Numerik | Halaman form /dispatchBatch terbuka | 1. Masukkan teks 'invalid_size' pada kolom ukuran batch.<br>2. Submit form. | Server melempar HTTP 422 tanpa korupsi data pada database. | **PASSED** |
| **TC-DASH-NT-04** | Admin Dashboard | Pilar 3: Negative True | `P0 (Critical)` | Proteksi Akses Tanpa Sesi Login (Unauthorized Access Guard) | Sesi login browser dihapus / mode anonim guest | 1. Kirim request GET langsung ke /dispatchBatch tanpa cookies. | Akses diblokir dan dialihkan aman ke halaman /login (HTTP 302/401). | **PASSED** |
| **TC-DASH-NT-05** | Admin Dashboard | Pilar 3: Negative True | `P0 (Critical)` | Aturan Bisnis: Penolakan Pengosongan Band Advance Booking Tersimpan | Band Advance Booking telah aktif di sistem | 1. Hapus seluruh baris advance booking dan kirim form kosong. | Server menolak dengan HTTP 422: 'Band advance booking yang sudah tersimpan harus diganti dengan daftar baru. Nilai itu tidak bisa dikosongkan.' | **PASSED** |
| **TC-DASH-NF-01** | Admin Dashboard | Pilar 4: Negative False | `P1 (High)` | Uji Idempotensi Submit Konfigurasi Identik Berturut-turut | Sesi admin aktif | 1. Lakukan submit konfigurasi batch yang sama sebanyak 3 kali berturut-turut. | Seluruh request diproses konsisten tanpa memicu error internal server 500. | **PASSED** |
| **TC-DASH-NF-02** | Admin Dashboard | Pilar 4: Negative False | `P2 (Medium)` | Sanitasi Baris Input Kosong / Nilai Format Kotor | Form radius band terbuka | 1. Tambahkan baris band dengan nilai empty string ''.<br>2. Submit form pengaturan. | Sistem secara elegan membersihkan baris kosong tanpa crash aplikasi. | **PASSED** |
| **TC-DASH-NF-03** | Admin Dashboard | Pilar 4: Negative False | `P1 (High)` | Pemulihan Otomatis Konfigurasi Baseline Staging Pasca-Uji | Pengujian skenario dashboard selesai | 1. Kirim payload baseline: size=5, delay=10s, duration=0, concurrent=5, rescans=2.<br>2. Verifikasi state akhir. | Konfigurasi Staging 100% pulih sempurna untuk kelangsungan ekosistem tim QA. | **PASSED** |
| **TC-DRV-PT-01** | Driver Mobile Apps | Pilar 1: Positive True | `P0 (Critical)` | Driver Online Menerima Siaran Batch Berisi Multiple Orders | Driver login & status Online di Beranda (com.evmoto.driver.app) | 1. Backend menyiarkan batch berisi 3 pesanan.<br>2. Driver memantau layar Beranda. | Seluruh 3 pesanan tampil simultan dalam format kartu daftar multiple order. | **PASSED** |
| **TC-DRV-PT-02** | Driver Mobile Apps | Pilar 1: Positive True | `P0 (Critical)` | Verifikasi Ketiadaan Countdown Timer pada Kartu Tawaran Batch | Multiple order batch tampil di layar Driver | 1. Periksa elemen kartu order.<br>2. Lakukan inspeksi komponen countdown timer. | Terkonfirmasi 100% TIDAK ADA countdown timer/detik mundur pada tawaran order. | **PASSED** |
| **TC-DRV-PT-03** | Driver Mobile Apps | Pilar 1: Positive True | `P0 (Critical)` | Driver Melakukan Swipe/Terima pada Salah Satu Order Spesifik | 3 tawaran order batch tersedia | 1. Driver memilih pesanan kedua (ORD-BATCH-02).<br>2. Geser tombol Terima Pesanan. | Pesanan terpilih aktif ke tahap 'Sedang Menjemput', slot kapasitas ter-update. | **PASSED** |
| **TC-DRV-PT-04** | Driver Mobile Apps | Pilar 1: Positive True | `P1 (High)` | Pemisahan Badge Label Order Reguler vs Advance Booking | Batch tawaran berisi pesanan reguler dan pesanan terjadwal | 1. Tinjau kartu order reguler dan kartu order advance booking. | Badge 'Pesanan Reguler' dan 'Advance Booking' tampil berbeda secara tegas. | **PASSED** |
| **TC-DRV-PF-01** | Driver Mobile Apps | Pilar 2: Positive False | `P0 (Critical)` | Penolakan Pengambilan Order Saat Batas Concurrent Tercapai | Driver memegang order aktif sampai kapasitas maksimal (limit 3/3) | 1. Driver mencoba menekan Terima pada order baru ke-4. | Sistem secara aman menolak dan memunculkan banner 'Batas order maksimal tercapai'. | **PASSED** |
| **TC-DRV-PF-02** | Driver Mobile Apps | Pilar 2: Positive False | `P1 (High)` | Tawaran Tetap Aktif Tanpa Auto-Expire pada Mode Durasi 0 | Mode batch duration=0 aktif di sistem | 1. Driver membiarkan tawaran pesanan terbuka beberapa menit. | Tawaran tidak hilang secara sepihak dan tetap dapat diambil oleh driver. | **PASSED** |
| **TC-DRV-PF-03** | Driver Mobile Apps | Pilar 2: Positive False | `P2 (Medium)` | Tampilan Empty State yang Rapi saat Tab Kategori Kosong | Hanya terdapat tawaran pesanan reguler di antrian | 1. Driver membuka Tab 'Advance Booking'. | Antarmuka menampilkan empty state informatif tanpa crash atau layout patah. | **PASSED** |
| **TC-DRV-NT-01** | Driver Mobile Apps | Pilar 3: Negative True | `P0 (Critical)` | Driver Menolak (Reject) Tawaran Order Spesifik | Batch order tampil di layar driver | 1. Driver menekan tombol 'Tolak' pada order ORD-BATCH-01. | Order dikeluarkan dari layar driver; order batch lainnya tetap utuh dan aktif. | **PASSED** |
| **TC-DRV-NT-02** | Driver Mobile Apps | Pilar 3: Negative True | `P0 (Critical)` | Driver Membatalkan (Cancel) Order Aktif dengan Alasan Resmi | Order ORD-BATCH-02 telah diterima dan berstatus Sedang Menjemput | 1. Driver menekan Batalkan Pesanan.<br>2. Pilih alasan 'Ban Bocor / Masalah Kendaraan'. | Order tercatat CANCELLED, lock dilepas, dan kapasitas driver kembali standby. | **PASSED** |
| **TC-DRV-NT-03** | Driver Mobile Apps | Pilar 3: Negative True | `P0 (Critical)` | Penanganan Race Condition saat Order Diambil Mitra Lain Lebih Cepat | Dua driver menerima siaran batch order yang sama | 1. Driver B mengklaim order lebih awal.<br>2. Driver A menekan terima pada order tersebut. | Driver A menerima notifikasi valid: 'Orderan sudah diambil oleh pengemudi lain'. | **PASSED** |
| **TC-DRV-NT-04** | Driver Mobile Apps | Pilar 3: Negative True | `P1 (High)` | Penolakan Penerimaan Tawaran saat Driver dalam Status Offline | Aplikasi driver dalam status Offline | 1. Upaya klaim batch order dikirimkan ke server. | Sistem menolak dengan error bahwa akun mitra sedang offline. | **PASSED** |
| **TC-DRV-NF-01** | Driver Mobile Apps | Pilar 4: Negative False | `P1 (High)` | Proteksi Multi-Tap / Double Swipe Tombol Terima Pesanan | Kartu tawaran aktif | 1. Driver menekan tombol Terima berkali-kali secara simultan. | Sistem menerapkan atomic lock; hanya request pertama diproses tanpa duplikasi. | **PASSED** |
| **TC-DRV-NF-02** | Driver Mobile Apps | Pilar 4: Negative False | `P2 (Medium)` | Idempotensi Aksi Tolak Tawaran (Anti-Double Reject Exception) | Order tawaran aktif | 1. Driver memicu event reject 2 kali berturut-turut pada ID pesanan yang sama. | Event kedua ditangani aman sebagai no-op tanpa memicu error atau force close. | **PASSED** |
| **TC-DRV-NF-03** | Driver Mobile Apps | Pilar 4: Negative False | `P1 (High)` | Ketahanan Siklus Background/Foreground saat Batch Tawaran Aktif | Batch tawaran terbuka di layar driver | 1. Minimize aplikasi ke background 5 detik.<br>2. Buka kembali aplikasi ke foreground. | Daftar pesanan tetap sinkron dan aplikasi tidak mengalami reset state liar. | **PASSED** |
| **TC-VOL-01** | Volume & Distance | Pilar 1: Positive True | `P0 (Critical)` | Penerimaan & Visualisasi Siaran Batch 8 Pesanan Simultan | Driver status Online di Beranda | 1. Sistem memancarkan batch berisi 8 order (5 Reguler + 3 Advance).<br>2. Verifikasi render UI. | Seluruh 8 pesanan berhasil dimuat dan ter-render sempurna tanpa lag. | **PASSED** |
| **TC-VOL-02** | Volume & Distance | Pilar 1: Positive True | `P0 (Critical)` | Stress Testing Beban Muat 15 Order Batch Simultan | Driver status Online di Beranda | 1. Sistem menyiarkan 15 order batch sekaligus.<br>2. Pantau penggunaan memory state. | 15 pesanan termuat utuh tanpa countdown timer, memory footprint stabil. | **PASSED** |
| **TC-VOL-03** | Volume & Distance | Pilar 2: Positive False | `P0 (Critical)` | Proteksi Batas Kapasitas Penuh 5 Concurrent Orders Driver | Driver telah memegang 5 order aktif (ORD-VOL-01 s/d 05) | 1. Driver mencoba menerima order ke-6 (ORD-VOL-06). | Sistem menolak dengan aman; order ke-6 tidak masuk ke antrian driver. | **PASSED** |
| **TC-VOL-04** | Volume & Distance | Pilar 1: Positive True | `P1 (High)` | Seleksi Presisi 1 Order dari Tumpukan 10 Pesanan Simultan | 10 pesanan batch tampil di layar driver | 1. Driver memilih dan menerima order ke-7 (ORD-TEN-07).<br>2. Periksa status 9 order lainnya. | Order ke-7 aktif ke trip driver; 9 order lainnya tetap standby di penawaran. | **PASSED** |
| **TC-DIST-01** | Volume & Distance | Pilar 1: Positive True | `P0 (Critical)` | Spektrum Lengkap 5 Band Radius Jarak Order Reguler (0-5 KM) | Band order biasa aktif: 0-1, 1-2, 2-3, 3-4, 4-5 KM | 1. Uji dispatch order berjarak 0.4 km, 1.5 km, 2.6 km, 3.7 km, dan 4.8 km. | Setiap order terpetakan secara presisi ke band radius yang sesuai. | **PASSED** |
| **TC-DIST-02** | Volume & Distance | Pilar 1: Positive True | `P1 (High)` | Boundary Value Analysis (BVA) Titik Potong Perbatasan KM Radius | Konfigurasi band radius KM aktif | 1. Uji nilai perbatasan: 0.99 km, 1.00 km, 1.99 km, 2.00 km, dan 5.00 km. | Titik potong KM ditangani deterministik sesuai spesifikasi interval PRD. | **PASSED** |
| **TC-DIST-03** | Volume & Distance | Pilar 1: Positive True | `P1 (High)` | Spektrum Jarak Dekat hingga Jauh Band Advance Booking (0-15 KM) | Band advance booking aktif: 0-1, 1-2, 2-5, 5-15 KM | 1. Uji pesanan jarak 0.8 km, 1.7 km, 4.2 km, 12.5 km, dan 14.9 km. | Seluruh pesanan advance booking dari jarak dekat s/d jauh terakomodasi sempurna. | **PASSED** |
| **TC-DIST-04** | Volume & Distance | Pilar 2: Positive False | `P1 (High)` | Penanganan Jarak di Luar Jangkauan Band Radius (Out of Range) | Batas atas band: Reguler 5.0 km, Advance Booking 15.0 km | 1. Uji order reguler jarak 8.5 km.<br>2. Uji order advance booking jarak 22.0 km. | Sistem menangani pesanan di luar jangkauan secara aman tanpa crash atau panic error. | **PASSED** |
| **TC-E2E-BATCH-01** | E2E Integration | Pilar 1: Positive True | `P0 (Critical)` | Master Lifecycle E2E: Admin Setup -> Batch Broadcast -> Driver Accept & Complete Trip | Admin Dashboard & Driver App terhubung ke Staging Dev | 1. Admin atur Jalur Batch ON (size=5, delay=10s, duration=0, concurrent=5).<br>2. Sistem terbitkan order Reguler (1.8 KM) & Advance (12 KM).<br>3. Driver tolak Advance dan terima Reguler.<br>4. Driver selesaikan trip pengantaran. | Alur sukses 100%, tanpa timer, struk pembayaran tunai Rp 12.000 terbit valid. | **PASSED** |
| **TC-E2E-BATCH-02** | E2E Integration | Pilar 3: Negative True | `P0 (Critical)` | Alur Pembatalan Pasca-Terima dengan Alasan Resmi Driver | Driver telah menerima pesanan batch ORD-E2E-CANCEL-01 | 1. Driver ajukan pembatalan dengan alasan 'Kendala Kendaraan Driver'.<br>2. Sistem verifikasi pelepasan pesanan. | Status pesanan beralih ke CANCELLED, lock dilepas, driver kembali siap menerima order. | **PASSED** |

---

## ✍️ 4. Pengesahan & Tanda Tangan QA

| Parameter | Keterangan Dokumen |
| :--- | :--- |
| **Disusun & Diverifikasi Oleh** | **Bhagus Arif Prayogo** |
| **Jabatan** | **Senior QA Engineer** |
| **Divisi** | Quality Assurance & Test Automation Ecosystem |
| **Status Kelayakan Rilis** | **APPROVED FOR PRODUCTION RELEASE** |
| **Tanggal Pengesahan** | 29 Oktober 2026 |

---
_Dokumen ini merupakan aset resmi dokumentasi QA Manual internal EVMOTO Transportasi Listrik._