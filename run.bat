@echo off
setlocal enabledelayedexpansion
title AFCR Timesheet OCR Server
cd /d "%~dp0"

echo ======================================================================
echo   AFFORDABLE FOOD CART RENTALS (AFCR)
echo   Timesheet and Document OCR Server Launcher
echo ======================================================================
echo.

set "PY_CMD="

:: 1. Test py launcher
py -3 -c "import sys" >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=py -3"
    echo [FOUND] Using Windows Python Launcher: py -3
    goto :run_app
)

:: 2. Test python in PATH (verify it can actually execute and is not a broken Store shim)
python -c "import sys" >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    echo [FOUND] Using python from PATH
    goto :run_app
)

:: 3. Scan common Python installation paths across user and system directories
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "C:\Program Files\Python313\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
    "%ProgramFiles(x86)%\Python312\python.exe"
    "%USERPROFILE%\miniconda3\python.exe"
    "%USERPROFILE%\anaconda3\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
) do (
    if exist %%P (
        %%P -c "import sys" >nul 2>nul
        if !errorlevel! equ 0 (
            set "PY_CMD=%%~P"
            echo [FOUND] Using Python at: %%~P
            goto :run_app
        )
    )
)

:: 4. Python not detected - Automatically download and install Python 3.12
echo ======================================================================
echo   Python was not detected on this computer.
echo   Automatically downloading and installing Python 3.12 for you...
echo ======================================================================
echo.
echo Downloading official 64-bit Python installer from python.org...

:: Try curl.exe first (native in Windows 10 & 11, robust against proxy and TLS restrictions)
curl.exe -f -s -L -o "%TEMP%\python_installer.exe" "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe" 2>nul

:: Fallback to PowerShell Invoke-WebRequest if curl.exe is unavailable
if not exist "%TEMP%\python_installer.exe" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]'Tls12,Tls13'; try { (New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', '$env:TEMP\python_installer.exe') } catch { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe' -OutFile '$env:TEMP\python_installer.exe' -UserAgent 'Mozilla/5.0' }" 2>nul
)

if exist "%TEMP%\python_installer.exe" (
    echo.
    echo Installing Python silently... Please wait 30-60 seconds...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
    del "%TEMP%\python_installer.exe" >nul 2>nul

    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"

    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        echo.
        echo [SUCCESS] Python installed successfully!
        goto :run_app
    )
)

echo.
echo [ERROR] Could not automatically locate or install Python.
echo Please download and install Python 3.12 from:
echo   https://www.python.org/downloads/
echo.
echo IMPORTANT: Check the box "Add python.exe to PATH" during installation.
echo.
pause
exit /b 1

:run_app
echo [LAUNCH] Starting launcher with: %PY_CMD%
echo.

if "%PY_CMD%"=="py -3" (
    py -3 "%~dp0launcher.py"
) else (
    "%PY_CMD%" "%~dp0launcher.py"
)

if %errorlevel% neq 0 (
    echo.
    echo Server exited with status code %errorlevel%.
    pause
)
exit /b
