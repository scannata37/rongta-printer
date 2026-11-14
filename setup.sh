#!/usr/bin/env bash
# One-time setup: register your USB receipt printer with macOS as "Receipt".
#
#   ./setup.sh            # auto-detect the printer
#   ./setup.sh MyPrinter  # use a different queue name
#
# Why the Generic driver? Recent macOS refuses "raw" printer queues
# ("Raw queues are no longer supported"). So we register the printer with
# Apple's built-in Generic driver, and the app sends each job with
# `lp -o raw`, which skips that driver. The printer gets our ESC/POS bytes untouched.
set -euo pipefail

NAME="${1:-Receipt}"
GENERIC_PPD="/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Resources/Generic.ppd"

echo "Looking for a USB printer… (make sure it's plugged in and switched on)"
URIS=$(lpinfo -v 2>/dev/null | awk '/usb:\/\//{print $2}' || true)

if [ -z "$URIS" ]; then
  echo "✗ No USB printer found. Check the cable, turn the printer on, and try again."
  exit 1
fi

COUNT=$(echo "$URIS" | wc -l | tr -d ' ')
if [ "$COUNT" -eq 1 ]; then
  URI="$URIS"
else
  echo "Found more than one USB printer:"
  i=1; while read -r u; do echo "  $i) $u"; i=$((i+1)); done <<< "$URIS"
  read -rp "Which one is the receipt printer? [1-$COUNT] " PICK
  URI=$(echo "$URIS" | sed -n "${PICK}p")
fi
echo "→ Using $URI"

if lpstat -p "$NAME" >/dev/null 2>&1; then
  echo "→ Replacing existing printer queue \"$NAME\""
  lpadmin -x "$NAME"
fi

if [ -f "$GENERIC_PPD" ]; then
  lpadmin -p "$NAME" -E -v "$URI" -P "$GENERIC_PPD" 2>&1 | grep -v "deprecated" || true
else
  lpadmin -p "$NAME" -E -v "$URI" -m raw
fi

if lpstat -p "$NAME" >/dev/null 2>&1; then
  echo "✓ Printer \"$NAME\" is set up."
  read -rp "Print a test slip? [Y/n] " T
  if [[ ! "$T" =~ ^[Nn] ]]; then
    printf '\x1b@\x1ba\x01\x1d!\x11IT WORKS\x1d!\x00\n\nReceipt Printer is set up.\n\n\n\n\n\x1dV\x00' | lp -d "$NAME" -o raw
  fi
  echo
  echo "Next: python3 app.py"
else
  echo "✗ Something went wrong registering the printer."
  exit 1
fi
