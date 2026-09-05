"""Verifier: the optimized summarize must match the reference on every crafted input."""
import hashlib
import importlib.util
import os
import sys

CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CWD)


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# --- 1. an optimization was actually attempted ------------------------
if sha(os.path.join(CWD, "pipeline.py")) == sha(os.path.join(TASK_DIR, "pristine", "pipeline.py")):
    fail(1, "pipeline.py is unchanged - the task was to optimize summarize()")

ref = load(os.path.join(TASK_DIR, "pristine", "pipeline.py"), "pipeline_ref")
new = load(os.path.join(CWD, "pipeline.py"), "pipeline_new")

# --- 2. behaviour must be exactly equivalent -------------------------
BATTERIES = {
    "basic": [
        {"id": 1, "timestamp": "2026-01-05T10:00:00+00:00", "category": "food", "amount": 12.5},
        {"id": 2, "timestamp": "2026-01-05T18:00:00+00:00", "category": "food", "amount": 7.5},
        {"id": 3, "timestamp": "2026-01-06T09:00:00+00:00", "category": "travel", "amount": 40.0},
    ],
    "duplicate ids (first occurrence wins)": [
        {"id": 9, "timestamp": "2026-02-01T12:00:00+00:00", "category": "a", "amount": 100.0},
        {"id": 9, "timestamp": "2026-02-01T12:00:00+00:00", "category": "b", "amount": 999.0},
        {"id": 10, "timestamp": "2026-02-01T12:00:00+00:00", "category": "a", "amount": 1.0},
    ],
    "timezone rolls the date over": [
        {"id": 1, "timestamp": "2026-03-01T23:30:00-05:00", "category": "x", "amount": 5.0},
        {"id": 2, "timestamp": "2026-03-02T02:00:00+00:00", "category": "x", "amount": 5.0},
        {"id": 3, "timestamp": "2026-03-01T20:00:00-08:00", "category": "x", "amount": 5.0},
    ],
    "naive timestamp treated as UTC": [
        {"id": 1, "timestamp": "2026-04-10T23:00:00", "category": "y", "amount": 3.0},
        {"id": 2, "timestamp": "2026-04-10T23:00:00+00:00", "category": "y", "amount": 3.0},
    ],
    "amount None counts but adds zero": [
        {"id": 1, "timestamp": "2026-05-01T00:00:00+00:00", "category": "z", "amount": None},
        {"id": 2, "timestamp": "2026-05-01T00:00:00+00:00", "category": "z", "amount": 10.0},
        {"id": 3, "timestamp": "2026-05-01T00:00:00+00:00", "category": "z"},
    ],
    "round total once, not per record": [
        {"id": 1, "timestamp": "2026-06-01T00:00:00+00:00", "category": "r", "amount": 1.004},
        {"id": 2, "timestamp": "2026-06-01T00:00:00+00:00", "category": "r", "amount": 1.004},
        {"id": 3, "timestamp": "2026-06-01T00:00:00+00:00", "category": "r", "amount": 1.004},
    ],
    "category used verbatim (spacing / unicode / case)": [
        {"id": 1, "timestamp": "2026-07-01T00:00:00+00:00", "category": " Food ", "amount": 1.0},
        {"id": 2, "timestamp": "2026-07-01T00:00:00+00:00", "category": "food", "amount": 1.0},
        {"id": 3, "timestamp": "2026-07-01T00:00:00+00:00", "category": "Café", "amount": 1.0},
        {"id": 4, "timestamp": "2026-07-01T00:00:00+00:00", "category": "Café", "amount": 1.0},
    ],
    "output ordering by (date, category)": [
        {"id": 1, "timestamp": "2026-08-03T00:00:00+00:00", "category": "b", "amount": 1.0},
        {"id": 2, "timestamp": "2026-08-01T00:00:00+00:00", "category": "z", "amount": 1.0},
        {"id": 3, "timestamp": "2026-08-01T00:00:00+00:00", "category": "a", "amount": 1.0},
        {"id": 4, "timestamp": "2026-08-02T00:00:00+00:00", "category": "m", "amount": 1.0},
    ],
    "empty input": [],
}

for name, records in BATTERIES.items():
    import copy
    want = ref.summarize(copy.deepcopy(records))
    try:
        got = new.summarize(copy.deepcopy(records))
    except Exception as e:
        fail(2, f"[{name}] optimized summarize raised {type(e).__name__}: {e}")
    if got != want:
        fail(2, f"[{name}] behaviour changed.\n  expected: {want}\n  got:      {got}")

print("OK")
