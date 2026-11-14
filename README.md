# Rongta Printer 🧾

A tiny local web app for printing to a Rongta 80mm thermal receipt printer from a Mac.

Dictate (e.g. with Wispr Flow), check the list, hit **Print**. There are three modes:

| Mode | Say something like… | Prints |
|---|---|---|
| 🛒 **Shopping list** | "Going to Trader Joe's. My list is bananas, milk and mac and cheese." | Checklist grouped by aisle, with the store name |
| ✅ **To-do** | "Today I need to call the bank, it's urgent, finish my resume and call mom and dad." | Checklist with a PRIORITY section first |
| 🏋️ **Gym** | "Push day. Bench 3 sets of 8 at 185, tricep pushdowns 3 by 12, 20 minutes on the treadmill." | Workout card with a box and a blank for every set |

### Presets (less typing)

- **Gym:** one tap loads a full **Push**, **Pull** or **Legs** day (a classic 3-day split). You can also just say "today's push". Below that, **Add exercises** has about 50 common lifts, core moves and cardio grouped by muscle. Tap to add, tap again to remove.
- **To-do:** **Daily essentials** (walk 10,000 steps, study AI tools for 2 hours, read, plan tomorrow…), **Deep work day** and **Reset day** routines, plus **Add common tasks** grouped into Health, Learning, Focus, Career and Home. Say "my daily routine" to load it by voice.
- All presets live in **`receipt/presets.py`**, which is plain data. Edit it to make them yours.

Shopping example:

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

Your browser opens at <http://localhost:8787>. Pick a mode, click the text box, dictate, check the list, and print. <kbd>⌘</kbd>+<kbd>Enter</kbd> also prints. Each mode keeps its own list, so you can switch tabs without losing anything.

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
- **`receipt/todo.py`** strips "I need to / gotta / remember to", marks a task as priority when you say "urgent", "important" or "top priority", and keeps "call mom and dad" as one task. (A one-word piece after "and" gets glued back onto the task before it.)
- **`receipt/presets.py`** holds the built-in routines and pick-lists. The UI gets them from `GET /api/presets`, and the parsers use them for voice shortcuts. "Today's push" always loads the preset. "Push day" loads it only if you didn't list your own exercises; otherwise it just becomes the title.
- **`receipt/gym.py`** pulls out sets × reps ("3 sets of 8", "3x8", "three by eight"), weight ("at 185", "with 60s", "100 kg") and time ("20 minutes", "1 mile"). Whatever words are left become the exercise name. "Push day", "leg day" and so on become the card title.
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
- [x] To-do list
- [x] Gym workout card
- [x] Presets: Push/Pull/Legs, daily to-do routines, pick-to-add libraries
- [ ] Use from your phone
- [ ] "Print folder" so Claude can drop a file and have it print automatically
