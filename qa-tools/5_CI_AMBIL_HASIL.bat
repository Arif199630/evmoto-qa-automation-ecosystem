@echo off
echo Mengunduh hasil run CI terakhir ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ci_jalankan.ps1" -HanyaAmbilHasil
echo.
pause
