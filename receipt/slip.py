"""A printer-agnostic description of a receipt slip.

A Slip is just an ordered list of lines, each with a few style flags.
The same Slip is rendered two ways:
  * to_escpos()  -> raw bytes the thermal printer understands
  * to_preview() -> JSON the web UI draws as an on-screen preview
Keeping one source of truth means the preview always matches the paper.
"""
from __future__ import annotations

import textwrap
import unicodedata
from typing import List, Optional

# Font A on an 80mm printer fits 48 characters per line.
# Double-width text fits half as many.
DEFAULT_WIDTH = 48

# --- ESC/POS command bytes -------------------------------------------------
ESC = b"\x1b"
GS = b"\x1d"
INIT = ESC + b"@"                    # reset printer to defaults
ALIGN = {"left": ESC + b"a\x00", "center": ESC + b"a\x01", "right": ESC + b"a\x02"}
BOLD_ON, BOLD_OFF = ESC + b"E\x01", ESC + b"E\x00"
SIZE_NORMAL = GS + b"!\x00"
SIZE_DOUBLE = GS + b"!\x11"          # double width + double height
CUT = GS + b"V\x00"                  # full cut

_SMART = {"‘": "'", "’": "'", "“": '"', "”": '"',
          "–": "-", "—": "-", "…": "...", " ": " "}


def to_ascii(text: str) -> str:
    """Thermal printers use old 8-bit code pages; stick to plain ASCII."""
    for k, v in _SMART.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


class Line:
    def __init__(self, text: str = "", align: str = "left", bold: bool = False,
                 big: bool = False, indent: int = 0):
        self.text = to_ascii(text)
        self.align = align
        self.bold = bold
        self.big = big
        self.indent = indent  # hanging indent for wrapped continuation lines


class Slip:
    def __init__(self, width: int = DEFAULT_WIDTH):
        self.width = width
        self.lines: List[Line] = []

    # -- building helpers --------------------------------------------------
    def add(self, text: str = "", **style) -> "Slip":
        self.lines.append(Line(text, **style))
        return self

    def blank(self, n: int = 1) -> "Slip":
        for _ in range(n):
            self.add("")
        return self

    def divider(self, char: str = "-") -> "Slip":
        return self.add(char * self.width)

    # -- layout --------------------------------------------------------------
    def _wrapped(self, line: Line) -> List[str]:
        """Split one logical line into physical printed lines."""
        cols = self.width // 2 if line.big else self.width
        if not line.text:
            return [""]
        return textwrap.wrap(line.text, width=cols,
                             subsequent_indent=" " * line.indent) or [""]

    # -- renderers -------------------------------------------------------------
    def to_escpos(self, feed: int = 4, cut: bool = True) -> bytes:
        out = bytearray(INIT)
        for line in self.lines:
            out += ALIGN[line.align]
            out += BOLD_ON if line.bold else BOLD_OFF
            out += SIZE_DOUBLE if line.big else SIZE_NORMAL
            for physical in self._wrapped(line):
                out += physical.encode("ascii") + b"\n"
        out += SIZE_NORMAL + BOLD_OFF + ALIGN["left"]
        out += b"\n" * feed  # push the last line past the cutter
        if cut:
            out += CUT
        return bytes(out)

    def to_preview(self) -> List[dict]:
        rows = []
        for line in self.lines:
            for physical in self._wrapped(line):
                rows.append({"text": physical, "align": line.align,
                             "bold": line.bold, "big": line.big})
        return rows

    def to_text(self) -> str:
        """Plain-text approximation, handy for tests and the terminal."""
        out = []
        for row in self.to_preview():
            cols = self.width // 2 if row["big"] else self.width
            t = row["text"]
            if row["align"] == "center":
                t = t.center(cols).rstrip()
            out.append(t)
        return "\n".join(out)
