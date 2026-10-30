import socket
import io
import base64
import os
from pathlib import Path
from PIL import Image
import qrcode
import pypdfium2 as pdfium

def get_local_ip() -> str:
    """
    Discovers the active local Wi-Fi or LAN IPv4 address.
    Works reliably across Windows, macOS, and Linux without external network requests.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not actually establish an external connection, but forces the OS
        # to determine the best outgoing network interface
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def generate_qr_code_data_url(data: str) -> str:
    """
    Generates a base64 Data URL for a high-contrast QR code image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e293b", back_color="#ffffff")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def convert_pdf_to_images(pdf_path: str, output_dir: Path) -> list:
    """
    Converts a multi-page or single-page PDF to a list of PNG image paths.
    """
    output_images = []
    pdf = pdfium.PdfDocument(pdf_path)
    base_name = Path(pdf_path).stem

    for page_idx in range(len(pdf)):
        page = pdf.get_page(page_idx)
        # 200 DPI render for crisp OCR
        bitmap = page.render(scale=2.0)
        pil_image = bitmap.to_pil()
        
        output_filename = f"{base_name}_page_{page_idx + 1}.png"
        output_file_path = output_dir / output_filename
        pil_image.save(output_file_path, format="PNG")
        output_images.append(str(output_file_path))
        
    return output_images

def parse_time_minutes(time_str: str):
    """Parses various time representations into minutes from midnight."""
    import re
    if not time_str:
        return None
    s = str(time_str).strip().lower().replace(" ", "").replace(".", ":")
    
    is_pm = "pm" in s
    is_am = "am" in s
    clean = re.sub(r'[a-z]', '', s)
    
    hours, minutes = 0, 0
    if ":" in clean:
        parts = clean.split(":")
        try:
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        except ValueError:
            return None
    elif len(clean) in [3, 4]:
        try:
            if len(clean) == 3:
                hours = int(clean[0])
                minutes = int(clean[1:])
            else:
                hours = int(clean[:2])
                minutes = int(clean[2:])
        except ValueError:
            return None
    elif len(clean) in [1, 2]:
        try:
            hours = int(clean)
            minutes = 0
        except ValueError:
            return None
    else:
        return None

    if is_pm and hours < 12:
        hours += 12
    elif is_am and hours == 12:
        hours = 0
        
    return hours * 60 + minutes

def calculate_time_duration(time_in_str: str, time_out_str: str) -> str:
    """
    Calculates duration between Time In and Time Out, formatting as HH:MM:SS.
    Handles afternoon shifts crossing 12 PM cleanly (e.g. 11:30 to 2:30).
    """
    in_min = parse_time_minutes(time_in_str)
    out_min = parse_time_minutes(time_out_str)
    if in_min is None or out_min is None:
        return "0:00:00"

    diff = out_min - in_min
    if diff <= 0 and out_min < 720:
        out_min += 720
        diff = out_min - in_min

    if diff < 0:
        diff += 1440

    hrs = diff // 60
    mins = diff % 60
    return f"{hrs}:{mins:02d}:00"

def format_minutes_to_time(minutes: int) -> str:
    """Formats minutes since midnight into HH:MM AM/PM string."""
    minutes = minutes % 1440
    hrs = minutes // 60
    mins = minutes % 60
    period = "AM"
    if hrs >= 12:
        period = "PM"
        if hrs > 12:
            hrs -= 12
    if hrs == 0:
        hrs = 12
    return f"{hrs:02d}:{mins:02d} {period}"

