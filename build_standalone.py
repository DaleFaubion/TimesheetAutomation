"""
PyInstaller build script for creating a bundled standalone executable
for AFCR Timesheet & Document OCR.
Works on Windows (producing .exe) and Linux.
"""
import os
import sys
import platform
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build():
    system = platform.system()
    print(f"Building AFCR Timesheet OCR Standalone Bundle for: {system}...")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=AFCR_Timesheet_OCR",
        "--onedir",             # Onedir is much faster to start and handles OCR model weights properly
        "--windowed",           # Don't show raw console window
        "--add-data", f"{BASE_DIR / 'templates'}{os.pathsep}templates",
        "--add-data", f"{BASE_DIR / 'static'}{os.pathsep}static",
        "--collect-all", "rapidocr_onnxruntime",
        "--collect-all", "openpyxl",
        "--collect-all", "qrcode",
        "--collect-all", "pypdfium2",
        str(BASE_DIR / "app.py")
    ]
    
    print("Running command:", " ".join(cmd))
    subprocess.check_call(cmd)
    
    dist_dir = BASE_DIR / "dist" / "AFCR_Timesheet_OCR"
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Standalone bundle built in: {dist_dir}")
    if system == "Windows":
        print(f"Executable: {dist_dir / 'AFCR_Timesheet_OCR.exe'}")
    else:
        print(f"Binary: {dist_dir / 'AFCR_Timesheet_OCR'}")
    print("=" * 60)

if __name__ == "__main__":
    build()
