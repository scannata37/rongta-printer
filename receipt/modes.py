"""One place that knows about every list type the app can print.

Each mode exposes the same two functions, so the server and UI don't care
which mode they're talking to:

  parse(text)  -> {"title": str|None, "items": [...]}
  build(data)  -> Slip       data = {"title", "items", "options"}

To add a new mode: write a module with parse + build_slip, then register it here.
"""
from __future__ import annotations

from typing import Callable, Dict

from . import gym, shopping, todo
from .slip import Slip


def _shopping_parse(text: str) -> dict:
    store, items = shopping.parse(text)
    return {"title": store, "items": items}


def _shopping_build(d: dict) -> Slip:
    items = [str(i).strip() for i in d.get("items", []) if str(i).strip()]
    by_aisle = (d.get("options") or {}).get("by_aisle", True)
    return shopping.build_slip(items, d.get("title") or None, by_aisle=bool(by_aisle))


def _todo_build(d: dict) -> Slip:
    items = [i for i in d.get("items", []) if str(i.get("text", "")).strip()]
    return todo.build_slip(items, d.get("title") or None)


def _gym_parse(text: str) -> dict:
    r = gym.parse(text)
    return {"title": r["title"], "items": r["exercises"]}


def _gym_build(d: dict) -> Slip:
    items = [i for i in d.get("items", []) if str(i.get("name", "")).strip()]
    return gym.build_slip(items, d.get("title") or None)


MODES: Dict[str, Dict[str, Callable]] = {
    "shopping": {"parse": _shopping_parse, "build": _shopping_build},
    "todo": {"parse": todo.parse, "build": _todo_build},
    "gym": {"parse": _gym_parse, "build": _gym_build},
}


def get(mode: str) -> Dict[str, Callable]:
    if mode not in MODES:
        raise KeyError("unknown mode: %s" % mode)
    return MODES[mode]
