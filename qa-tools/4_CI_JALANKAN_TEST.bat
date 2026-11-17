@echo off
echo Memicu test di GitHub Actions (emulator di cloud, tanpa BIOS/virtualisasi), memantau, lalu mengunduh hasil.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ci_jalankan.ps1"
echo.
pause
