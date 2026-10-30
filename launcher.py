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

def open_browser_delayed(url: str, delay: float = 1.5):
    """Opens browser after server starts."""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()

def main():
    print("=" * 60)
    print("  AFFORDABLE FOOD CART RENTALS (AFCR)")
    print("  Timesheet and Document OCR Server Launcher")
    print("=" * 60)
    print()

    # 1. Check Git updates
    check_git_updates()

    # 2. Verify dependencies
    verify_dependencies()

    # 3. Ensure Desktop Shortcut exists
    try:
        import create_shortcut
        create_shortcut.create_desktop_shortcut()
    except Exception as e:
        print(f"[SHORTCUT] Notice: {e}")

    # 4. Queue browser opening
    try:
        import config
        port = getattr(config, "DEFAULT_PORT", 5000)
    except Exception:
        port = 5000
    dashboard_url = f"http://localhost:{port}/manager"
    print(f"[LAUNCH] Launching browser to {dashboard_url}...")
    open_browser_delayed(dashboard_url, delay=1.8)

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
