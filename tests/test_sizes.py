import unittest

from receipt import modes
from receipt.slip import Slip, size_cmd, to_ascii


class SizeTests(unittest.TestCase):
    def build(self, size):
        return modes.get("todo")["build"]({"title": "Today", "options": {"size": size},
                                           "items": [{"text": "x " * 40, "priority": False}]})

    def test_size_command_bytes(self):
        self.assertEqual(size_cmd(1, 1), b"\x1d!\x00")
        self.assertEqual(size_cmd(1, 2), b"\x1d!\x01")   # tall
        self.assertEqual(size_cmd(2, 2), b"\x1d!\x11")   # large
        self.assertEqual(size_cmd(3, 3), b"\x1d!\x22")   # huge

    def test_body_lines_use_the_chosen_size(self):
        self.assertIn(b"\x1d!\x01", self.build("tall").to_escpos())
        self.assertIn(b"\x1d!\x22", self.build("huge").to_escpos())

    def test_wrapping_shrinks_with_size(self):
        for size, cols in [("normal", 48), ("tall", 48), ("large", 24), ("huge", 16)]:
            for row in self.build(size).to_preview():
                limit = 48 // row["w"]
                self.assertLessEqual(len(row["text"]), limit, (size, row))
            self.assertEqual(Slip(size=size).width, cols)

    def test_unknown_size_falls_back_to_normal(self):
        self.assertEqual(Slip(size="gigantic").size, "normal")

    def test_control_characters_are_stripped(self):
        self.assertEqual(to_ascii("hi\x1d!\x11there"), "hi!there")


if __name__ == "__main__":
    unittest.main()
