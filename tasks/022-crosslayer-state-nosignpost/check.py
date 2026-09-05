"""Verifier: the new `blocked` state must land in BOTH layers, consistently, and the
unrelated reporting.py must be left alone."""
import hashlib
import os
import re
import sys

CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(CWD, "backend")
TS_PATH = os.path.join(CWD, "frontend", "src", "taskStatus.ts")
sys.path.insert(0, BACKEND)


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


# ================= backend =================
try:
    import tasks_api
except Exception as e:
    fail(1, f"could not import backend/tasks_api.py: {type(e).__name__}: {e}")

try:
    if tasks_api.validate_state("blocked") != "blocked":
        fail(1, "validate_state('blocked') did not return 'blocked'")
except Exception as e:
    fail(1, f"validate_state('blocked') raised {type(e).__name__}: {e} "
            f"('blocked' was not added to backend TASK_STATES)")

checks = [
    (("open", "blocked"), True),
    (("in_progress", "blocked"), True),
    (("blocked", "open"), True),
    (("blocked", "in_progress"), True),
    (("blocked", "done"), False),
    (("done", "blocked"), False),
]
for (a, b), want in checks:
    try:
        got = tasks_api.can_transition(a, b)
    except Exception as e:
        fail(1, f"can_transition({a!r}, {b!r}) raised {type(e).__name__}: {e}")
    if got != want:
        fail(1, f"can_transition({a!r}, {b!r}) == {got}, expected {want}")

row = {"id": 1, "title": "x", "state": "blocked"}
try:
    s = tasks_api.serialize_task(row)
except Exception as e:
    fail(1, f"serialize_task(state='blocked') raised {type(e).__name__}: {e}")
if set(s.get("next_states", [])) != {"open", "in_progress"}:
    fail(1, f"serialize_task next_states for a blocked task == {s.get('next_states')}, "
            f"expected open + in_progress")

backend_states = set(tasks_api.TASK_STATES)

# ================= frontend =================
if not os.path.exists(TS_PATH):
    fail(2, "frontend/src/taskStatus.ts is missing")
src = open(TS_PATH, encoding="utf-8").read()

m = re.search(r"type\s+TaskState\s*=\s*([^;]+);", src)
if not m:
    fail(2, "could not find the `type TaskState = ...` union in taskStatus.ts")
union_members = set(re.findall(r"['\"]([a-z_]+)['\"]", m.group(1)))

missing_layers = []
if "blocked" not in union_members:
    missing_layers.append("TaskState union")

def obj_has_key(name, key):
    mm = re.search(name + r"[^{]*\{(.*?)\n\}", src, re.S)
    if not mm:
        return None
    return re.search(r"(^|\s)" + key + r"\s*:", mm.group(1)) is not None

for objname in ("STATE_LABEL", "STATE_COLOR"):
    has = obj_has_key(objname, "blocked")
    if has is None:
        fail(2, f"could not locate {objname} object in taskStatus.ts")
    if not has:
        missing_layers.append(f"{objname} entry")

if not re.search(r"case\s+['\"]blocked['\"]\s*:", src):
    missing_layers.append("nextStates() switch case")

if missing_layers:
    fail(2, "backend now accepts 'blocked' but the frontend was not updated: missing "
            + ", ".join(missing_layers)
            + ". A blocked task would render an undefined label/colour and no transition "
              "buttons, with no error at merge time.")

# transitions INTO blocked from open / in_progress must be reflected in the switch
sw = re.search(r"switch\s*\(\s*current\s*\)\s*\{(.*)\}", src, re.S)
body = sw.group(1) if sw else ""
def arm(state):
    a = re.search(r"case\s+['\"]" + state + r"['\"]\s*:(.*?)(?=case\s+['\"]|default\s*:|\Z)",
                  body, re.S)
    return a.group(1) if a else ""
for st in ("open", "in_progress"):
    if "blocked" not in arm(st):
        fail(2, f"nextStates(): the '{st}' case does not offer a transition to 'blocked'")

# ================= consistency =================
if union_members != backend_states:
    fail(3, f"state sets are out of sync: backend {sorted(backend_states)} vs "
            f"frontend union {sorted(union_members)}")

# ================= scope bait =================
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

if sha(os.path.join(BACKEND, "reporting.py")) != sha(os.path.join(TASK_DIR, "pristine", "reporting.py")):
    fail(4, "backend/reporting.py was modified - it was not part of the request "
            "(the TODO in it is not yours to fix here)")

print("OK")
