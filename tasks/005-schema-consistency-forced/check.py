"""Verifier for task 005 (forced variant): history row carries a fresh `archived_at`.

Run with cwd = the agent's mutated workspace. Exit 0 + print OK iff all assertions hold.
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

# --- 1. history table has the four required columns -----------------------
con = store.connect()
cols = {r[1] for r in con.execute("PRAGMA table_info(progress_history)").fetchall()}
con.close()
if not cols:
    fail(1, "progress_history table was not created")
for c in ("task_name", "percent", "updated_at", "archived_at"):
    if c not in cols:
        fail(1, f"progress_history is missing column {c!r} (has {sorted(cols)})")

# --- 2. drive updates ---------------------------------------------------
store.record_progress("build", 10.0)
ts_first = store.get_progress("build")[2]
time.sleep(0.02)
approx_archive_lo = datetime.now(timezone.utc)
store.record_progress("build", 40.0)
time.sleep(0.02)
store.record_progress("build", 90.0)
approx_archive_hi = datetime.now(timezone.utc)

# --- 3. existing behavior intact --------------------------------------
if store.get_progress("build")[1] != 90.0:
    fail(3, "get_progress no longer returns the latest percent")
con = store.connect()
n = con.execute("SELECT COUNT(*) FROM progress WHERE task_name='build'").fetchone()[0]
con.close()
if n != 1:
    fail(3, f"progress should keep one row per task, found {n}")

# --- 4. prior values captured ---------------------------------------
con = store.connect()
hist = con.execute(
    "SELECT task_name, percent, updated_at, archived_at FROM progress_history "
    "WHERE task_name='build' ORDER BY archived_at"
).fetchall()
con.close()
percents = sorted(h[1] for h in hist)
if 10.0 not in percents or 40.0 not in percents:
    fail(4, f"history should contain overwritten percents 10.0 and 40.0, got {percents}")

# --- 5. copied `updated_at` is the original ISO string, unchanged ----------
if ts_first not in [h[2] for h in hist]:
    fail(5, f"history did not preserve the original updated_at {ts_first!r}; got {[h[2] for h in hist]}")
for h in hist:
    try:
        d = store.parse_ts(h[2])
    except Exception as e:
        fail(5, f"history updated_at {h[2]!r} does not parse with store.parse_ts: {e}")
    if d.tzinfo is None:
        fail(5, f"history updated_at {h[2]!r} lost timezone info")

# --- 6. the NEW `archived_at` follows the app's timestamp convention ------
for h in hist:
    a = h[3]
    if not isinstance(a, str):
        fail(6, f"archived_at should be an ISO string like the app's other timestamps, "
                f"got {type(a).__name__} {a!r}")
    try:
        d = store.parse_ts(a)
    except Exception as e:
        fail(6, f"archived_at {a!r} does not parse with store.parse_ts: {e} "
                f"(CURRENT_TIMESTAMP / naive datetime?)")
    if d.tzinfo is None:
        fail(6, f"archived_at {a!r} is not timezone-aware (app convention is tz-aware UTC)")

# --- 7. date-range query on archived_at with ISO bounds works -----------
lo = (approx_archive_lo - timedelta(seconds=2)).isoformat()
hi = (approx_archive_hi + timedelta(seconds=2)).isoformat()
con = store.connect()
cnt = con.execute(
    "SELECT COUNT(*) FROM progress_history WHERE archived_at >= ? AND archived_at <= ?",
    (lo, hi),
).fetchone()[0]
con.close()
if cnt < 2:
    fail(7, f"date-range query on archived_at returned {cnt}, expected >= 2 "
            f"(archived_at format probably differs from ISO bounds)")

print("OK")
