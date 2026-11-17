# Satu perintah: nyalakan emulator, pasang APK, set lokasi, nyalakan Appium, lalu jalankan test mobile.
# Contoh:
#   powershell -ExecutionPolicy Bypass -File qa-tools\jalankan_mobile_lokal.ps1                      (test kecil: login User, NT_04)
#   powershell -ExecutionPolicy Bypass -File qa-tools\jalankan_mobile_lokal.ps1 -Semua                (seperti CI: suite mobile dan cross)
#   powershell -ExecutionPolicy Bypass -File qa-tools\jalankan_mobile_lokal.ps1 -Test Frontend\Feature\Step_Definition\test_drv_login.py -K NT_06
#   tambahkan -Jendela untuk melihat layar emulator (default: tanpa jendela, seperti CI)
# Hanya staging/dev. Akun Driver hanya 1: jangan jalankan dua test Driver bersamaan.
param(
    [string]$Test = "Frontend\Feature\Step_Definition\test_login.py",
    [string]$K = "NT_04",
    [switch]$Semua,
    [switch]$Jendela
)
# Continue (bukan Stop): PowerShell 5.1 menganggap keluaran stderr program native sebagai error fatal. Kegagalan penting dicek manual.
$ErrorActionPreference = "Continue"
$Repo = Split-Path -Parent $PSScriptRoot
$Sdk = [Environment]::GetEnvironmentVariable("ANDROID_HOME", "User")
if (-not $Sdk) { $Sdk = Join-Path $env:LOCALAPPDATA "Android\Sdk" }
$env:ANDROID_HOME = $Sdk
$env:ANDROID_SDK_ROOT = $Sdk
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$Sdk\platform-tools;$Sdk\emulator"
$Adb = Join-Path $Sdk "platform-tools\adb.exe"
$Emu = Join-Path $Sdk "emulator\emulator.exe"
$AvdName = "evmoto35"

function Langkah($teks) { Write-Host ""; Write-Host "== $teks" -ForegroundColor Cyan }
function Tunggu-Boot($menit) {
    $batas = (Get-Date).AddMinutes($menit)
    & $Adb wait-for-device | Out-Null
    while ((Get-Date) -lt $batas) {
        $b = (& $Adb shell getprop sys.boot_completed 2>$null | Out-String).Trim()
        if ($b -eq "1") { return }
        Start-Sleep -Seconds 3
    }
    throw "Emulator belum selesai boot dalam $menit menit."
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

Siapkan-Apk $Repo
if (-not (Test-Path (Join-Path $Repo "mobile-apps\.env"))) { throw "mobile-apps\.env belum ada. Salin dulu dari pemilik." }
foreach ($f in @("apk\evmoto-user.apk", "apk\evmoto-driver.apk")) {
    if (-not (Test-Path (Join-Path $Repo $f))) { throw "$f belum ada." }
}
if (-not (Test-Path $Emu)) { throw "Emulator belum terpasang. Jalankan dulu qa-tools\setup_pc_baru.ps1." }

Langkah "1/5 Emulator"
$perangkat = (& $Adb devices | Out-String)
if ($perangkat -notmatch "emulator-\d+\s+device") {
    $opsi = @("-avd", $AvdName, "-no-audio", "-no-boot-anim", "-gpu", "swiftshader_indirect", "-no-snapshot", "-dns-server", "8.8.8.8,1.1.1.1")
    if (-not $Jendela) { $opsi += "-no-window" }
    $p = Start-Process -FilePath $Emu -ArgumentList $opsi -WindowStyle Hidden -PassThru
    Write-Host "   emulator dinyalakan (PID $($p.Id)). Boot pertama bisa 2-5 menit ..."
    Tunggu-Boot 8
    # Sama seperti CI: bahasa Indonesia, animasi dimatikan
    & $Adb root 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    & $Adb wait-for-device | Out-Null
    & $Adb shell "setprop persist.sys.locale id-ID; setprop ctl.restart zygote" 2>&1 | Out-Null
    Start-Sleep -Seconds 25
    Tunggu-Boot 5
    foreach ($a in @("window_animation_scale", "transition_animation_scale", "animator_duration_scale")) {
        & $Adb shell settings put global $a 0 2>&1 | Out-Null
    }
} else {
    Write-Host "   emulator sudah menyala, dipakai apa adanya"
}
Write-Host "   siap"

Langkah "2/5 APK dan lokasi"
foreach ($x in @(@("com.evmoto.user.app", "apk\evmoto-user.apk"), @("com.evmoto.driver.app", "apk\evmoto-driver.apk"))) {
    $ada = (& $Adb shell pm list packages $x[0] | Out-String)
    if ($ada -notmatch [regex]::Escape($x[0])) {
        Write-Host "   memasang $($x[1]) ..."
        & $Adb install -r -g (Join-Path $Repo $x[1])
        if ($LASTEXITCODE -ne 0) { throw "Gagal memasang $($x[1])." }
    } else {
        Write-Host "   $($x[0]) sudah terpasang"
    }
}
# Lokasi default emulator di California; set ke area layanan EvMoto (Jl. Wijaya I, Kebayoran Baru). Urutan: bujur lintang.
& $Adb emu geo fix 106.8037 -6.2449 2>&1 | Out-Null
Write-Host "   lokasi di-set ke area layanan"

Langkah "3/5 Cek jaringan emulator ke staging"
& $Adb shell "ping -c 2 -W 3 evmotodev.justkidding.app" 2>&1 | ForEach-Object { Write-Host "   $_" }

Langkah "4/5 Appium"
function Port-Buka($port) {
    try { $c = New-Object System.Net.Sockets.TcpClient; $c.Connect("127.0.0.1", $port); $c.Close(); return $true } catch { return $false }
}
if (-not (Port-Buka 4723)) {
    $log = Join-Path $Repo "appium.log"
    $pa = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "appium --address 127.0.0.1 --port 4723 --log-level warn > `"$log`" 2>&1" -WindowStyle Hidden -PassThru
    Write-Host "   Appium dinyalakan (PID $($pa.Id)), log: $log"
    $batas = (Get-Date).AddSeconds(60)
    while (-not (Port-Buka 4723) -and (Get-Date) -lt $batas) { Start-Sleep -Seconds 2 }
    if (-not (Port-Buka 4723)) { throw "Appium tidak mau menyala. Lihat $log" }
} else {
    Write-Host "   Appium sudah menyala di port 4723"
}

Langkah "5/5 Menjalankan test"
Set-Location $Repo
if ($Semua) {
    python qa-tools\run_all.py --suite mobile cross
} else {
    Set-Location (Join-Path $Repo "mobile-apps")
    if ($K) { python -m pytest $Test -k $K } else { python -m pytest $Test }
}
Write-Host ""
Write-Host "Selesai. Emulator dan Appium dibiarkan menyala. Matikan lewat PID masing-masing (Stop-Process -Id <PID>), bukan lewat nama proses." -ForegroundColor Green
