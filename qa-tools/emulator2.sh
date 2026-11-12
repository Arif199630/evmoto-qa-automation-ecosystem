#!/usr/bin/env bash
# Emulator ke-2 (AVD yang sama, read-only) untuk skenario multi-pengguna: emulator-5556.
# Dipanggil dari langkah android-emulator-runner (satu baris per perintah) saat suites=skrip2.
set -u
mkdir -p bukti
EMU="${ANDROID_HOME:-$ANDROID_SDK_ROOT}/emulator/emulator"
AVD=$("$EMU" -list-avds | head -1)
echo "Menyalakan emulator ke-2 dari AVD $AVD"
nohup "$EMU" -avd "$AVD" -read-only -port 5556 -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect \
  -no-snapshot -dns-server 8.8.8.8,1.1.1.1 > bukti/emulator2.log 2>&1 &
timeout 600 adb -s emulator-5556 wait-for-device
timeout 600 adb -s emulator-5556 shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'
adb -s emulator-5556 root || true
sleep 5
adb -s emulator-5556 wait-for-device
adb -s emulator-5556 install -r -g apk/evmoto-user.apk
adb -s emulator-5556 install -r -g apk/evmoto-driver.apk
# Lokasi uji di area layanan EvMoto (Jl. Wijaya I, Jakarta Selatan); urutan: bujur lintang
adb -s emulator-5556 emu geo fix 106.8037 -6.2449 || true
adb devices
