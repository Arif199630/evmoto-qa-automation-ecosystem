@echo off
echo Setup PC baru (sekali jalan). Jendela UAC/winget mungkin meminta persetujuan Anda.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_pc_baru.ps1"
echo.
pause
