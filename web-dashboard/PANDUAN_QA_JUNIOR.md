# Panduan QA Automation Junior: Admin Dashboard EvMoto

Dokumen ini menjelaskan cara menjalankan dan menambah test untuk web admin EvMoto. Baca dari atas ke bawah sekali, lalu jadikan rujukan.

## 1. Apa yang diuji

Web admin EvMoto (backoffice). Test membuka browser Chrome, login, lalu menguji tiap menu admin.

| Environment | URL admin | Kapan dipakai |
|---|---|---|
| `dev` (staging) | `https://evmotoadmin.justkidding.app` | Default. Pakai ini untuk semua pengujian harian. |
| `production` | `https://dashboard.evmotoid.com` | Hanya bila diminta lead QA. Test bisa mengubah data. |

Environment dipilih lewat `ENVIRONMENT` di file `.env`. Bila kosong, test otomatis memakai `dev`.

## 2. Struktur folder

```text
Automation_Project_EvMoto/
├── config.py                  Pengaturan URL, akun, dan browser
├── .env                       Nilai environment (jangan dibagikan, berisi password)
├── Frontend/Feature/
│   ├── Pages/                 Satu file per menu: locator elemen + aksi (Page Object)
│   ├── Data/                  Data test: akun, payload SQLi/XSS
│   └── Step_Definition/       Skenario test (test_00_login.py ... test_24_...)
├── runners/                   Menjalankan satu modul saja
├── main_runner.py             Menjalankan semua modul + laporan
└── utils/                     Helper BDD, bug tracker, pembuat laporan
```

Aturan sederhana: **locator dan aksi** ada di `Pages/`, **skenario dan assertion** ada di `Step_Definition/`. Jangan menulis XPath langsung di file test.

## 3. Cara menjalankan

```bash
pip install -r requirements.txt pytest pytest-xdist
```

Semua test, tanpa membuka jendela browser (headless):

```bash
ENVIRONMENT=dev HEADLESS=true python -m pytest Frontend/Feature/Step_Definition -q
```

Lebih cepat, 4 browser paralel:

```bash
ENVIRONMENT=dev HEADLESS=true python -m pytest Frontend/Feature/Step_Definition -q -n 4
```

Satu modul saja, misalnya Driver Management:

```bash
ENVIRONMENT=dev HEADLESS=true python -m pytest Frontend/Feature/Step_Definition/test_07_driver_management.py -v
```

## 4. Pola sebuah test

Tiap test mengikuti pola Given-When-Then dan 4 pilar:

| Pilar | Arti | Contoh |
|---|---|---|
| 1 Positif True | Input valid, harus berhasil | Login dengan akun benar |
| 2 Positif False | Input valid, ditolak aturan bisnis | Data duplikat |
| 3 Negatif True | Input salah, harus ditolak dengan pesan | Password kosong |
| 4 Negatif False | Input berbahaya, sistem tetap aman | Payload SQL injection |

Contoh ringkas:

```python
def test_01_pilar1_positif_true_login_valid(self):
    # GIVEN: halaman login terbuka
    self.login_page.navigate()
    # WHEN: pengguna login dengan akun valid
    self.login_page.login(Config.VALID_USER, Config.VALID_PASS)
    # THEN: dashboard tampil
    self.assertTrue(self.login_page.is_dashboard_displayed(), "Dashboard harus tampil setelah login.")
```

Tiap assertion **wajib** memeriksa sesuatu yang bisa gagal dan memberi pesan yang jelas.

## 5. Hal yang perlu diperhatikan

- **Data test bergantung environment.** Beberapa test mencari data yang hanya ada di production (kota Jakarta, brand Polytron, plat B 4923 UCT, driver Bagas). Di staging test itu gagal karena datanya tidak ada, bukan karena aplikasinya rusak. Bila menambah test pencarian, ambil data yang ada di environment yang diuji.
- **Jangan menulis domain langsung.** Pakai `Config.BASE_URL`, jangan menulis `"evmotoid.com"`, supaya test berjalan di semua environment.
- **Hindari `time.sleep`.** Pakai method tunggu di `page_base.py` (`find_visible`, `wait_for_url_contains`). Sleep membuat test lambat dan tetap bisa gagal di jaringan yang pelan.
- **Satu skenario, satu file.** Jangan menyalin file test untuk membuat versi baru. Dua file yang sama membuat setiap test berjalan dua kali.
- **`.env` berisi password.** Jangan di-commit dan jangan dikirim lewat chat.

## 6. Perubahan perapian 9 November 2026

| Perubahan | Alasan |
|---|---|
| `test_login.py` dan `test_profile.py` dipindah ke `_archive/` | Isinya sama persis dengan `test_00_login.py` dan `test_24_profile_navigation.py`, jadi 60 test berjalan dua kali |
| Cek domain di `test_24` memakai domain environment aktif | Sebelumnya selalu gagal di staging karena memeriksa `evmotoid.com` |
| Default `ENVIRONMENT` menjadi `dev` dan `.env` diisi `dev` | Mencegah test tidak sengaja mengubah data production |

Backup sebelum perapian: folder `Automation_Project_EvMoto_backup_2026-11-09` di samping folder ini.

## 7. Cara kerja baru (10 November 2026)

- **Satu perintah untuk regression:** `python ../evmoto-qa-tools/run_all.py --suite all`. Urutannya quality gate, pengaman staging, test per file, lalu laporan PDF di `../evmoto-qa-tools/runs/`. Panduan lengkap ada di `../evmoto-qa-tools/README.md`.
- **Hanya dev/staging.** `staging_guard.py` membatalkan run bila `ENVIRONMENT` bukan dev/staging, atau bila URL mengarah ke `dashboard.evmotoid.com`, `api.evmotoid.com`, `new-api.evmotoid.com`.
- **Quality gate menolak pelanggaran baru:** method yang tidak ada, `assert True` atau `assert x or True`, domain production di file test, file test duplikat. Jalankan `python ../evmoto-qa-tools/quality_gate.py admin` atau `mobile` sebelum commit.
- **Fitur baru:** mulai dari `templates/template_test_fitur_baru.py`.
- **Skip selalu beralasan:** pakai `self.skipTest("alasan")` (Admin) atau `pytest.skip("alasan")` / `@pytest.mark.quarantine(reason="...")` (Mobile/API). Jangan menulis assertion yang selalu lulus.
