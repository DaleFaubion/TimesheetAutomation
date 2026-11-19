"""
AFCR Timesheet OCR Smart Launcher.
Handles dependency validation, git update checks, browser auto-launch,
and runs the Flask server cross-platform.
"""
import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_git_updates():
    """Checks for remote git updates if running inside a repository."""
    git_dir = BASE_DIR / ".git"
    if git_dir.exists():
        print("[SYNC] Checking for remote updates from GitHub...")
        try:
            res = subprocess.run(
                ["git", "pull", "--quiet"],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=10
            )
            if res.returncode == 0:
                print("[SYNC] Application is up to date!")
            else:
                print("[SYNC] Notice: Remote sync skipped or not configured.")
        except Exception:
            pass

def verify_dependencies():
    """Checks requirements.txt and installs missing packages."""
    if sys.platform == "win32":
        sys32 = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32"
        if not (sys32 / "vcruntime140_1.dll").exists():
            print("[SETUP] Installing required Microsoft Visual C++ Runtime for ONNX OCR...")
            installer = Path(os.environ.get("TEMP", "C:\\Temp")) / "vc_redist.x64.exe"
            try:
                subprocess.run([
                    "curl.exe", "-f", "-s", "-L", "-o", str(installer),
                    "https://aka.ms/vs/17/release/vc_redist.x64.exe"
                ], check=False)
                if installer.exists():
                    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process -FilePath '{installer}' -ArgumentList '/install /passive /norestart' -Verb RunAs -Wait"], check=False)
                    if not (sys32 / "vcruntime140_1.dll").exists():
                        subprocess.run([str(installer), "/install", "/passive", "/norestart"], check=False)
                    try:
                        installer.unlink()
                    except Exception:
                        pass
            except Exception as e:
                print(f"[WARN] Visual C++ setup notice: {e}")

    req_file = BASE_DIR / "requirements.txt"
    if req_file.exists():
        print("[CHECK] Verifying application dependencies...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
                check=False
            )
        except Exception as e:
            print(f"[WARN] Dependency check notice: {e}")

def launch_app_window(url: str, delay: float = 1.8):
    """
    Launches application in native standalone window mode via Edge or Chrome --app shell.
    Provides a distraction-free window frame without browser tabs or URL bars.
    Falls back gracefully to the default system web browser.
    """
    def _launch():
        time.sleep(delay)
        if sys.platform == "win32":
            # 1. Search for Microsoft Edge (Standard on Windows 10 & 11)
            edge_candidates = [
                Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
                Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
                Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
            ]
            for p in edge_candidates:
                if p.exists():
                    try:
                        print(f"[WINDOW] Launching native Edge standalone app shell...")
                        subprocess.Popen([str(p), f"--app={url}", "--window-size=1440,920"])
                        return
                    except Exception:
                        pass

            # 2. Search for Google Chrome
            chrome_candidates = [
                Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
                Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
                Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe"
            ]
            for p in chrome_candidates:
                if p.exists():
                    try:
                        print(f"[WINDOW] Launching native Chrome standalone app shell...")
                        subprocess.Popen([str(p), f"--app={url}", "--window-size=1440,920"])
                        return
                    except Exception:
                        pass

        # 3. Default browser fallback
        print(f"[WINDOW] Launching default web browser...")
        webbrowser.open(url)

    threading.Thread(target=_launch, daemon=True).start()

def main():
    print("=" * 60)
    print("  AFFORDABLE FOOD CART RENTALS (AFCR)")
    print("  Timesheet Modernization & Google Sheets Desktop App")
    print("=" * 60)
    print()

    # 1. Check Git and Releases updates
    try:
        import updater
        print(f"[VERSION] Current Installed Build: v{updater.get_current_version()}")
        up_info = updater.check_for_updates()
        if up_info.get("is_update_available"):
            print(f"[UPDATE] A new release (v{up_info.get('latest_version')}) is available!")
            if (BASE_DIR / ".git").exists():
                print("[UPDATE] Automatically pulling latest updates from GitHub...")
                check_git_updates()
            else:
                print(f"[UPDATE] Download latest release: {up_info.get('release_url')}")
        else:
            print("[SYNC] Application is up to date!")
    except Exception as e:
        check_git_updates()

    # 2. Verify dependencies
    verify_dependencies()

    # 3. Ensure Desktop Shortcut exists
    try:
        import create_shortcut
        create_shortcut.create_desktop_shortcut()
    except Exception as e:
        print(f"[SHORTCUT] Notice: {e}")

    # 4. Queue native standalone app shell launch
    try:
        import config
        port = getattr(config, "DEFAULT_PORT", 5000)
    except Exception:
        port = 5000
    dashboard_url = f"http://localhost:{port}/manager"
    launch_app_window(dashboard_url, delay=1.8)

    # 5. Start Flask App
    print("[START] Starting server (Press Ctrl+C to stop)...")
    print()
    
    app_script = BASE_DIR / "app.py"
    try:
        subprocess.run([sys.executable, str(app_script)], check=True)
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] Server stopped with error: {e}")
        input("Press Enter to close...")

if __name__ == "__main__":
    main()
