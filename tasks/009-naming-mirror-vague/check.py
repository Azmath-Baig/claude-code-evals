"""Verifier: a login-history table should reuse the app's naming conventions."""
import os
import re
import sys
import time

sys.path.insert(0, os.getcwd())
if os.path.exists("app.db"):
    os.remove("app.db")
import store  # noqa: E402


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


BAD_TS_NAMES = {"time", "timestamp", "logged_at", "login_at", "login_time",
                "ts", "when", "at", "date", "datetime", "occurred_at"}

store.init_db()

# --- 1. the two functions exist and round-trip ---------------------------
for fn in ("record_login", "get_recent_logins"):
    if not hasattr(store, fn):
        fail(1, f"store.{fn} was not added")

uid = store.create_user("Ada", "ada@example.com", "1 Road", "Town", "12345", "US")
for _ in range(3):
    store.record_login(uid)
    time.sleep(0.02)
rows = store.get_recent_logins(uid, limit=10)
if rows is None or len(list(rows)) < 3:
    fail(1, f"get_recent_logins returned {rows!r}; expected at least the 3 just written")

# --- 2. locate the new table ------------------------------------------
con = store.connect()
tables = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
).fetchall()]
non_core = [t for t in tables if t not in ("user", "task", "comment")]
if not non_core:
    con.close()
    fail(2, "no new table was created for login records")

def cols_of(t):
    return {r[1] for r in con.execute(f"PRAGMA table_info({t})").fetchall()}

login_table = next((t for t in non_core if "user_id" in cols_of(t)), non_core[0])
lcols = cols_of(login_table)
lsql = con.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (login_table,)
).fetchone()[0]

# --- 3. FK to user follows the user_id ... REFERENCES user(id) convention
if "user_id" not in lcols:
    con.close()
    fail(3, f"`{login_table}` has no `user_id` column (has {sorted(lcols)}); "
            f"the convention for a link to user is `user_id`")
if not re.search(r"user_id\s+INTEGER[^,]*references\s+user\s*\(", lsql, re.I):
    con.close()
    fail(3, f"`{login_table}.user_id` is missing an `INTEGER ... REFERENCES user(id)` clause:\n{lsql}")

# --- 4. the timestamp column is named `created_at` (the app-wide convention)
if "created_at" not in lcols:
    bad = sorted(lcols & BAD_TS_NAMES)
    con.close()
    fail(4, f"`{login_table}` has no `created_at` column; timestamp appears to be named "
            f"{bad or 'something non-conventional'}. Every other table uses `created_at`.")

row = con.execute(f"SELECT created_at FROM {login_table} LIMIT 1").fetchone()
con.close()

# --- 5. the timestamp value follows the ISO-8601 UTC convention --------
ts = row[0]
if not isinstance(ts, str):
    fail(5, f"{login_table}.created_at is {type(ts).__name__} {ts!r}; app timestamps are ISO strings")
try:
    d = store.parse_ts(ts)
except Exception as e:
    fail(5, f"{login_table}.created_at {ts!r} does not parse with store.parse_ts: {e} "
            f"(CURRENT_TIMESTAMP default, or a non-ISO format?)")
if d.tzinfo is None:
    fail(5, f"{login_table}.created_at {ts!r} is not timezone-aware; use now_iso()")

print("OK")
