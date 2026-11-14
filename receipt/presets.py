"""Built-in presets: ready-made workouts and to-do items you can tap to add.

Edit this file to change your defaults. Everything here is plain data.

Gym: a classic 3-day Push / Pull / Legs split.
  Push  = chest, shoulders, triceps (pressing away from you)
  Pull  = back, rear delts, biceps (pulling toward you)
  Legs  = quads, hamstrings, glutes, calves
Each day starts with a heavy compound lift, then moves to lighter accessory
work with higher reps.
"""
from __future__ import annotations


def ex(name, sets=None, reps=None, duration=None):
    return {"name": name, "sets": sets, "reps": reps, "weight": None,
            "unit": "lb", "duration": duration}


GYM_ROUTINES = {
    "push": {
        "label": "Push", "emoji": "💪", "title": "Push day",
        "blurb": "Chest · shoulders · triceps",
        "exercises": [
            ex("Barbell bench press", 4, 8),
            ex("Incline dumbbell press", 3, 10),
            ex("Overhead press", 3, 8),
            ex("Lateral raises", 3, 15),
            ex("Tricep pushdowns", 3, 12),
            ex("Overhead tricep extension", 3, 12),
        ],
    },
    "pull": {
        "label": "Pull", "emoji": "🧗", "title": "Pull day",
        "blurb": "Back · rear delts · biceps",
        "exercises": [
            ex("Deadlift", 3, 5),
            ex("Pull-ups", 3, 8),
            ex("Barbell row", 3, 8),
            ex("Seated cable row", 3, 10),
            ex("Face pulls", 3, 15),
            ex("Barbell curls", 3, 10),
            ex("Hammer curls", 3, 12),
        ],
    },
    "legs": {
        "label": "Legs", "emoji": "🦵", "title": "Leg day",
        "blurb": "Quads · hamstrings · glutes · calves",
        "exercises": [
            ex("Back squat", 4, 6),
            ex("Romanian deadlift", 3, 8),
            ex("Leg press", 3, 10),
            ex("Walking lunges (each leg)", 3, 10),
            ex("Lying leg curls", 3, 12),
            ex("Standing calf raises", 4, 15),
        ],
    },
}

GYM_LIBRARY = {
    "Chest": [ex("Barbell bench press", 4, 8), ex("Incline dumbbell press", 3, 10),
              ex("Dumbbell flyes", 3, 12), ex("Cable crossovers", 3, 15),
              ex("Dips", 3, 10), ex("Push-ups", 3, 15)],
    "Shoulders": [ex("Overhead press", 3, 8), ex("Seated dumbbell press", 3, 10),
                  ex("Arnold press", 3, 10), ex("Lateral raises", 3, 15),
                  ex("Rear delt flyes", 3, 15), ex("Face pulls", 3, 15)],
    "Triceps": [ex("Tricep pushdowns", 3, 12), ex("Overhead tricep extension", 3, 12),
                ex("Skull crushers", 3, 10), ex("Close-grip bench press", 3, 8)],
    "Back": [ex("Deadlift", 3, 5), ex("Pull-ups", 3, 8), ex("Lat pulldown", 3, 10),
             ex("Barbell row", 3, 8), ex("Seated cable row", 3, 10),
             ex("Single-arm dumbbell row", 3, 10), ex("T-bar row", 3, 8)],
    "Biceps": [ex("Barbell curls", 3, 10), ex("Hammer curls", 3, 12),
               ex("Incline dumbbell curls", 3, 10), ex("Cable curls", 3, 12),
               ex("Preacher curls", 3, 10)],
    "Legs": [ex("Back squat", 4, 6), ex("Front squat", 3, 6), ex("Romanian deadlift", 3, 8),
             ex("Leg press", 3, 10), ex("Bulgarian split squat", 3, 8),
             ex("Walking lunges (each leg)", 3, 10), ex("Leg extensions", 3, 15),
             ex("Lying leg curls", 3, 12), ex("Hip thrusts", 3, 10),
             ex("Standing calf raises", 4, 15)],
    "Core": [ex("Plank", 3, duration="60 sec"), ex("Hanging leg raises", 3, 12),
             ex("Cable crunches", 3, 15), ex("Ab wheel rollouts", 3, 10),
             ex("Russian twists", 3, 20)],
    "Cardio": [ex("Treadmill walk", duration="20 min"), ex("Incline walk", duration="15 min"),
               ex("Stairmaster", duration="15 min"), ex("Rowing machine", duration="10 min"),
               ex("Bike", duration="20 min"), ex("Outdoor walk", duration="1 mi")],
}

TODO_ROUTINES = {
    "daily": {
        "label": "Daily essentials", "emoji": "☀️", "title": "Today",
        "blurb": "Steps, learning, reading, planning",
        "items": ["Walk 10,000 steps", "Study AI tools for 2 hours",
                  "Drink 8 glasses of water", "Read 20 pages",
                  "Plan tomorrow's top 3 tasks"],
    },
    "deep": {
        "label": "Deep work day", "emoji": "🎯", "title": "Focus day",
        "blurb": "Big blocks, fewer distractions",
        "items": ["2 hours of deep work, phone in another room",
                  "Study AI tools for 2 hours", "Build or ship one small thing",
                  "Clear inbox to zero", "Walk 10,000 steps",
                  "Plan tomorrow's top 3 tasks"],
    },
    "reset": {
        "label": "Reset day", "emoji": "🧹", "title": "Reset",
        "blurb": "Home, errands, recharge",
        "items": ["15-minute tidy-up", "Do one load of laundry", "Meal prep for tomorrow",
                  "Take out trash and recycling", "Walk 10,000 steps",
                  "In bed by 11 PM"],
    },
}

TODO_LIBRARY = {
    "Health": ["Walk 10,000 steps", "Drink 8 glasses of water", "Work out for 45 minutes",
               "Stretch for 10 minutes", "Eat a vegetable with every meal", "In bed by 11 PM"],
    "Learning": ["Study AI tools for 2 hours", "Read 20 pages",
                 "Watch one tutorial and take notes", "Build or ship one small thing",
                 "Write down one thing I learned"],
    "Focus": ["Plan tomorrow's top 3 tasks", "2 hours of deep work, phone in another room",
              "Clear inbox to zero", "No social media before noon",
              "Review the week's goals"],
    "Career": ["Send 2 networking messages", "Apply to 2 jobs",
               "Update resume or portfolio", "Practice one interview answer out loud"],
    "Home": ["15-minute tidy-up", "Do one load of laundry", "Meal prep for tomorrow",
             "Take out trash and recycling", "Pay any bills due this week"],
}


def all_presets() -> dict:
    """Everything the UI needs, in one JSON-friendly blob."""
    return {
        "gym": {"routines": GYM_ROUTINES, "library": GYM_LIBRARY},
        "todo": {"routines": {k: {**v, "items": [{"text": t, "priority": False} for t in v["items"]]}
                              for k, v in TODO_ROUTINES.items()},
                 "library": {g: [{"text": t, "priority": False} for t in items]
                             for g, items in TODO_LIBRARY.items()}},
    }
