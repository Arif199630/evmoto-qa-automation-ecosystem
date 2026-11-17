@echo off
echo Menyalakan emulator, Appium, lalu menjalankan satu test kecil (login User, NT_04) ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0jalankan_mobile_lokal.ps1"
echo.
pause
