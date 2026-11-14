"""Send raw bytes to the thermal printer through macOS's print system (CUPS).

We hand the bytes to `lp -o raw`, which tells CUPS not to run them through
a driver. The printer itself interprets the ESC/POS commands.

Set RECEIPT_DRY_RUN=1 to write slips to ./out/ instead of printing.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

PRINTER_NAME = os.environ.get("RECEIPT_PRINTER", "Receipt")
DRY_RUN = os.environ.get("RECEIPT_DRY_RUN") == "1"
OUT_DIR = Path(__file__).resolve().parent.parent / "out"


class PrintError(Exception):
    pass


def status() -> dict:
    """Is the CUPS queue there and enabled?"""
    if DRY_RUN:
        return {"ok": True, "printer": PRINTER_NAME, "detail": "dry run (printing to ./out)"}
    try:
        r = subprocess.run(["lpstat", "-p", PRINTER_NAME],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "printer": PRINTER_NAME, "detail": str(e)}
    text = (r.stdout or r.stderr).strip()
    ok = r.returncode == 0 and "disabled" not in text
    return {"ok": ok, "printer": PRINTER_NAME, "detail": text or "not found — run ./setup.sh"}


def send(data: bytes) -> str:
    if DRY_RUN:
        OUT_DIR.mkdir(exist_ok=True)
        path = OUT_DIR / "last_slip.bin"
        path.write_bytes(data)
        return "dry run: wrote %d bytes to %s" % (len(data), path)
    try:
        r = subprocess.run(["lp", "-d", PRINTER_NAME, "-o", "raw"],
                           input=data, capture_output=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise PrintError(str(e))
    if r.returncode != 0:
        raise PrintError(r.stderr.decode(errors="replace").strip() or "lp failed")
    return r.stdout.decode(errors="replace").strip()
