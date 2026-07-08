@echo off
setlocal
pushd "%~dp0" || goto :error

py -3 -m venv venv || goto :error
"venv\Scripts\python.exe" -m pip install --upgrade pip || goto :error
"venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller || goto :error

"venv\Scripts\pyinstaller.exe" --clean --onedir --name CoretaxSlip --windowed ^
  --hidden-import selenium.webdriver.chrome.webdriver ^
  --hidden-import selenium.webdriver.chrome.service ^
  --hidden-import selenium.webdriver.chrome.options ^
  --hidden-import selenium.webdriver.common.selenium_manager ^
  --hidden-import selenium.webdriver.common.driver_finder ^
  gui.py || goto :error

copy /Y config.template.json "dist\CoretaxSlip\config.template.json" >nul
if not exist "dist\CoretaxSlip\config.json" copy /Y config.template.json "dist\CoretaxSlip\config.json" >nul
if exist "finance-release" rmdir /s /q "finance-release"
mkdir "finance-release" || goto :error
xcopy /E /I /Y "dist\CoretaxSlip" "finance-release\CoretaxSlip" >nul || goto :error

echo.
echo Build selesai.
echo Folder siap kirim ada di: finance-release\CoretaxSlip
echo Finance cukup buka CoretaxSlip.exe dari folder itu. Tidak perlu install Python.
echo Finance isi NIK, password, periode, dan tenant langsung dari tampilan aplikasi.
popd
pause
exit /b 0

:error
echo.
echo Build gagal. Cek error di atas.
popd 2>nul
pause
exit /b 1
