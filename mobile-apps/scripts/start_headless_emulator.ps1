<#
Menyalakan emulator Android TANPA jendela + Appium, lalu memasang APK staging.
Dengan ini test mobile menguji aplikasi EvMoto yang sebenarnya, tanpa HP fisik.

Kebutuhan mesin: RAM bebas minimal 4 GB, virtualisasi (WHPX/Hyper-V) aktif, Android SDK, Node + Appium.
Laptop QA dengan RAM pas-pasan sebaiknya memakai mesin CI/server (lihat ci/github-actions-android.yml).

Pemakaian (PowerShell, dari folder project):
  .\scripts\start_headless_emulator.ps1                 # AVD bawaan Samsung_Galaxy_S25, RAM 2048 MB
  .\scripts\start_headless_emulator.ps1 -Avd evmoto_ci -RamMb 1536
Setelah "SIAP", jalankan test tanpa HEADLESS_MOBILE:
  python ..\evmoto-qa-tools\run_all.py --suite mobile cross
#>
param(
    [string]$Avd = "Samsung_Galaxy_S25",
    [int]$RamMb = 2048,
    [int]$BootTimeoutSec = 300
)
$ErrorActionPreference = "Stop"
$sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA "Android\Sdk" }
$emulator = Join-Path $sdk "emulator\emulator.exe"
$adb = Join-Path $sdk "platform-tools\adb.exe"
if (-not (Test-Path $emulator)) { throw "Emulator tidak ditemukan di $emulator. Pasang Android SDK Emulator." }

# 1. Emulator tanpa jendela, tanpa audio, tanpa menyimpan snapshot
$logFile = Join-Path $env:TEMP "evmoto_emulator.log"
Start-Process -FilePath $emulator -ArgumentList @("-avd", $Avd, "-memory", $RamMb, "-no-window", "-no-audio",
    "-no-boot-anim", "-no-snapshot-save", "-gpu", "swiftshader_indirect") -RedirectStandardOutput $logFile -WindowStyle Hidden
Write-Host "Menunggu emulator '$Avd' boot (maks $BootTimeoutSec detik)..."
& $adb wait-for-device
$deadline = (Get-Date).AddSeconds($BootTimeoutSec)
do {
    Start-Sleep -Seconds 5
    $booted = (& $adb shell getprop sys.boot_completed 2>$null) -replace "\s", ""
} until ($booted -eq "1" -or (Get-Date) -gt $deadline)
if ($booted -ne "1") { throw "Emulator belum boot dalam $BootTimeoutSec detik. Cek $logFile (sering karena RAM kurang)." }

# 2. Matikan animasi supaya test stabil
& $adb shell settings put global window_animation_scale 0
& $adb shell settings put global transition_animation_scale 0
& $adb shell settings put global animator_duration_scale 0

# 3. Pasang APK staging dari .env (EVMOTO_USER_APK, EVMOTO_DRIVER_APK)
$envFile = Join-Path (Split-Path $PSScriptRoot -Parent) ".env"
foreach ($key in "EVMOTO_USER_APK", "EVMOTO_DRIVER_APK") {
    $line = Get-Content $envFile | Where-Object { $_ -match "^$key=" } | Select-Object -First 1
    $apk = if ($line) { ($line -split "=", 2)[1].Trim('"', " ") } else { "" }
    if ($apk -and (Test-Path $apk)) { & $adb install -r -g $apk | Out-Null; Write-Host "Terpasang: $apk" }
    else { Write-Warning "$key belum diisi atau file tidak ada; APK tidak dipasang." }
}

# 4. Appium
$appium = Get-Command appium -ErrorAction SilentlyContinue
if (-not $appium) { throw "Appium belum terpasang: npm install -g appium; appium driver install uiautomator2" }
Start-Process -FilePath $appium.Source -ArgumentList @("--address", "127.0.0.1", "--port", "4723", "--log-level", "warn") -WindowStyle Hidden
Write-Host "SIAP: emulator '$Avd' dan Appium (127.0.0.1:4723) berjalan tanpa jendela."
