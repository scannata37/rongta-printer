"""Shopping list: turn dictated speech into a clean, printable list.

Example input (straight out of Wispr Flow):
    "I'm going to Trader Joe's. This is my list: bananas, apples,
     a gallon of milk, some eggs and mac and cheese."
Parsed result:
    store = "Trader Joe's"
    items = ["Bananas", "Apples", "Gallon of milk", "Eggs", "Mac and cheese"]

This is rule-based on purpose (no AI, no internet): predictable and free.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Dict, List, Optional, Tuple

from .slip import Slip

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

GENERIC_STORES = {"store", "the store", "grocery store", "the grocery store",
                  "supermarket", "market", "grocery", "groceries", "shop", "shopping"}

# Phrases that contain "and" but are one item.
PROTECTED = ["mac and cheese", "macaroni and cheese", "half and half",
             "salt and pepper", "peanut butter and jelly", "bread and butter",
             "fish and chips", "chips and salsa", "sweet and sour", "rice and beans"]

LEAD_FILLERS = r"(?:and|also|plus|then|oh|um|uh|like|maybe|okay|ok|so|"\
               r"i need|we need|i want|i gotta|need|gotta|have to|to|get|grab|pick up|buy|"\
               r"some|a couple of|"\
               r"a couple|a few|a|an|the)\b"
TRAIL_FILLERS = r"\b(?:too|as well|please|i think|and stuff|and that's it|that's it|"\
                r"that is it|i guess)$"

INTRO_RE = re.compile(
    r"(going to|headed to|heading to|this is my list|here'?s my list|my list|"
    r"shopping list|grocery list|i'?m going|i am going|let'?s see|that'?s it|"
    r"that is it|that'?s all|that is all)", re.I)

LIST_MARKER_RE = re.compile(
    r"(?:my list|the list|list is|list|i need|we need|need to get|need to grab|pick up)"
    r"\s*(?:is|are)?\s*[:\-]", re.I)

STORE_RE = re.compile(
    r"\b(?:going|headed|heading|off|stopping)\s+(?:over\s+)?to\s+(?:the\s+)?"
    r"([A-Za-z0-9'&\.\- ]{2,40}?)(?=[\.,!?:;\n]|\s+(?:and|to|for|this|my|i|we)\b|$)",
    re.I)


def _clean_item(chunk: str) -> str:
    s = chunk.strip(" \t\r\n-*•.,;:!?\"")
    # strip leading filler words repeatedly ("and also some eggs" -> "eggs")
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"^" + LEAD_FILLERS + r"\s*", "", s, flags=re.I).strip()
        s = re.sub(r"\s*" + TRAIL_FILLERS, "", s, flags=re.I).strip(" ,.")
    return s[:1].upper() + s[1:] if s else ""


def extract_store(text: str) -> Optional[str]:
    m = STORE_RE.search(text)
    if not m:
        return None
    name = m.group(1).strip(" .'")
    if name.lower() in GENERIC_STORES or len(name) < 2:
        return None
    # "trader joe's" -> "Trader Joe's"; keep user's casing if they used caps
    if name.islower():
        name = " ".join(w[:1].upper() + w[1:] for w in name.split())
    return name


def parse(text: str) -> Tuple[Optional[str], List[str]]:
    """Return (store, items) from free-form dictated text."""
    text = (text or "").strip()
    if not text:
        return None, []
    store = extract_store(text)

    # If they said "my list is: ..." / "...:" keep only what comes after.
    body = text
    markers = list(LIST_MARKER_RE.finditer(text))
    if markers:
        body = text[markers[-1].end():]
    elif ":" in text:
        body = text.rsplit(":", 1)[1]

    # Protect multi-word items containing "and".
    for i, phrase in enumerate(PROTECTED):
        body = re.sub(re.escape(phrase), "\x00%d\x00" % i, body, flags=re.I)

    chunks = re.split(r"[,;\n•]|\.(?=\s|$)|\s+(?:and|&|plus)\s+", body, flags=re.I)

    items: List[str] = []
    seen = set()
    for chunk in chunks:
        chunk = re.sub(r"\x00(\d+)\x00", lambda m: PROTECTED[int(m.group(1))], chunk)
        if not chunk.strip():
            continue
        # Drop chatter like "I'm going to the store" that has no item in it.
        if INTRO_RE.search(chunk) and not markers and ":" not in text:
            continue
        item = _clean_item(chunk)
        if not item or len(item) > 60:
            continue
        key = item.lower()
        if key not in seen:
            seen.add(key)
            items.append(item)
    return store, items


# ---------------------------------------------------------------------------
# Grouping by aisle (store-walk order)
# ---------------------------------------------------------------------------

AISLES: List[Tuple[str, List[str]]] = [
    ("Produce", ["apple", "banana", "orange", "lemon", "lime", "grape", "berry",
                 "strawberr", "blueberr", "raspberr", "avocado", "tomato", "potato",
                 "onion", "garlic", "lettuce", "spinach", "kale", "salad", "carrot",
                 "celery", "pepper", "cucumber", "broccoli", "cauliflower", "zucchini",
                 "mushroom", "corn", "pear", "peach", "plum", "melon", "watermelon",
                 "pineapple", "mango", "cilantro", "parsley", "basil", "ginger",
                 "herb", "fruit", "veggie", "vegetable", "squash", "cabbage", "asparagus"]),
    ("Bakery", ["bread", "bagel", "bun", "roll", "tortilla", "muffin", "croissant",
                "pita", "baguette", "cake", "donut", "english muffin"]),
    ("Meat & Seafood", ["chicken", "beef", "steak", "pork", "bacon", "sausage", "ham",
                        "turkey", "ground", "salmon", "tuna steak", "shrimp", "fish",
                        "lamb", "hot dog", "deli", "salami", "meatball"]),
    ("Dairy & Eggs", ["milk", "egg", "cheese", "butter", "yogurt", "yoghurt", "cream",
                      "half and half", "sour cream", "cottage", "creamer"]),
    ("Frozen", ["frozen", "ice cream", "pizza", "waffle", "popsicle", "ice"]),
    ("Pantry", ["rice", "pasta", "noodle", "cereal", "oat", "flour", "sugar", "salt",
                "oil", "vinegar", "sauce", "ketchup", "mustard", "mayo", "peanut butter",
                "jelly", "jam", "honey", "syrup", "soup", "bean", "can", "canned",
                "spice", "seasoning", "coffee", "tea", "mac and cheese", "broth",
                "tuna", "protein powder", "granola"]),
    ("Snacks & Drinks", ["chip", "cracker", "cookie", "pretzel", "popcorn", "nut",
                         "candy", "chocolate", "snack", "bar", "soda", "water",
                         "juice", "seltzer", "beer", "wine", "gatorade", "drink",
                         "energy", "kombucha", "salsa"]),
    ("Household", ["paper towel", "toilet paper", "napkin", "trash bag", "foil",
                   "plastic wrap", "ziploc", "detergent", "soap", "dish", "sponge",
                   "shampoo", "conditioner", "toothpaste", "deodorant", "razor",
                   "tissue", "battery", "batteries", "cleaner", "bleach", "wipes"]),
]
OTHER = "Other"


def aisle_for(item: str) -> str:
    low = item.lower()
    # Longest keyword wins, so "peanut butter" beats "butter".
    best, best_len = OTHER, 0
    for aisle, words in AISLES:
        for w in words:
            if re.search(r"\b" + re.escape(w), low) and len(w) > best_len:
                best, best_len = aisle, len(w)
    return best


def group(items: List[str]) -> List[Tuple[str, List[str]]]:
    buckets: Dict[str, List[str]] = {}
    for it in items:
        buckets.setdefault(aisle_for(it), []).append(it)
    order = [a for a, _ in AISLES] + [OTHER]
    return [(a, buckets[a]) for a in order if a in buckets]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def build_slip(items: List[str], store: Optional[str] = None,
               by_aisle: bool = True, now: Optional[dt.datetime] = None,
               size: str = "normal") -> Slip:
    now = now or dt.datetime.now()
    slip = Slip(size=size)
    slip.add("SHOPPING LIST", align="center", big=True, bold=True)
    if store:
        slip.add(store, align="center", bold=True)
    hour = now.strftime("%I").lstrip("0") or "12"
    slip.add(now.strftime("%a, %b ") + str(now.day) + "  " + hour + now.strftime(":%M %p"),
             align="center")
    slip.divider()

    sections = group(items) if by_aisle else [("", items)]
    for i, (name, its) in enumerate(sections):
        if name:
            if i:
                slip.blank()
            slip.add(name.upper(), bold=True)
        for it in its:
            slip.add("[ ] " + it, indent=4)

    slip.divider()
    n = len(items)
    slip.add("%d item%s" % (n, "" if n == 1 else "s"), align="center")
    return slip
