"""Small text helpers shared by the To-do and Gym parsers."""
from __future__ import annotations

import datetime as dt
import re
from typing import List, Optional

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "twenty-five": 25, "thirty": 30, "forty": 40,
    "forty-five": 45, "fifty": 50, "sixty": 60,
}


def words_to_digits(text: str) -> str:
    """'three sets of ten' -> '3 sets of 10' (dictation sometimes spells numbers)."""
    for word in sorted(NUMBER_WORDS, key=len, reverse=True):
        text = re.sub(r"\b%s\b" % re.escape(word), str(NUMBER_WORDS[word]), text, flags=re.I)
    return text


def split_chunks(text: str, protected: Optional[List[str]] = None,
                 split_and: bool = True) -> List[str]:
    """Split on commas, semicolons, new lines, sentence ends and 'and'/'then'.

    Phrases in `protected` (e.g. "mac and cheese") are never split.
    """
    protected = protected or []
    for i, phrase in enumerate(protected):
        text = re.sub(re.escape(phrase), "\x00%d\x00" % i, text, flags=re.I)
    pattern = r"[,;\n•]|\.(?=\s|$)"
    if split_and:
        pattern += r"|\s+(?:and|&|plus|then|after that)\s+"
    parts = re.split(pattern, text, flags=re.I)
    restored = [re.sub(r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], p) for p in parts]
    return [p.strip() for p in restored if p and p.strip()]


def strip_lead(text: str, fillers: str) -> str:
    """Repeatedly remove leading filler words: 'and also I need to call' -> 'call'."""
    prev = None
    s = text.strip(" \t-*•.,;:!?\"")
    while prev != s:
        prev = s
        s = re.sub(r"^(?:%s)\b[\s,:]*" % fillers, "", s, flags=re.I).strip(" ,.")
    return s


def capitalize(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def date_line(now: Optional[dt.datetime] = None) -> str:
    now = now or dt.datetime.now()
    hour = now.strftime("%I").lstrip("0") or "12"
    return now.strftime("%a, %b ") + str(now.day) + "  " + hour + now.strftime(":%M %p")
