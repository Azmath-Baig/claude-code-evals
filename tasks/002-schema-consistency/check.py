"""Verifier for the schema-consistency task family.

Run with cwd = the agent's mutated workspace (verify.sh does this).
Exit 0 and print OK iff every assertion holds. Each failure prints [FAIL <n>].
"""
import os
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.getcwd())

if os.path.exists("app.db"):
    os.remove("app.db")

import store  # noqa: E402


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


store.init_db()

# --- 1. history table exists with the mirrored columns -----------------------
con = store.connect()
cols = {r[1] for r in con.execute("PRAGMA table_info(progress_history)").fetchall()}
con.close()
if not cols:
    fail(1, "progress_history table was not created")
for c in ("task_name", "percent", "updated_at"):
    if c not in cols:
        fail(1, f"progress_history is missing column {c!r} (has {sorted(cols)})")

# --- 2. drive several updates to the same task ------------------------------
store.record_progress("build", 10.0)
ts_first = store.get_progress("build")[2]
time.sleep(0.02)
store.record_progress("build", 40.0)
time.sleep(0.02)
store.record_progress("build", 90.0)

# --- 3. progress still holds exactly one, latest row per task --------------
if store.get_progress("build")[1] != 90.0:
    fail(3, "get_progress no longer returns the latest percent")
con = store.connect()
n = con.execute("SELECT COUNT(*) FROM progress WHERE task_name='build'").fetchone()[0]
con.close()
if n != 1:
    fail(3, f"progress should keep one row per task, found {n}")

# --- 4. history captured the prior values ---------------------------------
con = store.connect()
hist = con.execute(
    "SELECT task_name, percent, updated_at FROM progress_history "
    "WHERE task_name='build' ORDER BY updated_at"
).fetchall()
con.close()
percents = sorted(h[1] for h in hist)
if 10.0 not in percents or 40.0 not in percents:
    fail(4, f"history should contain the overwritten percents 10.0 and 40.0, got {percents}")

# --- 5. history timestamps use the SAME type/format as progress.updated_at -
for h in hist:
    ts = h[2]
    if not isinstance(ts, str):
        fail(5, f"history updated_at should be an ISO string like progress.updated_at, "
                f"got {type(ts).__name__} {ts!r}")
    try:
        d = store.parse_ts(ts)
    except Exception as e:
        fail(5, f"history updated_at {ts!r} does not parse with store.parse_ts: {e}")
    if d.tzinfo is None:
        fail(5, f"history updated_at {ts!r} lost timezone info (progress timestamps are tz-aware)")

# --- 6. the archived row keeps the ORIGINAL updated_at, not a fresh stamp --
hist_ts = [h[2] for h in hist]
if ts_first not in hist_ts:
    fail(6, f"history did not preserve the original updated_at {ts_first!r}; "
            f"got {hist_ts} (was the timestamp re-generated instead of copied?)")

# --- 7. a date-range query over history works (catches format drift) -------
lo = (store.parse_ts(ts_first) - timedelta(seconds=1)).isoformat()
hi = (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat()
con = store.connect()
cnt = con.execute(
    "SELECT COUNT(*) FROM progress_history WHERE updated_at >= ? AND updated_at <= ?",
    (lo, hi),
).fetchone()[0]
con.close()
if cnt < 2:
    fail(7, f"date-range query over progress_history returned {cnt}, expected >= 2 "
            f"(history timestamp format probably differs from the ISO bounds)")

print("OK")
