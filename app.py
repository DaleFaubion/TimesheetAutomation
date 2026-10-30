import os
import sys
import uuid
import json
import subprocess
import platform
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from werkzeug.utils import secure_filename

import config
import utils
import ocr_engine
import storage

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.urandom(24)  # for session

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'pdf'}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_mobile_user_agent(ua_string: str) -> bool:
    if not ua_string:
        return False
    ua_lower = ua_string.lower()
    return any(device in ua_lower for device in ['mobile', 'android', 'iphone', 'ipad', 'ipod'])

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '')
    if is_mobile_user_agent(user_agent) and not request.args.get('desktop_mode'):
        return redirect(url_for('mobile_scanner'))
    return redirect(url_for('manager_dashboard'))

@app.route('/m')
@app.route('/mobile')
def mobile_scanner():
    """Worker Mobile Camera & OCR Capture Interface."""
    return render_template('mobile.html')

@app.route('/manager')
def manager_dashboard():
    """Manager & Assistant Desktop Hub."""
    local_ip = utils.get_local_ip()
    port = config.DEFAULT_PORT
    mobile_url = f"http://{local_ip}:{port}/m"
    qr_code_data_url = utils.generate_qr_code_data_url(mobile_url)
    
    settings = config.get_settings()
    has_creds = config.GOOGLE_CREDENTIALS_PATH.exists()
    
    return render_template(
        'index.html',
        local_ip=local_ip,
        port=port,
        mobile_url=mobile_url,
        qr_code_data_url=qr_code_data_url,
        scans_folder=str(config.SCANS_DIR),
        google_sheets_enabled=settings.get("google_sheets_enabled", True),
        has_google_credentials=has_creds,
        google_sheet_title=settings.get("google_sheet_title", "FC TIMES_ FC121-130")
    )

_current_scan_progress = {
    "active": False,
    "total_pages": 1,
    "current_page": 0,
    "percent": 0,
    "message": "",
    "phase": "idle"
}

@app.route('/api/scan/progress', methods=['GET'])
def api_scan_progress():
    return jsonify(_current_scan_progress)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """
    Receives an uploaded file (image or PDF), runs preprocessing & OCR,
    and returns recognized fields & multi-row task entries.
    """
    global _current_scan_progress
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Empty file name"}), 400
        
    if not is_allowed_file(file.filename):
        return jsonify({"status": "error", "message": "Unsupported file format. Please upload JPG, PNG, or PDF."}), 400
        
    _current_scan_progress = {
        "active": True,
        "total_pages": 1,
        "current_page": 0,
        "percent": 5,
        "message": "Uploading file...",
        "phase": "upload"
    }

    ext = file.filename.rsplit('.', 1)[1].lower()
    timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp_prefix}_{uuid.uuid4().hex[:6]}.{ext}"
    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = config.IMAGES_DIR / safe_name
    file.save(saved_path)
    
    processing_image_path = str(saved_path)
    if ext == 'pdf':
        try:
            _current_scan_progress["message"] = "Rendering PDF pages..."
            _current_scan_progress["percent"] = 8
            rendered_pages = utils.convert_pdf_to_images(str(saved_path), config.IMAGES_DIR)
            if not rendered_pages:
                _current_scan_progress["active"] = False
                return jsonify({"status": "error", "message": "Failed to render PDF pages"}), 500
            
            total_pages = len(rendered_pages)
            _current_scan_progress["total_pages"] = total_pages
            _current_scan_progress["percent"] = 10
            _current_scan_progress["message"] = f"Extracted {total_pages} pages. Starting neural OCR..."

            all_rows = []
            all_blank_codes = []
            page_urls = []
            worker_name = ""
            cart_id = ""
            date_val = ""
            raw_text_parts = []

            for p_idx, p_path in enumerate(rendered_pages, 1):
                p_name = Path(p_path).name
                page_urls.append(f"/api/image/{p_name}")
                _current_scan_progress["current_page"] = p_idx
                page_start_pct = int(10 + (85 * (p_idx - 1) / total_pages))
                _current_scan_progress["percent"] = page_start_pct
                _current_scan_progress["message"] = f"Analyzing Page {p_idx} of {total_pages} (Neural OCR & digit boxes)..."

                p_res = ocr_engine.process_document_ocr(p_path)

                page_end_pct = int(10 + (85 * p_idx / total_pages))
                _current_scan_progress["percent"] = page_end_pct
                _current_scan_progress["message"] = f"Completed Page {p_idx} of {total_pages}"

                if not worker_name and p_res.get("worker_name"):
                    worker_name = p_res["worker_name"]
                if not cart_id and p_res.get("cart_id"):
                    cart_id = p_res["cart_id"]
                if not date_val and p_res.get("date"):
                    date_val = p_res["date"]

                if p_res.get("raw_text"):
                    raw_text_parts.append(f"--- Page {p_idx} ---\n{p_res['raw_text']}")

                for r in p_res.get("rows", []):
                    r["page"] = p_idx
                    all_rows.append(r)
                
                for b in p_res.get("blank_rows", []):
                    b["page"] = p_idx
                    all_blank_codes.append(b)

            if not cart_id:
                cart_id = ""
            if not worker_name:
                worker_name = ""
            if not date_val:
                date_val = datetime.now().strftime("%m/%d/%y")

            # Propagate cart_id to rows that didn't have one if cart_id was found
            if cart_id:
                for r in all_rows:
                    if not r.get("cart_id"):
                        r["cart_id"] = cart_id

            first_page_name = Path(rendered_pages[0]).name
            ocr_result = {
                "status": "success",
                "worker_name": worker_name,
                "date": date_val,
                "cart_id": cart_id,
                "rows": all_rows,
                "blank_rows": all_blank_codes,
                "total_pages": len(rendered_pages),
                "page_urls": page_urls,
                "image_name": first_page_name,
                "image_url": f"/api/image/{first_page_name}",
                "raw_text": "\n\n".join(raw_text_parts),
                "checkbox_count": 0,
                "is_multi_page": True,
                "fields": {
                    "worker_name": worker_name,
                    "date": date_val,
                    "cart_id": cart_id,
                    "raw_text": "\n\n".join(raw_text_parts)
                }
            }

            _current_scan_progress["percent"] = 100
            _current_scan_progress["message"] = "Verification complete!"
            _current_scan_progress["active"] = False

            print(f"\n[MULTI-PAGE OCR SCAN COMPLETED] Pages: {len(rendered_pages)}")
            print(f"  Worker: {worker_name} | Cart: {cart_id} | Total Rows: {len(all_rows)}")
            return jsonify(ocr_result)
        except Exception as e:
            _current_scan_progress["active"] = False
            return jsonify({"status": "error", "message": f"Could not process multi-page PDF: {str(e)}"}), 500
            
    try:
        _current_scan_progress["total_pages"] = 1
        _current_scan_progress["current_page"] = 1
        _current_scan_progress["percent"] = 25
        _current_scan_progress["message"] = "Analyzing timesheet (Perspective warp & handwriting OCR)..."

        ocr_result = ocr_engine.process_document_ocr(processing_image_path)
        ocr_result["image_name"] = safe_name
        ocr_result["image_url"] = f"/api/image/{safe_name}"
        ocr_result["page_urls"] = [ocr_result["image_url"]]
        ocr_result["total_pages"] = 1

        _current_scan_progress["percent"] = 100
        _current_scan_progress["message"] = "Verification complete!"
        _current_scan_progress["active"] = False

        print(f"\n[OCR SCAN COMPLETED] File: {safe_name}")
        print(f"  Worker: {ocr_result.get('worker_name')} | Date: {ocr_result.get('date')}")
        print(f"  Rows Extracted: {len(ocr_result.get('rows', []))}")

        return jsonify(ocr_result)
    except Exception as e:
        _current_scan_progress["active"] = False
        print(f"[ERROR] OCR processing failed: {e}")
        return jsonify({"status": "error", "message": f"OCR processing failed: {str(e)}"}), 500

@app.route('/api/test-scan', methods=['POST'])
def api_test_scan():
    """Generates and processes sample timesheet from actual 10/07/26 data."""
    import test_pipeline
    sample_file = config.IMAGES_DIR / "sample_test_timesheet.png"
    test_pipeline.create_sample_timesheet_image(sample_file)
    ocr_result = ocr_engine.process_document_ocr(str(sample_file))
    ocr_result["image_name"] = "sample_test_timesheet.png"
    ocr_result["image_url"] = "/api/image/sample_test_timesheet.png"
    ocr_result["page_urls"] = [ocr_result["image_url"]]
    ocr_result["total_pages"] = 1
    return jsonify(ocr_result)

@app.route('/api/test-scan-mt', methods=['POST'])
def api_test_scan_mt():
    """Generates and processes sample MT form timesheet (Frame Page 1)."""
    sample_file = config.IMAGES_DIR / "sample_mt_page1.png"
    from PIL import Image
    test_img_path = config.BASE_DIR / "test_mt_p1.png"
    if test_img_path.exists():
        img = Image.open(test_img_path)
        img.save(sample_file)

    ocr_result = ocr_engine.process_document_ocr(str(sample_file))
    ocr_result["image_name"] = "sample_mt_page1.png"
    ocr_result["image_url"] = "/api/image/sample_mt_page1.png"
    ocr_result["page_urls"] = [ocr_result["image_url"]]
    ocr_result["total_pages"] = 1
    return jsonify(ocr_result)

@app.route('/api/cart/<cart_id>/init-mt', methods=['POST'])
def api_init_cart_mt(cart_id):
    """Initializes the cart spreadsheet tab with all 96 MT build codes organized by category."""
    try:
        res = storage.initialize_cart_with_mt_codes(cart_id)
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/submit', methods=['POST'])
def api_submit():
    """
    Saves verified multi-row timesheet entries into the multi-tab Excel
    workbook and synchronizes to Google Sheets.
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({"status": "error", "message": "Missing submission data"}), 400
        
    try:
        res = storage.save_submission(data)
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save timesheet: {str(e)}"}), 500

@app.route('/api/cart/<cart_id>', methods=['GET'])
def api_get_cart(cart_id):
    """Returns row details and total logged time for a specific food cart tab."""
    try:
        data = storage.get_cart_data(cart_id)
        return jsonify({"status": "success", "cart": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/cart/<cart_id>/row/<int:row_idx>', methods=['PUT', 'POST'])
def api_update_cart_row(cart_id, row_idx):
    """Updates an existing entry by hand in Excel and syncs with Google Sheets."""
    data = request.get_json() or {}
    try:
        res = storage.update_cart_row(cart_id, row_idx, data)
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/cart/<cart_id>/row/<int:row_idx>', methods=['DELETE'])
def api_delete_cart_row(cart_id, row_idx):
    """Deletes an incorrect or duplicate entry by hand from Excel and Google Sheets."""
    try:
        res = storage.delete_cart_row(cart_id, row_idx)
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/cart/<cart_id>/row', methods=['POST'])
def api_add_cart_row(cart_id):
    """Adds a single entry by hand directly to a cart tab."""
    data = request.get_json() or {}
    try:
        res = storage.add_cart_row(cart_id, data)
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/carts/summary', methods=['GET'])
def api_get_carts_summary():
    """Returns overview of all food cart tabs (counts, total time)."""
    try:
        summaries = storage.get_all_cart_summaries()
        return jsonify({"status": "success", "carts": summaries})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    """Returns recent submission history."""
    history = storage.get_recent_history(50)
    return jsonify({"status": "success", "history": history})

@app.route('/api/submission/<submission_id>', methods=['DELETE', 'POST'])
def api_delete_submission(submission_id):
    """Deletes a submission from log."""
    try:
        success = storage.delete_submission(submission_id)
        if success:
            return jsonify({"status": "success", "message": f"Submission {submission_id} deleted."})
        return jsonify({"status": "error", "message": "Submission not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/google-sheets/status', methods=['GET'])
def api_google_sheets_status():
    """Checks Google Sheets connectivity and reports which auth method is active."""
    settings = config.get_settings()
    has_oauth = config.OAUTH_TOKEN_PATH.exists()
    has_service = config.GOOGLE_CREDENTIALS_PATH.exists()
    has_client_secrets = config.OAUTH_CLIENT_SECRETS_PATH.exists()
    status = storage.test_google_sheets_connection()
    status["settings"] = settings
    status["auth_method"] = "oauth" if has_oauth else ("service_account" if has_service else "none")
    status["has_oauth_token"] = has_oauth
    status["has_service_account"] = has_service
    status["has_client_secrets"] = has_client_secrets
    return jsonify(status)

@app.route('/api/google-sheets/sync-all', methods=['POST'])
def api_sync_all_google_sheets():
    """Syncs all cart tabs from Excel to Google Sheets."""
    res = storage.sync_all_tabs_to_google_sheets()
    return jsonify(res)

@app.route('/api/google-sheets/settings', methods=['GET', 'POST'])
def api_google_sheets_settings():
    """Get or update Google Sheets settings."""
    if request.method == 'POST':
        payload = request.get_json() or {}
        updated = config.save_settings(payload)
        return jsonify({"status": "success", "settings": updated})
    return jsonify({"status": "success", "settings": config.get_settings()})

@app.route('/api/google-sheets/upload-credentials', methods=['POST'])
def api_upload_credentials():
    """Uploads service account google_credentials.json."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    file = request.files['file']
    if not file.filename.endswith('.json'):
        return jsonify({"status": "error", "message": "Must be a JSON file"}), 400
    try:
        file.save(config.GOOGLE_CREDENTIALS_PATH)
        return jsonify({"status": "success", "message": "google_credentials.json saved successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/google-sheets/upload-client-secrets', methods=['POST'])
def api_upload_client_secrets():
    """Uploads OAuth client_secrets.json for the Sign in with Google flow."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    file = request.files['file']
    if not file.filename.endswith('.json'):
        return jsonify({"status": "error", "message": "Must be a JSON file"}), 400
    try:
        content = file.read()
        data = json.loads(content)
        if 'installed' not in data and 'web' not in data:
            return jsonify({"status": "error", "message": "This doesn't look like an OAuth client secrets file. Make sure you downloaded the 'Desktop App' credentials."}), 400
        config.OAUTH_CLIENT_SECRETS_PATH.write_bytes(content)
        return jsonify({"status": "success", "message": "Client secrets uploaded! You can now click Sign in with Google."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/google-sheets/oauth-start', methods=['POST'])
def api_oauth_start():
    """Launches the local OAuth flow. Opens the browser for the user to sign in."""
    if not config.OAUTH_CLIENT_SECRETS_PATH.exists():
        return jsonify({"status": "error", "message": "No OAuth client secrets file found. Upload your client_secrets.json first."}), 400
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(config.OAUTH_CLIENT_SECRETS_PATH), OAUTH_SCOPES
        )
        # Run local server flow in background thread so Flask doesn't block
        def run_flow():
            try:
                creds = flow.run_local_server(port=0, open_browser=True)
                token_data = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": list(creds.scopes) if creds.scopes else OAUTH_SCOPES
                }
                config.OAUTH_TOKEN_PATH.write_text(json.dumps(token_data, indent=2), encoding='utf-8')
                print("[OAuth] Token saved successfully.")
            except Exception as ex:
                print(f"[OAuth Error] {ex}")
        t = threading.Thread(target=run_flow, daemon=True)
        t.start()
        return jsonify({"status": "pending", "message": "Browser should open for Google sign-in. Return here once you've signed in."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/google-sheets/oauth-status', methods=['GET'])
def api_oauth_status():
    """Polls whether an OAuth token has been successfully saved."""
    if config.OAUTH_TOKEN_PATH.exists():
        return jsonify({"status": "connected", "message": "Google account connected!"})
    return jsonify({"status": "pending", "message": "Waiting for sign-in..."})

@app.route('/api/google-sheets/oauth-disconnect', methods=['POST'])
def api_oauth_disconnect():
    """Removes saved OAuth token, disconnecting from Google."""
    if config.OAUTH_TOKEN_PATH.exists():
        config.OAUTH_TOKEN_PATH.unlink()
    return jsonify({"status": "success", "message": "Disconnected from Google."})

@app.route('/api/image/<filename>')
def get_image(filename):
    """Serves scanned document images from Desktop/AFCR_Scans/Images/."""
    file_path = config.IMAGES_DIR / secure_filename(filename)
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path)

@app.route('/api/export/excel')
def export_excel():
    """Download the FC TIMES Excel workbook."""
    storage.ensure_workbook()
    return send_file(
        config.EXCEL_FC_WORKBOOK_PATH,
        as_attachment=True,
        download_name="FC TIMES_ FC121-130.xlsx"
    )

@app.route('/api/export/csv')
def export_csv():
    """Download the current CSV log."""
    storage.ensure_csv_file()
    return send_file(
        config.CSV_LOG_PATH,
        as_attachment=True,
        download_name="afcr_timesheet_log.csv"
    )

@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    """Opens the AFCR_Scans folder on Windows Desktop."""
    try:
        config.SCANS_DIR.mkdir(parents=True, exist_ok=True)
        folder_path = os.path.normpath(str(config.SCANS_DIR))
        system = platform.system()
        if system == "Windows":
            try:
                os.startfile(folder_path)
            except Exception:
                subprocess.Popen(['explorer', folder_path])
        elif system == "Darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
        return jsonify({"status": "success", "message": "Folder opened", "folder": folder_path})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/codes')
def get_codes():
    """Returns MT and RT codes database."""
    return jsonify(config.get_codes_db())

@app.route('/api/workers', methods=['GET', 'POST', 'DELETE'])
def api_workers():
    """Manages the AFCR worker roster dynamically without code changes."""
    if request.method == 'POST':
        data = request.get_json() or {}
        new_name = str(data.get("name", "")).strip()
        workers = config.get_worker_roster()
        if new_name:
            if new_name not in workers:
                workers.append(new_name)
                config.save_worker_roster(workers)
                return jsonify({"status": "success", "message": f"Added {new_name} to worker roster", "workers": workers})
            return jsonify({"status": "success", "message": f"{new_name} is already in the worker roster", "workers": workers})
        elif "roster" in data and isinstance(data["roster"], list):
            saved = config.save_worker_roster(data["roster"])
            return jsonify({"status": "success", "message": "Updated worker roster", "workers": saved})
        return jsonify({"status": "error", "message": "Invalid worker name"}), 400

    elif request.method == 'DELETE':
        data = request.get_json() or {}
        name_to_del = str(data.get("name", "")).strip()
        workers = config.get_worker_roster()
        if name_to_del in workers:
            workers = [w for w in workers if w.lower() != name_to_del.lower()]
            config.save_worker_roster(workers)
            return jsonify({"status": "success", "message": f"Removed {name_to_del} from roster", "workers": workers})
        return jsonify({"status": "error", "message": "Worker not found in roster"}), 404

    return jsonify({"status": "success", "workers": config.get_worker_roster()})

@app.route('/api/carts/tabs', methods=['GET', 'POST', 'DELETE'])
def api_cart_tabs():
    """Manages food cart / trailer tabs dynamically across Excel, Google Sheets, and UI."""
    if request.method == 'POST':
        data = request.get_json() or {}
        raw_tab = str(data.get("cart_id") or data.get("tab_name", "")).strip()
        if not raw_tab:
            return jsonify({"status": "error", "message": "Cart ID / trailer name required"}), 400
        
        norm_tab = storage.normalize_cart_tab(raw_tab)
        cur_tabs = config.get_cart_tabs()
        if norm_tab not in cur_tabs:
            cur_tabs.append(norm_tab)
            config.save_cart_tabs(cur_tabs)

        # Initialize tab in Excel workbook
        storage.ensure_workbook()
        import openpyxl
        wb = openpyxl.load_workbook(config.EXCEL_FC_WORKBOOK_PATH)
        if norm_tab not in wb.sheetnames:
            storage.init_cart_worksheet(wb, norm_tab)
            wb.save(config.EXCEL_FC_WORKBOOK_PATH)

        # Sync tab to Google Sheets if enabled
        if config.get_settings().get("google_sheets_enabled", True):
            try:
                storage.sync_tab_to_google_sheets(norm_tab)
            except Exception:
                pass

        return jsonify({
            "status": "success",
            "message": f"Trailer tab {norm_tab} created and synced",
            "cart_id": norm_tab,
            "cart_tabs": config.get_cart_tabs()
        })

    elif request.method == 'DELETE':
        data = request.get_json() or {}
        raw_tab = str(data.get("cart_id", "")).strip()
        norm_tab = storage.normalize_cart_tab(raw_tab)
        cur_tabs = config.get_cart_tabs()
        if norm_tab in cur_tabs:
            cur_tabs = [t for t in cur_tabs if t != norm_tab]
            config.save_cart_tabs(cur_tabs)
            return jsonify({"status": "success", "message": f"Removed {norm_tab}", "cart_tabs": cur_tabs})
        return jsonify({"status": "error", "message": "Cart tab not found"}), 404

    return jsonify({"status": "success", "cart_tabs": config.get_cart_tabs()})

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """Saves feedback or work notes from Elijah/workers to a persistent file."""
    data = request.get_json() or {}
    author = data.get("author", "Elijah").strip()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"status": "error", "message": "Feedback message cannot be empty"}), 400

    feedback_file = config.SCANS_DIR / "feedback_notes.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    entry = f"[{timestamp}] From: {author}\n{message}\n{'-' * 40}\n"

    try:
        config.SCANS_DIR.mkdir(parents=True, exist_ok=True)
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return jsonify({"status": "success", "message": "Feedback note saved for Dale!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    local_ip = utils.get_local_ip()
    port = config.DEFAULT_PORT
    print("=" * 60)
    print("  AFFORDABLE FOOD CART RENTALS (AFCR)")
    print("  Timesheet Automation & Google Sheets Sync Server")
    print("=" * 60)
    print(f"  * Manager Hub:        http://localhost:{port}/manager")
    print(f"  * Worker Scanner URL: http://{local_ip}:{port}/m")
    print(f"  * Scans Directory:    {config.SCANS_DIR}")
    print(f"  * FC Times Workbook:  {config.EXCEL_FC_WORKBOOK_PATH}")
    print("=" * 60)
    
    app.run(host=config.DEFAULT_HOST, port=port, debug=False)
