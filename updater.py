"""
AFCR Timesheet Auto-Updater.
Checks GitHub Releases silently on startup or on-demand from the dashboard.
Repository: DaleFaubion/TimesheetAutomation
"""
import os
import sys
import json
import urllib.request
import subprocess
from pathlib import Path

APP_VERSION = "2.1.0"
REPO_OWNER = "DaleFaubion"
REPO_NAME = "TimesheetAutomation"
BASE_DIR = Path(__file__).resolve().parent

def get_current_version() -> str:
    return APP_VERSION

def check_for_updates() -> dict:
    """
    Queries GitHub API for the latest release tag.
    Returns update status, latest version tag, release notes, and download URL.
    """
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AFCR-Timesheet-App"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                latest_tag = data.get("tag_name", "").lstrip("v")
                html_url = data.get("html_url", "")
                body = data.get("body", "")
                
                is_newer = _is_newer_version(latest_tag, APP_VERSION)
                return {
                    "status": "success",
                    "current_version": APP_VERSION,
                    "latest_version": latest_tag,
                    "is_update_available": is_newer,
                    "release_url": html_url,
                    "release_notes": body
                }
    except Exception as e:
        # Check if running inside git repo as fallback
        git_dir = BASE_DIR / ".git"
        if git_dir.exists():
            try:
                subprocess.run(["git", "fetch", "--quiet"], cwd=str(BASE_DIR), timeout=5, check=False)
                res = subprocess.run(["git", "status", "-uno"], cwd=str(BASE_DIR), capture_output=True, text=True, timeout=5)
                is_behind = "Your branch is behind" in res.stdout
                return {
                    "status": "git_checked",
                    "current_version": APP_VERSION,
                    "latest_version": "git-head",
                    "is_update_available": is_behind,
                    "release_url": f"https://github.com/{REPO_OWNER}/{REPO_NAME}",
                    "release_notes": "New commits are available on GitHub."
                }
            except Exception:
                pass

        return {
            "status": "offline_or_error",
            "current_version": APP_VERSION,
            "latest_version": APP_VERSION,
            "is_update_available": False,
            "error": str(e)
        }

def _is_newer_version(remote: str, current: str) -> bool:
    try:
        r_parts = [int(p) for p in remote.split(".") if p.isdigit()]
        c_parts = [int(p) for p in current.split(".") if p.isdigit()]
        return r_parts > c_parts
    except Exception:
        return remote > current

def apply_update() -> dict:
    """
    Applies updates via git pull if running from repository.
    """
    git_dir = BASE_DIR / ".git"
    if git_dir.exists():
        try:
            res = subprocess.run(["git", "pull"], cwd=str(BASE_DIR), capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                return {"status": "success", "message": "Updated successfully to latest version! Please restart the app."}
            return {"status": "error", "message": res.stderr or res.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "manual", "message": f"Please download the latest installer from https://github.com/{REPO_OWNER}/{REPO_NAME}/releases."}

