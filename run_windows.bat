@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" main.py
) else (
  echo Environment belum siap.
  echo Jalankan setup_windows.bat dulu untuk membuat venv dan install dependency.
)

pause
