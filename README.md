# AFCR Timesheet Automation & Google Sheets Integration

Turnkey OCR scanning web application for **Affordable Food Cart Rentals (AFCR)** built for **Windows** and configured to stream data into **Google Sheets** and local Excel workbooks with dedicated Food Cart tabs (`FC121` through `FC130`, `Shop`, etc.).

---

## 🎯 What's New & Core Architecture

1. **Food Cart (FC) Tabbed Structure**:
   * Standardized across all 10+ trailer tabs (`FC121`, `FC122`, `FC123`, `FC124`, `FC125`, `FC126`, `FC127`, `FC128`, `FC129`, `FC130`, `Shop`).
   * Standard 9-Column Format matching `FC127`:
     `Name` | `Task` | `Category` | `Build / Reconditioning` | `Code` | `Date` | `Time In` | `Out` | `Task Total`
   * Automatic calculation of task duration (`Task Total`) and banner formula for total trailer hours (`=SUM(I3:I500)`).

2. **Google Sheets Live Sync**:
   * Direct synchronization with your Google Drive spreadsheet (`FC TIMES_ FC121-130`).
   * Automatically creates and updates cart tabs on Google Sheets as timesheets are submitted.
   * Visual connection badge and settings modal to configure Spreadsheet URL / Sheet ID and upload `google_credentials.json` directly from the web browser.

3. **Multi-Row OCR Extraction**:
   * Scans hand-filled daily sheets containing multiple task rows (e.g. from `Daily Times 10.07.26.PDF`).
   * Extracts worker name, date, checkboxes, and all individual task lines with Time In, Time Out, Cart #, and Task descriptions.
   * Auto-matches keywords to **MT (Manufacturing / Build)** codes (`F1-F11`, `S1-S13`, `I1-I11`, `R1-R5`, `H1-H11`, `P1-P9`, `E1-E9`, `G1-G7`, `X1-X8`, `Q1-Q5`, `L1-L8`) and **RT (Reconditioning)** codes (`C1-C23`, `M1-M38`).

4. **Interactive Manager Hub on Windows**:
   * Switch between trailer tabs (`FC121` .. `FC130`, `Shop`, `All Audit Log`) right in your browser.
   * Live search and filtering by worker name, task, category, or code.
   * Interactive multi-row verification modal with image preview, code autocomplete, duration recalculation, and one-click submission.
   * Quick "Run Sample Scan (FC127)" button to instantly test with real timesheet data.

---

## 🚀 Quick Start on Windows

1. Double-click `run.bat` (or use the desktop shortcut).
2. The launcher automatically validates dependencies (`gspread`, `openpyxl`, `rapidocr-onnxruntime`), starts the local server, and opens the **Manager Hub** at `http://localhost:5000/manager`.
3. *(Optional)* To create a desktop icon at any time, run `create_desktop_shortcut.bat`.

---

## 📊 Google Sheets Setup (Zero-Friction)

1. Open the **Manager Hub** and click **"Google Sheets Config"** in the top toolbar.
2. Paste your Google Sheet URL (or Spreadsheet ID) from Google Drive.
3. Click **"Upload google_credentials.json"** to select your service account key file.
4. Click **"Test Connection"** to verify connection to your spreadsheet and see active tabs.
5. All future timesheet entries will stream automatically into both Google Sheets and your desktop `FC TIMES_ FC121-130.xlsx` file!

---

## 📁 Storage Locations on Windows

* **Excel Workbook:** `Desktop/AFCR_Scans/FC TIMES_ FC121-130.xlsx`
* **CSV Audit Log:** `Desktop/AFCR_Scans/afcr_timesheet_log.csv`
* **Scanned Photos:** `Desktop/AFCR_Scans/Images/`
* **Codes Reference:** `codes.json`
