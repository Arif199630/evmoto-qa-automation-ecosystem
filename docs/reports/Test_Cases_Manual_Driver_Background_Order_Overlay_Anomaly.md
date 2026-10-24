# Test Cases Manual: Driver Background Standby & Order Overlay Anomaly

**Dokumentasi Resmi QA Engineering EVMOTO**  
- **Target Aplikasi:** Mobile Android Driver Apps v1.9.27 (`com.evmoto.driver.app`) & Backend Dispatcher
- **Target Fitur:** Background Standby, Floating Overlay Window (`FlutterOverlayWindow`), Screen WakeLock, & Multi-Driver Bidding
- **Tanggal Pembaruan:** 2026-10-24 10:46:35
- **Penyusun:** Bhagus Arif Prayogo (Senior QA Engineer) & Antigravity QA Agent
- **Status Investigasi:** 🚨 CRITICAL BUG DETECTED (Pop-up order hanya muncul 3-5 detik saat handphone dibuka dari standby)

---

## 1. Ringkasan Eksekutif & Problem Statement

Mitra driver yang sedang standby dengan status **ONLINE** namun tidak membuka aplikasi EVMOTO secara foreground (smartphone dalam kondisi layar mati/terkunci di kantong/holder motor atau sedang membuka aplikasi lain seperti WhatsApp/TikTok/Maps) melaporkan bahwa:
> *"Saat order masuk ketika handphonenya dibuka saat mau liat popup order hanya muncul 3-5 detik saja langsung hilang, padahal driver mau swap/swipe orderan."*

Investigasi teknis membuktikan anomali ini berakar pada kombinasi:
1. **Missing Full-Screen Intent & Screen WakeLock:** Notifikasi order masuk tidak otomatis menyalakan layar ponsel, menyebabkan durasi countdown 15-20 detik terbuang 10-12 detik saat hp berada di kantong driver.
2. **Multi-Driver Bidding Race Condition:** Model broadcast pesanan "Siapa Cepat Dia Dapat" disambar driver lain yang sedang aktif foreground, memicu socket event `home_order_taken` yang menutup overlay secara mendadak tanpa transisi pesan yang informatif.
3. **Android Doze Mode & Lifecycle Resume Focus Conflict:** Focus window manager saat ponsel dibuka memicu collision pada `FlutterOverlayWindow`.

---

## 2. Matriks Test Case Manual Berbasis 4 Pilar QA

| Test Case ID | 4 Pilar QA | Priority | Modul / Komponen | Judul Skenario | Status Aktual |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-DRV-BG-01** | Pilar 1: Positif True | P0 (Critical) | Driver Background Overlay | Verifikasi Pop-Up Order Muncul dan Bertahan Utuh saat Driver Standby Membuka Aplikasi Lain | ❌ **FAILED (Bug 3-5s)** |
| **TC-DRV-BG-02** | Pilar 1: Positif True | P0 (Critical) | Driver Screen WakeLock | Verifikasi Layar Otomatis Menyala (Turn Screen On) saat Order Masuk dalam Kondisi Terkunci | ❌ **FAILED (Bug 3-5s)** |
| **TC-DRV-BG-03** | Pilar 2: Positif False | P0 (Critical) | Countdown Decay Guard | Proteksi Timer Decay: Grace Window Minimal 15 Detik saat Smartphone Baru Dibuka | ❌ **FAILED (Bug 3-5s)** |
| **TC-DRV-BG-04** | Pilar 2: Positif False | P1 (High) | Bidding Timeout | Verifikasi Penutupan Otomatis dan Status Auto-Reject saat Batas Waktu Bidding Habis Wajar | ✅ **PASSED** |
| **TC-DRV-BG-05** | Pilar 3: Negatif True | P0 (Critical) | Multi-Driver Bidding | Feedback Transisi Visual saat Order Diambil Driver Lain pada Model Siapa Cepat Dia Dapat | ❌ **FAILED (Bug Silent)** |
| **TC-DRV-BG-06** | Pilar 3: Negatif True | P1 (High) | Doze Mode Resilience | Ketahanan Koneksi Socket dan Timer Overlay saat Melewati Mode Hemat Daya Android | ✅ **PASSED** |
| **TC-DRV-BG-07** | Pilar 4: Negatif False | P0 (Critical) | Lifecycle Focus Guard | Proteksi Transisi Lifecycle (`resumed`) Mencegah Accidental Dismissal pada Overlay Window | ❌ **FAILED (Bug Conflict)** |
| **TC-DRV-BG-08** | Pilar 4: Negatif False | P1 (High) | OS Permission Guard | Deteksi dan Panduan Izin Autostart & Abaikan Optimalisasi Baterai pada OEM Android | ✅ **PASSED** |

---

## 3. Rincian Langkah Pengujian Setiap Skenario

### TC-DRV-BG-01: Verifikasi Pop-Up Order Muncul dan Bertahan Utuh saat Driver Membuka App Lain
- **Tujuan:** Memastikan floating overlay window bertahan minimal 20 detik saat driver sedang membuka WhatsApp.
- **Pra-Kondisi:** Driver akun 82283737237 status Online, EVMoto di background, WhatsApp aktif di layar. Izin overlay diizinkan.
- **Langkah-Langkah:**
  1. Trigger order baru dari backend ke driver.
  2. Amati floating overlay muncul di atas layar WhatsApp bersamaan dengan audio alert `new_order_incoming_1.mp3`.
  3. Tunggu 8 detik, lalu geser slider *"Swipe untuk mendapatkan orderan"*.
- **Hasil Diharapkan:** Pop-up tidak hilang dalam 3-5 detik. Swipe berhasil mengunci orderan ke status "Sedang Menjemput".
- **Hasil Aktual Saat Ini:** ❌ Pop-up lenyap dalam 3-5 detik sebelum sempat digeser.

### TC-DRV-BG-02: Verifikasi Layar Otomatis Menyala saat Order Masuk dalam Kondisi Layar Mati
- **Tujuan:** Layar smartphone harus otomatis menyala seketika order di-dispatch saat ponsel terkunci.
- **Pra-Kondisi:** Smartphone driver standby di kantong/holder dengan layar mati (Screen OFF).
- **Langkah-Langkah:**
  1. Kirim order masuk ke driver.
  2. Amati apakah layar ponsel langsung hidup otomatis.
- **Hasil Diharapkan:** Sistem memicu `FULL_SCREEN_INTENT` / `FLAG_TURN_SCREEN_ON` + `WAKE_LOCK`. Layar langsung ON menampilkan pop-up order.
- **Hasil Aktual Saat Ini:** ❌ Layar tetap mati gulita, hanya audio berdering. Driver butuh 10-12s untuk membuka hp sehingga waktu terbuang.

### TC-DRV-BG-03: Proteksi Timer Decay: Grace Window Minimal 15 Detik
- **Tujuan:** Mencegah hangusnya waktu acceptance saat hp terlambat dibuka.
- **Pra-Kondisi:** Ponsel di saku motor selama 10 detik saat notifikasi berbunyi.
- **Langkah-Langkah:**
  1. Buka kunci layar pada detik ke-11.
  2. Amati angka countdown yang tertera.
- **Hasil Diharapkan:** Driver diberikan Grace Window minimal 15 detik efektif terhitung sejak layar dibuka.
- **Hasil Aktual Saat Ini:** ❌ Countdown hanya menyisakan 3-4 detik lalu langsung lenyap.

### TC-DRV-BG-05: Feedback Transisi Visual saat Order Diambil Driver Lain
- **Tujuan:** Menyajikan feedback visual yang jelas saat order disambar driver lain dalam sistem broadcast.
- **Pra-Kondisi:** Order di-blast ke Driver A dan Driver B.
- **Langkah-Langkah:**
  1. Driver B swipe order di detik ke-5.
  2. Server kirim event `order_taken` ke Driver A.
  3. Amati tampilan di layar Driver A.
- **Hasil Diharapkan:** Tampil feedback dialog *"Orderan sudah diambil"* dan *"Semoga lain kali lebih beruntung!"* selama 3 detik sebelum overlay ditutup.
- **Hasil Aktual Saat Ini:** ❌ Overlay lenyap seketika tanpa pesan apapun (silent vanishing).

### TC-DRV-BG-07: Proteksi Transisi Lifecycle Mencegah Accidental Dismissal
- **Tujuan:** Focus transisi window OS tidak boleh merusak floating overlay.
- **Pra-Kondisi:** Pop-up overlay aktif, driver mengetuk icon EVMoto di recent apps.
- **Langkah-Langkah:**
  1. Amati transisi `AppLifecycleState.paused` -> `AppLifecycleState.resumed`.
- **Hasil Diharapkan:** Overlay tetap terpasang di WindowManager hingga driver swipe atau timeout habis.
- **Hasil Aktual Saat Ini:** ❌ Terjadi focus collision yang memicu `closeOrderOverlay()` secara prematur.

---

## 4. Rekomendasi Solusi Teknikal untuk Developer

1. **Mobile Flutter Team:**
   - Tambahkan `fullScreenIntent: true` pada `AndroidNotificationDetails` di `NotificationHelper`.
   - Konfigurasikan `WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON` dan `FLAG_KEEP_SCREEN_ON` pada `MainActivity` dan `OverlayService`.
   - Ubah logika timer di `OverlayOrderNotificationController` agar menghitung waktu berdasarkan timestamp saat layar pertama kali menyala (display on event), bukan saat background socket menerima event.
   - Tambahkan transisi animasi 3 detik dengan pesan `home_better_luck_next_time_id` saat menerima event `order_taken`.

2. **Backend Golang / Java Team:**
   - Pertimbangkan penerapan *Single-Driver Dedicated Window* (misal 15 detik untuk 1 driver prioritas sebelum dilempar ke driver berikutnya), bukan *blind blast* yang menimbulkan race condition ekstrem.
   - Sertakan parameter `server_dispatch_time` dan `display_grace_seconds` pada payload WebSocket order.
