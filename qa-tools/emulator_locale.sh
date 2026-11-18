#!/usr/bin/env bash
# Mengatur bahasa Indonesia di emulator CI dengan restart zygote, dan MENYALAKAN ULANG emulator bila crash setelahnya.
# Latar belakang (17 Nov 2026): restart zygote membuat swiftshader crash secara acak (galat 'context was preempted', lalu adb
# 'error: closed' / 'device offline'; sekitar 1 dari 16 shard per run), sehingga seluruh test shard itu tidak berjalan.
# Tanpa restart zygote, aplikasi tampil berbahasa Inggris (Appium language/locale, -prop, dan set-app-locales terbukti tidak cukup di API 35).
# Data emulator tetap setelah crash, jadi persist.sys.locale=id-ID yang sudah ditulis ikut terbaca saat boot ulang.
# Dipanggil dari ci.yml setelah emulator pertama menyala (android-emulator-runner menjalankan tiap baris script sebagai perintah terpisah,
# sehingga logika bercabang ditaruh di file ini).
set -u

SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/local/lib/android/sdk}}"
AVD_NAME="${AVD_NAME:-test}"   # nama default android-emulator-runner
EMU_OPTS=(-no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -no-snapshot -dns-server 8.8.8.8,1.1.1.1)

boot_ok() { [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; }
tunggu_boot() { # $1 = jumlah percobaan (2 detik per percobaan)
  local i
  for i in $(seq 1 "$1"); do boot_ok && return 0; sleep 2; done
  return 1
}

adb wait-for-device
tunggu_boot 90 || { echo "EMULATOR_TIDAK_BOOT_AWAL"; exit 1; }
sleep 15   # beri waktu emulator tenang sebelum zygote di-restart

adb shell "setprop persist.sys.locale id-ID; setprop ctl.restart zygote" || echo "setprop/restart zygote gagal; lanjut cek kesehatan emulator"
sleep 25

if [ "${SIMULASI_EMULATOR_MATI:-false}" = "true" ]; then
  echo "SIMULASI: mematikan emulator untuk menguji jalur pemulihan"
  pkill -f qemu-system || true
  sleep 3
fi

if adb wait-for-device 2>/dev/null && tunggu_boot 60; then
  echo "Emulator sehat setelah restart zygote"
else
  echo "EMULATOR_MATI_SETELAH_RESTART_ZYGOTE: menyalakan ulang emulator ($AVD_NAME), data tetap sehingga locale id-ID tersimpan"
  adb kill-server || true
  pkill -f qemu-system || true
  sleep 5
  nohup "$SDK/emulator/emulator" -avd "$AVD_NAME" "${EMU_OPTS[@]}" > emulator_ulang.log 2>&1 &
  adb start-server
  adb wait-for-device
  if ! tunggu_boot 150; then
    echo "EMULATOR_GAGAL_DINYALAKAN_ULANG"
    tail -40 emulator_ulang.log
    exit 1
  fi
  echo "Emulator berhasil dinyalakan ulang"
  adb root || true
  sleep 3
  adb wait-for-device
  # Pengaturan animasi dari android-emulator-runner tersimpan di data, ditulis ulang agar pasti
  for k in window_animation_scale transition_animation_scale animator_duration_scale; do adb shell settings put global "$k" 0.0 || true; done
fi

adb shell getprop persist.sys.locale || true
boot_ok || { echo "EMULATOR_MATI_SEBELUM_INSTALL_APK"; exit 1; }
