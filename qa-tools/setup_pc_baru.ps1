# Setup SEKALI JALAN untuk PC baru: Python, Node, JDK, Android SDK + emulator (meniru emulator CI), Appium.
# Jalankan dari PowerShell di folder repo:
#   powershell -ExecutionPolicy Bypass -File qa-tools\setup_pc_baru.ps1
# Aman dijalankan ulang (langkah yang sudah ada dilewati). Tidak menyentuh Production, tidak menyimpan kredensial.
# Syarat manual (tidak bisa otomatis): virtualisasi aktif di BIOS, file mobile-apps\.env, dan apk\evmoto-user.apk + apk\evmoto-driver.apk.
# Continue (bukan Stop): PowerShell 5.1 menganggap keluaran stderr program native sebagai error fatal. Kegagalan penting dicek manual.
$ErrorActionPreference = "Continue"
$Repo = Split-Path -Parent $PSScriptRoot
$Sdk = Join-Path $env:LOCALAPPDATA "Android\Sdk"
$AvdName = "evmoto35"
$Image = "system-images;android-35;google_apis;x86_64"   # sama dengan CI (api-level 35, google_apis, x86_64)
$ImageQ = [char]34 + $Image + [char]34                       # kutip wajib: tanda ; dibaca pemisah argumen oleh .bat

function Langkah($teks) { Write-Host ""; Write-Host "== $teks" -ForegroundColor Cyan }
function Ok($teks) { Write-Host "   OK  $teks" -ForegroundColor Green }
function Peringatan($teks) { Write-Host "   !!  $teks" -ForegroundColor Yellow }
function Muat-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Bisa($perintah, $argumen) {
    try { & $perintah $argumen 2>&1 | Out-Null; return ($LASTEXITCODE -eq 0) } catch { return $false }
}
function Pasang-Winget($id, $nama) {
    Write-Host "   memasang $nama ..."
    winget install -e --id $id --accept-package-agreements --accept-source-agreements --silent
    Muat-Path
}

# Salin otomatis APK dari folder Download kalau belum ada di apk\ (nama di Download: UserApps.apk dan DriverApps.apk)
function Siapkan-Apk($Repo) {
    New-Item -ItemType Directory -Force (Join-Path $Repo "apk") | Out-Null
    $unduhan = Join-Path $HOME "Downloads"
    foreach ($m in @(@("UserApps.apk", "evmoto-user.apk"), @("DriverApps.apk", "evmoto-driver.apk"))) {
        $tujuan = Join-Path $Repo ("apk\" + $m[1])
        $sumber = Join-Path $unduhan $m[0]
        if ((-not (Test-Path $tujuan)) -and (Test-Path $sumber)) {
            Copy-Item $sumber $tujuan
            Write-Host "   APK disalin dari Download: $($m[0]) -> apk\$($m[1])" -ForegroundColor Green
        }
    }
}

Langkah "1/6 Alat dasar (Python 3.12, Node.js LTS, JDK 17)"
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "winget tidak ditemukan. Pasang 'App Installer' dari Microsoft Store, lalu jalankan ulang." }
if (-not (Bisa "python" "--version")) { Pasang-Winget "Python.Python.3.12" "Python 3.12" }
if (-not (Bisa "node" "--version")) { Pasang-Winget "OpenJS.NodeJS.LTS" "Node.js LTS" }
if (-not (Bisa "java" "-version")) { Pasang-Winget "EclipseAdoptium.Temurin.17.JDK" "JDK 17" }
if (-not (Bisa "java" "-version")) {
    $jdk = Get-ChildItem "C:\Program Files\Eclipse Adoptium" -Directory -Filter "jdk-17*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($jdk) {
        $env:JAVA_HOME = $jdk.FullName
        $env:Path = "$($jdk.FullName)\bin;$env:Path"
        [Environment]::SetEnvironmentVariable("JAVA_HOME", $jdk.FullName, "User")
    }
}
foreach ($n in @(@("python", "--version"), @("node", "--version"), @("java", "-version"))) {
    if (Bisa $n[0] $n[1]) { Ok "$($n[0]) terpasang" } else { throw "$($n[0]) belum terdeteksi. Tutup PowerShell, buka lagi, lalu jalankan ulang skrip ini." }
}

Langkah "2/6 Android command-line tools"
$sdkmanager = Join-Path $Sdk "cmdline-tools\latest\bin\sdkmanager.bat"
$avdmanager = Join-Path $Sdk "cmdline-tools\latest\bin\avdmanager.bat"
if (-not (Test-Path $sdkmanager)) {
    $zip = Join-Path $env:TEMP "cmdline-tools.zip"
    $tmp = Join-Path $env:TEMP "cmdline-tools-ex"
    Write-Host "   mengunduh command-line tools ..."
    # curl.exe (bawaan Windows 10/11) menampilkan persen kemajuan; Invoke-WebRequest di PowerShell 5.1 tidak
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    curl.exe -L --fail --retry 3 -o $zip "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $zip)) { throw "Unduhan command-line tools gagal. Cek koneksi internet, lalu jalankan ulang." }
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    Expand-Archive $zip $tmp -ErrorAction Stop
    New-Item -ItemType Directory -Force (Join-Path $Sdk "cmdline-tools") | Out-Null
    Move-Item (Join-Path $tmp "cmdline-tools") (Join-Path $Sdk "cmdline-tools\latest") -ErrorAction Stop
}
Ok "command-line tools ada di $Sdk"

Langkah "3/6 Android SDK: platform-tools, emulator, API 35, system image"
$env:ANDROID_HOME = $Sdk
$env:ANDROID_SDK_ROOT = $Sdk
Write-Host "   menerima lisensi SDK ..."
(1..40 | ForEach-Object { "y" }) | & $sdkmanager --licenses 2>&1 | Out-Null
Write-Host "   memasang paket SDK (beberapa GB, mohon tunggu) ..."
& $sdkmanager "platform-tools" "emulator" ([char]34 + "platforms;android-35" + [char]34) $ImageQ
if ($LASTEXITCODE -ne 0) { throw "sdkmanager gagal memasang paket SDK." }
Ok "paket SDK terpasang"

# ANDROID_HOME dan PATH permanen (tingkat user, bukan sistem)
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $Sdk, "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $Sdk, "User")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
foreach ($p in @("$Sdk\platform-tools", "$Sdk\emulator", "$Sdk\cmdline-tools\latest\bin")) {
    if ($userPath -notlike "*$p*") { $userPath = "$userPath;$p" }
}
[Environment]::SetEnvironmentVariable("Path", $userPath, "User")
Muat-Path

Langkah "4/6 Emulator '$AvdName' (Pixel 6, API 35, RAM 4 GB, seperti CI)"
$daftar = & $avdmanager list avd 2>&1 | Out-String
if ($daftar -notmatch "Name:\s+$AvdName") {
    ("no" | & $avdmanager create avd -n $AvdName -k $ImageQ -d pixel_6 --force) | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "avdmanager gagal membuat emulator." }
}
$cfg = Join-Path $HOME ".android\avd\$AvdName.avd\config.ini"
if (Test-Path $cfg) {
    $isi = Get-Content $cfg
    if ($isi -match "^hw\.ramSize=") { $isi = $isi -replace "^hw\.ramSize=.*", "hw.ramSize=4096" } else { $isi += "hw.ramSize=4096" }
    if ($isi -match "^disk\.dataPartition\.size=") { $isi = $isi -replace "^disk\.dataPartition\.size=.*", "disk.dataPartition.size=6000M" } else { $isi += "disk.dataPartition.size=6000M" }
    Set-Content -Path $cfg -Value $isi -Encoding ASCII
}
Ok "emulator $AvdName siap"
Write-Host "   cek akselerasi virtualisasi:"
& (Join-Path $Sdk "emulator\emulator.exe") -accel-check 2>&1 | ForEach-Object { Write-Host "     $_" }

Langkah "5/6 Dependensi Python dan Appium"
Set-Location $Repo
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
python -m pip install -r mobile-apps\requirements.txt --quiet
Ok "paket Python terpasang"
$appiumAda = $false
try { npm list -g appium --depth=0 2>&1 | Out-Null; $appiumAda = ($LASTEXITCODE -eq 0) } catch { }
if (-not $appiumAda) { npm install -g appium@3 }
$drivers = (appium driver list --installed 2>&1 | Out-String)
if ($drivers -notmatch "uiautomator2") { appium driver install uiautomator2 }
Ok "Appium dan driver uiautomator2 siap"

Langkah "6/6 Cek berkas yang harus disiapkan manual"
Siapkan-Apk $Repo
$kurang = @()
if (-not (Test-Path (Join-Path $Repo "mobile-apps\.env"))) { $kurang += "mobile-apps\.env (isi dari pemilik, jangan di-commit)" }
if (-not (Test-Path (Join-Path $Repo "apk\evmoto-user.apk"))) { $kurang += "apk\evmoto-user.apk" }
if (-not (Test-Path (Join-Path $Repo "apk\evmoto-driver.apk"))) { $kurang += "apk\evmoto-driver.apk" }
if ($kurang.Count -eq 0) { Ok "mobile-apps\.env dan kedua APK sudah ada" } else { $kurang | ForEach-Object { Peringatan "belum ada: $_" } }

Write-Host ""
Write-Host "Setup selesai. Langkah berikutnya: powershell -ExecutionPolicy Bypass -File qa-tools\jalankan_mobile_lokal.ps1" -ForegroundColor Green
