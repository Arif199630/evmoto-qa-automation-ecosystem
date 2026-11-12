#!/usr/bin/env bash
# Emulator tambahan untuk skenario multi-perangkat (suites=skrip2): emulator-5556, dan emulator-5558 bila skripnya
# e2e_multi_user.py (Driver sendirian di 5558 + dua User). Dipanggil satu baris dari android-emulator-runner.
# Emulator pertama tidak memakai -read-only, jadi AVD-nya tidak bisa dipakai dua kali (bukti run 43181530548:
# "Another emulator instance is running"); tiap emulator tambahan memakai AVD sendiri dari system image yang sama.
set -u
mkdir -p bukti
SDK="${ANDROID_HOME:-$ANDROID_SDK_ROOT}"
EMU="$SDK/emulator/emulator"
AVD1=$("$EMU" -list-avds | head -1)
SYSDIR=$(grep '^image.sysdir.1' "$HOME/.android/avd/$AVD1.avd/config.ini" | cut -d= -f2 | tr -d ' ')
PKG=$(echo "${SYSDIR%/}" | tr '/' ';')
AVDMGR=$(ls "$SDK"/cmdline-tools/*/bin/avdmanager | head -1)

nyalakan() {
  local port=$1 avd="evmoto$1" dev="emulator-$1"
  echo "AVD $avd dari $PKG"
  echo no | "$AVDMGR" create avd -n "$avd" -k "$PKG" --force
  nohup "$EMU" -avd "$avd" -port "$port" -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect \
    -no-snapshot -dns-server 8.8.8.8,1.1.1.1 > "bukti/emulator$port.log" 2>&1 &
}

siapkan() {
  local dev="emulator-$1"
  timeout 600 adb -s "$dev" wait-for-device || { tail -20 "bukti/emulator$1.log"; exit 1; }
  timeout 600 adb -s "$dev" shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'
  adb -s "$dev" root || true
  sleep 5
  adb -s "$dev" wait-for-device
  adb -s "$dev" install -r -g apk/evmoto-user.apk
  adb -s "$dev" install -r -g apk/evmoto-driver.apk
  # Lokasi uji di area layanan EvMoto (Jl. Wijaya I, Jakarta Selatan); urutan: bujur lintang
  adb -s "$dev" emu geo fix 106.8037 -6.2449 || true
}

PORTS="5556"
[ "${FILE_INCLUDE:-}" = "e2e_multi_user.py" ] && PORTS="5556 5558"
for p in $PORTS; do nyalakan "$p"; done
for p in $PORTS; do siapkan "$p"; done
adb devices
