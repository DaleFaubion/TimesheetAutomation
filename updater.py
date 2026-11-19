"""
AFCR Timesheet Auto-Updater.
Checks GitHub (branch 'main') silently on startup or on-demand from the dashboard.
Safeguards user credentials and settings.json across git updates.
Repository: DaleFaubion/TimesheetAutomation
"""
import os
import sys
import json
import shutil
import urllib.request
import subprocess
from pathlib import Path

APP_VERSION = "2.1.0"
REPO_OWNER = "DaleFaubion"
REPO_NAME = "TimesheetAutomation"
BASE_DIR = Path(__file__).resolve().parent

def get_current_version() -> str:
    """Returns the installed application version string."""
    return APP_VERSION

def get_git_executable() -> str:
    """Locates the git executable on the system across PATH and standard Windows locations."""
    git_path = shutil.which("git")
    if git_path:
        return git_path

    if sys.platform == "win32":
        candidates = [
            Path(r"C:\Program Files\Git\cmd\git.exe"),
            Path(r"C:\Program Files\Git\bin\git.exe"),
            Path(r"C:\Program Files (x86)\Git\cmd\git.exe"),
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Git" / "cmd" / "git.exe",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    return "git"

def backup_user_settings() -> dict:
    """
    Backs up settings.json to settings.local.json and a system temp file
    so user API keys and sheet URLs are never lost during git operations.
    """
    settings_file = BASE_DIR / "settings.json"
    local_settings_file = BASE_DIR / "settings.local.json"
    temp_dir = Path(os.environ.get("TEMP", "C:\\Temp"))
    temp_backup = temp_dir / "afcr_settings_backup.json"

    saved_data = {}
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            with open(local_settings_file, "w", encoding="utf-8") as f:
                json.dump(saved_data, f, indent=2)
            try:
                temp_dir.mkdir(parents=True, exist_ok=True)
                with open(temp_backup, "w", encoding="utf-8") as f:
                    json.dump(saved_data, f, indent=2)
            except Exception:
                pass
        except Exception as e:
            print(f"[UPDATE] Warning during settings backup: {e}")

    # Mark settings.json as assume-unchanged in git if inside repo
    git_bin = get_git_executable()
    git_dir = BASE_DIR / ".git"
    if git_dir.exists():
        try:
            subprocess.run([git_bin, "update-index", "--assume-unchanged", "settings.json"],
                           cwd=str(BASE_DIR), capture_output=True, timeout=5, check=False)
        except Exception:
            pass

    return saved_data

def restore_user_settings(saved_data: dict = None):
    """
    Restores and merges user settings back into settings.json after git pull.
    Ensures repository defaults are kept while user settings (API key, sheets URL) are preserved.
    """
    settings_file = BASE_DIR / "settings.json"
    local_settings_file = BASE_DIR / "settings.local.json"
    temp_backup = Path(os.environ.get("TEMP", "C:\\Temp")) / "afcr_settings_backup.json"

    backup_data = dict(saved_data) if saved_data else {}
    if not backup_data and local_settings_file.exists():
        try:
            with open(local_settings_file, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
        except Exception:
            pass

    if not backup_data and temp_backup.exists():
        try:
            with open(temp_backup, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
        except Exception:
            pass

    if not backup_data:
        return

    current_data = {}
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                current_data = json.load(f)
        except Exception:
            pass

    current_data.update(backup_data)
    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2)
    except Exception as e:
        print(f"[UPDATE] Warning restoring settings.json: {e}")

    # Also keep settings.local.json in sync
    try:
        with open(local_settings_file, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2)
    except Exception:
        pass

def check_for_updates() -> dict:
    """
    Queries Git origin/main or GitHub Commits API for new updates.
    Returns status, latest version/commit, update availability, and commit notes.
    """
    git_bin = get_git_executable()
    git_dir = BASE_DIR / ".git"

    # 1. Primary: Git Remote Check
    if git_dir.exists():
        try:
            # Quick silent fetch with 5-second timeout
            subprocess.run([git_bin, "fetch", "--quiet", "origin", "main"],
                           cwd=str(BASE_DIR), timeout=6, check=False)

            head_sha = subprocess.run([git_bin, "rev-parse", "HEAD"],
                                     cwd=str(BASE_DIR), capture_output=True, text=True, timeout=3).stdout.strip()
            origin_sha = subprocess.run([git_bin, "rev-parse", "origin/main"],
                                       cwd=str(BASE_DIR), capture_output=True, text=True, timeout=3).stdout.strip()

            count_res = subprocess.run([git_bin, "rev-list", "--count", "HEAD..origin/main"],
                                       cwd=str(BASE_DIR), capture_output=True, text=True, timeout=3)
            count = int(count_res.stdout.strip()) if count_res.returncode == 0 and count_res.stdout.strip().isdigit() else 0

            if count > 0:
                msg = subprocess.run([git_bin, "log", "-1", "--pretty=format:%s", "origin/main"],
                                     cwd=str(BASE_DIR), capture_output=True, text=True, timeout=3).stdout.strip()
                remote_short = origin_sha[:7] if origin_sha else "latest"
                return {
                    "status": "update_available",
                    "current_version": APP_VERSION,
                    "latest_version": f"v{APP_VERSION} ({remote_short})",
                    "is_update_available": True,
                    "release_url": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/commits/main",
                    "release_notes": f"{count} new update(s) available from GitHub: {msg}",
                    "commits_behind": count,
                    "latest_commit_msg": msg,
                    "latest_commit_hash": remote_short
                }
            elif head_sha and origin_sha:
                return {
                    "status": "up_to_date",
                    "current_version": APP_VERSION,
                    "latest_version": APP_VERSION,
                    "is_update_available": False,
                    "release_url": f"https://github.com/{REPO_OWNER}/{REPO_NAME}",
                    "release_notes": "Application is up to date with GitHub main."
                }
        except Exception:
            pass

    # 2. Fallback: GitHub Commits API
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/main"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AFCR-Timesheet-App"
            }
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                remote_sha = data.get("sha", "")
                commit_msg = data.get("commit", {}).get("message", "").split("\n")[0]
                remote_short = remote_sha[:7] if remote_sha else "latest"

                is_newer = False
                if git_dir.exists():
                    try:
                        local_sha = subprocess.run([git_bin, "rev-parse", "HEAD"],
                                                   cwd=str(BASE_DIR), capture_output=True, text=True, timeout=3).stdout.strip()
                        is_newer = (remote_sha != local_sha) and bool(remote_sha and local_sha)
                    except Exception:
                        pass

                return {
                    "status": "success",
                    "current_version": APP_VERSION,
                    "latest_version": f"v{APP_VERSION} ({remote_short})",
                    "is_update_available": is_newer,
                    "release_url": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/commits/main",
                    "release_notes": f"New commit on GitHub: {commit_msg}",
                    "latest_commit_msg": commit_msg,
                    "latest_commit_hash": remote_short
                }
    except Exception as e:
        pass

    return {
        "status": "offline_or_error",
        "current_version": APP_VERSION,
        "latest_version": APP_VERSION,
        "is_update_available": False,
        "release_notes": "Could not connect to GitHub. Working in offline mode."
    }

def apply_update() -> dict:
    """
    Applies updates via git pull from origin main.
    Safeguards settings.json, handles autostash, and updates dependencies.
    """
    git_dir = BASE_DIR / ".git"
    if not git_dir.exists():
        return {
            "status": "manual",
            "message": f"This installation is not running from a git clone. Please visit https://github.com/{REPO_OWNER}/{REPO_NAME} to download the latest files."
        }

    git_bin = get_git_executable()
    saved_settings = backup_user_settings()

    try:
        # 1. Pull latest commits using autostash to preserve any local edits
        res = subprocess.run(
            [git_bin, "pull", "--autostash", "origin", "main"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )

        # 2. Immediately restore user settings so no config/keys are dropped
        restore_user_settings(saved_settings)

        if res.returncode == 0:
            # 3. Check and install dependencies if requirements.txt exists
            req_file = BASE_DIR / "requirements.txt"
            if req_file.exists():
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
                        check=False,
                        timeout=35
                    )
                except Exception:
                    pass

            return {
                "status": "success",
                "message": "Updated successfully to the latest version from GitHub! Please reload your browser or restart the launcher."
            }
        else:
            err = res.stderr.strip() or res.stdout.strip()
            # If autostash failed due to conflicting unstaged changes, try standard pull
            retry = subprocess.run(
                [git_bin, "pull", "origin", "main"],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=30
            )
            restore_user_settings(saved_settings)
            if retry.returncode == 0:
                return {
                    "status": "success",
                    "message": "Updated successfully to the latest version from GitHub! Please reload your browser or restart the launcher."
                }
            return {
                "status": "error",
                "message": f"Git pull notice: {err}"
            }
    except Exception as e:
        restore_user_settings(saved_settings)
        return {
            "status": "error",
            "message": f"Update failed: {str(e)}"
        }

def auto_update_on_startup(verbose: bool = True) -> bool:
    """
    Checks for updates and applies them silently or verbosely during application startup.
    Returns True if an update was downloaded and applied.
    """
    try:
        info = check_for_updates()
        if info.get("is_update_available"):
            notes = info.get("release_notes", "")
            if verbose:
                print(f"[UPDATE] New update detected on GitHub!")
                print(f"[UPDATE] Details: {notes}")
                print("[UPDATE] Pulling latest updates from GitHub main branch...")
            res = apply_update()
            if res.get("status") == "success":
                if verbose:
                    print(f"[UPDATE] {res.get('message')}")
                return True
            else:
                if verbose:
                    print(f"[UPDATE] Notice: {res.get('message')}")
        return False
    except Exception as e:
        if verbose:
            print(f"[UPDATE] Auto-update check notice: {e}")
        return False
