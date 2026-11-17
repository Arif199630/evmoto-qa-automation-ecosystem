# Memicu workflow CI (emulator di cloud GitHub) dari PC mana pun TANPA virtualisasi/BIOS, memantau sampai selesai,
# lalu mengunduh hasilnya (XML JUnit, screenshot, laporan PDF) ke folder hasil_ci\<nomor-run>.
# Hanya staging/dev: workflow punya staging_guard yang membatalkan run ke production.
# Contoh:
#   powershell -ExecutionPolicy Bypass -File qa-tools\ci_jalankan.ps1
#   powershell -ExecutionPolicy Bypass -File qa-tools\ci_jalankan.ps1 -Suites mobile -FileFilter "^test_drv_login[.]py" -KFilter NT_04
#   powershell -ExecutionPolicy Bypass -File qa-tools\ci_jalankan.ps1 -HanyaAmbilHasil          (unduh hasil run terakhir)
#   powershell -ExecutionPolicy Bypass -File qa-tools\ci_jalankan.ps1 -HanyaAmbilHasil -RunId 123456789
param(
    [string]$Suites,
    [string]$FileFilter,
    [string]$KFilter,
    [string]$RunId,
    [switch]$HanyaAmbilHasil
)
# Continue (bukan Stop): PowerShell 5.1 menganggap stderr program native sebagai error fatal. Kegagalan penting dicek manual.
$ErrorActionPreference = "Continue"
$Repo = "Arif199630/evmoto-qa-automation-ecosystem"
$Akun = "Arif199630"
$Root = Split-Path -Parent $PSScriptRoot

function Langkah($teks) { Write-Host ""; Write-Host "== $teks" -ForegroundColor Cyan }
function Muat-Path { $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") }

Langkah "1/4 GitHub CLI"
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "   memasang GitHub CLI ..."
    winget install -e --id GitHub.cli --accept-package-agreements --accept-source-agreements --silent
    Muat-Path
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        $gh = "C:\Program Files\GitHub CLI"
        if (Test-Path "$gh\gh.exe") { $env:Path = "$gh;$env:Path" } else { throw "gh belum terdeteksi. Tutup jendela ini, buka lagi, lalu jalankan ulang." }
    }
}
Write-Host "   gh siap"

Langkah "2/4 Login GitHub sebagai $Akun"
$status = (gh auth status 2>&1 | Out-String)
if ($status -notmatch $Akun) {
    Write-Host "   Browser akan terbuka. Login SENDIRI di sana sebagai akun $Akun (password tidak diketik ke terminal)."
    gh auth login --hostname github.com --git-protocol https --web
    $status = (gh auth status 2>&1 | Out-String)
    if ($status -notmatch $Akun) { throw "Login sebagai $Akun belum berhasil. Jalankan ulang dan pilih akun yang benar." }
}
Write-Host "   login OK"

if (-not $HanyaAmbilHasil) {
    Langkah "3/4 Memicu workflow di GitHub Actions"
    if (-not $Suites) {
        $Suites = Read-Host "Suite yang dijalankan: all / admin / api / mobile / skrip  [Enter = all]"
        if (-not $Suites) { $Suites = "all" }
        if (-not $FileFilter) { $FileFilter = Read-Host "Filter nama file test, mis. ^test_drv_login[.]py  [Enter = semua]" }
        if (-not $KFilter) { $KFilter = Read-Host "Filter nama test (pytest -k), mis. NT_04  [Enter = semua]" }
    }
    $argumen = @("workflow", "run", "ci.yml", "-R", $Repo, "-f", "suites=$Suites")
    if ($FileFilter) { $argumen += @("-f", "file_filter=$FileFilter") }
    if ($KFilter) { $argumen += @("-f", "k_filter=$KFilter") }
    $mulai = (Get-Date).ToUniversalTime().AddSeconds(-30)
    gh @argumen
    if ($LASTEXITCODE -ne 0) { throw "Gagal memicu workflow." }
    Write-Host "   workflow dipicu: suites=$Suites file_filter=$FileFilter k_filter=$KFilter"

    Write-Host "   mencari run yang baru dibuat ..."
    $RunId = $null
    for ($i = 0; $i -lt 20 -and -not $RunId; $i++) {
        Start-Sleep -Seconds 5
        $daftar = gh run list -R $Repo --workflow ci.yml --event workflow_dispatch --limit 5 --json databaseId,createdAt,url 2>$null | ConvertFrom-Json
        $baru = $daftar | Where-Object { [datetime]$_.createdAt -ge $mulai } | Select-Object -First 1
        if ($baru) { $RunId = "$($baru.databaseId)"; Write-Host "   run: $($baru.url)" }
    }
    if (-not $RunId) { throw "Run baru tidak ditemukan. Cek tab Actions di GitHub." }

    Write-Host ""
    Write-Host "   Memantau sampai selesai. Run penuh bisa berjam-jam. Boleh tutup jendela ini (Ctrl+C);" -ForegroundColor Yellow
    Write-Host "   hasilnya bisa diunduh nanti lewat 5_CI_AMBIL_HASIL.bat" -ForegroundColor Yellow
    gh run watch $RunId -R $Repo --interval 30 --exit-status
}

Langkah "4/4 Mengunduh hasil"
if (-not $RunId) {
    $terakhir = gh run list -R $Repo --workflow ci.yml --limit 1 --json databaseId 2>$null | ConvertFrom-Json
    $RunId = "$($terakhir[0].databaseId)"
}
if (-not $RunId) { throw "Tidak ada run yang bisa diunduh." }
$out = Join-Path $Root "hasil_ci\$RunId"
New-Item -ItemType Directory -Force $out | Out-Null
gh run download $RunId -R $Repo -D $out
Write-Host "   hasil run $RunId disimpan di: $out" -ForegroundColor Green
$pdf = Get-ChildItem $out -Recurse -Filter *.pdf -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pdf) { Write-Host "   laporan PDF: $($pdf.FullName)"; Start-Process $pdf.FullName }
Start-Process explorer.exe $out
