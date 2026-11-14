# Slip 🧾 (Rongta receipt printer app)

A tiny local web app for printing to a Rongta 80mm thermal receipt printer from a Mac.

Dictate (e.g. with Wispr Flow), check the list, hit **Print**. There are three modes:

| Mode | Say something like… | Prints |
|---|---|---|
| 🛒 **Shopping list** | "Going to Trader Joe's. My list is bananas, milk and mac and cheese." | Checklist grouped by aisle, with the store name |
| ✅ **To-do** | "Today I need to call the bank, it's urgent, finish my resume and call mom and dad." | Checklist with a PRIORITY section first |
| 🏋️ **Gym** | "Push day. Bench 3 sets of 8 at 185, tricep pushdowns 3 by 12, 20 minutes on the treadmill." | Workout card with a box and a blank for every set |

### Point-and-click templates

Every tab starts with templates. Tap one and its items open as a checklist with everything **pre-ticked**. Untick what you're skipping, then **Print**, or choose **Edit as list** to tweak further.

| Tab | Templates | Why |
|---|---|---|
| 🏋️ Gym | **Push · Pull · Legs**, each with an **A (strength)** and **B (volume)** day | The standard 6-day PPL layout. A days lead with heavy compound lifts at 5-8 reps and 2-3 min rest; B days use different angles at 8-15 reps and 60-90 s rest. Each card prints rep *ranges*, rest times, and the rule "hit the top of the range on every set → add weight next time." |
| ✅ To-do | **Daily essentials**, **1-3-5 day**, **Ivy Lee six**, **Deep work day**, **Reset day** | 1-3-5 = one big task, three medium, five small. Ivy Lee = six tasks written the night before, done in order. Those two print as **blank fill-in sheets** for a pen. |
| 🛒 Shopping | **Weekly staples**, **High-protein**, **Quick run** | Common baskets. Untick what's already in the fridge. |

Under **Build your own**, every tab also has a tap-to-add library: about 50 exercises by muscle, tasks grouped into Health / Learning / Focus / Career / Home, and about 70 groceries by aisle.

Voice shortcuts still work: "today's push", "today's legs", "my daily routine".

All of it lives in **`receipt/presets.py`** as plain data, with the reasoning written at the top. Edit it to make it yours.

### Three looks

Switch in the top-right corner (your choice is remembered):
- **Studio:** clean and light, with color used only to mean something (orange push, blue pull, purple legs)
- **Night:** dark gym-app style with a lime accent
- **Receipt:** black-and-white monospace that matches the paper

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
- [x] Point-and-click templates: PPL A/B, 1-3-5, Ivy Lee, grocery baskets
- [x] Three switchable designs
- [ ] Use from your phone
- [ ] "Print folder" so Claude can drop a file and have it print automatically
