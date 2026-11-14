import datetime as dt
import unittest

from receipt.shopping import aisle_for, build_slip, parse
from receipt.slip import CUT, INIT


class ParseTests(unittest.TestCase):
    def test_store_and_list_marker(self):
        store, items = parse("I'm going to Trader Joe's. This is my list: bananas, apples, "
                             "a gallon of milk, some eggs and mac and cheese.")
        self.assertEqual(store, "Trader Joe's")
        self.assertEqual(items, ["Bananas", "Apples", "Gallon of milk", "Eggs", "Mac and cheese"])

    def test_generic_store_is_ignored(self):
        store, items = parse("I'm going to the store. I need bananas, chicken breast, and paper towels.")
        self.assertIsNone(store)
        self.assertEqual(items, ["Bananas", "Chicken breast", "Paper towels"])

    def test_rambling_speech(self):
        store, items = parse("Okay so I'm heading to Market Basket and I need to grab some "
                             "ground beef, tortillas, salsa, and uh sour cream too")
        self.assertEqual(store, "Market Basket")
        self.assertEqual(items, ["Ground beef", "Tortillas", "Salsa", "Sour cream"])

    def test_sentences_and_newlines(self):
        self.assertEqual(parse("Going to the grocery store. Bananas. Apples. Coffee. That's it.")[1],
                         ["Bananas", "Apples", "Coffee"])
        self.assertEqual(parse("milk\neggs\nmilk")[1], ["Milk", "Eggs"])

    def test_empty(self):
        self.assertEqual(parse(""), (None, []))


class AisleTests(unittest.TestCase):
    def test_longest_keyword_wins(self):
        self.assertEqual(aisle_for("Peanut butter"), "Pantry")
        self.assertEqual(aisle_for("Butter"), "Dairy & Eggs")
        self.assertEqual(aisle_for("Bananas"), "Produce")
        self.assertEqual(aisle_for("Lightbulbs"), "Other")


class SlipTests(unittest.TestCase):
    def test_escpos_bytes(self):
        slip = build_slip(["Bananas", "Café au lait"], "Trader Joe’s",
                          now=dt.datetime(2026, 11, 13, 21, 5))
        data = slip.to_escpos()
        self.assertTrue(data.startswith(INIT))
        self.assertTrue(data.endswith(CUT))
        data.decode("ascii")  # everything must be plain ASCII
        self.assertIn(b"Cafe au lait", data)
        self.assertIn(b"Trader Joe's", data)

    def test_long_item_wraps_within_width(self):
        slip = build_slip(["x " * 60])
        for row in slip.to_preview():
            limit = 24 if row["big"] else 48
            self.assertLessEqual(len(row["text"]), limit)


if __name__ == "__main__":
    unittest.main()
