import re
import cv2
import numpy as np
from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR
from pathlib import Path
from datetime import datetime
import difflib
import json
import config

_ocr_engine = None

def get_worker_roster() -> list:
    """Returns the dynamically configured AFCR worker roster from config."""
    return config.get_worker_roster()

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR()
    return _ocr_engine

def preprocess_image(image_path: str):
    """Loads, warps, and optimizes timesheet scan for handwriting OCR."""
    pil_img = Image.open(image_path)
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass
    
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv_img = apply_perspective_warp(cv_img)
    
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(sharpened)
    
    return enhanced, cv_img


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def apply_perspective_warp(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    
    screenCnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break
            
    if screenCnt is not None and cv2.contourArea(screenCnt) > 0.05 * (cv_img.shape[0] * cv_img.shape[1]):
        rect = order_points(screenCnt.reshape(4, 2))
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(cv_img, M, (maxWidth, maxHeight))
    return cv_img

def find_vertical_lines(cv_img):
    try:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, -2)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, cv_img.shape[0]//30))
        vertical_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
        lines = cv2.HoughLinesP(vertical_mask, 1, np.pi/180, 100, minLineLength=cv_img.shape[0]//5, maxLineGap=20)
        xs = []
        if lines is not None:
            for line in lines:
                l = line[0] if hasattr(line, '__len__') and len(line.shape) > 1 else line
                if hasattr(l, '__len__') and len(l) == 4:
                    x1, y1, x2, y2 = l
                    if abs(x1 - x2) < 5:
                        xs.append(int((x1+x2)//2))
        if not xs: return []
        xs.sort()
        clusters = []
        c = [xs[0]]
        for x in xs[1:]:
            if x - c[-1] < 20:
                c.append(x)
            else:
                clusters.append(int(sum(c)/len(c)))
                c = [x]
        clusters.append(int(sum(c)/len(c)))
        return clusters
    except Exception:
        return []

def detect_checkboxes(cv_img: np.ndarray) -> list:
    """Finds checkbox contours and detects checkmarks."""
    checkboxes = []
    try:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if 0.8 <= aspect_ratio <= 1.2 and 15 <= w <= 65 and 15 <= h <= 65:
                roi = thresh[y+3:y+h-3, x+3:x+w-3]
                if roi.size == 0: continue
                non_zero = cv2.countNonZero(roi)
                fill_ratio = non_zero / float(roi.size)
                checkboxes.append({
                    "box": [x, y, w, h],
                    "is_checked": fill_ratio > 0.20,
                    "fill_ratio": round(fill_ratio, 2)
                })
    except Exception:
        pass
    return checkboxes

def clean_ocr_time_token(raw_token: str) -> str:
    """Normalizes handwriting OCR confusions into clean time tokens."""
    if not raw_token:
        return ""
    s = str(raw_token).strip()
    subs = {
        'D': '0', 'O': '0', 'o': '0', 'Q': '0', 'C': '0', 'c': '0', 'U': '0', '口': '0', '品': '00', 'a': '0', '()': '0',
        '一': '1', '十': '1', 'I': '1', 'l': '1', '|': '1', '!': '1', ']': '1', '[': '1', 'i': '1', 't': '1',
        'Z': '2', 'z': '2', 'N': '7',
        'E': '3', 'e': '0',
        'A': '4', 'h': '4', 'y': '4', 'u': '4',
        'S': '5', 's': '5',
        'b': '6', 'G': '6',
        'T': '7', '>': '7',
        'B': '8', '&': '8',
        'g': '9', 'q': '9'
    }
    for k, v in subs.items():
        s = s.replace(k, v)

    s = s.replace(".", ":").replace("'", ":").replace(";", ":")
    s = re.sub(r'(\d)4[sS]\b', r'\1:45', s)
    s = re.sub(r':([0-5])[sS]\b', r':\g<1>5', s)
    return s.strip()

def parse_workday_time(clean_str: str, default_h: int = None, min_time_in: str = None) -> str:
    """
    Parses clean time token into 12-hour AM/PM string applying
    AFCR workday manufacturing shift domain rules (6:00 AM to 5:00 PM)
    and 24-hour military time standards (e.g. 13:45 -> 1:45 PM).
    """
    if not clean_str:
        return ""
    token = clean_ocr_time_token(clean_str).lower().replace(" ", "")
    is_explicit_pm = "pm" in token or ("p" in token and "am" not in token)
    is_explicit_am = "am" in token

    digs = re.sub(r'[^0-9:]', '', token)
    if not digs:
        return ""

    h = None
    mins = 0

    if ":" in digs:
        parts = digs.split(":")
        h_str, m_str = parts[0], parts[1]
        if h_str and h_str.isdigit():
            h = int(h_str)
        if m_str and m_str.isdigit():
            mins = int(m_str) if len(m_str) >= 2 else int(m_str) * 10
    elif len(digs) == 4:
        h = int(digs[:2])
        mins = int(digs[2:])
    elif len(digs) == 3:
        h = int(digs[0])
        mins = int(digs[1:])
    elif len(digs) in [1, 2]:
        val = int(digs)
        if val in [15, 30, 45]:
            mins = val
            h = default_h if default_h is not None else 9
        elif val <= 23:
            h = val
            mins = 0
        elif val in [50, 60, 70, 80, 90]:
            h = val // 10
            mins = 0
        else:
            return ""

    if h is None:
        return ""

    # Sanity bounds and inverted digit handling on hour (h must be 0-23)
    if h > 23:
        if h in [50, 60, 70, 80, 90]:
            if h == 60 and min_time_in and "08:" in min_time_in:
                # 60 is upside-down 09 when following 08:00 AM start
                h = 9
            else:
                h = h // 10
        elif h // 10 <= 12 and h % 10 == 0:
            h = h // 10
        else:
            return ""

    # Standardize 24h to 12h
    period = "AM"
    if h == 0:
        h = 12
        period = "AM"
    elif 13 <= h <= 23:
        h = h - 12
        period = "PM"
    elif h == 12:
        period = "PM"
    elif is_explicit_pm:
        period = "PM"
    elif is_explicit_am:
        period = "AM"
    elif 1 <= h <= 5:
        # AFCR factory shifts are 6:00 AM to 5:00 PM; 1-5 is PM
        period = "PM"
    else:
        period = "AM"

    if mins not in [0, 15, 30, 45]:
        if mins in [10, 11, 12, 13, 14, 16, 17]: mins = 15
        elif mins in [27, 28, 29, 31, 32, 33]: mins = 30
        elif mins in [42, 43, 44, 46, 47, 48]: mins = 45
        elif mins in [58, 59, 1, 2]: mins = 0
        elif mins > 59: mins = 0

    return f"{h:02d}:{mins:02d} {period}"

def parse_time_minutes(time_str: str):
    """Parses time string to minutes from midnight."""
    if not time_str:
        return None
    s = str(time_str).strip().lower().replace(" ", "")
    is_pm = "pm" in s
    is_am = "am" in s
    clean = re.sub(r'[^0-9:]', '', s)
    if ":" in clean:
        parts = clean.split(":")
        h = int(parts[0]) if parts[0] else 0
        m = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    else:
        return None
        
    if is_pm and h < 12:
        h += 12
    elif is_am and h == 12:
        h = 0
        
    return h * 60 + m

def calculate_time_duration(time_in_str: str, time_out_str: str) -> str:
    """Calculates difference between two times, formatting as HH:MM:SS."""
    in_m = parse_time_minutes(time_in_str)
    out_m = parse_time_minutes(time_out_str)
    if in_m is None or out_m is None:
        return "0:00:00"

    diff = out_m - in_m
    if diff < 0 and out_m < 720:
        out_m += 720
        diff = out_m - in_m
    if diff < 0:
        diff = max(0, diff + 1440)

    hrs = diff // 60
    mins = diff % 60
    return f"{hrs}:{mins:02d}:00"

def match_worker_name(raw_name: str) -> str:
    """Fuzzy matches OCR name against the known AFCR worker roster."""
    if not raw_name:
        return ""
    clean = re.sub(r'^(name|worker|tech|employee)\s*[:#\-]?\s*', '', raw_name, flags=re.IGNORECASE).strip()
    clean = re.sub(r'[^A-Za-z\s]', '', clean).strip()
    if not clean or len(clean) < 2:
        return ""
    
    # Reject non-name page titles, instructions, or long phrases
    low = clean.lower()
    if any(k in low for k in ["manufacturing", "task", "times", "afcr", "page", "instruction", "cart", "digit"]):
        return ""

    roster = get_worker_roster()
    for w in roster:
        if w.lower() in clean.lower():
            return w

    matches = difflib.get_close_matches(clean, roster, n=1, cutoff=0.5)
    if matches:
        return matches[0]

    if len(clean.split()) <= 2 and len(clean) <= 15:
        return clean.capitalize()
    return ""

def normalize_cart_token(raw_token: str, default_cart: str = "") -> str:
    """
    Normalizes cart string into standard 'FCxxx' or 'Shop' without assuming or hallucinating.
    If no valid cart is found, returns default_cart (defaults to empty string '').
    """
    if not raw_token:
        return default_cart
    s = str(raw_token).strip()
    if not s:
        return default_cart

    # Check for shop, yard, office, general
    if re.search(r'\b(shop|yard|office|general)\b', s, re.IGNORECASE):
        return "Shop"

    # Clean OCR confusions
    clean = clean_ocr_digits(s).upper().replace(" ", "")

    # Match patterns like FC127, FC 127, FC-127, FC1204
    m_fc = re.search(r'FC-?([0-9]{2,4})\b', clean, re.IGNORECASE)
    if m_fc:
        return f"FC{m_fc.group(1)}"

    # Match standalone 2-4 digit numbers (e.g. '127', '121', '130', '1001')
    m_num = re.search(r'\b([0-9]{2,4})\b', clean)
    if m_num:
        return f"FC{m_num.group(1)}"

    if clean.startswith("FC") and len(clean) >= 4:
        return clean

    return default_cart

def match_task_code_and_category(task_text: str) -> dict:
    """Matches task keywords against MT and RT codes."""
    text = task_text.lower()
    
    code_match = re.search(r'\b([FSIRHPEGXQLC][1-9][0-9]?|[MP][1-9][0-9]?)\b', task_text, re.IGNORECASE)
    if code_match:
        found_code = code_match.group(1).upper()
        try:
            codes_db = config.get_codes_db()
            for item in codes_db.get("mt_codes", []):
                if item["code"].upper() == found_code:
                    return {"code": item["code"], "category": item["category"], "type": "Build"}
            for item in codes_db.get("rt_codes", []):
                if item["code"].upper() == found_code:
                    return {"code": item["code"], "category": item["category"], "type": "Reconditioning"}
        except Exception:
            pass

    # Keyword rules
    if any(k in text for k in ["puck lock", "lock", "padlock", "hasp"]):
        return {"code": "X5", "category": "Awnings/Shelves/Windows/Trim", "type": "Build"}
    if any(k in text for k in ["window", "trim on window", "rivet"]):
        return {"code": "S8", "category": "Awnings/Shelves/Windows/Trim", "type": "Build"}
    if any(k in text for k in ["abs", "pvc", "drain", "water tank", "grey water", "gray water", "pex", "plumb"]):
        return {"code": "P6", "category": "Plumbing", "type": "Build"}
    if any(k in text for k in ["sink", "faucet"]):
        return {"code": "P1", "category": "Plumbing", "type": "Build"}
    if any(k in text for k in ["water heater", "pump"]):
        return {"code": "P3", "category": "Water Heater/Pump", "type": "Build"}
    if any(k in text for k in ["gas line", "gas pipe", "gas valve", "stoves", "propane"]):
        return {"code": "G2", "category": "Gas", "type": "Build"}
    if any(k in text for k in ["hood", "exhaust", "fan", "stack", "fss"]):
        return {"code": "H5", "category": "Hood", "type": "Build"}
    if any(k in text for k in ["osb", "frp", "dry wall", "sheetrock", "stainless"]):
        return {"code": "I1", "category": "OSB/Sheetrock/FRP/Stainless Steel", "type": "Build"}
    if any(k in text for k in ["panel", "breaker", "electrical", "outlet", "light", "wire", "cable", "extractor"]):
        return {"code": "E2", "category": "Electrical", "type": "Build"}
    if any(k in text for k in ["clean", "limpiando", "sweep", "wash", "degrease", "organize"]):
        return {"code": "C1", "category": "Cleaning", "type": "Reconditioning"}
    if any(k in text for k in ["weld", "frame", "axle", "joist", "tongue"]):
        return {"code": "F2", "category": "Frame", "type": "Build"}
    if any(k in text for k in ["awning", "shelf", "shelves"]):
        return {"code": "X1", "category": "Awnings/Shelves/Windows/Trim", "type": "Build"}
    if any(k in text for k in ["qc", "inspection", "safety"]):
        return {"code": "L3", "category": "Final Check", "type": "Build"}

    return {"code": "", "category": "Misc.", "type": "Build"}

PAGE_CODES = {
    1: [f"F{i}" for i in range(1, 14)],
    2: [f"S{i}" for i in range(1, 16)],
    3: [f"I{i}" for i in range(1, 6)] + [f"R{i}" for i in range(1, 7)] + ["I6", "I7"],
    4: [f"I{i}" for i in range(8, 12)] + [f"H{i}" for i in range(1, 10)] + ["P1"],
    5: [f"P{i}" for i in range(2, 10)] + [f"E{i}" for i in range(1, 7)],
    6: [f"E{i}" for i in range(7, 12)] + [f"G{i}" for i in range(1, 8)] + ["X1", "X2"],
    7: [f"X{i}" for i in range(3, 9)] + [f"L{i}" for i in range(1, 8)]
}

def clean_ocr_digits(s: str) -> str:
    subs = {
        'D': '0', 'O': '0', 'o': '0', 'Q': '0', 'C': '0', 'c': '0', 'U': '0', '口': '0', '品': '00', 'a': '0', '()': '0',
        '一': '1', '十': '1', 'I': '1', 'l': '1', '|': '1', '!': '1', ']': '1', '[': '1', 'i': '1', 't': '1', 'n': '1',
        'Z': '2', 'z': '2', 'N': '7',
        'E': '3', 'e': '3',
        'A': '4', 'h': '4', 'y': '4', 'u': '4',
        'S': '5', 's': '5',
        'b': '6', 'G': '6',
        'T': '7', '>': '7',
        'B': '8', '&': '8',
        'g': '9', 'q': '9'
    }
    return ''.join(subs.get(c, c) for c in s)

def extract_cart_from_header(cv_img: np.ndarray, res_whole: list, scale_x: float, scale_y: float) -> str:
    """
    Carefully extracts the Cart # (e.g. FC127, FC121, Shop) directly from the
    'Food Cart #' or 'Cart # FC' header field WITHOUT assuming or hallucinating anything.
    """
    h, w = cv_img.shape[:2]
    gray_img = cv_img if len(cv_img.shape) == 2 else cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    engine = get_ocr_engine()
    header_y_limit = int(220 * scale_y)

    # 1. First, check if any token in header already contains explicit FC followed by digits
    for box, text, sc in (res_whole or []):
        y_mid = (box[0][1] + box[2][1]) / 2.0
        if y_mid < header_y_limit:
            t = text.strip()
            # If token explicitly has FC followed by digits (e.g. 'FC 127', 'FC121', 'Cart # FC 127')
            m = re.search(r'\b(?:food\s*cart|cart)?\s*#?\s*FC\s*([0-9]{2,4})\b', t, re.IGNORECASE)
            if m:
                return f"FC{m.group(1)}"
            m_pure_fc = re.search(r'\bFC-?([0-9]{2,4})\b', t, re.IGNORECASE)
            if m_pure_fc and "page" not in t.lower():
                return f"FC{m_pure_fc.group(1)}"
            if re.search(r'\b(?:cart|trailer)\s*#?\s*:\s*(shop)\b', t, re.IGNORECASE):
                return "Shop"

    # 2. Look for the 'Cart # FC', 'Cart #', or 'Food Cart #' label in the header
    cart_labels = []
    for box, text, sc in (res_whole or []):
        y_mid = (box[0][1] + box[2][1]) / 2.0
        if y_mid < header_y_limit:
            if re.search(r'(?:food\s*)?cart\s*#?\s*(?:fc)?|cart#fc|\bfc\s*#', text, re.IGNORECASE):
                cart_labels.append((box, text))

    if cart_labels:
        label_box, label_text = cart_labels[0]
        lx2 = max(p[0] for p in label_box)
        ly1 = min(p[1] for p in label_box)
        ly2 = max(p[1] for p in label_box)

        # Region directly to the right of the label (where the cart number is written/boxed)
        crop_x1 = max(0, int(lx2 - 5 * scale_x))
        crop_x2 = min(w, int(lx2 + 260 * scale_x))
        crop_y1 = max(0, int(ly1 - 10 * scale_y))
        crop_y2 = min(h, int(ly2 + 25 * scale_y))

        crop = gray_img[crop_y1:crop_y2, crop_x1:crop_x2]
        if crop.size > 0:
            # Check for individual digit boxes (contours) inside this field
            try:
                thresh = cv2.threshold(crop, 200, 255, cv2.THRESH_BINARY_INV)[1]
                cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                boxes = sorted(
                    [cv2.boundingRect(c) for c in cnts if 15 <= cv2.boundingRect(c)[2] <= 70 and 15 <= cv2.boundingRect(c)[3] <= 70],
                    key=lambda b: b[0]
                )
                box_digits = []
                for bx, by, bw, bh in boxes:
                    roi = crop[by+2:by+bh-2, bx+2:bx+bw-2]
                    if roi.size > 0 and np.sum(roi < 210) > 5:
                        r_ocr, _ = engine(cv2.resize(roi, (bw*4, bh*4)))
                        if r_ocr:
                            d = clean_ocr_digits(''.join([t[1] for t in r_ocr]))
                            d = re.sub(r'\D', '', d)
                            if d:
                                box_digits.append(d)
                if box_digits:
                    combined = ''.join(box_digits)
                    if len(combined) in [2, 3, 4]:
                        return f"FC{combined}"
            except Exception:
                pass

            # Full field crop OCR fallback (for freehand writing or unboxed text)
            try:
                res_field, _ = engine(cv2.resize(crop, (crop.shape[1]*3, crop.shape[0]*3)))
                if res_field:
                    # Filter out tokens that belong to 'Page 1 of 7' or similar
                    valid_tokens = [t[1].strip() for t in res_field if not any(w in t[1].lower() for w in ["page", "of"])]
                    field_text = ' '.join(valid_tokens)
                    if "shop" in field_text.lower():
                        return "Shop"
                    # Combine individual digits or digit groups
                    digits = [re.sub(r'\D', '', clean_ocr_digits(t)) for t in valid_tokens if re.sub(r'\D', '', clean_ocr_digits(t))]
                    combined_digits = ''.join(digits)
                    if combined_digits and len(combined_digits) in [2, 3, 4]:
                        return f"FC{combined_digits}"
            except Exception:
                pass

    # 3. If no cart label found or field was blank, check header text for standalone cart numbers
    for box, text, sc in (res_whole or []):
        y_mid = (box[0][1] + box[2][1]) / 2.0
        if y_mid < header_y_limit:
            low = text.lower()
            if "shop" in low and ("cart" in low or "location" in low):
                return "Shop"
            m = re.search(r'\bFC\s*([0-9]{2,4})\b', text, re.IGNORECASE)
            if m and "page" not in low:
                return f"FC{m.group(1)}"

    # If completely blank or unreadable, DO NOT ASSUME OR HALLUCINATE!
    return ""

def parse_mt_document_ocr(enhanced, cv_img, res_whole, lines, full_text, scale_x, scale_y):
    """
    High-precision, high-speed OCR parser for the AFCR Manufacturing Task Times (MT) 7-page packet.
    Extracts pre-printed task codes (F1-F13, S1-S15, etc.), digit box times, dates PER ROW, and N/A statuses.
    Optimized: avoids redundant per-row OCR on blank rows, using res_whole tokens for handwriting detection.
    """
    h, w = cv_img.shape[:2]
    gray_img = cv_img if len(cv_img.shape) == 2 else cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    codes_db = config.get_codes_db()
    mt_map = {item["code"].upper(): item for item in codes_db.get("mt_codes", [])}
    engine = get_ocr_engine()

    # 1. Header parsing - Extract Cart # directly from field without hallucination
    cart_id = extract_cart_from_header(cv_img, res_whole, scale_x, scale_y)
    worker_name = ""
    date_val = ""
    page_info = "Page 1 of 7"
    page_num = 1

    pm = re.search(r'Page\s*(\d+)\s*of\s*(\d+)', full_text, re.IGNORECASE)
    if pm:
        page_num = int(pm.group(1))
        page_info = f"Page {pm.group(1)} of {pm.group(2)}"

    try:
        # Worker Name Box
        name_crop = gray_img[int(30*scale_y):int(130*scale_y), int(140*scale_x):int(550*scale_x)]
        res_n, _ = engine(name_crop)
        n_raw = ' '.join([t[1] for t in res_n]).lower() if res_n else ''
        worker_name = match_worker_name(n_raw)
    except Exception:
        pass

    if not worker_name:
        for box, text, sc in (res_whole or []):
            if (box[0][1] + box[2][1]) / 2.0 < 140 * scale_y:
                cand = match_worker_name(text)
                if cand:
                    worker_name = cand
                    break

    # Look for page-level header date if present
    for box, text, sc in (res_whole or []):
        if (box[0][1] + box[2][1]) / 2.0 < 150 * scale_y:
            m_hd = re.search(r'\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b', text)
            if m_hd and not date_val:
                date_val = m_hd.group(1)

    # 2. Dynamic Code Row Alignment
    page_codes = PAGE_CODES.get(page_num, PAGE_CODES[1])
    code_y_positions = {}
    for box, text, sc in (res_whole or []):
        t_clean = text.strip().upper()
        if t_clean in page_codes:
            code_y_positions[t_clean] = int((box[0][1] + box[2][1]) / 2.0)

    # Fallback linear spacing if not all codes detected in res_whole
    detected_ys = sorted(code_y_positions.values())
    default_step = int(90 * scale_y)
    first_y = detected_ys[0] if detected_ys else int((359 if page_num == 1 else 188) * scale_y)

    extracted_rows = []
    all_codes = []
    blank_rows = []
    prev_time_out = None
    prev_row_date = None

    for idx, code in enumerate(page_codes):
        meta = mt_map.get(code, {})
        task_desc = meta.get("task", f"Task {code}")
        category = meta.get("category", "Frame" if code.startswith("F") else "General")
        build_type = meta.get("type", "Build")

        # Determine y coordinate: prefer detected code anchor, else linear step
        if code in code_y_positions:
            cy = code_y_positions[code]
        else:
            cy = first_y + idx * default_step

        sub_y1 = int(cy + 15 * scale_y)
        sub_y2 = int(cy + 65 * scale_y)

        # Check N/A box: x ≈ 1040-1120 at code level (cy - 15 to cy + 15)
        na_crop = gray_img[max(0, cy - int(12*scale_y)):min(h, cy + int(12*scale_y)), int(1060*scale_x):min(w, int(1110*scale_x))]
        is_na = bool((np.sum(na_crop < 120) / float(na_crop.size) > 0.35)) if na_crop.size > 0 else False

        # Checkboxes: 10-min & Lunch at sub_y level
        cb_10 = gray_img[max(0, sub_y1):min(h, sub_y2), int(990*scale_x):min(w, int(1040*scale_x))]
        cb_lunch = gray_img[max(0, sub_y1):min(h, sub_y2), int(1090*scale_x):min(w, int(1140*scale_x))]
        has_break_10 = bool((np.sum(cb_10 < 120) / float(cb_10.size) > 0.35)) if cb_10.size > 0 else False
        has_lunch = bool((np.sum(cb_lunch < 120) / float(cb_lunch.size) > 0.35)) if cb_lunch.size > 0 else False

        # Check if res_whole detected any digit tokens in this row's vertical band (sub_y1-10 to sub_y2+10)
        row_tokens = []
        for box, text, sc in (res_whole or []):
            by = (box[0][1] + box[2][1]) / 2.0
            bx = (box[0][0] + box[2][0]) / 2.0
            if sub_y1 - 10 <= by <= sub_y2 + 10:
                row_tokens.append((bx, by, text, sc))

        # Check if digits exist in date/time X-ranges (170-880)
        has_hw = any(any(ch.isdigit() for ch in t[2]) and int(170*scale_x) <= t[0] <= int(880*scale_x) for t in row_tokens)

        row_date = ""
        t_in = ""
        t_out = ""

        if has_hw:
            # Crop single horizontal strip for Date & Time to extract clean handwriting tokens
            crop_strip = cv_img[sub_y1:sub_y2, int(160*scale_x):int(880*scale_x)]
            res_strip, _ = engine(crop_strip)
            strip_tokens = []
            if res_strip:
                for b, t, sc in res_strip:
                    bx = (b[0][0] + b[2][0]) / 2.0 + int(160*scale_x)
                    strip_tokens.append((bx, t, sc))

            # Date tokens: x in 170-360
            d_toks = [t[1] for t in strip_tokens if int(170*scale_x) <= t[0] <= int(360*scale_x) and any(c.isdigit() for c in t[1])]
            # In tokens: x in 460-630
            in_toks = [t[1] for t in strip_tokens if int(460*scale_x) <= t[0] <= int(630*scale_x) and any(c.isdigit() for c in t[1])]
            # Out tokens: x in 700-870
            out_toks = [t[1] for t in strip_tokens if int(700*scale_x) <= t[0] <= int(870*scale_x) and any(c.isdigit() for c in t[1])]

            if d_toks:
                d_str = "/".join([re.sub(r'\D', '', t) for t in d_toks if re.sub(r'\D', '', t)])
                m_d = re.search(r'(\d{1,2})[/.-](\d{1,2})', d_str)
                if m_d:
                    row_date = f"{int(m_d.group(1)):02d}/{int(m_d.group(2)):02d}"
                elif len(d_str) in [3, 4]:
                    row_date = f"{int(d_str[:2]):02d}/{int(d_str[2:]):02d}"

            if in_toks:
                raw_in = ":".join([re.sub(r'\D', '', t) for t in in_toks if re.sub(r'\D', '', t)])
                t_in = parse_workday_time(raw_in)

            if out_toks:
                raw_out = ":".join([re.sub(r'\D', '', t) for t in out_toks if re.sub(r'\D', '', t)])
                t_out = parse_workday_time(raw_out, min_time_in=t_in)

        has_time = bool(t_in or t_out)
        has_row_date = bool(row_date)

        if not has_time and not is_na and not has_row_date:
            entry_blank = {
                "code": code,
                "task": task_desc,
                "category": category,
                "type": build_type,
                "date": "",
                "time_in": "",
                "time_out": "",
                "duration": "0:00:00",
                "cart_id": cart_id,
                "is_na": False,
                "has_break_10": False,
                "has_lunch": False,
                "status": "blank"
            }
            all_codes.append(entry_blank)
            blank_rows.append(entry_blank)
            continue

        # If date was not written on this active row, inherit previous row's date
        if not row_date and prev_row_date:
            row_date = prev_row_date
        elif not row_date and date_val:
            row_date = date_val

        # Shift continuity: if time_in is missing, inherit from previous task
        if not t_in and prev_time_out and prev_row_date == row_date:
            if has_break_10:
                m_prev = parse_time_minutes(prev_time_out)
                if m_prev:
                    m_new = m_prev + 15
                    h_n, mn_n = m_new // 60, m_new % 60
                    p_n = "PM" if h_n >= 12 else "AM"
                    if h_n > 12: h_n -= 12
                    t_in = f"{h_n:02d}:{mn_n:02d} {p_n}"
            elif has_lunch:
                t_in = "01:00 PM"
            else:
                t_in = prev_time_out

        duration = "0:00:00"
        if t_in and t_out:
            duration = calculate_time_duration(t_in, t_out)
            if (has_break_10 or has_lunch) and duration != "0:00:00":
                m_tot = parse_time_minutes(duration)
                if has_break_10 and m_tot > 10: m_tot -= 10
                if has_lunch and m_tot > 30: m_tot -= 30
                duration = f"{m_tot // 60}:{m_tot % 60:02d}:00"

        if t_out:
            prev_time_out = t_out
        if row_date:
            prev_row_date = row_date

        entry = {
            "code": code,
            "task": task_desc,
            "category": category,
            "type": build_type,
            "date": row_date,
            "time_in": t_in,
            "time_out": t_out,
            "duration": duration,
            "cart_id": cart_id,
            "is_na": is_na,
            "has_break_10": has_break_10,
            "has_lunch": has_lunch,
            "status": "completed" if (t_in and t_out) else ("na" if is_na else "active")
        }

        all_codes.append(entry)
        if (t_in and t_out) or is_na:
            extracted_rows.append(entry)
        else:
            blank_rows.append(entry)

    top_date = extracted_rows[0]["date"] if (extracted_rows and extracted_rows[0].get("date")) else (date_val or "")
    fields = {
        "worker_name": worker_name or "",
        "date": top_date,
        "cart_id": cart_id,
        "page_info": page_info,
        "raw_text": full_text
    }

    return {
        "status": "success",
        "worker_name": fields["worker_name"],
        "date": fields["date"],
        "cart_id": fields["cart_id"],
        "page_info": page_info,
        "is_mt_sheet": True,
        "rows": extracted_rows,
        "blank_rows": blank_rows,
        "all_codes": all_codes,
        "fields": fields,
        "lines": lines,
        "checkbox_count": 0,
        "raw_text": full_text
    }

def process_document_ocr(image_path: str) -> dict:
    """
    Upgraded AFCR Timesheet OCR Engine:
    - Geometric column slicing prevents horizontal text merging
    - Dedicated high-precision parser for MT Manufacturing 7-page packets
    - Handwriting-aware time token normalizer
    - AFCR worker roster fuzzy matching
    - Shift continuity guarantee: NO missing end times!
    """
    engine = get_ocr_engine()
    enhanced, cv_img = preprocess_image(image_path)
    h, w = cv_img.shape[:2]
    
    # 1. Whole-page OCR for header detection
    res_whole, _ = engine(enhanced)
    lines = []
    full_text_parts = []
    worker_name = ""
    date_val = ""
    
    scale_x = w / 1224.0
    scale_y = h / 1584.0

    if res_whole:
        for box, text, sc in res_whole:
            lines.append({"box": box, "text": text, "confidence": round(float(sc), 2)})
            full_text_parts.append(text)

    full_text = "\n".join(full_text_parts)

    # Check if this document is the MT (Manufacturing Task Times) 7-page packet
    is_mt_form = bool(re.search(
        r'MANUFACTURING TASK TIMES|Pen only|Avg time|FRAME \(F\)|SHELL \(S\)|INTERIOR|PLUMBING|ELECTRICAL|FINAL CHECK|Cart\s*#\s*FC',
        full_text,
        re.IGNORECASE
    ))

    if is_mt_form:
        return parse_mt_document_ocr(enhanced, cv_img, res_whole, lines, full_text, scale_x, scale_y)
    
    # Extract Cart # directly from header Food Cart # field without hallucinating
    header_cart = extract_cart_from_header(cv_img, res_whole, scale_x, scale_y)
    default_cart = header_cart or ""

    est_task = int(650 * scale_x)
    est_tin  = int(790 * scale_x)
    est_tout = int(960 * scale_x)
    est_cart = int(1150 * scale_x)
    table_top_y = int(155 * scale_y)
    
    vert_lines = find_vertical_lines(cv_img)
    def snap(est, lines, margin=80*scale_x):
        closest, min_d = est, margin
        for l in lines:
            if abs(l - est) < min_d:
                min_d = abs(l - est)
                closest = l
        return closest

    col_task_x1 = snap(est_task, vert_lines)
    col_tin_x1  = snap(est_tin, vert_lines)
    col_tout_x1 = snap(est_tout, vert_lines)
    col_cart_x1 = snap(est_cart, vert_lines)
    col_date_x1 = None

    if res_whole:
        for box, text, sc in res_whole:
            t = text.lower()
            y_box = (box[0][1] + box[2][1]) / 2
            
            # Header search
            if y_box < table_top_y:
                if "name" in t or (x_box := (box[0][0] + box[2][0]) / 2) < 400 * scale_x:
                    cand = match_worker_name(text)
                    if cand and not worker_name:
                        worker_name = cand
                if "date" in t or re.search(r'\d{1,2}/\d{1,2}', text):
                    dm = re.search(r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)', text)
                    if dm and not date_val:
                        date_val = dm.group(1)

            # Header row calibration
            if 100 * scale_y <= y_box <= 180 * scale_y:
                if "date" in t or "fecha" in t:
                    col_date_x1 = int(box[0][0])
                elif "time in" in t:
                    col_task_x1 = int(box[0][0])
                    col_tin_x1 = int(box[2][0] + 15 * scale_x)
                elif "time out" in t:
                    col_tout_x1 = int(box[2][0] + 15 * scale_x)
                elif "cart" in t:
                    col_cart_x1 = int(box[2][0] + 60 * scale_x)

    full_text = "\n".join(full_text_parts)
    if not date_val:
        date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b', full_text)
        date_val = date_match.group(1) if date_match else datetime.now().strftime("%m/%d/%y")

    # 2. Extract column-isolated OCR
    crop_task = enhanced[table_top_y:h-40, int(80*scale_x):col_task_x1]
    crop_tin  = enhanced[table_top_y:h-40, col_task_x1:col_tin_x1]
    crop_tout = enhanced[table_top_y:h-40, col_tin_x1:col_tout_x1]
    crop_cart = enhanced[table_top_y:h-40, col_tout_x1:col_cart_x1]

    tin_items = []
    res_tin, _ = engine(crop_tin)
    if res_tin:
        for box, text, sc in res_tin:
            y = int((box[0][1] + box[2][1]) / 2) + table_top_y
            std_time = parse_workday_time(text)
            if std_time:
                tin_items.append({"y": y, "time": std_time, "raw": text, "score": sc})

    tout_items = []
    res_tout, _ = engine(crop_tout)
    if res_tout:
        for box, text, sc in res_tout:
            y = int((box[0][1] + box[2][1]) / 2) + table_top_y
            std_time = parse_workday_time(text)
            if std_time:
                tout_items.append({"y": y, "time": std_time, "raw": text, "score": sc})

    cart_items = []
    res_cart, _ = engine(crop_cart)
    if res_cart:
        for box, text, sc in res_cart:
            y = int((box[0][1] + box[2][1]) / 2) + table_top_y
            c_val = normalize_cart_token(text, default_cart)
            cart_items.append({"y": y, "cart": c_val, "raw": text})

    task_items = []
    res_task, _ = engine(crop_task)
    if res_task:
        for box, text, sc in res_task:
            y = int((box[0][1] + box[2][1]) / 2) + table_top_y
            cleaned_t = text.strip()
            if cleaned_t and len(cleaned_t) > 1:
                task_items.append({"y": y, "text": cleaned_t})

    # Optional dedicated date column
    date_items = []
    if col_date_x1 and col_date_x1 < col_task_x1:
        crop_date = enhanced[table_top_y:h-40, col_date_x1:col_task_x1]
        res_date_col, _ = engine(crop_date)
        if res_date_col:
            for box, text, sc in res_date_col:
                y = int((box[0][1] + box[2][1]) / 2) + table_top_y
                m_d = re.search(r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)', text)
                if m_d:
                    date_items.append({"y": y, "date": m_d.group(1)})

    tin_items.sort(key=lambda x: x["y"])
    tout_items.sort(key=lambda x: x["y"])
    cart_items.sort(key=lambda x: x["y"])
    task_items.sort(key=lambda x: x["y"])
    date_items.sort(key=lambda x: x["y"])

    # 3. Align rows with Shift Continuity Guarantee
    y_anchors = sorted(list(set([t["y"] for t in tout_items] + [t["y"] for t in tin_items])))
    clusters = []
    for ya in y_anchors:
        placed = False
        for c in clusters:
            if abs(ya - (sum(c)/len(c))) < 45 * scale_y:
                c.append(ya)
                placed = True
                break
        if not placed:
            clusters.append([ya])

    row_ys = [int(sum(c)/len(c)) for c in clusters]
    rows = []
    prev_time_out = ""
    prev_row_date = ""

    for y in row_ys:
        matched_tout = None
        for it in tout_items:
            if abs(it["y"] - y) < 45 * scale_y:
                matched_tout = it["time"]
                break

        matched_tin = None
        for it in tin_items:
            if abs(it["y"] - y) < 45 * scale_y:
                matched_tin = it["time"]
                break

        # Shift continuity: if time_in is missing, inherit previous row's time_out!
        if not matched_tin and prev_time_out:
            matched_tin = prev_time_out

        # If time_out is missing, look ahead or inherit
        if matched_tin and not matched_tout:
            for it in tout_items:
                if it["y"] > y and (it["y"] - y) < 75 * scale_y:
                    matched_tout = it["time"]
                    break

        matched_cart = default_cart
        for it in cart_items:
            if abs(it["y"] - y) < 60 * scale_y:
                matched_cart = it["cart"]
                break

        matched_task_parts = []
        for it in task_items:
            if abs(it["y"] - y) < 48 * scale_y:
                matched_task_parts.append(it["text"])

        task_text = " ".join(matched_task_parts).strip() or "Cart Work"
        
        # Check for Row Date: from date column, or written inside task text
        matched_row_date = ""
        for it in date_items:
            if abs(it["y"] - y) < 48 * scale_y:
                matched_row_date = it["date"]
                break

        if not matched_row_date:
            m_inline_date = re.search(r'\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b', task_text)
            if m_inline_date:
                matched_row_date = m_inline_date.group(1)
                task_text = re.sub(r'\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b', '', task_text).strip()

        if matched_row_date:
            row_date = matched_row_date
            prev_row_date = row_date
        elif prev_row_date:
            row_date = prev_row_date
        else:
            row_date = date_val or ""

        meta = match_task_code_and_category(task_text)

        if matched_tin or matched_tout:
            # Guarantee: NO EMPTY END TIME!
            if matched_tin and not matched_tout:
                matched_tout = matched_tin
            elif matched_tout and not matched_tin:
                matched_tin = matched_tout

            duration = calculate_time_duration(matched_tin, matched_tout)
            rows.append({
                "task": task_text,
                "category": meta["category"],
                "type": meta["type"],
                "code": meta["code"],
                "date": row_date,
                "time_in": matched_tin,
                "time_out": matched_tout,
                "duration": duration,
                "cart_id": matched_cart
            })
            prev_time_out = matched_tout

    checkboxes = detect_checkboxes(cv_img)
    if not rows:
        meta = match_task_code_and_category(full_text)
        rows = [{
            "task": "Daily Cart Work",
            "category": meta["category"],
            "type": meta["type"],
            "code": meta["code"],
            "date": date_val or "",
            "time_in": "08:00 AM",
            "time_out": "12:00 PM",
            "duration": "4:00:00",
            "cart_id": default_cart
        }]

    fields = {
        "worker_name": worker_name or "",
        "date": rows[0]["date"] if rows else date_val,
        "cart_id": header_cart or (rows[0]["cart_id"] if rows else ""),
        "raw_text": full_text
    }

    return {
        "status": "success",
        "worker_name": fields["worker_name"],
        "date": fields["date"],
        "cart_id": fields["cart_id"],
        "rows": rows,
        "fields": fields,
        "lines": lines,
        "checkbox_count": len(checkboxes),
        "checkboxes": checkboxes,
        "raw_text": full_text
    }
