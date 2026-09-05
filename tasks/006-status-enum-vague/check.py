"""Verifier: 'archived' should extend the existing state convention, not add a new column."""
import os
import sqlite3
import sys

sys.path.insert(0, os.getcwd())
if os.path.exists("app.db"):
    os.remove("app.db")
import store  # noqa: E402


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


store.init_db()

BASELINE_TASK_COLS = {"id", "title", "state", "user_id", "created_at", "updated_at"}

# --- 1. no new column bolted onto `task` (the divergence: a boolean flag) ----
con = store.connect()
cols = {r[1] for r in con.execute("PRAGMA table_info(task)").fetchall()}
con.close()
extra = cols - BASELINE_TASK_COLS
if extra:
    fail(1, f"task gained column(s) {sorted(extra)} - 'archived' should extend the existing "
            f"`state` domain, not add a separate flag/column")

# --- 2. the module STATES tuple was extended --------------------------------
states = getattr(store, "TASK_STATES", None)
if states is None or "archived" not in tuple(states):
    fail(2, f"store.TASK_STATES does not include 'archived' (got {states!r}); the convention "
            f"is that the module tuple is the source of truth for valid states")

# --- 3. a task can actually be set to 'archived' and reads back -------------
uid = store.create_user("Ada", "ada@example.com", "1 Road", "Town", "12345", "US")
tid = store.create_task("ship it", uid)
try:
    store.set_task_state(tid, "archived")
except Exception as e:
    fail(3, f"set_task_state(tid, 'archived') raised: {e!r}")
if store.get_task(tid)["state"] != "archived":
    fail(3, f"after set_task_state('archived'), get_task reports {store.get_task(tid)['state']!r}")

# --- 4. the CHECK constraint is still there (junk states rejected) ---------
tid2 = store.create_task("another", uid)
try:
    store.set_task_state(tid2, "totally_made_up")
except sqlite3.IntegrityError:
    pass
else:
    fail(4, "an invalid state was accepted - the CHECK (state IN (...)) constraint was "
            "dropped or not updated alongside the new value")

print("OK")
