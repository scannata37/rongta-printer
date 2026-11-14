"""Gym: dictated workout -> a card with a box per set to check off.

    "Push day. Bench press 3 sets of 8 at 185, incline dumbbell press 3x10
     with 60s, tricep pushdowns 3 by 12, and 20 minutes on the treadmill."
becomes
    PUSH DAY
    Bench press               3 x 8 @ 185 lb
    [ ] ____  [ ] ____  [ ] ____
    ...
The blanks are for writing what you actually lifted.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import List, Optional

from .presets import GYM_ROUTINES
from .slip import Slip
from .text import capitalize, date_line, split_chunks, strip_lead, words_to_digits

FILLERS = (r"add in|add|and|also|plus|then|oh|um|uh|so|okay|ok|alright|first|next|finally|"
           r"lastly|today|i'm doing|i am doing|i'm gonna do|i'm going to do|"
           r"i'm going to|i want to do|i want to|i'll do|i'll|let's do|"
           r"we're doing|doing|do|some|a few|a couple of|a|an|the|i|gonna")

TITLE_RE = re.compile(
    r"\b(push|pull|leg|legs|upper(?: body)?|lower(?: body)?|chest|back|arms?|"
    r"shoulders?|full[- ]body|cardio|core|abs|glutes?)\s+(day|workout)\b", re.I)

SETS_REPS_RE = re.compile(
    r"\b(\d+)\s*(?:x|×|by|sets? of|sets? x|times)\s*(\d+)(?:\s*reps?)?\b", re.I)
SETS_ONLY_RE = re.compile(r"\b(\d+)\s*sets?\b", re.I)
REPS_ONLY_RE = re.compile(r"\b(\d+)\s*reps?\b", re.I)
# After sets/reps/duration are pulled out, any number left is the weight:
# "at 185", "@ 60", "with 60s", "100 kg", or just "185".
WEIGHT_RE = re.compile(
    r"(?:(?:\bat|@|\bwith|\busing)\s*)?(\d+(?:\.\d+)?)\s*(lbs?\b|pounds?\b|kgs?\b|kilos?\b|s\b)?", re.I)
DURATION_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(min(?:ute)?s?|hours?|hrs?|miles?|mi|km|seconds?|secs?)\b", re.I)
# "Today's push", "it's pull day", "legs workout", "doing legs" -> load that preset.
PRESET_RE = re.compile(
    r"\b(?:(?:today'?s|today is|it'?s|doing|let'?s do|time for)\s+(push|pull|legs?)\b"
    r"(?:\s+(?:day|workout))?|(push|pull|legs?)\s+(?:day|workout)\b)", re.I)

# Words that mean a chunk is chatter, not an exercise.
SKIP_RE = re.compile(r"^(?:workout|that'?s it|that'?s all|done|warm ?up|add|also add|plus)$", re.I)


def _unit(u: Optional[str]) -> str:
    u = (u or "").lower()
    if u.startswith("k"):
        return "kg"
    return "lb"


def _duration_unit(u: str) -> str:
    u = u.lower()
    if u.startswith("h"):
        return "hr"
    if u.startswith("mi") and u not in ("min", "mins", "minute", "minutes"):
        return "mi"
    if u.startswith("km"):
        return "km"
    if u.startswith("s"):
        return "sec"
    return "min"


def parse_exercise(chunk: str) -> Optional[dict]:
    s = words_to_digits(chunk)
    ex = {"name": "", "sets": None, "reps": None, "weight": None, "unit": "lb", "duration": None}

    m = SETS_REPS_RE.search(s)
    if m:
        ex["sets"], ex["reps"] = int(m.group(1)), int(m.group(2))
        s = s[:m.start()] + " " + s[m.end():]
    else:
        m = SETS_ONLY_RE.search(s)
        if m:
            ex["sets"] = int(m.group(1)); s = s[:m.start()] + " " + s[m.end():]
        m = REPS_ONLY_RE.search(s)
        if m:
            ex["reps"] = int(m.group(1)); s = s[:m.start()] + " " + s[m.end():]

    m = DURATION_RE.search(s)
    if m:
        ex["duration"] = "%s %s" % (m.group(1), _duration_unit(m.group(2)))
        s = s[:m.start()] + " " + s[m.end():]

    m = WEIGHT_RE.search(s)
    if m:
        num = m.group(1)
        ex["weight"] = float(num) if "." in num else int(num)
        ex["unit"] = _unit(m.group(2))
        s = s[:m.start()] + " " + s[m.end():]

    # What's left is the exercise name.
    name = re.sub(r"\b(?:on the|on a|of|each side|each|per side|reps?|sets?|lbs?|pounds?|kgs?)\b", " ", s, flags=re.I)
    name = re.sub(r"\s{2,}", " ", name)
    name = strip_lead(name, FILLERS).strip(" ,.-")
    if not name or SKIP_RE.match(name) or len(name) > 50:
        return None
    ex["name"] = capitalize(name)
    return ex


def parse(text: str) -> dict:
    """Return {"title": str|None, "exercises": [...]}."""
    text = (text or "").strip()
    title = None
    preset: List[dict] = []
    m = PRESET_RE.search(text)
    if m:
        key = (m.group(1) or m.group(2)).lower()
        key = "legs" if key.startswith("leg") else key
        rest = text[:m.start()] + text[m.end():]
        rest_body = rest.split(":", 1)[1] if ":" in rest else rest
        said_exercises = any(parse_exercise(c) for c in split_chunks(rest_body))
        # "Today's push" always loads the preset. "Push day" only does when
        # nothing else was said; otherwise it's just the title of their own list.
        if m.group(1) or not said_exercises:
            routine = GYM_ROUTINES[key]
            title = routine["title"]
            preset = [dict(e) for e in routine["exercises"]]
            text = rest
    m = None if preset else TITLE_RE.search(text)
    if m:
        title = "%s %s" % (m.group(1), m.group(2))
        text = text[:m.start()] + text[m.end():]
    if ":" in text:
        text = text.split(":", 1)[1]

    # Preset first, then anything else they said ("today's push, add face pulls")
    exercises: List[dict] = list(preset)
    names = {e["name"].lower() for e in exercises}
    for chunk in split_chunks(text):
        ex = parse_exercise(chunk)
        if ex and ex["name"].lower() not in names:
            names.add(ex["name"].lower())
            exercises.append(ex)
    return {"title": capitalize(title) if title else None, "exercises": exercises}


def describe(ex: dict) -> str:
    """'3 x 8 @ 185 lb', '20 min', '3 sets', '' ..."""
    parts = []
    if ex.get("sets") and ex.get("reps"):
        parts.append("%s x %s" % (ex["sets"], ex["reps"]))
    elif ex.get("sets"):
        parts.append("%s sets" % ex["sets"])
    elif ex.get("reps"):
        parts.append("%s reps" % ex["reps"])
    if ex.get("weight") not in (None, ""):
        parts.append("@ %s %s" % (ex["weight"], ex.get("unit") or "lb"))
    if ex.get("duration"):
        parts.append(str(ex["duration"]))
    return " ".join(parts)


def build_slip(exercises: List[dict], title: Optional[str] = None,
               now: Optional[dt.datetime] = None) -> Slip:
    slip = Slip()
    slip.add((title or "WORKOUT").upper(), align="center", big=True, bold=True)
    slip.add(date_line(now), align="center")
    slip.divider()

    for i, ex in enumerate(exercises):
        if i:
            slip.blank()
        name, detail = ex.get("name", "").strip(), describe(ex)
        gap = slip.width - len(name) - len(detail)
        if detail and gap >= 2:
            slip.add(name + " " * gap + detail, bold=True)
        else:
            slip.add(name, bold=True)
            if detail:
                slip.add(detail)
        try:
            sets = int(ex.get("sets") or 0)
        except (TypeError, ValueError):
            sets = 0
        if sets > 0 and not ex.get("duration"):
            # one box + blank per set; 4 fit on a 48-char line
            boxes = ["[ ] ____  "] * min(sets, 12)
            for j in range(0, len(boxes), 4):
                slip.add("".join(boxes[j:j + 4]).rstrip())
        else:
            slip.add("[ ] done")

    slip.divider()
    slip.add("Notes: " + "_" * (slip.width - 7))
    slip.blank()
    slip.add("_" * slip.width)
    n = len(exercises)
    slip.blank()
    slip.add("%d exercise%s - go get it" % (n, "" if n == 1 else "s"), align="center")
    return slip
