# AFCR Timesheet Automation PowerShell Launcher
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  AFFORDABLE FOOD CART RENTALS (AFCR)" -ForegroundColor Cyan
Write-Host "  Timesheet and Document OCR Server Launcher" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$pyCmd = $null

# 1. Test py launcher
try {
    $res = & py -3 -c "import sys; print(sys.executable)" 2>$null
    if ($LASTEXITCODE -eq 0 -and $res) {
        $pyCmd = "py"
        Write-Host "[FOUND] Using Windows Python Launcher: py -3" -ForegroundColor Green
    }
} catch {}

# 2. Test python in PATH
if (-not $pyCmd) {
    try {
        $res = & python -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $res) {
            $pyCmd = "python"
            Write-Host "[FOUND] Using python from PATH" -ForegroundColor Green
        }
    } catch {}
}

# 3. Check known paths
if (-not $pyCmd) {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:ProgramFiles\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles\Python310\python.exe",
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe",
        "$env:USERPROFILE\miniconda3\python.exe",
        "$env:USERPROFILE\anaconda3\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe"
    )
    foreach ($cand in $candidates) {
        if (Test-Path -LiteralPath $cand) {
            try {
                $res = & $cand -c "import sys; print(sys.executable)" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $pyCmd = $cand
                    Write-Host "[FOUND] Using Python at: $cand" -ForegroundColor Green
                    break
                }
            } catch {}
        }
    }
}

# 4. Auto-install if missing
if (-not $pyCmd) {
    Write-Host "[INFO] Python is not installed. Downloading Python 3.12..." -ForegroundColor Yellow
    $installer = "$env:TEMP\python_installer.exe"
    
    # Try native curl.exe first
    try {
        & curl.exe -f -s -L -o $installer "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
    } catch {}

    # Fallback to Invoke-WebRequest
    if (-not (Test-Path -LiteralPath $installer)) {
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]'Tls12,Tls13'
            Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe" -OutFile $installer -UserAgent "Mozilla/5.0"
        } catch {}
    }
    Write-Host "[INFO] Installing Python silently... Please wait 30-60 seconds..." -ForegroundColor Yellow
    Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0" -Wait
    Remove-Item -Path $installer -Force -ErrorAction SilentlyContinue

    $installedPath = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    if (Test-Path -LiteralPath $installedPath) {
        $pyCmd = $installedPath
        Write-Host "[SUCCESS] Python installed successfully!" -ForegroundColor Green
    }
}

if (-not $pyCmd) {
    Write-Host "[ERROR] Could not find or install Python. Please install from https://www.python.org/downloads/" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[LAUNCH] Starting launcher with: $pyCmd" -ForegroundColor Cyan
if ($pyCmd -eq "py") {
    & py -3 "$PSScriptRoot\launcher.py"
} else {
    & $pyCmd "$PSScriptRoot\launcher.py"
}
