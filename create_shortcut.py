import sys
import os
from pathlib import Path
import config

def create_desktop_shortcut():
    desktop_dir = config.get_desktop_dir()
    project_dir = Path(__file__).resolve().parent
    bat_target = project_dir / "run.bat"
    shortcut_path = desktop_dir / "AFCR Timesheet OCR.lnk"

    ico_path = project_dir / "static" / "images" / "afcr_logo.ico"
    icon_line = f"$Shortcut.IconLocation = '{ico_path}'" if ico_path.exists() else ""

    ps_script = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = '{bat_target}'
    $Shortcut.WorkingDirectory = '{project_dir}'
    $Shortcut.Description = 'AFCR Timesheet and Document OCR Web App'
    {icon_line}
    $Shortcut.Save()
    """
    
    ps_file = project_dir / "_temp_shortcut.ps1"
    try:
        ps_file.write_text(ps_script, encoding="utf-8")
        os.system(f'powershell -ExecutionPolicy Bypass -NoProfile -File "{ps_file}"')
    finally:
        if ps_file.exists():
            ps_file.unlink()

    if shortcut_path.exists():
        print(f"[SUCCESS] Shortcut created on Desktop: {shortcut_path}")
    else:
        # Also try standard Desktop just in case
        std_desktop = Path.home() / "Desktop" / "AFCR Timesheet OCR.lnk"
        print(f"[NOTICE] Check Desktop path: {shortcut_path}")

if __name__ == "__main__":
    create_desktop_shortcut()
