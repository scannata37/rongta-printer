"""Built-in templates and pick-lists. Plain data: edit freely.

Research notes behind these choices
-----------------------------------
Gym (Push / Pull / Legs)
  * Push = chest, shoulders, triceps. Pull = back, rear delts, biceps.
    Legs = quads, hamstrings, glutes, calves.
  * Each day comes in two flavors, like most 6-day PPL plans:
      A = strength: heavy compound first, lower reps (5-8), longer rest.
      B = volume:   same muscles, different angles, 8-15 reps, shorter rest.
  * Rep RANGES, not single numbers. Progression rule printed on every card:
    when every set hits the top of the range, add weight next time.
  * Rest: ~2-3 min on big compound lifts, ~60-90 s on isolation work.

To-do
  * "1-3-5": one big task, three medium, five small (nine max).
  * "Ivy Lee": write six tasks the night before, ranked, and work in order.
  * Habits: short, specific, measurable ("Walk 10,000 steps", not "exercise").
  Sheets print blank, numbered lines you fill in with a pen.

Shopping
  * Point-and-click staples by aisle, plus a few common "runs".
"""
from __future__ import annotations

# ----------------------------------------------------------------------------
# Gym
# ----------------------------------------------------------------------------
HEAVY, MED, LIGHT = "2-3 min", "90 sec", "60 sec"


def ex(name, sets=None, reps=None, rest=None, duration=None):
    return {"name": name, "sets": sets, "reps": reps, "weight": None,
            "unit": "lb", "duration": duration, "rest": rest}


GYM_ROUTINES = {
    "push": {
        "label": "Push A", "group": "Push", "flavor": "Strength", "emoji": "💪",
        "color": "#ff6b35", "title": "Push day",
        "blurb": "Chest · shoulders · triceps",
        "exercises": [
            ex("Barbell bench press", 4, "5-8", HEAVY),
            ex("Overhead press", 3, "6-8", HEAVY),
            ex("Incline dumbbell press", 3, "8-12", MED),
            ex("Lateral raises", 3, "12-15", LIGHT),
            ex("Tricep pushdowns", 3, "10-12", LIGHT),
            ex("Overhead tricep extension", 3, "10-12", LIGHT),
        ],
    },
    "push_b": {
        "label": "Push B", "group": "Push", "flavor": "Volume", "emoji": "💪",
        "color": "#ff6b35", "title": "Push day B",
        "blurb": "Chest · shoulders · triceps",
        "exercises": [
            ex("Incline barbell press", 4, "6-10", HEAVY),
            ex("Seated dumbbell press", 3, "8-12", MED),
            ex("Cable crossovers", 3, "12-15", LIGHT),
            ex("Dips", 3, "8-12", MED),
            ex("Lateral raises", 4, "12-15", LIGHT),
            ex("Skull crushers", 3, "10-12", LIGHT),
        ],
    },
    "pull": {
        "label": "Pull A", "group": "Pull", "flavor": "Strength", "emoji": "🧗",
        "color": "#2f80ed", "title": "Pull day",
        "blurb": "Back · rear delts · biceps",
        "exercises": [
            ex("Deadlift", 3, "3-5", HEAVY),
            ex("Pull-ups", 3, "6-10", HEAVY),
            ex("Barbell row", 3, "6-8", HEAVY),
            ex("Face pulls", 3, "12-15", LIGHT),
            ex("Barbell curls", 3, "8-12", LIGHT),
            ex("Hammer curls", 3, "10-12", LIGHT),
        ],
    },
    "pull_b": {
        "label": "Pull B", "group": "Pull", "flavor": "Volume", "emoji": "🧗",
        "color": "#2f80ed", "title": "Pull day B",
        "blurb": "Back · rear delts · biceps",
        "exercises": [
            ex("Lat pulldown", 4, "8-12", MED),
            ex("Seated cable row", 3, "10-12", MED),
            ex("Single-arm dumbbell row", 3, "10-12", MED),
            ex("Rear delt flyes", 3, "12-15", LIGHT),
            ex("Incline dumbbell curls", 3, "10-12", LIGHT),
            ex("Cable curls", 3, "12-15", LIGHT),
        ],
    },
    "legs": {
        "label": "Legs A", "group": "Legs", "flavor": "Strength", "emoji": "🦵",
        "color": "#9b51e0", "title": "Leg day",
        "blurb": "Quads · hamstrings · glutes · calves",
        "exercises": [
            ex("Back squat", 4, "5-8", HEAVY),
            ex("Romanian deadlift", 3, "6-10", HEAVY),
            ex("Leg press", 3, "8-12", MED),
            ex("Lying leg curls", 3, "10-12", LIGHT),
            ex("Standing calf raises", 4, "10-15", LIGHT),
        ],
    },
    "legs_b": {
        "label": "Legs B", "group": "Legs", "flavor": "Volume", "emoji": "🦵",
        "color": "#9b51e0", "title": "Leg day B",
        "blurb": "Quads · hamstrings · glutes · calves",
        "exercises": [
            ex("Front squat", 3, "6-10", HEAVY),
            ex("Bulgarian split squat", 3, "8-12", MED),
            ex("Hip thrusts", 3, "8-12", MED),
            ex("Leg extensions", 3, "12-15", LIGHT),
            ex("Seated leg curls", 3, "12-15", LIGHT),
            ex("Seated calf raises", 4, "12-20", LIGHT),
        ],
    },
}

GYM_LIBRARY = {
    "Chest": [ex("Barbell bench press", 4, "5-8", HEAVY), ex("Incline dumbbell press", 3, "8-12", MED),
              ex("Dumbbell flyes", 3, "10-15", LIGHT), ex("Cable crossovers", 3, "12-15", LIGHT),
              ex("Dips", 3, "8-12", MED), ex("Push-ups", 3, "10-20", LIGHT)],
    "Shoulders": [ex("Overhead press", 3, "6-8", HEAVY), ex("Seated dumbbell press", 3, "8-12", MED),
                  ex("Arnold press", 3, "8-12", MED), ex("Lateral raises", 3, "12-15", LIGHT),
                  ex("Rear delt flyes", 3, "12-15", LIGHT), ex("Face pulls", 3, "12-15", LIGHT)],
    "Triceps": [ex("Tricep pushdowns", 3, "10-12", LIGHT), ex("Overhead tricep extension", 3, "10-12", LIGHT),
                ex("Skull crushers", 3, "8-12", LIGHT), ex("Close-grip bench press", 3, "6-8", HEAVY)],
    "Back": [ex("Deadlift", 3, "3-5", HEAVY), ex("Pull-ups", 3, "6-10", HEAVY),
             ex("Lat pulldown", 3, "8-12", MED), ex("Barbell row", 3, "6-8", HEAVY),
             ex("Seated cable row", 3, "10-12", MED), ex("Single-arm dumbbell row", 3, "10-12", MED),
             ex("T-bar row", 3, "6-10", HEAVY)],
    "Biceps": [ex("Barbell curls", 3, "8-12", LIGHT), ex("Hammer curls", 3, "10-12", LIGHT),
               ex("Incline dumbbell curls", 3, "10-12", LIGHT), ex("Cable curls", 3, "12-15", LIGHT),
               ex("Preacher curls", 3, "8-12", LIGHT)],
    "Legs": [ex("Back squat", 4, "5-8", HEAVY), ex("Front squat", 3, "6-10", HEAVY),
             ex("Romanian deadlift", 3, "6-10", HEAVY), ex("Leg press", 3, "8-12", MED),
             ex("Bulgarian split squat", 3, "8-12", MED), ex("Walking lunges (each leg)", 3, "10-12", MED),
             ex("Leg extensions", 3, "12-15", LIGHT), ex("Lying leg curls", 3, "10-12", LIGHT),
             ex("Hip thrusts", 3, "8-12", MED), ex("Standing calf raises", 4, "10-15", LIGHT)],
    "Core": [ex("Plank", 3, duration="60 sec"), ex("Hanging leg raises", 3, "10-15", LIGHT),
             ex("Cable crunches", 3, "12-15", LIGHT), ex("Ab wheel rollouts", 3, "8-12", LIGHT),
             ex("Russian twists", 3, "20", LIGHT)],
    "Cardio": [ex("Treadmill walk", duration="20 min"), ex("Incline walk", duration="15 min"),
               ex("Stairmaster", duration="15 min"), ex("Rowing machine", duration="10 min"),
               ex("Bike", duration="20 min"), ex("Outdoor walk", duration="1 mi")],
}

GYM_FOOTER = "Hit the top of the rep range on every set? Add weight next time."

# ----------------------------------------------------------------------------
# To-do
# ----------------------------------------------------------------------------


def task(text, priority=False, section=None):
    return {"text": text, "priority": priority, "section": section}


def blanks(section, n, label, numbered=False):
    """Empty lines to fill in with a pen. `label` is what the picker shows."""
    return [{"text": "", "priority": False, "section": section, "blank": True,
             "label": ("%s %d" % (label, i + 1)) if n > 1 else label,
             "num": (i + 1) if numbered else None} for i in range(n)]


TODO_ROUTINES = {
    "daily": {
        "label": "Daily essentials", "emoji": "☀️", "color": "#f2a900", "title": "Today",
        "blurb": "Small habits that compound",
        "items": [task("Walk 10,000 steps"), task("Study AI tools for 2 hours", True),
                  task("Drink 8 glasses of water"), task("Read 20 pages"),
                  task("10 minutes of stretching"), task("Plan tomorrow's top 3 tasks")],
    },
    "135": {
        "label": "1-3-5 day", "emoji": "🎯", "color": "#e5484d", "title": "1-3-5",
        "blurb": "1 big · 3 medium · 5 small", "sheet": True,
        "items": blanks("THE 1 BIG THING (2-4 hrs)", 1, "Big task")
                 + blanks("3 MEDIUM (30-60 min)", 3, "Medium task")
                 + blanks("5 SMALL (quick wins)", 5, "Small task"),
    },
    "ivy": {
        "label": "Ivy Lee six", "emoji": "🌙", "color": "#3e63dd", "title": "Tomorrow's six",
        "blurb": "Write 6 tonight, do them in order", "sheet": True,
        "items": blanks("IN ORDER - FINISH ONE, THEN THE NEXT", 6, "Task", numbered=True),
    },
    "deep": {
        "label": "Deep work day", "emoji": "🧠", "color": "#12a594", "title": "Focus day",
        "blurb": "Big blocks, fewer distractions",
        "items": [task("2 hours of deep work, phone in another room", True),
                  task("Study AI tools for 2 hours"), task("Build or ship one small thing"),
                  task("Clear inbox to zero"), task("Walk 10,000 steps"),
                  task("Plan tomorrow's top 3 tasks")],
    },
    "reset": {
        "label": "Reset day", "emoji": "🧹", "color": "#8e4ec6", "title": "Reset",
        "blurb": "Home, errands, recharge",
        "items": [task("15-minute tidy-up"), task("Do one load of laundry"),
                  task("Meal prep for tomorrow"), task("Take out trash and recycling"),
                  task("Pay any bills due this week"), task("In bed by 11 PM")],
    },
}

TODO_LIBRARY = {
    "Health": ["Walk 10,000 steps", "Drink 8 glasses of water", "Work out for 45 minutes",
               "10 minutes of stretching", "Eat a vegetable with every meal", "In bed by 11 PM"],
    "Learning": ["Study AI tools for 2 hours", "Read 20 pages",
                 "Watch one tutorial and take notes", "Build or ship one small thing",
                 "Write down one thing I learned"],
    "Focus": ["Plan tomorrow's top 3 tasks", "2 hours of deep work, phone in another room",
              "Clear inbox to zero", "No social media before noon", "Review the week's goals"],
    "Career": ["Send 2 networking messages", "Apply to 2 jobs",
               "Update resume or portfolio", "Practice one interview answer out loud"],
    "Home": ["15-minute tidy-up", "Do one load of laundry", "Meal prep for tomorrow",
             "Take out trash and recycling", "Pay any bills due this week"],
}

# ----------------------------------------------------------------------------
# Shopping
# ----------------------------------------------------------------------------
SHOPPING_ROUTINES = {
    "staples": {
        "label": "Weekly staples", "emoji": "🧺", "color": "#30a46c", "title": None,
        "blurb": "The usual basket",
        "items": ["Bananas", "Apples", "Spinach", "Onions", "Eggs", "Milk", "Greek yogurt",
                  "Bread", "Chicken breast", "Rice", "Coffee", "Paper towels"],
    },
    "protein": {
        "label": "High-protein", "emoji": "🥩", "color": "#e5484d", "title": None,
        "blurb": "Gym-week groceries",
        "items": ["Chicken breast", "Ground turkey", "Salmon", "Eggs", "Greek yogurt",
                  "Cottage cheese", "Protein powder", "Oats", "Rice", "Broccoli",
                  "Sweet potatoes", "Bananas"],
    },
    "quick": {
        "label": "Quick run", "emoji": "⚡", "color": "#f2a900", "title": None,
        "blurb": "In and out",
        "items": ["Milk", "Eggs", "Bread", "Bananas", "Coffee"],
    },
}

SHOPPING_LIBRARY = {
    "Produce": ["Bananas", "Apples", "Berries", "Lemons", "Avocados", "Spinach", "Lettuce",
                "Tomatoes", "Onions", "Garlic", "Potatoes", "Sweet potatoes", "Broccoli",
                "Carrots", "Bell peppers"],
    "Meat & Seafood": ["Chicken breast", "Ground beef", "Ground turkey", "Steak", "Salmon",
                       "Shrimp", "Bacon", "Deli turkey"],
    "Dairy & Eggs": ["Eggs", "Milk", "Butter", "Greek yogurt", "Cheddar cheese",
                     "Cottage cheese", "Cream cheese"],
    "Bakery": ["Bread", "Bagels", "Tortillas", "English muffins"],
    "Pantry": ["Rice", "Pasta", "Oats", "Cereal", "Peanut butter", "Olive oil", "Coffee",
               "Canned tuna", "Black beans", "Pasta sauce", "Protein powder"],
    "Frozen": ["Frozen vegetables", "Frozen berries", "Frozen pizza", "Ice cream"],
    "Snacks & Drinks": ["Chips", "Granola bars", "Almonds", "Sparkling water", "Juice"],
    "Household": ["Paper towels", "Toilet paper", "Trash bags", "Dish soap",
                  "Laundry detergent", "Shampoo", "Toothpaste"],
}


def all_presets() -> dict:
    """Everything the UI needs, in one JSON-friendly blob."""
    def todo_items(items):
        return [i if isinstance(i, dict) else task(i) for i in items]
    return {
        "gym": {"routines": GYM_ROUTINES, "library": GYM_LIBRARY},
        "todo": {"routines": {k: {**v, "items": todo_items(v["items"])} for k, v in TODO_ROUTINES.items()},
                 "library": {g: todo_items(items) for g, items in TODO_LIBRARY.items()}},
        "shopping": {"routines": SHOPPING_ROUTINES, "library": SHOPPING_LIBRARY},
    }
