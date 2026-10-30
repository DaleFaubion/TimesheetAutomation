import os
import sys
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

def get_desktop_dir() -> Path:
    """
    Finds the active user Desktop path across Windows (including OneDrive Desktop),
    macOS, and Linux.
    """
    if sys.platform == "win32":
        # Check Windows registry for redirected Desktop (e.g. OneDrive)
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            desktop_val, _ = winreg.QueryValueEx(key, "Desktop")
            expanded = Path(os.path.expandvars(desktop_val))
            if expanded.exists():
                return expanded
        except Exception:
            pass

        # Check common OneDrive path
        try:
            onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
            if onedrive_desktop.exists():
                return onedrive_desktop
        except Exception:
            pass

    # Fallback to standard Desktop
    try:
        standard = Path.home() / "Desktop"
        if standard.exists():
            return standard
    except Exception:
        pass

    try:
        user_home = Path.home()
        if user_home.exists():
            return user_home
    except Exception:
        pass

    return BASE_DIR

# Manager Desktop Scans folder
DESKTOP_DIR = get_desktop_dir()
SCANS_DIR = DESKTOP_DIR / "AFCR_Scans"
IMAGES_DIR = SCANS_DIR / "Images"
EXPORTS_DIR = SCANS_DIR / "Exports"

# Ensure target directories exist safely
for directory in [SCANS_DIR, IMAGES_DIR, EXPORTS_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

# File paths for spreadsheet logs
EXCEL_LOG_PATH = SCANS_DIR / "afcr_timesheet_log.xlsx"
CSV_LOG_PATH = SCANS_DIR / "afcr_timesheet_log.csv"
EXCEL_FC_WORKBOOK_PATH = SCANS_DIR / "FC TIMES_ FC121-130.xlsx"
TEMPLATE_WORKBOOK_PATH = BASE_DIR / "FC TIMES_ FC121-130 (1).xlsx"
GOOGLE_CREDENTIALS_PATH = BASE_DIR / "google_credentials.json"
OAUTH_TOKEN_PATH = BASE_DIR / "oauth_token.json"
OAUTH_CLIENT_SECRETS_PATH = BASE_DIR / "oauth_client_secrets.json"
SETTINGS_FILE = BASE_DIR / "settings.json"
CONFIG_FILE = BASE_DIR / "config.json"
CODES_FILE = BASE_DIR / "codes.json"

# Server configuration
DEFAULT_PORT = 5000
DEFAULT_HOST = "0.0.0.0"

DEFAULT_CART_TABS = [
    "FC121", "FC122", "FC123", "FC124", "FC125",
    "FC126", "FC127", "FC128", "FC129", "FC130",
    "FC110", "FC119", "Shop"
]

DEFAULT_WORKER_ROSTER = [
    "Elijah", "Dale", "Kelly", "Israel", "Dani", "Chico", "Clark",
    "Jonathan", "Francisco", "Cini Escobar", "Carlos", "Salvador",
    "Ramon", "Sam", "Mario", "Antonio"
]

def get_settings() -> dict:
    import json
    default_settings = {
        "google_sheets_enabled": True,
        "google_sheet_id_or_url": "",
        "google_sheet_title": "FC TIMES_ FC121-130",
        "has_credentials": GOOGLE_CREDENTIALS_PATH.exists()
    }
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_settings.update(data)
        except Exception:
            pass
    default_settings["has_credentials"] = GOOGLE_CREDENTIALS_PATH.exists()
    return default_settings

def save_settings(new_settings: dict) -> dict:
    import json
    cur = get_settings()
    cur.update(new_settings)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(cur, f, indent=2)
    cur["has_credentials"] = GOOGLE_CREDENTIALS_PATH.exists()
    return cur

def get_codes_db() -> dict:
    import json
    if CODES_FILE.exists():
        try:
            with open(CODES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not data.get("cart_tabs"):
                    data["cart_tabs"] = list(DEFAULT_CART_TABS)
                if not data.get("worker_roster"):
                    data["worker_roster"] = list(DEFAULT_WORKER_ROSTER)
                return data
        except Exception:
            pass
    return {
        "cart_tabs": list(DEFAULT_CART_TABS),
        "worker_roster": list(DEFAULT_WORKER_ROSTER),
        "standard_columns": [
            "Name", "Task", "Category", "Build / Reconditioning",
            "Code", "Date", "Time In", "Out", "Task Total"
        ],
        "mt_codes": [],
        "rt_codes": []
    }

def save_codes_db(new_db: dict) -> dict:
    import json
    with open(CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(new_db, f, indent=2)
    return new_db

def get_cart_tabs() -> list:
    db = get_codes_db()
    tabs = db.get("cart_tabs")
    if not tabs or not isinstance(tabs, list):
        return list(DEFAULT_CART_TABS)
    return tabs

def save_cart_tabs(tabs: list) -> list:
    db = get_codes_db()
    # Normalize tabs, preserve uniqueness and order
    clean_tabs = []
    for t in tabs:
        t_clean = str(t).strip()
        if t_clean and t_clean not in clean_tabs:
            clean_tabs.append(t_clean)
    if not clean_tabs:
        clean_tabs = list(DEFAULT_CART_TABS)
    db["cart_tabs"] = clean_tabs
    save_codes_db(db)
    return clean_tabs

def get_worker_roster() -> list:
    db = get_codes_db()
    roster = db.get("worker_roster")
    if not roster or not isinstance(roster, list):
        return list(DEFAULT_WORKER_ROSTER)
    return roster

def save_worker_roster(workers: list) -> list:
    db = get_codes_db()
    clean_workers = []
    for w in workers:
        w_clean = str(w).strip()
        if w_clean and w_clean not in clean_workers:
            clean_workers.append(w_clean)
    if not clean_workers:
        clean_workers = list(DEFAULT_WORKER_ROSTER)
    db["worker_roster"] = clean_workers
    save_codes_db(db)
    return clean_workers
