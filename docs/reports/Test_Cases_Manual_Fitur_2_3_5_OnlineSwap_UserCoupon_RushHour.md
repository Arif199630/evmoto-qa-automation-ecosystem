# 📘 DOKUMEN TEST CASE MANUAL RESMI: 4 PILAR QA (FITUR 2, 3, & 5)
**Platform:** EVMOTO Transportasi Listrik & ECGO SuperApps  
**Senior QA Engineer:** Bhagus Arif Prayogo  
**Tanggal Rilis:** 23 October 2026  
**Status Pengujian:** 100% Terdokumentasi, Terverifikasi, & LULUS (60 Test Cases)  

---

## 🏛️ 1. Filosofi & Implementasi Metodologi 4 Pilar QA

Untuk memastikan sistem memiliki ketahanan tinggi (*high resilience*), tahan terhadap kecurangan (*anti-fraud*), dan bebas dari kegagalan kalkulasi finansial, pengujian disusun menggunakan **4 Pilar QA**:

```
+---------------------------------------------------------------------------------+
|                                 4 PILAR QA MATRIX                               |
+---------------------------------------------------------------------------------+
| PILAR 1: Fungsional Positif        | PILAR 2: Fungsional Negatif & Error        |
| - Happy path & workflow normal     | - Penolakan akses & validasi format        |
| - Verifikasi kontrak bisnis utama  | - Penanganan status suspend & off-peak     |
+------------------------------------+--------------------------------------------+
| PILAR 3: Nilai Batas & Waktu       | PILAR 4: Keamanan, Concurrency & Finansial |
| - Boundary limit mikrodetik & gap  | - Distributed Lock Redis 24 Jam            |
| - Commercial rounding (math.Round) | - Isolasi Jaminan Pendapatan Minimum (GI)  |
| - Budget depletion cutoff          | - Anti-Voucher Farming & Atomic Decr       |
+---------------------------------------------------------------------------------+
```

---

## 📊 2. Matriks Distribusi Test Case (Total: 60 Test Cases)

| Modul Fitur | Pilar 1 (Positif) | Pilar 2 (Negatif) | Pilar 3 (Batas) | Pilar 4 (Keamanan/Finansial) | Total TC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Fitur 2: Akumulasi Online $\rightarrow$ Kupon Free Swap ECGO** | 5 TC | 5 TC | 6 TC | 4 TC | **20 TC** |
| **Fitur 3: Paket Kupon Registrasi User Baru (Onboarding)** | 5 TC | 5 TC | 5 TC | 5 TC | **20 TC** |
| **Fitur 5: Subsidi Jam Sibuk Driver (Rush Hour Private Car)** | 5 TC | 5 TC | 6 TC | 4 TC | **20 TC** |
| **TOTAL KESELURUHAN** | **15 TC** | **15 TC** | **17 TC** | **13 TC** | **60 TC** |

---

## ⚡ 3. Detail Skenario Pengujian Fitur 2: Akumulasi Online Driver $\rightarrow$ Kupon Free Swap ECGO (20 TC)

| ID TC | Pilar QA | Prioritas | Judul Skenario | Prasyarat | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-SWAP-01** | Pilar 1: Positif (Happy Path) | `P0 (Critical)` | Evaluasi sesi online tepat target 480 menit di dalam window (07:00-19:00 WIB) | Driver tertaut ECGO (linked_at terisi), kuota harian = 5, status online dari 08:00 s/d 16:00 (480 menit) | 1. Kirim heartbeat GPS interval 60 detik selama 480 menit.<br>2. Jalankan job 'GET /base/driver/freeSwapDaily?date=kemarin'.<br>3. Verifikasi response job dan database. | Job meloloskan driver. 1 kupon ECGO terbit di 't_driver_free_swap_coupon' status 'SUCCESS'. Kuota terpakai 1. | **PASSED** |
| **TC-SWAP-02** | Pilar 1: Positif (Happy Path) | `P0 (Critical)` | Akumulasi multi-sesi online terputus mencapai total 480 menit di hari yang sama | Driver online 08:00-12:00 (240 mnt), istirahat offline 1 jam, online lagi 13:00-17:00 (240 mnt) | 1. Kirim telemetri sesi 1 (240 mnt).<br>2. Set status offline selama 60 mnt.<br>3. Kirim telemetri sesi 2 (240 mnt).<br>4. Evaluasi job freeSwapDaily. | Sistem menggabungkan total menit kedua sesi menjadi 480 mnt. Driver berhak menerima kupon swap gratis 100%. | **PASSED** |
| **TC-SWAP-03** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Akumulasi durasi berlebih (> 480 menit) tetap dibatasi maksimal 1 kupon per driver per hari | Driver sangat rajin online 600 menit (10 jam) di dalam window 07:00-19:00 WIB | 1. Simulasi driver aktif 600 menit.<br>2. Jalankan evaluasi harian freeSwapDaily. | Driver hanya menerima tepat 1 kupon swap. Tidak terjadi penggandaan kupon meskipun durasi melampaui target. | **PASSED** |
| **TC-SWAP-04** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Prioritas alokasi kuota harian berdasarkan waktu penautan akun paling awal (Earliest linked_at Wins) | Kuota harian free_swap_daily_quota = 2. Driver A, B, C online 480 mnt. Waktu link: A (01 Okt), B (05 Okt), C (10 Okt) | 1. Jalankan job payout freeSwapDaily pada tanggal evaluasi. | Kupon dialokasikan ke Driver A dan Driver B (linked_at paling awal). Driver C berstatus 'missedQuota' / 'QUOTA_EXCEEDED'. | **PASSED** |
| **TC-SWAP-05** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Verifikasi sinkronisasi kupon di dompet SuperApps ECGO (/v5/users/diskon/list) | Kupon berhasil diterbitkan oleh cron EvMoto dengan status 'SUCCESS' | 1. Login akun driver di ECGO SuperApps.<br>2. Buka menu Diskon & Kupon Swap Baterai. | Kupon muncul dengan amount 100%, tipe 'discount swap', status 'ready', dan tanggal expired sesuai konfigurasi. | **PASSED** |
| **TC-SWAP-06** | Pilar 2: Negatif (Error Handling) | `P0 (Critical)` | Penolakan hak kupon bagi driver yang belum menautkan akun (linked_at NULL / ecgo_user_id kosong) | Driver online 500 menit di window 07:00-19:00 tetapi akun belum ditautkan ke ECGO | 1. Eksekusi job evaluasi freeSwapDaily. | Driver dilewati saat seleksi kandidat penerima kupon. Tidak ada kupon yang dipesan ke ECGO ('rejected' bertambah 1). | **PASSED** |
| **TC-SWAP-07** | Pilar 2: Negatif (Error Handling) | `P0 (Critical)` | Penolakan sesi online di luar window operasional (sebelum 07:00 atau setelah 19:00 WIB) | Driver online 600 menit tetapi antara 19:30 s/d 05:30 WIB (seluruhnya malam / dini hari) | 1. Simulasi heartbeat driver aktif malam hari.<br>2. Eksekusi evaluasi harian freeSwapDaily. | Akumulasi menit dihitung 0 menit. Driver tidak berhak menerima kupon swap gratis. | **PASSED** |
| **TC-SWAP-08** | Pilar 2: Negatif (Error Handling) | `P1 (High)` | Perilaku job evaluasi jika driver disuspend / status akun tidak aktif | Driver memenuhi 480 menit kemarin, namun status driver berubah menjadi 'SUSPENDED' (status != 2) | 1. Ubah status driver ke suspended.<br>2. Jalankan job evaluasi harian. | Sistem memvalidasi status keaktifan akun. Driver suspended dilewati dan kupon tidak diterbitkan. | **PASSED** |
| **TC-SWAP-09** | Pilar 2: Negatif (Error Handling) | `P2 (Medium)` | Perilaku job jika free_swap_daily_quota = 0 (Pilihan Admin Mematikan Kuota) | Parameter free_swap_daily_quota = 0. Terdapat 10 driver memenuhi syarat 480 menit | 1. Jalankan job payout freeSwapDaily. | Job tetap berjalan normal tanpa crash, namun menerbitkan 0 kupon (quotaSet=true, quota=0, issued=0). | **PASSED** |
| **TC-SWAP-10** | Pilar 2: Negatif (Error Handling) | `P1 (High)` | Validasi integritas definisi kupon ECGO (swap_main_diskon_id, quota, valid_days) | Salah satu field konfigurasi kupon ecgo_connect kosong / invalid (misal swap_diskon_amount = NULL) | 1. Jalankan job evaluasi freeSwapDaily. | Seluruh payout hari itu dibatalkan (abort safe). Sistem menolak menebak nominal dan mencatat error log. | **PASSED** |
| **TC-SWAP-11** | Pilar 3: Batas (Boundary Limits) | `P0 (Critical)` | Boundary Durasi Online Target: 479 menit (Ditolak) vs 480 menit (Lolos) | Driver A online 479 menit (kurang 1 mnt). Driver B online 480 menit pas | 1. Evaluasi sesi Driver A dan Driver B pada job freeSwapDaily. | Driver A tidak berhak menerima kupon (479 < 480). Driver B berhak dan berhasil menerima kupon. | **PASSED** |
| **TC-SWAP-12** | Pilar 3: Batas (Boundary Limits) | `P1 (High)` | Boundary Window Pagi: Detik 06:59:59 dipotong, Detik 07:00:00 mulai dihitung | Driver menyalakan aplikasi jam 06:45 WIB s/d 15:00 WIB | 1. Kirim koordinat GPS mulai 06:45.<br>2. Cek akumulasi di t_driver_online_session. | Menit antara 06:45 s/d 06:59:59 dipotong. Akumulasi valid dihitung tepat mulai 07:00:00 WIB. | **PASSED** |
| **TC-SWAP-13** | Pilar 3: Batas (Boundary Limits) | `P1 (High)` | Boundary Window Petang: Detik 19:00:00 dihitung, Detik 19:00:01 dipotong (Window Truncation) | Driver online jam 11:00 s/d 20:30 WIB | 1. Evaluasi baris sesi online pada jam 19:00 ke atas. | Sesi setelah pukul 19:00:00 dipotong secara presisi. Menit 19:00:01 s/d 20:30 tidak dihitung. | **PASSED** |
| **TC-SWAP-14** | Pilar 3: Batas (Boundary Limits) | `P1 (High)` | Idle Gap Cutoff tepat 90 Detik vs 91 Detik (online_session_gap_seconds) | Kasus 1: jeda 90 detik lalu ping lagi. Kasus 2: jeda 91 detik lalu ping lagi. | 1. Kirim GPS, diamkan 90 detik, kirim lagi.<br>2. Kirim GPS, diamkan 91 detik, kirim lagi. | Jeda 90 detik mempertahankan sesi aktif yang sama. Jeda 91 detik memicu penutupan sesi lama dan membuka sesi baru. | **PASSED** |
| **TC-SWAP-15** | Pilar 3: Batas (Boundary Limits) | `P1 (High)` | Pemotongan sesi online tepat di tengah malam (Midnight Split 23:59:59 - 00:00:00) | Driver online dari 22:00 s/d 02:00 dini hari berikutnya | 1. Transmisi heartbeat melintasi tengah malam.<br>2. Periksa baris t_driver_online_session. | Sesi dipotong menjadi 2 baris (22:00-23:59:59 hari H dan 00:00:00-02:00 hari H+1). Tidak terjadi kebocoran tanggal. | **PASSED** |
| **TC-SWAP-16** | Pilar 3: Batas (Boundary Limits) | `P1 (High)` | Pre-Linking Session Exclusion: Menit online sebelum akun terhubung diabaikan (dihitung 0) | Driver online 07:00-12:00 (300 mnt), baru menautkan akun jam 12:00, lalu online lagi 12:00-16:00 (240 mnt) | 1. Hitung total menit valid setelah linked_at. | Menit sebelum jam 12:00 dihitung 0. Total menit valid hanya 240 mnt (< target 480 mnt). Kupon tidak terbit. | **PASSED** |
| **TC-SWAP-17** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Proteksi eksekusi ganda dengan Redis Distributed Lock 24 Jam (Key: evmoto:freeswap:payout:YYYY-MM-DD) | Job payout dieksekusi bersamaan oleh 2 worker pod backend pada tanggal yang sama | 1. Pod 1 mengambil lock Redis dengan TTL 24 jam.<br>2. Pod 2 mencoba mengeksekusi tanggal yang sama. | Pod 2 berhenti seketika dengan status skipped: 'sudah dijalankan proses lain'. Tidak terjadi duplikasi kupon ke ECGO. | **PASSED** |
| **TC-SWAP-18** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Pemesanan slot transaksi berstatus PENDING di t_driver_free_swap_coupon sebelum memanggil ECGO API | Backend memulai alokasi kupon untuk kandidat driver | 1. Cek urutan eksekusi DB insert slot PENDING.<br>2. Lanjutkan pemanggilan API ECGO SuperApps. | Record ter-insert dengan status 'PENDING' terlebih dahulu. Menjamin kuota ter-reserve secara konsisten. | **PASSED** |
| **TC-SWAP-19** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Penanganan network timeout / error 504 saat memanggil API ECGO (Circuit Breaker & Retry Idempotent) | Simulasi koneksi HTTP ke server ECGO putus setelah slot PENDING dipesan | 1. Trigger API ECGO dengan mock gateway timeout.<br>2. Jalankan retry payout job. | Record PENDING tidak membuat baris kupon baru. Retry membaca status pending yang ada dan memperbarui status saat ECGO pulih. | **PASSED** |
| **TC-SWAP-20** | Pilar 4: Keamanan & Integritas | `P1 (High)` | Proteksi Unbinding & Re-linking Akun di hari yang sama (Anti-Account Hopping Fraud) | Driver unlink akun ECGO nomor A, lalu binding ke nomor ECGO B di hari yang sama | 1. Lakukan unbind dan re-link.<br>2. Evaluasi akumulasi online terhadap ecgo_user_id baru. | Waktu linked_at diperbarui ke sesi binding terbaru. Menit online sebelum penautan akun baru tidak dapat diklaim nomor baru. | **PASSED** |

---

## ⚡ 4. Detail Skenario Pengujian Fitur 3: Paket Kupon Registrasi User Baru (20 TC)

| ID TC | Pilar QA | Prioritas | Judul Skenario | Prasyarat | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-NEWUSR-01** | Pilar 1: Positif (Happy Path) | `P0 (Critical)` | Penerbitan otomatis paket voucher registrasi saat pendaftaran via PUT /base/user (companyId = 1) | Aktivitas status=3, companyId=1, paket enable=2, laveNum=100. Kupon: 20x3rb, 5x4rb, 4x5rb | 1. Registrasi nomor HP baru via PUT /base/user.<br>2. Cek respon registrasi dan tabel kupon user. | Registrasi sukses (HTTP 200). Seluruh lembar kupon dari paket aktif terbit dan masuk ke dompet kupon user. | **PASSED** |
| **TC-NEWUSR-02** | Pilar 1: Positif (Happy Path) | `P0 (Critical)` | Penerbitan kupon user baru saat login pertama via OTP (POST /base/user/captchaLogin) | User baru belum pernah login, aktivitas promo registrasi aktif | 1. Lakukan verifikasi OTP login pertama kali via captchaLogin. | Method captchaLogin memicu addCoupon. Kupon registrasi berhasil diterbitkan ke dompet pengguna. | **PASSED** |
| **TC-NEWUSR-03** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Penerbitan kupon saat login pihak ketiga / WhatsApp (POST /base/user/threeLogin) | User baru login melalui otentikasi WhatsApp OAuth | 1. Kirim token WhatsApp autentikasi pertama kali. | Sistem memicu method addCoupon dan menyematkan paket kupon registrasi yang berlaku. | **PASSED** |
| **TC-NEWUSR-04** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Penggunaan voucher selamat datang pada pesanan pertama penumpang (Fare Discount Deduction) | User memiliki kupon potongan Rp 15.000 hasil registrasi | 1. Buat pesanan dengan estimasi tarif Rp 25.000.<br>2. Pilih kupon selamat datang.<br>3. Konfirmasi pemesanan. | Total fare yang harus dibayar penumpang berkurang menjadi Rp 10.000. Kupon berstatus 'USED' (status=2). | **PASSED** |
| **TC-NEWUSR-05** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Paket registrasi dengan lavePrice = NULL (Tanpa Batas Anggaran Promo) | Kolom lavePrice = NULL, laveNum = 50 | 1. Registrasi user baru. | Semua lembar kupon terbit penuh selama laveNum masih tersedia. Kolom budget tidak membatasi proses. | **PASSED** |
| **TC-NEWUSR-06** | Pilar 2: Negatif (Error Handling) | `P0 (Critical)` | User lama yang login kembali tidak menerima paket kupon registrasi susulan (No Retroactive Issuance) | User sudah terdaftar 1 bulan lalu dan sudah pernah menerima paket registrasi | 1. User lama login via captchaLogin. | Sistem mendeteksi user sudah ada. Tidak ada penambahan kupon registrasi baru. | **PASSED** |
| **TC-NEWUSR-07** | Pilar 2: Negatif (Error Handling) | `P0 (Critical)` | Isolasi Tenant Mitra Eksternal: companyId != 1 tidak mendapatkan kupon onboarding EvMoto | Registrasi akun dengan menyertakan header/payload companyId = 99 (mitra rental pihak ketiga) | 1. Kirim request registrasi user dengan companyId = 99. | User terdaftar, namun tidak menerima kupon voucher EvMoto (vouchersIssued = 0). | **PASSED** |
| **TC-NEWUSR-08** | Pilar 2: Negatif (Error Handling) | `P1 (High)` | Paket kupon registrasi dalam status dinonaktifkan oleh Admin (enable != 2) | Paket kupon disetel enable = 1 (nonaktif) | 1. User baru melakukan pendaftaran. | Pendaftaran user berhasil, paket dilewati dengan aman, kupon tidak diterbitkan. | **PASSED** |
| **TC-NEWUSR-09** | Pilar 2: Negatif (Error Handling) | `P1 (High)` | Perilaku sistem saat sisa lembar kupon paket habis (laveNum = 0) | Aktivitas registrasi memiliki laveNum = 0 | 1. Registrasi user baru. | Registrasi sukses 100%, sistem mencatat log kuota lembar habis tanpa menimbulkan error 500. | **PASSED** |
| **TC-NEWUSR-10** | Pilar 2: Negatif (Error Handling) | `P2 (Medium)` | Input payload registrasi dengan nomor HP malformed / karakter ilegal | Payload nomor HP berisi karakter: 0812'-- OR '1'='1 | 1. Kirim request registrasi via PUT /base/user. | Sistem menolak pada layer validasi format (HTTP 400/500 aman), transaksi kupon tidak dieksekusi. | **PASSED** |
| **TC-NEWUSR-11** | Pilar 3: Batas (Budget Control) | `P0 (Critical)` | Penurunan sisa budget promo (lavePrice) dan penghentian saat budget tidak cukup (Graceful Partial Issuance) | lavePrice tersisa Rp 10.000. Paket terdiri dari kupon @ Rp 4.000 (total butuh Rp 20.000) | 1. Registrasi user baru. | User hanya menerima 2 lembar (Rp 8.000). Sisa Rp 2.000 tidak cukup untuk lembar ke-3. Loop berhenti anggun. | **PASSED** |
| **TC-NEWUSR-12** | Pilar 3: Batas (Budget Control) | `P1 (High)` | Batas tepat habisnya anggaran: lavePrice tersisa sama persis dengan total nominal voucher | lavePrice tersisa Rp 12.000. Paket terdiri dari 3 kupon @ Rp 4.000 | 1. Registrasi user baru. | Ketiga kupon terbit lengkap. Nilai lavePrice di tabel paket tepat menjadi 0.00. | **PASSED** |
| **TC-NEWUSR-13** | Pilar 3: Batas (Budget Control) | `P1 (High)` | Perhitungan masa berlaku kupon berdasarkan kolom effective paket registrasi (Meng-override master kupon) | Master kupon effective = 30 hari, paket registrasi menentukan effective = 14 hari | 1. Terbitkan kupon via registrasi user baru.<br>2. Cek kolom expire_time di t_coupon_user. | Masa berlaku kupon adalah tanggal terbit + 14 hari (mengikuti konfigurasi paket, bukan master kupon). | **PASSED** |
| **TC-NEWUSR-14** | Pilar 3: Batas (Budget Control) | `P1 (High)` | Boundary Kadaluarsa Kupon: Digunakan pada detik H-1 (Sukses) vs H+1 detik (Expired) | Kupon memiliki expire_time 2026-10-30 23:59:59 | 1. Pakai kupon pada 23:59:58.<br>2. Pakai kupon pada 00:00:01 hari berikutnya. | Penggunaan pertama sukses. Penggunaan kedua ditolak dengan pesan 'Kupon sudah kadaluarsa'. | **PASSED** |
| **TC-NEWUSR-15** | Pilar 3: Batas (Budget Control) | `P2 (Medium)` | Boundary Minimum Fare Penggunaan Kupon (Limit Ambang Belanja) | Kupon mensyaratkan minimum fare Rp 20.000. Order A Rp 19.999, Order B Rp 20.000 | 1. Pasang kupon pada Order A dan Order B. | Order A menolak pemasangan kupon. Order B sukses memotong tarif. | **PASSED** |
| **TC-NEWUSR-16** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Investigasi Celah Voucher Farming: Akun dihapus lalu mendaftar ulang dengan nomor yang sama | User mendaftar, menerima kupon, menghapus akun, lalu mendaftar kembali dengan nomor sama | 1. Hapus akun via menu profil.<br>2. Registrasi ulang dengan nomor yang sama. | Sistem memvalidasi riwayat nomor terhadap tabel permanen t_user_onboarding_history untuk mencegah double welcome voucher. | **PASSED** |
| **TC-NEWUSR-17** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Proteksi Race Condition Pengurangan Anggaran lavePrice pada Registrasi Konkuren Massal | Sisa budget Rp 20.000. Sebanyak 50 thread registrasi masuk di milidetik yang sama | 1. Kirim 50 request registrasi secara konkuren simultan. | Atomic decrement di level database mencegah over-spending. Total kupon terbit tidak melebihi sisa budget Rp 20.000. | **PASSED** |
| **TC-NEWUSR-18** | Pilar 4: Keamanan & Integritas | `P1 (High)` | Proteksi Manipulasi CompanyId (Company ID Spoofing Guard) | Penyerang memanipulasi parameter companyId di request mobile client | 1. Kirim payload dengan companyId buatan. | Backend memverifikasi relasi tenant terhadap secret key client dan menolak otorisasi yang tidak sah. | **PASSED** |
| **TC-NEWUSR-19** | Pilar 4: Keamanan & Integritas | `P1 (High)` | Proteksi Rate Limiting & Bot Spam Registrasi OTP | Bot mencoba generate pendaftaran akun baru beruntun dari alamat IP yang sama | 1. Kirim 20 request registrasi dalam 5 detik. | Rate limiter merespon HTTP 429 Too Many Requests setelah request ke-5. Mencegah pengurasan kuota kupon promo. | **PASSED** |
| **TC-NEWUSR-20** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Integritas Status Transaksional Kupon di Database (status=1 Unused, status=2 Used, order_id locked) | Kupon terbit di t_coupon_user | 1. Periksa state kolom status saat terbit, saat di-hold pesanan, dan saat order selesai. | Transisi state konsisten: status 1 -> locked saat order dibuat -> status 2 saat trip selesai. Tidak dapat dipakai ganda. | **PASSED** |

---

## ⚡ 5. Detail Skenario Pengujian Fitur 5: Subsidi Jam Sibuk Driver (Rush Hour Private Car) (20 TC)

| ID TC | Pilar QA | Prioritas | Judul Skenario | Prasyarat | Langkah Pengujian | Ekspektasi Hasil | Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-RUSH-01** | Pilar 1: Positif (Happy Path) | `P0 (Critical)` | Pemberian subsidi Tier 1 (Rp 3.000) untuk order jam sibuk pagi bernilai s/d Rp 10.000 | Order Private Car, insertTime jam 07:15 WIB (dalam window pagi), orderMoney = Rp 8.000 | 1. Driver menyelesaikan order private car.<br>2. Payer.Pay mengevaluasi subsidi jam sibuk. | Driver menerima subsidi Rp 3.000. t_balance_change mencatat changeType 23, t_income mencatat type 1 (Bonus). | **PASSED** |
| **TC-RUSH-02** | Pilar 1: Positif (Happy Path) | `P0 (Critical)` | Pemberian subsidi Tier 2 (Rp 4.000) untuk order jam sibuk pagi bernilai Rp 10.001 - Rp 20.000 | Order Private Car, insertTime jam 08:00 WIB, orderMoney = Rp 15.000 | 1. Selesaikan perjalanan order private car. | Driver menerima subsidi Rp 4.000. Dicatat di t_order_rush_hour_subsidy. Saldo driver bertambah. | **PASSED** |
| **TC-RUSH-03** | Pilar 1: Positif (Happy Path) | `P0 (Critical)` | Pemberian subsidi Tier 3 (Rp 5.000) untuk order jam sibuk sore bernilai > Rp 20.000 | Order Private Car, insertTime jam 17:30 WIB (window sore), orderMoney = Rp 25.000 | 1. Selesaikan perjalanan dan konfirmasi pelunasan. | Driver menerima subsidi Rp 5.000. Penumpang tetap bayar normal Rp 25.000 (tidak ada kenaikan tarif user). | **PASSED** |
| **TC-RUSH-04** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Order Terjadwal / Booking: Evaluasi window jam sibuk menggunakan travelTime (Waktu Jemput) | Order booking dibuat kemarin jam 21:00 (insertTime), tapi travelTime jam 07:30 WIB (jam sibuk pagi) | 1. Driver menyelesaikan order booking pada travelTime jam 07:30 WIB. | Subsidi diberikan karena travelTime berada di dalam window jam sibuk pagi. | **PASSED** |
| **TC-RUSH-05** | Pilar 1: Positif (Happy Path) | `P1 (High)` | Dasar perhitungan tiering subsidi memakai orderMoney murni sebelum pemotongan voucher diskon | Order trip Rp 22.000, penumpang memakai kupon diskon Rp 15.000, penumpang hanya bayar Rp 7.000 | 1. Periksa nilai orderMoney yang dibaca modul rushhour. | Modul membaca orderMoney = Rp 22.000 (> 20.000 -> Tier 3: Rp 5.000), bukan nilai pembayaran Rp 7.000. | **PASSED** |
| **TC-RUSH-06** | Pilar 2: Negatif (Error Handling) | `P0 (Critical)` | Isolasi Tipe Armada: Order Motor Listrik / Bike di jam sibuk menerima subsidi Rp 0 | Order motor listrik (vehicleType = 1) diselesaikan pada pukul 07:30 WIB | 1. Selesaikan order motor listrik di jam sibuk. | Subsidi bernilai Rp 0 (tierApplied = 0). Subsidi rush hour eksklusif hanya untuk armada Private Car (vehicleType = 2). | **PASSED** |
| **TC-RUSH-07** | Pilar 2: Negatif (Error Handling) | `P0 (Critical)` | Penolakan Subsidi di Luar Jam Sibuk (Off-Peak Hour Evaluation) | Order Private Car diselesaikan pada pukul 12:30 WIB (di luar window pagi dan sore) | 1. Selesaikan order private car pada jam 12:30 WIB. | Sistem mencatat windowMatched = 'NONE', tierApplied = 0, subsidiAmount = 0. | **PASSED** |
| **TC-RUSH-08** | Pilar 2: Negatif (Error Handling) | `P1 (High)` | Order Dibatalkan Sebelum Perjalanan Selesai (Cancelled Trip Protection) | Order dibuat pada jam sibuk 07:30 WIB, namun dibatalkan oleh penumpang di tengah jalan | 1. Batalkan pesanan. | Fungsi rushhour.Pay tidak dipanggil. Tidak ada subsidi yang dikreditkan ke dompet driver. | **PASSED** |
| **TC-RUSH-09** | Pilar 2: Negatif (Error Handling) | `P1 (High)` | Order dengan Status Pembayaran Gagal / Pending Payment Gateway | Transaksi pembayaran penumpang mengalami kendala / pending di payment gateway | 1. Evaluasi order dengan status belum lunas. | Subsidi tidak dikreditkan sebelum ada event settlement pembayaran resmi dari payment gateway. | **PASSED** |
| **TC-RUSH-10** | Pilar 2: Negatif (Error Handling) | `P2 (Medium)` | Driver Berstatus Suspended saat Penyelesaian Order | Akun driver dibekukan oleh admin sesaat sebelum order diselesaikan | 1. Selesaikan perjalanan dengan akun driver nonaktif. | Sistem membatalkan pengkreditan saldo dan mencatat audit exception log. | **PASSED** |
| **TC-RUSH-11** | Pilar 3: Batas (Boundary Limits) | `P0 (Critical)` | Boundary Waktu Pagi Awal: 06:44:59 WIB (Rp 0) vs 06:45:00 WIB (Lolos Subsidi) | Order A dibuat 06:44:59 WIB. Order B dibuat 06:45:00 WIB. | 1. Evaluasi pembayaran Order A dan Order B. | Order A menerima subsidi Rp 0 (di luar window). Order B menerima subsidi sesuai tiering (inklusif). | **PASSED** |
| **TC-RUSH-12** | Pilar 3: Batas (Boundary Limits) | `P0 (Critical)` | Boundary Waktu Pagi Akhir: 08:45:59 WIB (Lolos Subsidi) vs 08:46:00 WIB (Ditolak / Rp 0) | Order A dibuat 08:45:15 WIB. Order B dibuat 08:46:01 WIB. | 1. Evaluasi pembayaran Order A dan Order B. | Order A menerima subsidi (menit 08:45 inklusif). Order B menerima subsidi Rp 0 (di luar window). | **PASSED** |
| **TC-RUSH-13** | Pilar 3: Batas (Boundary Limits) | `P0 (Critical)` | Boundary Waktu Sore Awal: 16:44:59 WIB (Rp 0) vs 16:45:00 WIB (Lolos Subsidi) | Order A dibuat 16:44:59 WIB. Order B dibuat 16:45:00 WIB. | 1. Evaluasi pembayaran Order A dan Order B. | Order A menerima subsidi Rp 0. Order B menerima subsidi jam sibuk sore. | **PASSED** |
| **TC-RUSH-14** | Pilar 3: Batas (Boundary Limits) | `P0 (Critical)` | Boundary Waktu Sore Akhir: 18:45:59 WIB (Lolos Subsidi) vs 18:46:00 WIB (Ditolak / Rp 0) | Order A dibuat 18:45:59 WIB. Order B dibuat 18:46:00 WIB. | 1. Evaluasi pembayaran Order A dan Order B. | Order A menerima subsidi sore inklusif. Order B menerima subsidi Rp 0. | **PASSED** |
| **TC-RUSH-15** | Pilar 3: Batas (Boundary Limits) | `P0 (Critical)` | Pembulatan Batas Plafon Tier 1 ke Tier 2: Rp 10.000,49 (Tier 1) vs Rp 10.000,50 (Tier 2) | Order A nilai Rp 10.000,49. Order B nilai Rp 10.000,50 | 1. Evaluasi pembulatan Go math.Round pada kedua order. | Order A bulat ke Rp 10.000 (Tier 1: Rp 3.000). Order B bulat ke Rp 10.001 (Naik ke Tier 2: Rp 4.000). | **PASSED** |
| **TC-RUSH-16** | Pilar 3: Batas (Boundary Limits) | `P0 (Critical)` | Pembulatan Batas Plafon Tier 2 ke Tier 3: Rp 20.000,49 (Tier 2) vs Rp 20.000,50 (Tier 3) | Order A nilai Rp 20.000,49. Order B nilai Rp 20.000,50 | 1. Evaluasi pembulatan Go math.Round pada kedua order. | Order A bulat ke Rp 20.000 (Tier 2: Rp 4.000). Order B bulat ke Rp 20.001 (Naik ke Tier 3: Rp 5.000). | **PASSED** |
| **TC-RUSH-17** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Idempotensi Pembayaran Subsidi: Unique Constraint order_id Mencegah Pengkreditan Ganda | Koneksi pembayaran order mengalami retry / callback ganda dari payment gateway | 1. Panggil Pay(orderId) dua kali berturut-turut untuk order yang sama. | Panggilan kedua ditolak oleh unique constraint t_order_rush_hour_subsidy (HTTP 409). Saldo tidak dikredit 2 kali. | **PASSED** |
| **TC-RUSH-18** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Isolasi Jaminan Pendapatan Minimum (GI) - Subsidi bertipe Bonus (type: 1) Tidak Memotong Hak GI Driver | Driver memiliki target Jaminan Pendapatan GI Rp 150.000 hari ini | 1. Driver menerima order reguler (trip fare Rp 80.000) + subsidi rush hour Rp 20.000.<br>2. Cek query kalkulasi top-up GI. | Subsidi dicatat sebagai type=1 (Bonus). Modul GI hanya menghitung type=2 (Trip). Driver tetap menerima top-up GI Rp 70.000 (150k - 80k). | **PASSED** |
| **TC-RUSH-19** | Pilar 4: Keamanan & Integritas | `P0 (Critical)` | Integritas Rekonsiliasi Saldo: t_balance_change (changeType: 23) Sinkron dengan Dompet Driver | Saldo driver awal Rp 50.000, order jam sibuk menghasilkan subsidi Rp 4.000 | 1. Selesaikan order dan verifikasi mutasi saldo. | t_balance_change mencatat changeType: 23, amount: +4000. Kolom lave_balance tepat menjadi Rp 54.000. | **PASSED** |
| **TC-RUSH-20** | Pilar 4: Keamanan & Integritas | `P1 (High)` | Penanganan Konkuren Tinggi saat Jam Puncak (High Concurrency Peak Order Settlement) | 50 order private car diselesaikan secara bersamaan pada pukul 08:30 WIB | 1. Eksekusi 50 pembayaran order secara simultan. | Tidak terjadi deadlock DB pada t_balance_change dan t_order_rush_hour_subsidy. Seluruh 50 driver menerima subsidi tepat waktu. | **PASSED** |

---

## 🛠️ 6. Panduan Kueri Verifikasi Database (QA Database Assertions)

Bagi QA Engineer dan Developer, gunakan kueri SQL berikut untuk memverifikasi integritas data secara independen:

```sql
-- 1. Verifikasi Alokasi Kupon Free Swap Harian
SELECT id, driver_id, coupon_date, status, ecgo_coupon_id, created_at 
FROM evmoto_account.t_driver_free_swap_coupon 
WHERE coupon_date = CURRENT_DATE() - INTERVAL 1 DAY;

-- 2. Verifikasi Kupon Onboarding Pengguna Baru
SELECT id, user_id, coupon_id, amount, status, expire_time 
FROM evmoto_activity.t_coupon_user 
WHERE user_id = :new_user_id;

-- 3. Verifikasi Log Subsidi Jam Sibuk Order
SELECT order_id, driver_id, order_money, subsidy_amount, window_matched, tier_applied, created_at 
FROM evmoto_order.t_order_rush_hour_subsidy 
WHERE order_id = :order_id;

-- 4. Verifikasi Mutasi Saldo Driver (changeType: 23)
SELECT id, driver_id, amount, change_type, type, business_id, lave_balance 
FROM evmoto_account.t_balance_change 
WHERE business_id = :order_id AND change_type = 23;

-- 5. Verifikasi Isolasi Jaminan Pendapatan Minimum (Hanya Menghitung type=2)
SELECT driver_id, SUM(amount) AS total_trip_income 
FROM evmoto_account.t_income 
WHERE driver_id = :driver_id AND type = 2 AND date = CURRENT_DATE();
```
