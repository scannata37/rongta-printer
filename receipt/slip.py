"""A printer-agnostic description of a receipt slip.

A Slip is just an ordered list of lines, each with a few style flags.
The same Slip is rendered two ways:
  * to_escpos()  -> raw bytes the thermal printer understands
  * to_preview() -> JSON the web UI draws as an on-screen preview
Keeping one source of truth means the preview always matches the paper.

Text size
---------
ESC/POS printers scale text in whole steps only: width x1..x8 and height
x1..x8, set with the command GS ! n. A Slip has a `size` (normal / tall /
large / huge) that sets the scale of the body text; titles are always one
step bigger. Wider text means fewer characters per line, so the Slip's
`width` (characters per line) shrinks with it and everything wraps to fit.
"""
from __future__ import annotations

import textwrap
import unicodedata
from typing import List, Tuple

# Font A on an 80mm printer fits 48 characters per line at normal size.
PAPER_COLS = 48
DEFAULT_WIDTH = PAPER_COLS

# size name -> (body (width, height), title (width, height))
SIZES = {
    "normal": ((1, 1), (2, 2)),
    "tall":   ((1, 2), (2, 2)),   # taller letters, same number per line
    "large":  ((2, 2), (3, 3)),   # 2x everything: 24 characters per line
    "huge":   ((3, 3), (4, 4)),   # 3x: 16 characters per line
}

# --- ESC/POS command bytes -------------------------------------------------
ESC = b"\x1b"
GS = b"\x1d"
INIT = ESC + b"@"                    # reset printer to defaults
ALIGN = {"left": ESC + b"a\x00", "center": ESC + b"a\x01", "right": ESC + b"a\x02"}
BOLD_ON, BOLD_OFF = ESC + b"E\x01", ESC + b"E\x00"
CUT = GS + b"V\x00"                  # full cut


def size_cmd(w: int, h: int) -> bytes:
    """GS ! n: high nibble = width - 1, low nibble = height - 1."""
    return GS + b"!" + bytes([((w - 1) << 4) | (h - 1)])


SIZE_NORMAL = size_cmd(1, 1)          # GS ! 0x00
SIZE_DOUBLE = size_cmd(2, 2)          # GS ! 0x11

_SMART = {"‘": "'", "’": "'", "“": '"', "”": '"',
          "–": "-", "—": "-", "…": "...", " ": " "}


def to_ascii(text: str) -> str:
    """Thermal printers use old 8-bit code pages; stick to plain ASCII.
    Control characters are dropped so text can't sneak in printer commands."""
    for k, v in _SMART.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in text if ch >= " " or ch == "\t")


class Line:
    def __init__(self, text: str = "", align: str = "left", bold: bool = False,
                 big: bool = False, indent: int = 0, fill: str = ""):
        self.text = to_ascii(text)
        self.align = align
        self.bold = bold
        self.big = big        # title-sized
        self.indent = indent  # hanging indent for wrapped continuation lines
        self.fill = fill      # repeat this character across the full line (dividers)


class Slip:
    def __init__(self, width: int = DEFAULT_WIDTH, size: str = "normal"):
        self.size = size if size in SIZES else "normal"
        self.body_scale, self.title_scale = SIZES[self.size]
        # characters per line for body text at this size
        self.width = max(8, width // self.body_scale[0])
        self.paper_cols = width
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
        self.lines.append(Line("", fill=char))
        return self

    # -- layout --------------------------------------------------------------
    def scale_of(self, line: Line) -> Tuple[int, int]:
        return self.title_scale if line.big else self.body_scale

    def cols_of(self, line: Line) -> int:
        return max(4, self.paper_cols // self.scale_of(line)[0])

    def _wrapped(self, line: Line) -> List[str]:
        """Split one logical line into physical printed lines."""
        cols = self.cols_of(line)
        if line.fill:
            return [line.fill * cols]
        if not line.text:
            return [""]
        return textwrap.wrap(line.text, width=cols,
                             subsequent_indent=" " * min(line.indent, cols // 3)) or [""]

    # -- renderers -------------------------------------------------------------
    def to_escpos(self, feed: int = 4, cut: bool = True) -> bytes:
        out = bytearray(INIT)
        for line in self.lines:
            out += ALIGN[line.align]
            out += BOLD_ON if line.bold else BOLD_OFF
            out += size_cmd(*self.scale_of(line))
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
            w, h = self.scale_of(line)
            for physical in self._wrapped(line):
                rows.append({"text": physical, "align": line.align, "bold": line.bold,
                             "big": line.big, "w": w, "h": h})
        return rows

    def to_text(self) -> str:
        """Plain-text approximation, handy for tests and the terminal."""
        out = []
        for row in self.to_preview():
            cols = max(4, self.paper_cols // row["w"])
            t = row["text"]
            if row["align"] == "center":
                t = t.center(cols).rstrip()
            elif row["align"] == "right":
                t = t.rjust(cols)
            out.append(t)
        return "\n".join(out)
