# Rongta Printer 🧾

A tiny local web app for printing to a Rongta 80mm thermal receipt printer from a Mac.

Dictate a shopping list (e.g. with Wispr Flow) and it becomes a clean list grouped by aisle. Then hit **Print**.

> "I'm going to Trader Joe's. This is my list: bananas, apples, a gallon of milk, some eggs and mac and cheese."

becomes:

```
     SHOPPING LIST
      Trader Joe's
  Fri, Nov 13  9:05 PM
------------------------
PRODUCE
[ ] Bananas
[ ] Apples

DAIRY & EGGS
[ ] Gallon of milk
[ ] Eggs

PANTRY
[ ] Mac and cheese
------------------------
        5 items
```

No dependencies: it's just Python 3 (already on your Mac) and the built-in print system.

## Setup (once)

1. Plug the printer in over USB and switch it on.
2. Run these commands:
   ```bash
   git clone https://github.com/scannata37/rongta-printer.git
   cd rongta-printer
   ./setup.sh          # finds the printer and registers it as "Receipt"
   ```

## Run

```bash
python3 app.py
```

Your browser opens at <http://localhost:8787>. Click the text box, dictate, check the list, and print. <kbd>⌘</kbd>+<kbd>Enter</kbd> also prints.

| Setting | How |
|---|---|
| Use a different printer queue name | `RECEIPT_PRINTER=MyPrinter python3 app.py` |
| Different port | `PORT=9000 python3 app.py` |
| Test without paper | `RECEIPT_DRY_RUN=1 python3 app.py` (writes bytes to `out/last_slip.bin`) |

## How it works

```
 browser UI  ──HTTP──▶  app.py (local server)  ──bytes──▶  lp -o raw  ──USB──▶  printer
 (static/index.html)     receipt/shopping.py              (macOS CUPS)
                         receipt/slip.py
```

- **`receipt/shopping.py`** parses dictation into items. It's rule-based: it splits on commas, "and" and new lines, drops filler words ("some", "uh", "I need to grab"), spots the store ("going to Market Basket"), and keeps phrases like "mac and cheese" together. It also sorts items into aisles in the order you'd walk the store.
- **`receipt/slip.py`** describes a slip as styled lines (centered, bold, big). The same object renders two ways: to **ESC/POS bytes** for the printer, and to **JSON** for the on-screen preview. So the preview always matches the paper.
- **`receipt/printer.py`** pipes the bytes to `lp -d Receipt -o raw`. `-o raw` tells macOS not to run the job through a driver, so the printer receives the ESC/POS commands untouched.
- **Why `setup.sh` uses Apple's Generic driver:** recent macOS refuses "raw" printer queues, so the queue gets a placeholder driver and every job bypasses it with `-o raw`.

### ESC/POS cheat sheet (what the bytes mean)

| Bytes | Meaning |
|---|---|
| `ESC @` | reset printer |
| `ESC a n` | align: 0 left, 1 center, 2 right |
| `ESC E n` | bold on/off |
| `GS ! 0x11` | double width + height (`0x00` = normal) |
| `GS V 0` | cut paper |

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

## Roadmap

- [x] Shopping list
- [ ] To-do list
- [ ] Gym workout card
- [ ] "Print folder" so Claude can drop a file and have it print automatically
