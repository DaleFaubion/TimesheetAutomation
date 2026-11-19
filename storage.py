import csv
import json
import os
import shutil
import re
from datetime import datetime
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import config
import utils

STANDARD_HEADERS = [
    "Name",
    "Task",
    "Category",
    "Build / Reconditioning",
    "Code",
    "Date",
    "Time In",
    "Out",
    "Task Total"
]

CSV_HEADERS = [
    "Submission ID",
    "Timestamp",
    "Source",
    "Worker Name",
    "Date",
    "Cart #",
    "Task",
    "Category",
    "Build / Reconditioning",
    "Code",
    "Time In",
    "Time Out",
    "Task Total",
    "Image File"
]

def normalize_cart_tab(raw_cart: str) -> str:
    """
    Normalizes a cart string into a standard tab name:
    e.g. '127' -> 'FC127', 'FC 127' -> 'FC127', '110' -> 'FC110', 'shop' -> 'Shop'
    """
    if not raw_cart:
        return "Shop"
    raw = str(raw_cart).strip()
    if not raw:
        return "Shop"
    
    # Check for shop or yard
    if re.search(r'shop|yard|office', raw, re.IGNORECASE):
        return "Shop"
        
    # Extract number (e.g. 127 from "FC127" or "127")
    match = re.search(r'(\d{2,4})', raw)
    if match:
        num = match.group(1)
        return f"FC{num}"
        
    return raw.upper().replace(" ", "")

def ensure_csv_file():
    """Ensures CSV audit log exists with headers."""
    config.SCANS_DIR.mkdir(parents=True, exist_ok=True)
    if not config.CSV_LOG_PATH.exists():
        with open(config.CSV_LOG_PATH, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def ensure_workbook():
    """
    Ensures that the multi-tab FC TIMES Excel workbook exists in Desktop/AFCR_Scans
    as a local template / export backup.
    """
    config.SCANS_DIR.mkdir(parents=True, exist_ok=True)
    target_path = config.EXCEL_FC_WORKBOOK_PATH

    if not target_path.exists():
        if config.TEMPLATE_WORKBOOK_PATH.exists():
            shutil.copy2(config.TEMPLATE_WORKBOOK_PATH, target_path)
            return

        # Create new workbook with standard tabs
        wb = openpyxl.Workbook()
        default_sheet = wb.active
        wb.remove(default_sheet)

        standard_tabs = config.get_cart_tabs()
        for tab_name in standard_tabs:
            init_cart_worksheet(wb, tab_name)

        try:
            wb.save(target_path)
        except Exception as e:
            print(f"[Notice] Could not initialize Excel file: {e}")

def init_cart_worksheet(wb, tab_name: str):
    """Initializes an Excel worksheet with standard AFCR headers and formatting."""
    ws = wb.create_sheet(title=tab_name)
    
    # Row 1: Trailer info & Total Time
    ws.cell(row=1, column=1, value=f"Trailer Number: {tab_name}")
    ws.cell(row=1, column=8, value="Total Time:")
    ws.cell(row=1, column=9, value="=SUM(I3:I500)")
    
    title_font = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
    ws.cell(row=1, column=1).font = title_font
    ws.cell(row=1, column=8).font = title_font
    ws.cell(row=1, column=9).font = Font(name="Calibri", size=11, bold=True, color="047857")

    # Row 2: Standard column headers
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='medium', color='0F172A')
    )

    ws.append(STANDARD_HEADERS)
    ws.row_dimensions[2].height = 24

    for col_num in range(1, len(STANDARD_HEADERS) + 1):
        cell = ws.cell(row=2, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border

    widths = [16, 32, 22, 18, 10, 14, 12, 12, 14]
    for col_idx, width in enumerate(widths, 1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    return ws

def save_submission(record: dict) -> dict:
    """
    Saves a verified submission record.
    1. Validates all rows (ensuring start and end times are populated).
    2. Appends directly to the local CSV audit log (Desktop/AFCR_Scans/afcr_timesheet_log.csv).
    3. Pushes directly to Google Sheets as the PRIMARY source of truth (batch-appending per cart tab).
    Eliminates openpyxl background disk writes to avoid Windows file-locking crashes.
    """
    ensure_csv_file()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    submission_id = f"AFCR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    source = record.get("source", "Office Scanner")
    image_name = record.get("image_name", "")
    worker_name = record.get("worker_name", "").strip() or "Unknown Worker"
    date_val = record.get("date", "").strip() or datetime.now().strftime("%m/%d/%y")

    # If payload contains structured multi-rows
    rows = record.get("rows", [])
    if not rows:
        single_task = record.get("notes") or record.get("task") or "Timesheet Entry"
        single_cart = record.get("cart_id") or (config.get_cart_tabs()[0] if config.get_cart_tabs() else "Shop")
        single_hours = record.get("hours_worked") or "01:00:00"
        single_code = record.get("job_code") or ""
        rows = [{
            "task": single_task,
            "category": "General",
            "type": "Build",
            "code": single_code,
            "time_in": "08:00 AM",
            "time_out": "09:00 AM",
            "duration": single_hours,
            "cart_id": single_cart
        }]

    # Look up codes database for category & build type normalization
    codes_db = config.get_codes_db()
    code_meta_map = {}
    for code_list in [codes_db.get("mt_codes", []), codes_db.get("ot_codes", []), codes_db.get("rt_codes", [])]:
        for c_item in code_list:
            if c_item.get("code"):
                code_meta_map[c_item["code"].upper()] = c_item

    # Validate and normalize rows
    validated_rows = []
    for idx, item in enumerate(rows):
        t_in = str(item.get("time_in", "")).strip()
        t_out = str(item.get("time_out", "")).strip()

        # If time_out is missing, check if next row has time_in
        if not t_out and idx + 1 < len(rows):
            next_in = str(rows[idx + 1].get("time_in", "")).strip()
            if next_in:
                t_out = next_in

        # If time_in is missing, inherit from previous row's time_out
        if not t_in and idx > 0 and len(validated_rows) > 0:
            prev_out = validated_rows[-1]["time_out"]
            if prev_out:
                t_in = prev_out

        # If time_out is still missing, calculate from duration or default
        if not t_out and t_in:
            dur = str(item.get("duration", "")).strip()
            in_min = utils.parse_time_minutes(t_in)
            if in_min is not None and dur and dur != "0:00:00":
                dur_min = utils.parse_time_minutes(dur)
                if dur_min is not None:
                    t_out = utils.format_minutes_to_time((in_min + dur_min) % 1440)
            if not t_out and in_min is not None:
                t_out = utils.format_minutes_to_time((in_min + 30) % 1440)

        if not t_in:
            t_in = "08:00 AM"
            if not t_out:
                t_out = "09:00 AM"

        # Calculate exact duration
        dur_final = utils.calculate_time_duration(t_in, t_out)
        
        code_val = str(item.get("code", "")).strip().upper()
        meta = code_meta_map.get(code_val, {})
        
        task_name = str(item.get("task", "")).strip() or meta.get("task") or "General Work"
        category = str(item.get("category", "")).strip() or meta.get("category") or "Misc."
        build_type = str(item.get("type", "")).strip() or meta.get("type") or "Build"

        row_cart = str(item.get("cart_id", "")).strip() or str(record.get("cart_id", "")).strip() or "Shop"
        row_date = str(item.get("date", "")).strip() or date_val

        v_item = {
            "task": task_name,
            "category": category,
            "type": build_type,
            "code": code_val,
            "time_in": t_in,
            "time_out": t_out,
            "duration": dur_final,
            "cart_id": normalize_cart_tab(row_cart),
            "date": row_date
        }
        validated_rows.append(v_item)

    synced_tabs = set()
    csv_rows_to_write = []

    for v_item in validated_rows:
        tab_name = v_item["cart_id"]
        synced_tabs.add(tab_name)

        csv_rows_to_write.append([
            submission_id,
            timestamp,
            source,
            worker_name,
            v_item["date"],
            tab_name,
            v_item["task"],
            v_item["category"],
            v_item["type"],
            v_item["code"],
            v_item["time_in"],
            v_item["time_out"],
            v_item["duration"],
            image_name
        ])

    # 1. Append to local CSV audit log
    try:
        with open(config.CSV_LOG_PATH, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for r in csv_rows_to_write:
                writer.writerow(r)
    except Exception as e:
        print(f"[CSV Log Write Error] {e}")

    # 2. Synchronize directly to Google Sheets (Primary Database)
    google_sync_res = sync_submission_to_google_sheets(worker_name, date_val, validated_rows)

    return {
        "status": "success",
        "submission_id": submission_id,
        "timestamp": timestamp,
        "rows_saved": len(validated_rows),
        "tabs_updated": list(synced_tabs),
        "csv_path": str(config.CSV_LOG_PATH),
        "google_sync": google_sync_res
    }

def _get_gspread_client():
    """
    Returns an authenticated gspread client.
    Priority: OAuth token > Service Account JSON.
    """
    import gspread
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]

    # 1. Try OAuth token first
    if config.OAUTH_TOKEN_PATH.exists():
        try:
            token_data = json.loads(config.OAUTH_TOKEN_PATH.read_text(encoding='utf-8'))
            creds = Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=token_data.get("scopes", SCOPES)
            )
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_data["token"] = creds.token
                config.OAUTH_TOKEN_PATH.write_text(json.dumps(token_data, indent=2), encoding='utf-8')
            return gspread.authorize(creds)
        except Exception as e:
            print(f"[OAuth] Token auth failed, falling back to service account: {e}")

    # 2. Fall back to service account JSON
    if config.GOOGLE_CREDENTIALS_PATH.exists():
        return gspread.service_account(filename=str(config.GOOGLE_CREDENTIALS_PATH))

    raise Exception("No Google credentials found. Please connect your Google account in Settings.")

def _open_google_spreadsheet(gc, settings: dict = None):
    """
    Centralized, resilient helper to open Elijah's Google Spreadsheet.
    Attempts: URL -> Key/ID -> Title -> Accessible spreadsheets.
    """
    if settings is None:
        settings = config.get_settings()
    sheet_id_or_url = settings.get("google_sheet_id_or_url", "").strip()
    sheet_title = settings.get("google_sheet_title", "").strip() or "FC TIMES_ FC121-130"

    # 1. Open by URL if provided
    if sheet_id_or_url:
        if "docs.google.com" in sheet_id_or_url:
            return gc.open_by_url(sheet_id_or_url)
        else:
            try:
                return gc.open_by_key(sheet_id_or_url)
            except Exception:
                pass

    # 2. Open by Title
    if sheet_title:
        try:
            return gc.open(sheet_title)
        except Exception:
            pass

    # 3. Fallback: Search accessible spreadsheets
    try:
        all_sheets = gc.openall()
        if all_sheets:
            for s in all_sheets:
                if sheet_title.lower() in s.title.lower() or "timesheet" in s.title.lower() or "fc" in s.title.lower():
                    return s
            return all_sheets[0]
    except Exception:
        pass

    raise Exception(f"Could not open Google Sheet '{sheet_title}'. Please verify the Google Sheet URL in Settings.")

def sync_submission_to_google_sheets(worker_name: str, date_val: str, rows: list) -> dict:
    """
    Fast batch-append of timesheet rows to Elijah's Google Sheets tabs.
    Groups rows by cart tab and sends all rows for a tab in a SINGLE API call.
    Auto-creates and formats the cart tab if it does not yet exist.
    """
    settings = config.get_settings()
    if not settings.get("google_sheets_enabled", True):
        return {"status": "skipped", "message": "Google Sheets sync disabled in settings"}

    has_oauth = config.OAUTH_TOKEN_PATH.exists()
    has_service = config.GOOGLE_CREDENTIALS_PATH.exists()
    if not has_oauth and not has_service:
        return {
            "status": "not_configured",
            "message": "No Google credentials found. Connect your Google account in Settings."
        }

    try:
        gc = _get_gspread_client()
        sh = _open_google_spreadsheet(gc, settings)

        # Group rows by cart tab
        rows_by_tab = {}
        for item in rows:
            cart_raw = item.get("cart_id") or "Shop"
            tab_name = normalize_cart_tab(cart_raw)
            if tab_name not in rows_by_tab:
                rows_by_tab[tab_name] = []

            row_to_push = [
                worker_name,
                str(item.get("task", "")).strip() or "General Work",
                str(item.get("category", "")).strip() or "Misc.",
                str(item.get("type", "Build")).strip() or "Build",
                str(item.get("code", "")).strip(),
                str(item.get("date", date_val)).strip() or date_val,
                str(item.get("time_in", "")).strip(),
                str(item.get("time_out", "")).strip(),
                str(item.get("duration", "")).strip()
            ]
            rows_by_tab[tab_name].append(row_to_push)

        tabs_pushed = {}
        for tab_name, tab_rows in rows_by_tab.items():
            try:
                ws = sh.worksheet(tab_name)
            except Exception:
                ws = sh.add_worksheet(title=tab_name, rows=500, cols=12)
                ws.append_row([f"Trailer Number: {tab_name}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"], value_input_option='USER_ENTERED')
                ws.append_row(STANDARD_HEADERS, value_input_option='USER_ENTERED')

            # Ensure header rows exist if worksheet was completely empty
            try:
                first_row = ws.row_values(1)
                if not first_row:
                    ws.update('A1:I2', [
                        [f"Trailer Number: {tab_name}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"],
                        STANDARD_HEADERS
                    ], value_input_option='USER_ENTERED')
            except Exception:
                pass

            # Fast single-request batch append for this cart tab
            ws.append_rows(tab_rows, value_input_option='USER_ENTERED')
            tabs_pushed[tab_name] = len(tab_rows)

        return {
            "status": "success",
            "spreadsheet_title": sh.title,
            "spreadsheet_url": sh.url,
            "tabs_updated": tabs_pushed
        }

    except Exception as e:
        print(f"[Google Sheets Error] {e}")
        return {"status": "error", "message": str(e)}

def test_google_sheets_connection() -> dict:
    """Tests connection to Google Sheets and returns spreadsheet info."""
    has_oauth = config.OAUTH_TOKEN_PATH.exists()
    has_service = config.GOOGLE_CREDENTIALS_PATH.exists()
    if not has_oauth and not has_service:
        return {
            "connected": False,
            "error": "No Google credentials found. Sign in with Google or upload a service account JSON in Settings."
        }

    try:
        gc = _get_gspread_client()
        sh = _open_google_spreadsheet(gc)

        worksheets = [w.title for w in sh.worksheets()]
        return {
            "connected": True,
            "title": sh.title,
            "url": sh.url,
            "worksheets": worksheets
        }
    except Exception as e:
        err_msg = str(e)
        cause = getattr(e, '__cause__', None)
        if not err_msg and cause:
            err_msg = str(cause)
        if not err_msg:
            err_msg = repr(e)
        if "Google Sheets API has not been used" in err_msg or "it is disabled" in err_msg:
            err_msg = "Google Sheets API is disabled in your Google Cloud project. Please visit https://console.developers.google.com/apis/api/sheets.googleapis.com/overview and click Enable."
        elif isinstance(e, PermissionError):
            if cause:
                err_msg = f"Permission error: {cause}"
            else:
                err_msg = "Permission denied. Ensure the Google Sheets API is enabled and your account has access to the sheet."

        return {
            "connected": False,
            "error": err_msg
        }

def get_cart_data(cart_id: str) -> dict:
    """
    Returns the headers, rows, and total hours for a specific cart sheet tab.
    Priority 1: Read live from Google Sheets if connected.
    Priority 2: Fall back to local CSV audit log if offline or unconfigured.
    Priority 3: Fall back to local Excel in read-only mode if available.
    """
    cart_tab = normalize_cart_tab(cart_id)

    # Priority 1: Google Sheets (Source of Truth)
    settings = config.get_settings()
    if settings.get("google_sheets_enabled", True) and (config.OAUTH_TOKEN_PATH.exists() or config.GOOGLE_CREDENTIALS_PATH.exists()):
        try:
            gc = _get_gspread_client()
            sh = _open_google_spreadsheet(gc, settings)
            try:
                ws = sh.worksheet(cart_tab)
                all_vals = ws.get_all_values()
                if all_vals:
                    total_time_str = "0:00:00"
                    if len(all_vals) >= 1 and len(all_vals[0]) >= 9:
                        total_time_str = all_vals[0][8]

                    rows = []
                    for idx, r in enumerate(all_vals[2:], start=3):
                        if not any(r):
                            continue
                        name = r[0] if len(r) > 0 else ""
                        task = r[1] if len(r) > 1 else ""
                        category = r[2] if len(r) > 2 else ""
                        build_type = r[3] if len(r) > 3 else ""
                        code = r[4] if len(r) > 4 else ""
                        date_val = r[5] if len(r) > 5 else ""
                        time_in = r[6] if len(r) > 6 else ""
                        time_out = r[7] if len(r) > 7 else ""
                        task_total = r[8] if len(r) > 8 else ""

                        if not task and not time_in and not time_out and not code:
                            continue

                        # Dynamic duration calculation if missing
                        if (not task_total or task_total == "0:00:00" or task_total.startswith("=")) and time_in and time_out:
                            task_total = utils.calculate_time_duration(time_in, time_out)

                        rows.append({
                            "row_idx": idx,
                            "name": name,
                            "task": task,
                            "category": category,
                            "type": build_type,
                            "code": code,
                            "date": date_val,
                            "time_in": time_in,
                            "time_out": time_out,
                            "task_total": task_total
                        })

                    if (not total_time_str or total_time_str == "0:00:00" or total_time_str.startswith("=") or "total" in total_time_str.lower()) and rows:
                        total_time_str = calculate_rows_total_time(rows)

                    return {
                        "cart_id": cart_tab,
                        "exists": True,
                        "total_time": total_time_str,
                        "rows": rows,
                        "source": "google_sheets"
                    }
            except Exception:
                pass
        except Exception as e:
            print(f"[Google Sheets Cart Read Notice] {e}")

    # Priority 2: Fall back to local CSV audit log
    ensure_csv_file()
    csv_rows = []
    if config.CSV_LOG_PATH.exists():
        try:
            with open(config.CSV_LOG_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader, start=3):
                    if normalize_cart_tab(row.get("Cart #", "")) == cart_tab:
                        t_in = row.get("Time In", "")
                        t_out = row.get("Time Out", "")
                        t_tot = row.get("Task Total", "")
                        if (not t_tot or t_tot == "0:00:00") and t_in and t_out:
                            t_tot = utils.calculate_time_duration(t_in, t_out)

                        csv_rows.append({
                            "row_idx": idx,
                            "name": row.get("Worker Name", ""),
                            "task": row.get("Task", ""),
                            "category": row.get("Category", ""),
                            "type": row.get("Build / Reconditioning", "Build"),
                            "code": row.get("Code", ""),
                            "date": row.get("Date", ""),
                            "time_in": t_in,
                            "time_out": t_out,
                            "task_total": t_tot
                        })
        except Exception as e:
            print(f"[CSV Cart Read Error] {e}")

    if csv_rows:
        return {
            "cart_id": cart_tab,
            "exists": True,
            "total_time": calculate_rows_total_time(csv_rows),
            "rows": csv_rows,
            "source": "csv_audit_log"
        }

    # Priority 3: Fall back to Excel file in read-only mode if exists
    if config.EXCEL_FC_WORKBOOK_PATH.exists():
        try:
            wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH, data_only=True, read_only=True)
            if cart_tab in wb.sheetnames:
                ws = wb[cart_tab]
                rows = []
                for r_idx, row in enumerate(ws.iter_rows(min_row=3, values_only=True), start=3):
                    if not row or not any(row):
                        continue
                    name = str(row[0] or "") if len(row) > 0 else ""
                    task = str(row[1] or "") if len(row) > 1 else ""
                    t_in = format_time_cell(row[6]) if len(row) > 6 else ""
                    t_out = format_time_cell(row[7]) if len(row) > 7 else ""
                    t_tot = format_duration_cell(row[8]) if len(row) > 8 else ""

                    if not task and not t_in and not t_out:
                        continue

                    if (not t_tot or t_tot == "0:00:00" or t_tot.startswith("=")) and t_in and t_out:
                        t_tot = utils.calculate_time_duration(t_in, t_out)

                    rows.append({
                        "row_idx": r_idx,
                        "name": name,
                        "task": task,
                        "category": str(row[2] or "") if len(row) > 2 else "",
                        "type": str(row[3] or "Build") if len(row) > 3 else "Build",
                        "code": str(row[4] or "") if len(row) > 4 else "",
                        "date": format_date_cell(row[5]) if len(row) > 5 else "",
                        "time_in": t_in,
                        "time_out": t_out,
                        "task_total": t_tot
                    })
                wb.close()
                return {
                    "cart_id": cart_tab,
                    "exists": True,
                    "total_time": calculate_rows_total_time(rows),
                    "rows": rows,
                    "source": "excel_readonly"
                }
            wb.close()
        except Exception:
            pass

    return {
        "cart_id": cart_tab,
        "exists": False,
        "rows": [],
        "total_time": "0:00:00",
        "source": "none"
    }

def calculate_rows_total_time(rows: list) -> str:
    """Calculates sum of HH:MM:SS durations across rows."""
    total_seconds = 0
    for r in rows:
        val = r.get("task_total", "")
        if ":" in str(val):
            parts = str(val).split(":")
            try:
                hrs = int(parts[0])
                mins = int(parts[1]) if len(parts) > 1 else 0
                secs = int(parts[2]) if len(parts) > 2 else 0
                total_seconds += (hrs * 3600) + (mins * 60) + secs
            except ValueError:
                pass
    hrs = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hrs}:{mins:02d}:{secs:02d}"

def get_all_cart_summaries() -> list:
    """Returns summaries of all cart tabs (number of tasks, total time)."""
    cart_tabs = config.get_cart_tabs()
    summaries = []

    # Check if Google Sheets is connected
    settings = config.get_settings()
    sh = None
    if settings.get("google_sheets_enabled", True) and (config.OAUTH_TOKEN_PATH.exists() or config.GOOGLE_CREDENTIALS_PATH.exists()):
        try:
            gc = _get_gspread_client()
            sh = _open_google_spreadsheet(gc, settings)
        except Exception:
            sh = None

    if sh:
        try:
            available_worksheets = {w.title: w for w in sh.worksheets()}
            for tab_name in cart_tabs:
                norm_tab = normalize_cart_tab(tab_name)
                if norm_tab in available_worksheets:
                    ws = available_worksheets[norm_tab]
                    vals = ws.get_all_values()
                    count = max(0, len(vals) - 2) if len(vals) >= 2 else 0
                    total_time = "0:00:00"
                    if len(vals) >= 1 and len(vals[0]) >= 9:
                        total_time = vals[0][8]
                    if not total_time or total_time.startswith("="):
                        data_rows = [{"task_total": r[8]} for r in vals[2:] if len(r) >= 9]
                        total_time = calculate_rows_total_time(data_rows)
                    summaries.append({
                        "cart_id": norm_tab,
                        "entry_count": count,
                        "total_time": total_time
                    })
                else:
                    summaries.append({
                        "cart_id": norm_tab,
                        "entry_count": 0,
                        "total_time": "0:00:00"
                    })
            return summaries
        except Exception as e:
            print(f"[Google Sheets Summaries Error] {e}")

    # Fallback: Calculate from CSV audit log
    ensure_csv_file()
    tab_counts = {normalize_cart_tab(t): [] for t in cart_tabs}
    try:
        with open(config.CSV_LOG_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ct = normalize_cart_tab(row.get("Cart #", ""))
                if ct not in tab_counts:
                    tab_counts[ct] = []
                tab_counts[ct].append(row)
    except Exception:
        pass

    for tab_name in cart_tabs:
        norm_tab = normalize_cart_tab(tab_name)
        rows = tab_counts.get(norm_tab, [])
        dur_rows = [{"task_total": r.get("Task Total", "")} for r in rows]
        summaries.append({
            "cart_id": norm_tab,
            "entry_count": len(rows),
            "total_time": calculate_rows_total_time(dur_rows)
        })

    return summaries

def format_date_cell(val) -> str:
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%m/%d/%y")
    return str(val)

def format_time_cell(val) -> str:
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%I:%M %p")
    return str(val)

def format_duration_cell(val) -> str:
    if val is None:
        return "0:00:00"
    if hasattr(val, "total_seconds"):
        total_secs = int(val.total_seconds())
        hrs = total_secs // 3600
        mins = (total_secs % 3600) // 60
        secs = total_secs % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return str(val)

def get_recent_history(limit: int = 50) -> list:
    """Retrieves recent entries from CSV log."""
    ensure_csv_file()
    records = []
    try:
        with open(config.CSV_LOG_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except Exception as e:
        print(f"Error reading history: {e}")

    return list(reversed(records))[:limit]

def delete_submission(submission_id: str) -> bool:
    """Removes submission from CSV."""
    if not submission_id:
        return False

    if config.CSV_LOG_PATH.exists():
        rows = []
        headers = None
        try:
            with open(config.CSV_LOG_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for row in reader:
                    if row and row[0].strip() != submission_id.strip():
                        rows.append(row)

            if headers:
                with open(config.CSV_LOG_PATH, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
            return True
        except Exception as e:
            print(f"Error deleting row: {e}")
            return False

    return False

def sync_tab_to_google_sheets(tab_name: str) -> dict:
    """
    Syncs the contents of a specific cart tab into Google Sheets.
    Pulls data from CSV audit log or Excel and uploads to Google Sheets.
    """
    settings = config.get_settings()
    if not settings.get("google_sheets_enabled", True):
        return {"status": "skipped", "message": "Google Sheets sync disabled in settings"}

    has_oauth = config.OAUTH_TOKEN_PATH.exists()
    has_service = config.GOOGLE_CREDENTIALS_PATH.exists()
    if not has_oauth and not has_service:
        return {"status": "not_configured", "message": "No Google credentials found."}

    try:
        gc = _get_gspread_client()
        sh = _open_google_spreadsheet(gc, settings)

        norm_tab = normalize_cart_tab(tab_name)
        try:
            ws = sh.worksheet(norm_tab)
        except Exception:
            ws = sh.add_worksheet(title=norm_tab, rows=500, cols=12)

        cart_info = get_cart_data(norm_tab)
        rows = cart_info.get("rows", [])

        header_row1 = [f"Trailer Number: {norm_tab}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"]
        all_values = [header_row1, STANDARD_HEADERS]
        for r in rows:
            all_values.append([
                r.get("name", ""),
                r.get("task", ""),
                r.get("category", ""),
                r.get("type", "Build"),
                r.get("code", ""),
                r.get("date", ""),
                r.get("time_in", ""),
                r.get("time_out", ""),
                r.get("task_total", "")
            ])

        ws.clear()
        ws.update('A1', all_values, value_input_option='USER_ENTERED')
        return {"status": "success", "message": f"Tab {norm_tab} synced to Google Sheets"}
    except Exception as e:
        print(f"[Google Sheets Sync Tab Error] {e}")
        return {"status": "error", "message": str(e)}

def sync_all_tabs_to_google_sheets() -> dict:
    """
    Syncs all cart tabs into Google Sheets.
    """
    cart_tabs = config.get_cart_tabs()
    synced = []
    errors = []
    for tab in cart_tabs:
        res = sync_tab_to_google_sheets(tab)
        if res.get("status") == "success":
            synced.append(tab)
        else:
            errors.append(f"{tab}: {res.get('message')}")
    return {
        "status": "success" if synced else "error",
        "synced": synced,
        "errors": errors,
        "count": len(synced)
    }

def update_cart_row(cart_id: str, row_idx: int, updated_data: dict) -> dict:
    """
    Updates an existing entry by hand in Google Sheets and CSV log.
    Eliminates openpyxl file locking.
    """
    cart_tab = normalize_cart_tab(cart_id)
    new_cart_raw = updated_data.get("cart_id")
    new_cart_tab = normalize_cart_tab(new_cart_raw) if new_cart_raw else cart_tab

    time_in = str(updated_data.get("time_in", "")).strip()
    time_out = str(updated_data.get("time_out", "")).strip()
    duration = str(updated_data.get("task_total", "")).strip()

    if time_in and time_out:
        duration = utils.calculate_time_duration(time_in, time_out)
    elif not duration or duration == "0:00:00":
        duration = "0:00:00"

    worker_name = str(updated_data.get("name", "")).strip()
    task_name = str(updated_data.get("task", "")).strip()
    category = str(updated_data.get("category", "")).strip() or "Misc."
    build_type = str(updated_data.get("type", "Build")).strip() or "Build"
    code = str(updated_data.get("code", "")).strip()
    date_val = str(updated_data.get("date", "")).strip()

    # Update Google Sheets if connected
    try:
        gc = _get_gspread_client()
        sh = _open_google_spreadsheet(gc)
        ws = sh.worksheet(cart_tab)

        if new_cart_tab != cart_tab:
            # Delete from old tab
            ws.delete_rows(row_idx)
            # Add to new tab
            try:
                target_ws = sh.worksheet(new_cart_tab)
            except Exception:
                target_ws = sh.add_worksheet(title=new_cart_tab, rows=500, cols=12)
                target_ws.append_row([f"Trailer Number: {new_cart_tab}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"], value_input_option='USER_ENTERED')
                target_ws.append_row(STANDARD_HEADERS, value_input_option='USER_ENTERED')
            target_ws.append_row([worker_name, task_name, category, build_type, code, date_val, time_in, time_out, duration], value_input_option='USER_ENTERED')
        else:
            # Update in place in Google Sheets
            ws.update(f'A{row_idx}:I{row_idx}', [[worker_name, task_name, category, build_type, code, date_val, time_in, time_out, duration]], value_input_option='USER_ENTERED')
    except Exception as e:
        print(f"[Google Sheets Row Update Notice] {e}")

    # Also update in local CSV if found
    try:
        ensure_csv_file()
        if config.CSV_LOG_PATH.exists():
            rows = []
            with open(config.CSV_LOG_PATH, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for r in reader:
                    if r and len(r) >= 13 and r[5] == cart_tab and r[3] == worker_name and r[9] == code:
                        r[3] = worker_name
                        r[4] = date_val
                        r[5] = new_cart_tab
                        r[6] = task_name
                        r[7] = category
                        r[8] = build_type
                        r[9] = code
                        r[10] = time_in
                        r[11] = time_out
                        r[12] = duration
                    rows.append(r)
            if headers:
                with open(config.CSV_LOG_PATH, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
    except Exception as ex:
        print(f"[CSV Row Update Notice] {ex}")

    return {
        "status": "success",
        "message": f"Updated entry for {worker_name} ({task_name})",
        "cart_id": new_cart_tab
    }

def delete_cart_row(cart_id: str, row_idx: int, row_data: dict = None) -> dict:
    """
    Deletes an entry from Excel, CSV audit log, and Google Sheets.
    Uses row_idx and optional row_data fields for precision matching across sources.
    """
    if row_data is None:
        row_data = {}

    cart_tab = normalize_cart_tab(cart_id)
    w_name = str(row_data.get("name", "")).strip()
    t_task = str(row_data.get("task", "")).strip()
    t_in = str(row_data.get("time_in", "")).strip()
    t_out = str(row_data.get("time_out", "")).strip()
    t_code = str(row_data.get("code", "")).strip()
    date_val = str(row_data.get("date", "")).strip()

    deleted_from = []

    # 1. Delete from local Excel workbook
    if config.EXCEL_FC_WORKBOOK_PATH.exists():
        try:
            wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)
            if cart_tab in wb.sheetnames:
                ws = wb[cart_tab]
                target_r = None
                
                # Match by cell contents if row_data provided
                if w_name or t_task:
                    for r_i in range(3, ws.max_row + 1):
                        cell_name = str(ws.cell(r_i, 1).value or "").strip()
                        cell_task = str(ws.cell(r_i, 2).value or "").strip()
                        if (not w_name or cell_name.lower() == w_name.lower()) and \
                           (not t_task or cell_task.lower() == t_task.lower()):
                            target_r = r_i
                            break

                if target_r is None and 3 <= row_idx <= ws.max_row:
                    target_r = row_idx

                if target_r and 3 <= target_r <= ws.max_row:
                    ws.delete_rows(target_r, 1)
                    wb.save(config.EXCEL_FC_WORKBOOK_PATH)
                    deleted_from.append("Excel")
                    print(f"[Excel] Deleted row {target_r} from {cart_tab}")
        except Exception as ex:
            print(f"[Excel Delete Row Error] {ex}")

    # 2. Delete matching entry from CSV audit log
    if config.CSV_LOG_PATH.exists():
        try:
            rows = []
            deleted_csv = False
            with open(config.CSV_LOG_PATH, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for r in reader:
                    if not deleted_csv and r and len(r) >= 12:
                        r_cart = normalize_cart_tab(r[5])
                        if r_cart == cart_tab:
                            r_worker = r[3].strip()
                            r_task = r[6].strip()
                            if (not w_name or r_worker.lower() == w_name.lower()) and \
                               (not t_task or r_task.lower() == t_task.lower()):
                                deleted_csv = True
                                continue
                    rows.append(r)
            if headers and deleted_csv:
                with open(config.CSV_LOG_PATH, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
                deleted_from.append("CSV")
                print(f"[CSV] Deleted row from {cart_tab}")
        except Exception as ex:
            print(f"[CSV Delete Row Error] {ex}")

    # 3. Delete from Google Sheets if connected
    settings = config.get_settings()
    if settings.get("google_sheets_enabled", True) and (config.OAUTH_TOKEN_PATH.exists() or config.GOOGLE_CREDENTIALS_PATH.exists()):
        try:
            gc = _get_gspread_client()
            sh = _open_google_spreadsheet(gc, settings)
            ws = sh.worksheet(cart_tab)
            if 3 <= row_idx <= ws.row_count:
                ws.delete_rows(row_idx)
                deleted_from.append("Google Sheets")
        except Exception as e:
            print(f"[Google Sheets Delete Row Notice] {e}")

    return {
        "status": "success",
        "message": f"Row deleted from {cart_tab} ({', '.join(deleted_from) if deleted_from else 'local storage'})",
        "deleted_from": deleted_from
    }

def clear_cart_tab(cart_id: str) -> dict:
    """
    Clears all timesheet entries from a specific food cart tab across Excel,
    CSV audit log, and Google Sheets while preserving Row 1 (header title & formula)
    and Row 2 (column headers).
    """
    cart_tab = normalize_cart_tab(cart_id)
    cleared_from = []

    # 1. Clear in local Excel workbook
    if config.EXCEL_FC_WORKBOOK_PATH.exists():
        try:
            wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)
            if cart_tab in wb.sheetnames:
                ws = wb[cart_tab]
                if ws.max_row > 2:
                    ws.delete_rows(3, ws.max_row - 2)
                ws.cell(1, 1, value=f"Trailer Number: {cart_tab}")
                ws.cell(1, 8, value="Total Time:")
                ws.cell(1, 9, value="=SUM(I3:I500)")
                for c_idx, h_name in enumerate(STANDARD_HEADERS, start=1):
                    ws.cell(2, c_idx, value=h_name)
                wb.save(config.EXCEL_FC_WORKBOOK_PATH)
                cleared_from.append("Excel")
                print(f"[Excel] Cleared all entries for {cart_tab}")
        except Exception as ex:
            print(f"[Excel Clear Cart Error] {ex}")

    # 2. Clear all rows matching this cart from CSV audit log
    if config.CSV_LOG_PATH.exists():
        try:
            kept_rows = []
            with open(config.CSV_LOG_PATH, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for r in reader:
                    if r and len(r) >= 6:
                        if normalize_cart_tab(r[5]) != cart_tab:
                            kept_rows.append(r)
                    else:
                        kept_rows.append(r)
            if headers:
                with open(config.CSV_LOG_PATH, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(kept_rows)
                cleared_from.append("CSV")
                print(f"[CSV] Cleared entries for {cart_tab}")
        except Exception as ex:
            print(f"[CSV Clear Cart Error] {ex}")

    # 3. Clear data in Google Sheets worksheet
    settings = config.get_settings()
    if settings.get("google_sheets_enabled", True) and (config.OAUTH_TOKEN_PATH.exists() or config.GOOGLE_CREDENTIALS_PATH.exists()):
        try:
            gc = _get_gspread_client()
            sh = _open_google_spreadsheet(gc, settings)
            try:
                ws = sh.worksheet(cart_tab)
                if ws.row_count > 2:
                    header_r1 = [f"Trailer Number: {cart_tab}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"]
                    ws.clear()
                    ws.update('A1:I2', [header_r1, STANDARD_HEADERS], value_input_option='USER_ENTERED')
                    cleared_from.append("Google Sheets")
                    print(f"[Google Sheets] Cleared entries for {cart_tab}")
            except Exception:
                pass
        except Exception as ex:
            print(f"[Google Sheets Clear Cart Error] {ex}")

    return {
        "status": "success",
        "message": f"All data for trailer {cart_tab} cleared successfully.",
        "cart_id": cart_tab,
        "cleared_from": cleared_from
    }

def add_cart_row(cart_id: str, data: dict) -> dict:
    """Directly adds a single row by hand to a specific cart tab."""
    time_in = str(data.get("time_in", "08:00 AM")).strip()
    time_out = str(data.get("time_out", "09:00 AM")).strip()
    dur = data.get("task_total") or data.get("duration") or ""
    if time_in and time_out:
        dur = utils.calculate_time_duration(time_in, time_out)

    return save_submission({
        "source": "Manual Hand Input",
        "worker_name": data.get("name") or data.get("worker_name") or "",
        "date": data.get("date") or datetime.now().strftime("%m/%d/%y"),
        "rows": [{
            "task": data.get("task") or "General Work",
            "category": data.get("category") or "Misc.",
            "type": data.get("type") or "Build",
            "code": data.get("code") or "",
            "time_in": time_in,
            "time_out": time_out,
            "duration": dur or "01:00:00",
            "cart_id": cart_id
        }]
    })

def initialize_cart_with_mt_codes(cart_id: str) -> dict:
    """
    Formats the given food cart tab with all MT build codes organized by category.
    Sets up the worksheet in Google Sheets.
    """
    cart_tab = normalize_cart_tab(cart_id)
    codes_db = config.get_codes_db()
    mt_codes = codes_db.get("mt_codes", [])

    rows_to_seed = []
    current_cat = None
    for item in mt_codes:
        cat = item.get("category", "General")
        if cat != current_cat:
            current_cat = cat
            rows_to_seed.append([f"=== {cat.upper()} ===", "", "", "", "", "", "", "", ""])

        rows_to_seed.append([
            "",
            item.get("task", ""),
            cat,
            item.get("type", "Build"),
            item.get("code", ""),
            "",
            "",
            "",
            ""
        ])

    # Push to Google Sheets if connected
    try:
        gc = _get_gspread_client()
        sh = _open_google_spreadsheet(gc)
        try:
            ws = sh.worksheet(cart_tab)
            ws.clear()
        except Exception:
            ws = sh.add_worksheet(title=cart_tab, rows=500, cols=12)

        header_row1 = [f"Trailer Number: {cart_tab}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"]
        all_values = [header_row1, STANDARD_HEADERS] + rows_to_seed
        ws.update('A1', all_values, value_input_option='USER_ENTERED')
    except Exception as e:
        print(f"[Init MT Codes Google Sheets Notice] {e}")

    return {
        "status": "success",
        "cart_id": cart_tab,
        "total_codes": len(mt_codes),
        "message": f"Successfully initialized {cart_tab} with {len(mt_codes)} MT build codes."
    }

def clear_all_timesheet_entries() -> dict:
    """
    Clears all timesheet entries across all cart tabs in Google Sheets and local audit log
    so Elijah can start fresh with production data.
    Automatically saves a timestamped backup before clearing.
    Preserves Row 1 (Trailer Number & Total Time formula) and Row 2 (Headers).
    """
    ensure_csv_file()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = config.EXPORTS_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_filename = f"afcr_timesheet_backup_{timestamp}.csv"
    backup_path = backup_dir / backup_filename

    # 1. Create safety backup of the CSV audit log
    if config.CSV_LOG_PATH.exists():
        shutil.copy2(config.CSV_LOG_PATH, backup_path)

    # 2. Reset afcr_timesheet_log.csv to empty headers
    with open(config.CSV_LOG_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

    # 3. Clear data rows in Google Sheets tabs (keeping Row 1 & 2 intact)
    cleared_tabs = []
    settings = config.get_settings()
    if settings.get("google_sheets_enabled", True) and (config.OAUTH_TOKEN_PATH.exists() or config.GOOGLE_CREDENTIALS_PATH.exists()):
        try:
            gc = _get_gspread_client()
            sh = _open_google_spreadsheet(gc, settings)
            for ws in sh.worksheets():
                tab_title = ws.title
                try:
                    # Keep Row 1 and Row 2 intact, clear everything below
                    total_rows = ws.row_count
                    if total_rows > 2:
                        header_row1 = [f"Trailer Number: {tab_title}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"]
                        ws.clear()
                        ws.update('A1:I2', [header_row1, STANDARD_HEADERS], value_input_option='USER_ENTERED')
                        cleared_tabs.append(tab_title)
                except Exception as ex:
                    print(f"[Clear Tab Error {tab_title}] {ex}")
        except Exception as e:
            print(f"[Google Sheets Clear All Error] {e}")

    # 4. Safely clear local Excel workbook if it exists without crashing on lock
    if config.EXCEL_FC_WORKBOOK_PATH.exists():
        try:
            wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)
            for sname in wb.sheetnames:
                ws_x = wb[sname]
                if ws_x.max_row > 2:
                    ws_x.delete_rows(3, ws_x.max_row - 2)
                ws_x.cell(1, 1, value=f"Trailer Number: {sname}")
                ws_x.cell(1, 8, value="Total Time:")
                ws_x.cell(1, 9, value="=SUM(I3:I500)")
            wb.save(config.EXCEL_FC_WORKBOOK_PATH)
        except Exception as e:
            print(f"[Local Excel Clear Notice - Ignored] {e}")

    return {
        "status": "success",
        "message": f"All timesheet entries cleared successfully. Fresh production state ready.",
        "backup_file": str(backup_path),
        "backup_name": backup_filename,
        "cleared_tabs": cleared_tabs
    }
