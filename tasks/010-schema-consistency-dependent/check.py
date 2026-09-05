"""Verifier: the new progress_history must fit report.py, which is already in the repo."""
import datetime as _dt
import os
import sys
import time

sys.path.insert(0, os.getcwd())
if os.path.exists("app.db"):
    os.remove("app.db")


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


import store  # noqa: E402
try:
    import report  # noqa: E402
except Exception as e:  # pragma: no cover
    fail(0, f"could not import report.py (was it changed / broken?): {type(e).__name__}: {e}")

store.init_db()

store.record_progress("build", 10.0)
ts1 = store.get_progress("build")[2]
time.sleep(0.05)
store.record_progress("build", 40.0)
ts2 = store.get_progress("build")[2]
time.sleep(0.05)
store.record_progress("build", 90.0)
ts3 = store.get_progress("build")[2]
time.sleep(0.05)
t_after = _dt.datetime.now(_dt.timezone.utc).isoformat()


def midpoint(a, b):
    da, db = store.parse_ts(a), store.parse_ts(b)
    return (da + (db - da) / 2).isoformat()


# --- 1. report.py can actually use the table the agent built ---------------
try:
    n = report.times_superseded("build")
except Exception as e:
    fail(1, f"report.py cannot use progress_history: {type(e).__name__}: {e} "
            f"-- it expects columns (task_name, percent, updated_at)")

# --- 2. explicit column-name check (clearer than the SQL error) -----------
con = store.connect()
cols = {r[1] for r in con.execute("PRAGMA table_info(progress_history)").fetchall()}
con.close()
if "updated_at" not in cols:
    fail(2, f"progress_history has no `updated_at` column (has {sorted(cols)}). "
            f"report.py selects and filters on progress_history.updated_at.")

# --- 3. snapshot-before-overwrite semantics (report.py documents this) ----
if n != 2:
    fail(3, f"report.times_superseded('build') == {n}, expected 2. report.py counts only "
            f"SUPERSEDED values (not the live one): progress_history should gain a row when "
            f"a value is overwritten, not one per record_progress call.")

# --- 4. point-in-time reads via report.progress_as_of -------------------
for q, want in [(midpoint(ts1, ts2), 10.0),
                (midpoint(ts2, ts3), 40.0),
                (t_after, 90.0)]:
    got = report.progress_as_of("build", q)
    if got != want:
        fail(4, f"report.progress_as_of('build', {q}) == {got!r}, expected {want}")

# --- 5. superseded rows keep their ORIGINAL updated_at ------------------
con = store.connect()
hist_ts = [r[0] for r in con.execute(
    "SELECT updated_at FROM progress_history WHERE task_name = 'build'"
).fetchall()]
con.close()
for want_ts in (ts1, ts2):
    if want_ts not in hist_ts:
        fail(5, f"progress_history is missing the original updated_at {want_ts!r} "
                f"(got {hist_ts}). A superseded row must be copied in unchanged, not "
                f"re-stamped with the archive time.")

print("OK")
