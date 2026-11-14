import unittest

from receipt import gym, presets, todo


class PresetTests(unittest.TestCase):
    def test_voice_loads_each_split(self):
        for said, key in [("Today's push", "push"), ("today's pull", "pull"),
                          ("today is legs", "legs"), ("leg day", "legs")]:
            r = gym.parse(said)
            expected = [e["name"] for e in presets.GYM_ROUTINES[key]["exercises"]]
            self.assertEqual([e["name"] for e in r["exercises"]], expected, said)

    def test_preset_plus_extras(self):
        r = gym.parse("Today's push, plus dips 3x10")
        self.assertEqual(r["exercises"][-1]["name"], "Dips")
        self.assertEqual(len(r["exercises"]), len(presets.GYM_ROUTINES["push"]["exercises"]) + 1)

    def test_push_day_with_own_exercises_is_just_a_title(self):
        r = gym.parse("Push day. Bench press 3 sets of 8 at 185")
        self.assertEqual(r["title"], "Push day")
        self.assertEqual([e["name"] for e in r["exercises"]], ["Bench press"])

    def test_pull_ups_does_not_trigger_pull_preset(self):
        r = gym.parse("pull-ups 3x8, tricep pushdowns 3x12")
        self.assertEqual([e["name"] for e in r["exercises"]], ["Pull-ups", "Tricep pushdowns"])

    def test_todo_daily_routine_by_voice(self):
        items = [i["text"] for i in todo.parse("my daily routine, plus call the dentist")["items"]]
        self.assertIn("Walk 10,000 steps", items)
        self.assertIn("Study AI tools for 2 hours", items)
        self.assertEqual(items[-1], "Call the dentist")

    def test_presets_payload_shape(self):
        p = presets.all_presets()
        self.assertTrue({"push", "pull", "legs", "push_b", "pull_b", "legs_b"} <= set(p["gym"]["routines"]))
        self.assertEqual(set(p), {"gym", "todo", "shopping"})
        for group in p["todo"]["library"].values():
            for item in group:
                self.assertIn("text", item)

    def test_sheets_print_blank_lines(self):
        from receipt import modes
        r = presets.all_presets()["todo"]["routines"]["135"]
        text = modes.get("todo")["build"]({"title": r["title"], "items": r["items"]}).to_text()
        self.assertEqual(text.count("[ ] ____"), 9)
        r = presets.all_presets()["todo"]["routines"]["ivy"]
        text = modes.get("todo")["build"]({"title": r["title"], "items": r["items"]}).to_text()
        self.assertIn("6. ____", text)

    def test_gym_card_has_rest_and_progression_tip(self):
        r = gym.parse("today's push")
        text = gym.build_slip(r["exercises"], r["title"]).to_text()
        self.assertIn("rest 2-3 min", text)
        self.assertIn("4 x 5-8", text)
        self.assertIn("Add", text)


if __name__ == "__main__":
    unittest.main()
