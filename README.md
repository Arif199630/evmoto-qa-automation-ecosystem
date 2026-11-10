# EvMoto QA Automation Ecosystem

[![evmoto-regression](https://github.com/Arif199630/evmoto-qa-automation-ecosystem/actions/workflows/ci.yml/badge.svg)](https://github.com/Arif199630/evmoto-qa-automation-ecosystem/actions/workflows/ci.yml)

Regression otomatis untuk ekosistem EvMoto: web Admin Dashboard, REST API backend, aplikasi User dan Driver, serta alur yang menghubungkan ketiganya. Hanya berjalan di environment **dev/staging**.

Semua angka di laporan berasal dari hasil test yang benar-benar dijalankan (JUnit XML). Tidak ada angka lulus yang ditulis tetap.

## Struktur

| Folder | Isi |
|---|---|
| `web-dashboard/` | Test web Admin Dashboard (Selenium, Chrome headless) |
| `mobile-apps/` | Test aplikasi User dan Driver (Appium), test lintas aplikasi, dan `api-testing/` (REST API) |
| `qa-tools/` | Satu perintah regression, quality gate, mock layanan, penggabung hasil, pembuat PDF |
| `performance-testing/` | Load test Locust |
| `docs/` | Test case manual dan laporan |
| `.github/workflows/ci.yml` | Regression di GitHub Actions |

## Menjalankan di GitHub Actions

Tab **Actions** → **evmoto-regression** → **Run workflow**. Workflow juga jalan otomatis setiap push ke `main` dan setiap Senin-Jumat 08:00 WIB.

| Job | Yang diuji | Cara |
|---|---|---|
| `quality-gate` | Kode automation | Menolak method yang tidak ada, assertion palsu, domain production, file test ganda |
| `admin` | Web admin staging | Chrome headless |
| `api` | Backend staging | HTTP; endpoint yang belum ada di staging dijawab mock dan ditandai `mock` di laporan |
| `mobile` (6 shard) | APK User dan Driver dev | Emulator Android x86_64 + Appium, tanpa HP fisik |
| `laporan` | - | Menggabungkan semua hasil menjadi satu PDF (artifact `laporan-regression-pdf`) |

Saat test mobile gagal, CI menyimpan screenshot dan struktur layar (XML) di artifact `hasil-mobile-*`. Dari situ bisa dilihat apakah layar aplikasi memang salah (bug aplikasi) atau locator test yang salah (bug automation).

### Secrets yang dibutuhkan

Settings → Secrets and variables → Actions. Nilainya tidak pernah ditulis di repo.

| Secret | Isi |
|---|---|
| `ENV_WEB_DASHBOARD` | Isi `.env` untuk `web-dashboard/` (format sama dengan `web-dashboard/.env.example`) |
| `ENV_MOBILE_APPS` | Isi `.env` untuk `mobile-apps/` (format sama dengan `mobile-apps/.env.example`) |
| `APK_PASSPHRASE` | Kunci untuk membuka APK dev terenkripsi di Release `apk-dev` |

APK dev disimpan di Release `apk-dev` dalam bentuk terenkripsi (`evmoto-apk-dev.tar.gz.enc`, AES-256). Tanpa `APK_PASSPHRASE` file itu tidak bisa dibuka.

## Menjalankan di komputer sendiri

```bash
pip install -r requirements.txt
cp web-dashboard/.env.example web-dashboard/.env      # isi akun staging
cp mobile-apps/.env.example mobile-apps/.env
python qa-tools/run_all.py --suite admin api --mock-services
```

Mobile butuh emulator Android dan Appium (`mobile-apps/scripts/start_headless_emulator.ps1`). Tanpa emulator, `--simulator` hanya memeriksa kode test, bukan aplikasi. Panduan lengkap: `qa-tools/README.md`, `web-dashboard/PANDUAN_QA_JUNIOR.md`, `mobile-apps/PANDUAN_QA_JUNIOR.md`.

## Aturan data sensitif

- Nomor HP, OTP, PIN, username, dan password akun uji hanya ada di `.env` (tidak di-commit) atau GitHub Secrets.
- Di kode, nilainya dibaca lewat `os.environ.get("NAMA_ENV")`; di dokumen ditulis sebagai `<NAMA_ENV>`.
- `staging_guard.py` membatalkan run bila URL mengarah ke production.
- Sebelum commit, pastikan tidak ada nomor HP, password, token, atau path pribadi di file yang berubah.
