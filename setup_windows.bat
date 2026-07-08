@echo off
setlocal
cd /d "%~dp0"

if exist "venv" rmdir /s /q "venv"
py -3 -m venv venv || goto :eof
"venv\Scripts\python.exe" -m pip install --upgrade pip || goto :eof
"venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :eof

echo.
echo Setup selesai.
echo Selanjutnya jalankan run_windows.bat
pause
