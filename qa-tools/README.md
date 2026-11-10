# evmoto-qa-tools: regression EvMoto yang valid, tanpa device fisik

Folder ini menjalankan seluruh automation EvMoto (Admin Dashboard, REST API, Mobile User & Driver, lintas aplikasi) dengan satu perintah, hanya di dev/staging.

## Satu perintah

```bash
python run_all.py --suite all              # semua suite (mobile butuh emulator headless + Appium)
python run_all.py --suite admin api        # tanpa mobile
python run_all.py --suite all --simulator  # mobile memakai simulator; hasil mobile = validasi kode test saja
```

Urutan yang dijalankan:

1. **Quality gate** (`quality_gate.py`): menolak run bila ada pelanggaran **baru**, yaitu method yang dipanggil tetapi tidak ada, `assert True` / `assert x or True` / `assertTrue(True)`, domain production di file test, file test duplikat, atau conftest ganda.
2. **Pengaman staging** (`staging_guard.py` di tiap project): run dibatalkan bila `ENVIRONMENT` bukan dev/staging atau URL mengarah ke `dashboard.evmotoid.com`, `api.evmotoid.com`, `new-api.evmotoid.com`.
3. **Test**: tiap file test di prosesnya sendiri (`run_per_file.py`), paralel, hasil JUnit XML per file.
4. **Laporan** (`report.py`): `runs/<tanggal_jam>/Laporan_Regression_EvMoto.pdf`, semua angka dari JUnit XML.

Progres live: `python progress_server.py`, lalu buka `http://localhost:8799`.

## Arti status

| Status | Arti |
|---|---|
| Lulus | Sistem staging berperilaku sesuai harapan test |
| Gagal / Error | Ada yang salah di sistem, data, atau kode test; lihat penyebab di PDF |
| Skip | Selalu dengan alasan tertulis: karantina, URL staging belum ada, atau data uji belum ada |

**Karantina** (`@pytest.mark.quarantine(reason=...)`) dipakai untuk test yang belum bisa divalidasi terhadap staging, misalnya endpoint belum dideploy. Test ini tidak dihitung lulus maupun gagal. Jalankan dengan `RUN_QUARANTINE=1` untuk mencobanya.

## Mobile tanpa HP fisik

| Mode | Perintah | Yang teruji |
|---|---|---|
| Emulator headless + Appium | `scripts/start_headless_emulator.ps1` lalu `run_all.py --suite mobile cross` | Aplikasi EvMoto sungguhan |
| CI (Linux + KVM) | `ci/github-actions-android.yml` di project mobile | Aplikasi sungguhan, terjadwal |
| Simulator | `run_all.py --suite mobile --simulator` | Hanya kode test dan Page Object |

Tanpa Appium dan tanpa `--simulator`, test mobile gagal dengan pesan jelas; tidak ada lagi perpindahan diam-diam ke simulator.

## Checklist setiap ada fitur baru

1. Salin template: `templates/template_test_fitur_baru.py` di project terkait.
2. Locator dan aksi baru masuk ke Page Object, bukan ke file test.
3. Logika angka (tarif, subsidi, saldo, kuota) diuji lewat API (`api-testing/suites/`) dengan data yang dibuat test sendiri.
4. Kontrak API dari backend (OpenAPI/kode), bukan dari respons mock. Bila endpoint belum ada di staging, beri `quarantine` dengan alasan.
5. Jalankan `python quality_gate.py <admin|mobile>` sampai LULUS.
6. Jalankan `python run_all.py --suite <suite terkait>` dan lampirkan PDF-nya ke PR/tiket fitur.
7. Setelah membereskan pelanggaran lama: `python quality_gate.py <project> --update-baseline`.

## Mock layanan yang belum ada di staging

Sebagian test API butuh layanan atau endpoint yang belum ada di staging. Tanpa mock, test itu di-skip. Dengan mock, test dijalankan ke server tiruan di laptop sendiri (`mock_services/mock_server.py`, hanya `127.0.0.1`, tanpa paket pip baru).

**Hasil test mock BUKAN bukti backend berjalan.** Test itu hanya membuktikan alur automation benar terhadap kontrak tiruan. Di JUnit XML, test yang memanggil mock punya properti `mock=true`, dan PDF memberi catatan jumlahnya.

### Cara menjalankan

```bash
# lewat run_all (mock dinyalakan dan dimatikan otomatis, log di runs/<tanggal_jam>/mock_services.log)
python run_all.py --suite api --mock-services

# manual
python mock_services/mock_server.py                      # terminal 1, port 8790
cd ../evmoto-user-mobile-automation/api-testing           # terminal 2
USE_MOCK_SERVICES=1 python -m pytest -q -o addopts="" -p no:cacheprovider
```

Tanpa `USE_MOCK_SERVICES=1` semuanya berjalan seperti biasa (test tetap di-skip/karantina). Bila mock belum jalan, pytest berhenti dengan pesan jelas. Jangan menjalankan dua pytest sekaligus ke mock yang sama: tiap sesi pytest me-reset state mock.

### Yang di-mock

| Layanan (fixture) | Endpoint | Test yang terbuka |
|---|---|---|
| ECGO SuperApps (`ecgo_superapps.json`) | `POST /v5/users/onboarding/generateOtp/sms`, `POST /v5/users/onboarding/verifyOtp`, `GET /v5/users/evmoto-connect/status`, `POST /v5/users/evmoto-connect/start`, `GET /v5/users/diskon/list` | suite ECGO (auth 04-06, boundary 04, security 04, `test_ecgo_swap_api`, integrated 02 & 05) |
| ECGO Connect bridge (`connect_bridge.json`) | `POST /connect/link` | alur penautan akun |
| EvMoto fitur baru (`evmoto_new_features.json`) | `GET /account/base/driver/freeSwapDaily`, `PUT /account/base/user`, `POST /account/base/user/threeLogin`, `POST /order/api/order/rushHourSubsidy` | karantina Fitur 2, 3, 5 |
| EvMoto order (`evmoto_order.json`) | `POST /order/api/user/estimateFare`, `/createOrder`, `/cancelOrder` | karantina `usr_02`-`usr_04` |

Yang **tetap ke staging sungguhan**: login driver/penumpang, `queryHomeData`, `ecgo/wallet/status`, `v2/online`, dan halaman Dashboard Admin (`/login`, `/ecgoConnect`, `/freeSwap`, `/ecgoConnect/drivers`). Pengaman production tetap aktif.

Cara kerjanya: `api-testing/mock_layanan.py` mengisi `ECGO_API_BASE_URL` (bila kosong) dan `CONNECT_BRIDGE_URL` (bila tidak diisi) ke mock, `ApiConfig.MOCK_ROUTED_ENDPOINTS` menentukan endpoint EvMoto mana yang dikirim ke mock, dan `KARANTINA_DENGAN_MOCK` menentukan test karantina mana yang dijalankan. Akun ECGO mock memakai nomor palsu `080000000001`; semua data mock berawalan `QA-MOCK`.

Akun ECGO mock sudah tertaut di awal (`sudah_terhubung_di_awal: true`), jadi tiap file test bisa jalan sendiri. Untuk mencoba alur penautan dari awal (start, lalu `/connect/link`, lalu status), kirim `POST /__reset` dengan body `{"ecgo_terhubung": false}`.

### Aturan kontrak mock

1. Kontrak mock (field, kode status, aturan bisnis di `fixtures/*.json`) diambil dari yang diuji test, **bukan** dari backend. Wajib dikonfirmasi tim backend sebelum dianggap benar.
2. Ubah perilaku lewat fixture JSON dulu. Kode Python di `mock_server.py` hanya untuk rute yang butuh state (lock tanggal, duplikat order, klaim voucher, status tertaut).
3. Rute tanpa state cukup ditulis di fixture: `{"method": "GET", "path": "/x", "respons": {"status": 200, "body": {...}}}`.
4. Jangan menulis data pribadi asli di fixture. Pakai awalan `QA-MOCK` dan nomor palsu.

### Menghapus mock setelah staging siap

1. Hapus endpoint dari `ApiConfig.MOCK_ROUTED_ENDPOINTS` (`api-testing/config/api_config.py`), atau isi `ECGO_API_BASE_URL` di `.env` untuk ECGO.
2. Hapus test dari `KARANTINA_DENGAN_MOCK` (`api-testing/mock_layanan.py`), lalu lepas `@pytest.mark.quarantine` bila test sudah lulus ke staging.
3. Hapus rute dari `mock_services/fixtures/*.json` (dan handler-nya di `mock_server.py` bila tidak dipakai lagi).
4. Jalankan tanpa `--mock-services`; pastikan test itu lulus ke staging tanpa properti `mock=true`.

## Pekerjaan yang masih terbuka

- Mobile: 32 method dipanggil tetapi belum ada, 127 `assert True` bertanda `TODO(QA)` (tercatat di `quality_baseline_mobile.json`).
- API: 21 test dikarantina (free swap, voucher onboarding, rush hour subsidy, order user) sampai endpoint/kontrak dikonfirmasi backend; test ECGO di-skip sampai `ECGO_API_BASE_URL` staging diisi.
- Admin: pencarian Vehicle Brand di staging tidak menemukan brand yang ada (kandidat bug aplikasi, perlu dicek developer).
