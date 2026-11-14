import unittest

from receipt import gym, modes, todo


class TodoTests(unittest.TestCase):
    def test_priority_and_and_gluing(self):
        r = todo.parse("Today I need to call the bank, it's urgent, finish my resume, "
                       "go to the gym and call mom and dad.")
        self.assertEqual([i["text"] for i in r["items"]],
                         ["Call the bank", "Finish my resume", "Go to the gym", "Call mom and dad"])
        self.assertEqual([i["priority"] for i in r["items"]], [True, False, False, False])

    def test_list_intro_and_top_priority(self):
        r = todo.parse("My to-do list for Saturday: mow the lawn, fix the fence, groceries. "
                       "Top priority is the tax forms.")
        self.assertEqual([i["text"] for i in r["items"]],
                         ["Mow the lawn", "Fix the fence", "Groceries", "The tax forms"])
        self.assertTrue(r["items"][-1]["priority"])

    def test_colon_that_is_not_an_intro(self):
        r = todo.parse("Also important: pay the electric bill")
        self.assertEqual(r["items"], [{"text": "Pay the electric bill", "priority": True}])

    def test_slip_puts_priority_first(self):
        text = todo.build_slip([{"text": "B", "priority": False},
                                {"text": "A", "priority": True}]).to_text()
        self.assertLess(text.index("[ ] A"), text.index("[ ] B"))


class GymTests(unittest.TestCase):
    def test_full_workout(self):
        r = gym.parse("Push day. Bench press 3 sets of 8 at 185, incline dumbbell press 3x10 "
                      "with 60s, tricep pushdowns three by twelve, and 20 minutes on the treadmill.")
        self.assertEqual(r["title"], "Push day")
        ex = {e["name"]: e for e in r["exercises"]}
        self.assertEqual(list(ex), ["Bench press", "Incline dumbbell press",
                                    "Tricep pushdowns", "Treadmill"])
        self.assertEqual((ex["Bench press"]["sets"], ex["Bench press"]["reps"],
                          ex["Bench press"]["weight"]), (3, 8, 185))
        self.assertEqual(ex["Incline dumbbell press"]["weight"], 60)
        self.assertEqual((ex["Tricep pushdowns"]["sets"], ex["Tricep pushdowns"]["reps"]), (3, 12))
        self.assertEqual(ex["Treadmill"]["duration"], "20 min")

    def test_kg_and_sets_only(self):
        r = gym.parse("Leg day: leg press 4 by 12 at 100 kg, walking lunges 3 sets")
        lp, lunges = r["exercises"]
        self.assertEqual((lp["weight"], lp["unit"]), (100, "kg"))
        self.assertEqual((lunges["sets"], lunges["reps"]), (3, None))

    def test_one_box_per_set(self):
        text = gym.build_slip([{"name": "Squat", "sets": 5, "reps": 5, "weight": 225}]).to_text()
        self.assertEqual(text.count("[ ] ____"), 5)
        self.assertIn("5 x 5 @ 225 lb", text)


class ModeRegistryTests(unittest.TestCase):
    def test_every_mode_round_trips(self):
        samples = {"shopping": "milk, eggs", "todo": "call mom, do laundry",
                   "gym": "squat 5x5 at 225"}
        for name, text in samples.items():
            m = modes.get(name)
            parsed = m["parse"](text)
            data = m["build"]({"title": parsed.get("title"), "items": parsed["items"],
                               "options": {}}).to_escpos()
            self.assertTrue(data.endswith(b"\x1dV\x00"), name)


if __name__ == "__main__":
    unittest.main()
