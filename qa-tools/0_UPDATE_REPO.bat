@echo off
echo Mengambil versi terbaru dari GitHub ...
git -C "%~dp0.." pull --ff-only
echo.
pause
