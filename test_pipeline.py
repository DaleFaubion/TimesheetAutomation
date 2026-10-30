"""
Automated End-to-End Test for AFCR Timesheet OCR Pipeline.
Generates a realistic test timesheet image matching the physical scanned forms,
tests OCR extraction, and validates Excel/CSV writing with food cart tabs.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import config
import ocr_engine
import storage

def create_sample_timesheet_image(output_path: Path):
    """
    Generates a realistic daily timesheet image matching the actual AFCR paper form
    (Task / Job | Time In | Time Out | Cart #).
    """
    width, height = 1000, 1300
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Outer border / paper effect
    draw.rectangle([20, 20, width - 20, height - 20], outline=(200, 200, 200), width=1)

    # Top Header: NAME and DATE
    y = 50
    draw.text((60, y), "NAME:  Israel", fill=(10, 10, 10))
    draw.text((650, y), "DATE:  10/07/26", fill=(10, 10, 10))

    # Table Header Line
    y += 50
    draw.line([60, y, 940, y], fill=(60, 60, 60), width=2)
    y += 8
    draw.text((100, y), "Task / Job", fill=(40, 40, 40))
    draw.text((540, y), "Time In", fill=(40, 40, 40))
    draw.text((680, y), "Time Out", fill=(40, 40, 40))
    draw.text((820, y), "Cart #", fill=(40, 40, 40))
    y += 28
    draw.line([60, y, 940, y], fill=(60, 60, 60), width=2)

    # Table Column Vertical Dividers
    table_top = y - 36
    table_bottom = 1180
    draw.line([60, table_top, 60, table_bottom], fill=(120, 120, 120), width=1)
    draw.line([500, table_top, 500, table_bottom], fill=(120, 120, 120), width=1)
    draw.line([650, table_top, 650, table_bottom], fill=(120, 120, 120), width=1)
    draw.line([790, table_top, 790, table_bottom], fill=(120, 120, 120), width=1)
    draw.line([940, table_top, 940, table_bottom], fill=(120, 120, 120), width=1)

    # Real tasks from Israel's sheet (Daily Times 10.07.26.PDF Page 1)
    sample_rows = [
        ("Put Equipment away", "7:30", "8:00", "Shop"),
        ("Run ABS indirect drain, air vent R.V.C., Gray water", "8:00", "10:45", "127"),
        ("Clamp ABS install Hood", "10:45", "12:00", "127"),
        ("Lunch", "12:00", "12:30", ""),
        ("Install Gas line", "12:30", "2:45", "127"),
        ("Prep puck lock", "2:45", "3:45", "127"),
        ("Load Metal y Aluminum organized", "3:45", "4:30", "127"),
        ("", "", "", ""),
        ("", "", "", ""),
        ("", "", "", "")
    ]

    row_h = 70
    for idx, (task, t_in, t_out, cart) in enumerate(sample_rows):
        cur_y = y + (idx * row_h)
        if cur_y + row_h > table_bottom:
            break
        
        # Horizontal row line
        draw.line([60, cur_y + row_h, 940, cur_y + row_h], fill=(180, 180, 180), width=1)

        # Row text
        if task:
            draw.text((75, cur_y + 22), task, fill=(20, 20, 20))
        if t_in:
            draw.text((545, cur_y + 22), t_in, fill=(20, 20, 20))
        if t_out:
            draw.text((695, cur_y + 22), t_out, fill=(20, 20, 20))
        if cart:
            draw.text((835, cur_y + 22), cart, fill=(20, 20, 20))

    img.save(output_path, "PNG")
    print(f"Sample test timesheet generated at: {output_path}")

def run_test():
    test_img_path = config.SCANS_DIR / "sample_test_timesheet.png"
    create_sample_timesheet_image(test_img_path)

    print("\n--- Running OCR Extraction ---")
    result = ocr_engine.process_document_ocr(str(test_img_path))
    print(f"Status: {result['status']}")
    print(f"Worker Name: {result.get('worker_name')}")
    print(f"Date: {result.get('date')}")
    print(f"Extracted Rows Count: {len(result.get('rows', []))}")
    for idx, r in enumerate(result.get('rows', []), 1):
        print(f"  [{idx}] {r.get('cart_id')} | {r.get('task')} | {r.get('time_in')} -> {r.get('time_out')} ({r.get('duration')}) | Code: {r.get('code')}")

    print("\n--- Testing Storage Commit (Multi-Tab Excel & CSV) ---")
    save_res = storage.save_submission({
        "source": "Sample Test",
        "worker_name": result.get("worker_name", "Israel"),
        "date": result.get("date", "10/07/26"),
        "rows": result.get("rows", []),
        "image_name": "sample_test_timesheet.png"
    })
    print("Storage Result:", save_res)

    print("\n--- Checking Cart Data for FC127 ---")
    cart_data = storage.get_cart_data("FC127")
    print(f"FC127 Total Time: {cart_data.get('total_time')}, Rows: {len(cart_data.get('rows', []))}")

if __name__ == "__main__":
    run_test()
