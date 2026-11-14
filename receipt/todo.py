"""To-do list: dictated tasks -> checklist, with priorities printed first.

    "Today I need to call the bank, it's urgent, finish my resume,
     go to the gym and call mom and dad."
becomes
    PRIORITY  [ ] Call the bank
              [ ] Finish my resume
              [ ] Go to the gym
              [ ] Call mom and dad
"""
from __future__ import annotations

import datetime as dt
import re
from typing import List, Optional

from .presets import TODO_ROUTINES
from .slip import Slip
from .text import capitalize, date_line, split_chunks, strip_lead

FILLERS = (r"and|also|plus|then|oh|um|uh|so|okay|ok|alright|first|first thing|"
           r"second|next|finally|lastly|today|tonight|tomorrow|this morning|"
           r"this afternoon|i need to|i have to|i've got to|i gotta|i should|"
           r"i want to|i'd like to|i'm going to|i am going to|need to|have to|"
           r"got to|gotta|should|remember to|don't forget to|make sure to|"
           r"make sure i|i also|is|are|i|to")

PRIORITY_RE = re.compile(
    r"\b(?:it'?s |that'?s |this is |is )?(?:super |really |very )?"
    r"(?:urgent|asap|a priority|top priority|priority|important|first thing)\b", re.I)

INTRO_RE = re.compile(r"^(?:my |the )?(?:to[- ]?do|todo|task)s?(?: list)?(?: for .*| is| are)?$|"
                      r"^here'?s (?:my|the) list$|^that'?s (?:it|all)$", re.I)


ROUTINE_RE = re.compile(
    r"\b(?:my |the )?(daily (?:routine|habits|essentials)|deep work day|focus day|reset day)\b", re.I)


def parse(text: str) -> dict:
    """Return {"items": [{"text": str, "priority": bool}, ...]}."""
    text = (text or "").strip()
    preset: List[dict] = []
    m = ROUTINE_RE.search(text)
    if m:
        phrase = m.group(1).lower()
        key = "daily" if phrase.startswith("daily") else ("reset" if "reset" in phrase else "deep")
        preset = [dict(t) for t in TODO_ROUTINES[key]["items"]]
        text = text[:m.start()] + text[m.end():]
    head, sep, tail = text.partition(":")
    # "My to-do list for today: ..." -> keep what follows the colon
    if sep and re.search(r"\b(?:list|to[- ]?do|todo|tasks?|plan)\b", head, re.I):
        text = tail
    # Split on commas/periods first, then on "and"/"then" inside each piece.
    # A one-word piece after "and" belongs to the task before it
    # ("call mom and dad"), so glue it back on.
    chunks: List[str] = []
    for piece in split_chunks(text, split_and=False):
        subs = [x for x in re.split(r"\s+(?:and|&|then|after that)\s+", piece, flags=re.I) if x.strip()]
        for k, c in enumerate(subs):
            if k and len(c.split()) == 1 and not PRIORITY_RE.fullmatch(c.strip()):
                chunks[-1] += " and " + c
            else:
                chunks.append(c)

    items: List[dict] = list(preset)
    seen = {i["text"].lower() for i in items}
    for chunk in chunks:
        is_priority = bool(PRIORITY_RE.search(chunk))
        cleaned = PRIORITY_RE.sub("", chunk)
        cleaned = strip_lead(re.sub(r"\s{2,}", " ", cleaned), FILLERS)
        if not cleaned:
            # "it's urgent" on its own refers to the task before it
            if is_priority and items:
                items[-1]["priority"] = True
            continue
        if INTRO_RE.match(cleaned) or len(cleaned) > 80:
            continue
        task = capitalize(cleaned)
        if task.lower() in seen:
            continue
        seen.add(task.lower())
        items.append({"text": task, "priority": is_priority})
    return {"items": items}


def build_slip(items: List[dict], title: Optional[str] = None,
               now: Optional[dt.datetime] = None, size: str = "normal") -> Slip:
    slip = Slip(size=size)
    slip.add((title or "TO-DO").upper(), align="center", big=True, bold=True)
    slip.add(date_line(now), align="center")
    slip.divider()

    def line(it: dict, bold: bool = False):
        if it.get("blank"):
            # an empty line to fill in by hand
            prefix = ("%d. " % it["num"]) if it.get("num") else "[ ] "
            slip.add(prefix + "_" * (slip.width - len(prefix)))
            slip.blank()
        else:
            slip.add("[ ] " + it["text"], bold=bold, indent=4)

    if any(it.get("section") for it in items):
        # Template sheets (1-3-5, Ivy Lee): print each section in order.
        first, current = True, None
        for it in items:
            sec = it.get("section")
            if first or sec != current:
                if not first and slip.lines[-1].text:
                    slip.blank()
                first = False
                if sec:
                    slip.add(sec, bold=True)
                current = sec
            line(it, bold=bool(it.get("priority")))
    else:
        top = [i for i in items if i.get("priority")]
        rest = [i for i in items if not i.get("priority")]
        if top:
            slip.add("PRIORITY", bold=True)
            for it in top:
                line(it, bold=True)
            if rest:
                slip.blank()
                slip.add("EVERYTHING ELSE", bold=True)
        for it in rest:
            line(it)

    slip.divider()
    real = [i for i in items if not i.get("blank")]
    if real:
        n = len(real)
        slip.add("%d task%s - you got this" % (n, "" if n == 1 else "s"), align="center")
    else:
        slip.add("Fill it in. Start at the top.", align="center")
    return slip
