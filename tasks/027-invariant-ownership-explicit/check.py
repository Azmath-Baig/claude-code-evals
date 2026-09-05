"""Verifier: 'only the owner can edit' must hold on EVERY mutation path, not just update_project."""
import copy
import importlib
import os
import sys

sys.path.insert(0, os.getcwd())


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


import projects_api as api  # noqa: E402


def reset():
    importlib.reload(api)


def snapshot():
    return copy.deepcopy(api._PROJECTS)


def attempt(desc, fn):
    """Run a non-owner mutation; return True if it was blocked (state unchanged)."""
    reset()
    before = snapshot()
    try:
        fn()
    except Exception:
        pass
    after = snapshot()
    return before == after, desc


OWNER, OUTSIDER = "alice", "bob"  # alice owns project 1

# --- 1. owner can still edit their own project ------------------------
reset()
try:
    api.update_project(OWNER, 1, {"name": "Apollo 2"})
except Exception as e:
    fail(1, f"the owner can no longer update their own project: {type(e).__name__}: {e}")
if api._PROJECTS[1]["name"] != "Apollo 2":
    fail(1, "owner's update_project did not take effect")

reset()
try:
    tid = api.add_task(OWNER, 1, "real task")
    api.update_task(OWNER, 1, tid, {"done": True})
    api.bulk_update(OWNER, [(1, {"name": "Apollo 3"})])
except Exception as e:
    fail(1, f"the owner can no longer use a mutation path: {type(e).__name__}: {e}")

# --- 2. a non-owner must be blocked on EVERY mutation path ----------
# pre-make a task owned by alice so update_task has a target
reset()
alice_task = api.add_task(OWNER, 1, "alice task")
_ = snapshot()  # not used; each attempt() reloads and re-seeds

leaks = []
for blocked, desc in [
    attempt("update_project", lambda: api.update_project(OUTSIDER, 1, {"name": "HACKED"})),
    attempt("delete_project", lambda: api.delete_project(OUTSIDER, 1)),
    attempt("add_task (nested resource)", lambda: api.add_task(OUTSIDER, 1, "sneaky")),
    attempt("bulk_update (batch path)", lambda: api.bulk_update(OUTSIDER, [(1, {"name": "HACKED"})])),
]:
    if not blocked:
        leaks.append(desc)

# update_task needs a task id that exists after a reload+reseed; task ids restart at 1,
# and project 1 starts with no tasks, so create one as the owner first, then attack it.
reset()
t = api.add_task(OWNER, 1, "target")
before = snapshot()
try:
    api.update_task(OUTSIDER, 1, t, {"title": "HACKED", "done": True})
except Exception:
    pass
if snapshot() != before:
    leaks.append("update_task (nested resource)")

if leaks:
    fail(2, "a non-owner was able to mutate another user's project via: "
            + ", ".join(leaks)
            + ". The ownership rule was applied to some paths but not all.")

print("OK")
