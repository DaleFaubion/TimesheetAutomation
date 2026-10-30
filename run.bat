@echo off
title AFCR Timesheet OCR Server
cd /d "%~dp0"

:: 1. Check if python is in PATH
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=python
    goto :run_app
)

:: 2. Check if py launcher is in PATH
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=py
    goto :run_app
)

:: 3. Check common Python installation paths
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    set PY_CMD=python
    goto :run_app
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    set PY_CMD=python
    goto :run_app
)
if exist "%ProgramFiles%\Python312\python.exe" (
    set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
    set PY_CMD=python
    goto :run_app
)

:: 4. Python is not installed - Automatically download and install Python 3.12!
echo ======================================================================
echo   [AFCR TIMESHEET OCR] Python is not installed.
echo   Automatically downloading and installing Python for you...
echo ======================================================================
echo.
echo Downloading official Python installer from python.org...

powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', '$env:TEMP\python_installer.exe')"

if exist "%TEMP%\python_installer.exe" (
    echo.
    echo Installing Python silently (adding to PATH)...
    echo Please wait 30-60 seconds...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
    del "%TEMP%\python_installer.exe" >nul 2>nul
    
    :: Update PATH for current session
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        echo.
        echo [SUCCESS] Python installed successfully!
        set PY_CMD=python
        goto :run_app
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        echo.
        echo [SUCCESS] Python installed successfully!
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        goto :run_app
    )
)

echo.
echo [ERROR] Automatic installation could not be completed.
echo Please install Python manually from: https://www.python.org/downloads/
echo Make sure to check "Add python.exe to PATH".
echo.
pause
exit /b 1

:run_app
%PY_CMD% launcher.py
if %errorlevel% neq 0 (
    echo.
    echo Server exited with status code %errorlevel%.
    pause
)
exit /b
