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

def ensure_workbook():
    """
    Ensures that the multi-tab FC TIMES Excel workbook exists in Desktop/AFCR_Scans.
    If not, seeds it from the template file or creates standard tabs.
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

        wb.save(target_path)

def init_cart_worksheet(wb, tab_name: str):
    """Initializes a worksheet with standard AFCR headers and formatting."""
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

    # Adjust widths
    widths = [16, 32, 22, 18, 10, 14, 12, 12, 14]
    for col_idx, width in enumerate(widths, 1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    return ws

def ensure_csv_file():
    """Ensures CSV audit log exists with headers."""
    if not config.CSV_LOG_PATH.exists():
        with open(config.CSV_LOG_PATH, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def save_submission(record: dict) -> dict:
    """
    Saves a verified submission record.
    Supports multi-row timesheets where each row is routed to its respective Cart Tab.
    Also appends to CSV log and triggers Google Sheets sync.
    """
    ensure_workbook()
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
        # Fallback for single-row legacy payload
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

    # Validate rows to guarantee NO row is ever saved with missing end time or missing start time
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
        
        v_item = dict(item)
        v_item["time_in"] = t_in
        v_item["time_out"] = t_out
        v_item["duration"] = dur_final
        v_item["task"] = str(item.get("task", "")).strip() or "General Work"
        v_item["cart_id"] = str(item.get("cart_id", "")).strip() or str(record.get("cart_id", "")).strip() or "Shop"
        validated_rows.append(v_item)

    wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)

    saved_items_count = 0
    synced_tabs = set()
    csv_rows_to_write = []

    for item in validated_rows:
        cart_raw = item.get("cart_id") or record.get("cart_id") or "Shop"
        tab_name = normalize_cart_tab(cart_raw)
        synced_tabs.add(tab_name)

        if tab_name not in wb.sheetnames:
            ws = init_cart_worksheet(wb, tab_name)
        else:
            ws = wb[tab_name]

        # Row fields
        task_name = item["task"]
        category = str(item.get("category", "")).strip() or "Misc."
        build_type = str(item.get("type", "Build")).strip() or "Build"
        code = str(item.get("code", "")).strip()
        time_in = item["time_in"]
        time_out = item["time_out"]
        duration = item["duration"]
        row_date = str(item.get("date", "")).strip() or date_val

        col_map = get_sheet_column_mapping(ws)

        # Check if code already exists in worksheet (e.g. pre-populated MT build sheet)
        matched_row_idx = None
        if code:
            for r in range(3, ws.max_row + 1):
                cell_code = str(ws.cell(r, col_map.get("code", 5)).value or "").strip().upper()
                if cell_code == code.upper():
                    matched_row_idx = r
                    break

        if matched_row_idx:
            next_row = matched_row_idx
            ws.cell(row=next_row, column=col_map.get("name", 1), value=worker_name)
            if task_name:
                ws.cell(row=next_row, column=col_map.get("task", 2), value=task_name)
            if category:
                ws.cell(row=next_row, column=col_map.get("category", 3), value=category)
            if build_type:
                ws.cell(row=next_row, column=col_map.get("type", 4), value=build_type)
            ws.cell(row=next_row, column=col_map.get("code", 5), value=code)
            ws.cell(row=next_row, column=col_map.get("date", 6), value=row_date)
            ws.cell(row=next_row, column=col_map.get("time_in", 7), value=time_in)
            ws.cell(row=next_row, column=col_map.get("time_out", 8), value=time_out)
            ws.cell(row=next_row, column=col_map.get("task_total", 9), value=duration)
        else:
            # Determine next row in worksheet
            next_row = max(3, ws.max_row + 1)
            row_values = [
                worker_name,
                task_name,
                category,
                build_type,
                code,
                row_date,
                time_in,
                time_out,
                duration
            ]
            ws.append(row_values)
            ws.row_dimensions[next_row].height = 20

            # Styling data row
            row_fill_color = "F8FAFC" if next_row % 2 == 0 else "FFFFFF"
            row_fill = PatternFill(start_color=row_fill_color, end_color=row_fill_color, fill_type="solid")
            cell_font = Font(name="Calibri", size=10)
            thin_border = Border(
                left=Side(style='thin', color='E2E8F0'),
                right=Side(style='thin', color='E2E8F0'),
                top=Side(style='thin', color='E2E8F0'),
                bottom=Side(style='thin', color='E2E8F0')
            )

            for col_idx in range(1, len(row_values) + 1):
                cell = ws.cell(row=next_row, column=col_idx)
                cell.fill = row_fill
                cell.font = cell_font
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")
                if col_idx in [5, 6, 7, 8, 9]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")

        saved_items_count += 1

        # CSV log row
        csv_rows_to_write.append([
            submission_id,
            timestamp,
            source,
            worker_name,
            row_date,
            tab_name,
            task_name,
            category,
            build_type,
            code,
            time_in,
            time_out,
            duration,
            image_name
        ])

    wb.save(config.EXCEL_FC_WORKBOOK_PATH)

    # Append to CSV
    with open(config.CSV_LOG_PATH, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for r in csv_rows_to_write:
            writer.writerow(r)

    # Google Sheets Sync: Synchronize all updated cart tabs directly so Excel & Google Sheets NEVER diverge
    google_sync_res = {}
    if config.get_settings().get("google_sheets_enabled", True):
        for tab in synced_tabs:
            google_sync_res[tab] = sync_tab_to_google_sheets(tab)

    return {
        "status": "success",
        "submission_id": submission_id,
        "timestamp": timestamp,
        "rows_saved": saved_items_count,
        "tabs_updated": list(synced_tabs),
        "excel_path": str(config.EXCEL_FC_WORKBOOK_PATH),
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
            import json
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
                # Re-save refreshed token
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
    Centralized, resilient helper to open Google Spreadsheet.
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

    # 3. Fallback: Search accessible spreadsheets for matching or active workbook
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
    Pushes rows to their respective cart tabs in Google Sheets.
    Uses OAuth token if available, otherwise falls back to service account.
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

        tabs_pushed = {}
        for item in rows:
            cart_raw = item.get("cart_id") or "Shop"
            tab_name = normalize_cart_tab(cart_raw)

            try:
                ws = sh.worksheet(tab_name)
            except Exception:
                ws = sh.add_worksheet(title=tab_name, rows=200, cols=12)
                ws.append_row([f"Trailer Number: {tab_name}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I200)"])
                ws.append_row(STANDARD_HEADERS)

            row_to_push = [
                worker_name,
                str(item.get("task", "")).strip(),
                str(item.get("category", "")).strip(),
                str(item.get("type", "Build")).strip(),
                str(item.get("code", "")).strip(),
                str(item.get("date", date_val)).strip(),
                str(item.get("time_in", "")).strip(),
                str(item.get("time_out", "")).strip(),
                str(item.get("duration", "")).strip()
            ]

            ws.append_row(row_to_push, value_input_option='USER_ENTERED')
            tabs_pushed[tab_name] = tabs_pushed.get(tab_name, 0) + 1

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
    """
    ensure_workbook()
    cart_tab = normalize_cart_tab(cart_id)

    wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH, data_only=True)
    if cart_tab not in wb.sheetnames:
        return {
            "cart_id": cart_tab,
            "exists": False,
            "rows": [],
            "total_time": "0:00:00"
        }

    ws = wb[cart_tab]
    total_time_raw = ws.cell(row=1, column=9).value or ws.cell(row=1, column=10).value or "0:00:00"
    total_time_str = format_duration_cell(total_time_raw)

    col_map = get_sheet_column_mapping(ws)
    rows = []
    for r in range(3, ws.max_row + 1):
        name = ws.cell(r, col_map.get("name", 1)).value
        task = ws.cell(r, col_map.get("task", 2)).value
        time_in_cell = format_time_cell(ws.cell(r, col_map["time_in"]).value) if "time_in" in col_map else ""
        time_out_cell = format_time_cell(ws.cell(r, col_map["time_out"]).value) if "time_out" in col_map else ""
        task_total_cell = format_duration_cell(ws.cell(r, col_map["task_total"]).value) if "task_total" in col_map else ""

        # Ignore completely blank rows
        if not task and not time_in_cell and not time_out_cell:
            continue

        # If time_out is missing but we have time_in and task_total, derive time_out
        if not time_out_cell and time_in_cell and task_total_cell and task_total_cell != "0:00:00":
            in_min = utils.parse_time_minutes(time_in_cell)
            dur_min = utils.parse_time_minutes(task_total_cell)
            if in_min is not None and dur_min is not None:
                time_out_cell = utils.format_minutes_to_time((in_min + dur_min) % 1440)

        # Dynamic task total
        if (not task_total_cell or task_total_cell == "0:00:00" or task_total_cell.startswith("=")) and time_in_cell and time_out_cell:
            task_total_cell = utils.calculate_time_duration(time_in_cell, time_out_cell)

        category = ws.cell(r, col_map["category"]).value if "category" in col_map else ""
        build_type = ws.cell(r, col_map["type"]).value if "type" in col_map else ""
        code = ws.cell(r, col_map["code"]).value if "code" in col_map else ""
        date_val = ws.cell(r, col_map["date"]).value if "date" in col_map else ""

        row_dict = {
            "row_idx": r,
            "name": str(name or ""),
            "task": str(task or ""),
            "category": str(category or ""),
            "type": str(build_type or ""),
            "code": str(code or ""),
            "date": format_date_cell(date_val),
            "time_in": time_in_cell,
            "time_out": time_out_cell,
            "task_total": task_total_cell
        }
        rows.append(row_dict)

    if (not total_time_str or total_time_str == "0:00:00" or total_time_str.startswith("=") or "total" in total_time_str.lower() or "trailer" in total_time_str.lower()) and rows:
        total_time_str = calculate_rows_total_time(rows)

    return {
        "cart_id": cart_tab,
        "exists": True,
        "total_time": total_time_str,
        "rows": rows
    }

def get_sheet_column_mapping(ws) -> dict:
    """
    Dynamically maps column indices for a worksheet based on Row 2 headers.
    Accommodates older sheets that had 6, 7, 8, or 9 columns.
    """
    col_map = {
        "name": 1,
        "task": 2,
        "category": 3,
        "type": 4,
        "code": 5,
        "date": 6,
        "time_in": 7,
        "time_out": 8,
        "task_total": 9
    }
    
    detected = {}
    for col_idx in range(1, 15):
        val = str(ws.cell(2, col_idx).value or '').strip().lower()
        if not val:
            continue
        if 'name' in val and 'name' not in detected:
            detected['name'] = col_idx
        elif ('task' in val or 'job' in val) and 'total' not in val and 'task' not in detected:
            detected['task'] = col_idx
        elif 'category' in val and 'category' not in detected:
            detected['category'] = col_idx
        elif ('build' in val or 'maintenance' in val or 'reconditioning' in val) and 'type' not in detected:
            detected['type'] = col_idx
        elif 'code' in val and 'code' not in detected:
            detected['code'] = col_idx
        elif 'date' in val and 'date' not in detected:
            detected['date'] = col_idx
        elif ('time in' in val or val == 'in') and 'time_in' not in detected:
            detected['time_in'] = col_idx
        elif ('out' in val or 'time out' in val) and 'time_out' not in detected:
            detected['time_out'] = col_idx
        elif ('total' in val or 'task total' in val) and 'task_total' not in detected:
            detected['task_total'] = col_idx

    col_map.update(detected)
    return col_map

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
    ensure_workbook()
    wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH, data_only=True)
    summaries = []

    for name in wb.sheetnames:
        ws = wb[name]
        col_map = get_sheet_column_mapping(ws)
        count = 0
        rows = []
        name_col = col_map.get("name", 1)
        task_col = col_map.get("task", 2)
        total_col = col_map.get("task_total", 9)

        for r in range(3, ws.max_row + 1):
            if ws.cell(r, name_col).value or ws.cell(r, task_col).value:
                count += 1
                t_in = format_time_cell(ws.cell(r, col_map["time_in"]).value) if "time_in" in col_map else ""
                t_out = format_time_cell(ws.cell(r, col_map["time_out"]).value) if "time_out" in col_map else ""
                t_tot = format_duration_cell(ws.cell(r, total_col).value)
                if (not t_tot or t_tot == "0:00:00" or t_tot.startswith("=")) and t_in and t_out:
                    t_tot = utils.calculate_time_duration(t_in, t_out)
                rows.append({"task_total": t_tot})

        total_time_val = ws.cell(1, total_col).value or ws.cell(1, 9).value or ws.cell(1, 8).value or "0:00:00"
        time_str = format_duration_cell(total_time_val)
        if (not time_str or time_str == "0:00:00" or time_str.startswith("=") or "total" in time_str.lower() or "trailer" in time_str.lower()) and rows:
            time_str = calculate_rows_total_time(rows)

        summaries.append({
            "cart_id": name,
            "entry_count": count,
            "total_time": time_str
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
    Syncs the entire contents of a cart tab from the local Excel workbook to Google Sheets.
    Keeps Google Sheets as an exact synchronized replica of Excel.
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
            ws = sh.add_worksheet(title=norm_tab, rows=200, cols=12)

        # Fetch current Excel rows for this tab
        cart_info = get_cart_data(norm_tab)
        excel_rows = cart_info.get("rows", [])

        # Build sheet values:
        # Row 1: Trailer info & Total Time
        # Row 2: Standard column headers
        # Row 3+: Data rows
        header_row1 = [f"Trailer Number: {norm_tab}", "", "", "", "", "", "", "Total Time:", "=SUM(I3:I500)"]
        all_values = [header_row1, STANDARD_HEADERS]
        for r in excel_rows:
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
        ws.update(all_values, 'A1', value_input_option='USER_ENTERED')
        return {"status": "success", "message": f"Tab {norm_tab} synced to Google Sheets"}
    except Exception as e:
        print(f"[Google Sheets Sync Tab Error] {e}")
        return {"status": "error", "message": str(e)}


def sync_all_tabs_to_google_sheets() -> dict:
    """
    Syncs every cart tab from the master local Excel workbook into Google Sheets.
    Creates and formats all missing tabs automatically.
    """
    ensure_workbook()
    wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH, data_only=True)
    synced = []
    errors = []
    for tab in wb.sheetnames:
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
    Updates an existing entry by hand in the Excel workbook.
    If the manager moved the entry to a different cart, it relocates to that tab.
    Automatically re-calculates task duration and syncs with Google Sheets.
    """
    ensure_workbook()
    cart_tab = normalize_cart_tab(cart_id)
    new_cart_raw = updated_data.get("cart_id")
    new_cart_tab = normalize_cart_tab(new_cart_raw) if new_cart_raw else cart_tab

    wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)
    if cart_tab not in wb.sheetnames:
        return {"status": "error", "message": f"Cart tab {cart_tab} does not exist"}

    ws = wb[cart_tab]
    if row_idx < 3 or row_idx > ws.max_row:
        return {"status": "error", "message": f"Invalid row index {row_idx}"}

    col_map = get_sheet_column_mapping(ws)

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

    if new_cart_tab != cart_tab:
        # Row was moved to another cart trailer
        ws.delete_rows(row_idx, 1)
        if new_cart_tab not in wb.sheetnames:
            target_ws = init_cart_worksheet(wb, new_cart_tab)
        else:
            target_ws = wb[new_cart_tab]

        row_values = [worker_name, task_name, category, build_type, code, date_val, time_in, time_out, duration]
        target_ws.append(row_values)
        wb.save(config.EXCEL_FC_WORKBOOK_PATH)

        sync_tab_to_google_sheets(cart_tab)
        sync_tab_to_google_sheets(new_cart_tab)
    else:
        # Update in place
        ws.cell(row=row_idx, column=col_map.get("name", 1), value=worker_name)
        ws.cell(row=row_idx, column=col_map.get("task", 2), value=task_name)
        ws.cell(row=row_idx, column=col_map.get("category", 3), value=category)
        ws.cell(row=row_idx, column=col_map.get("type", 4), value=build_type)
        ws.cell(row=row_idx, column=col_map.get("code", 5), value=code)
        ws.cell(row=row_idx, column=col_map.get("date", 6), value=date_val)
        ws.cell(row=row_idx, column=col_map.get("time_in", 7), value=time_in)
        ws.cell(row=row_idx, column=col_map.get("time_out", 8), value=time_out)
        ws.cell(row=row_idx, column=col_map.get("task_total", 9), value=duration)
        wb.save(config.EXCEL_FC_WORKBOOK_PATH)

        sync_tab_to_google_sheets(cart_tab)

    return {
        "status": "success",
        "message": f"Updated entry for {worker_name} ({task_name})",
        "cart_id": new_cart_tab
    }


def delete_cart_row(cart_id: str, row_idx: int) -> dict:
    """
    Deletes an incorrect or duplicate row by hand from the Excel workbook
    and syncs the deletion to Google Sheets.
    """
    ensure_workbook()
    cart_tab = normalize_cart_tab(cart_id)
    wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)
    if cart_tab not in wb.sheetnames:
        return {"status": "error", "message": f"Cart tab {cart_tab} does not exist"}

    ws = wb[cart_tab]
    if row_idx < 3 or row_idx > ws.max_row:
        return {"status": "error", "message": f"Invalid row index {row_idx}"}

    ws.delete_rows(row_idx, 1)
    # Ensure total formula remains intact
    ws.cell(row=1, column=8, value="Total Time:")
    ws.cell(row=1, column=9, value="=SUM(I3:I500)")
    wb.save(config.EXCEL_FC_WORKBOOK_PATH)

    sync_tab_to_google_sheets(cart_tab)
    return {"status": "success", "message": f"Row {row_idx} deleted from {cart_tab}"}


def add_cart_row(cart_id: str, data: dict) -> dict:
    """
    Directly adds a single row by hand to a specific cart tab.
    """
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
    Formats the given food cart tab with all 96 MT build codes organized by category.
    Creates clean category banner headers (FRAME, SHELL, INTERIOR, ROOF, HOOD,
    PLUMBING, ELECTRICAL, GAS, EXTERIOR FINISH, FINAL CHECK).
    """
    ensure_workbook()
    cart_tab = normalize_cart_tab(cart_id)
    wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)

    if cart_tab in wb.sheetnames:
        ws = wb[cart_tab]
        wb.remove(ws)

    ws = init_cart_worksheet(wb, cart_tab)

    codes_db = config.get_codes_db()
    mt_codes = codes_db.get("mt_codes", [])

    banner_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    banner_font = Font(name="Calibri", size=10, bold=True, color="F8FAFC")
    data_font = Font(name="Calibri", size=10)
    center_align = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    current_cat = None
    for item in mt_codes:
        cat = item.get("category", "General")
        if cat != current_cat:
            current_cat = cat
            row_idx = ws.max_row + 1
            ws.append([f"=== {cat.upper()} ===", "", "", "", "", "", "", "", ""])
            ws.row_dimensions[row_idx].height = 22
            for c in range(1, 10):
                cell = ws.cell(row=row_idx, column=c)
                cell.fill = banner_fill
                cell.font = banner_font
                cell.alignment = Alignment(vertical="center")

        row_idx = ws.max_row + 1
        ws.append([
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
        ws.row_dimensions[row_idx].height = 20

        row_fill_color = "F8FAFC" if row_idx % 2 == 0 else "FFFFFF"
        row_fill = PatternFill(start_color=row_fill_color, end_color=row_fill_color, fill_type="solid")

        for col_idx in range(1, 10):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.fill = row_fill
            cell.font = data_font
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")
            if col_idx in [5, 6, 7, 8, 9]:
                cell.alignment = center_align

    wb.save(config.EXCEL_FC_WORKBOOK_PATH)

    # Sync tab structure to Google Sheets if enabled
    try:
        sync_tab_to_google_sheets(cart_tab)
    except Exception:
        pass

    return {
        "status": "success",
        "cart_id": cart_tab,
        "total_codes": len(mt_codes),
        "message": f"Successfully initialized {cart_tab} with {len(mt_codes)} MT build codes."
    }

