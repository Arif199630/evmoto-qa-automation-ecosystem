@echo off
echo Menjalankan suite mobile dan cross seperti CI. Ini lama; biarkan jendela terbuka.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0jalankan_mobile_lokal.ps1" -Semua
echo.
pause
