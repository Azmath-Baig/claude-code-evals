"""Verifier: linking a comment to a user should follow the <table>_id FK convention."""
import os
import re
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

# --- 1. comment has a `user_id` column: INTEGER, NOT NULL -------------------
con = store.connect()
info = {r[1]: r for r in con.execute("PRAGMA table_info(comment)").fetchall()}
sql = con.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name='comment'"
).fetchone()[0]
con.close()

if "user_id" not in info:
    fail(1, f"comment has no `user_id` column (has {sorted(info)}). The codebase names "
            f"foreign keys `<table>_id`.")
_, _, col_type, notnull, _, _ = info["user_id"]
if col_type.upper() not in ("INTEGER", "INT", ""):
    fail(1, f"comment.user_id is {col_type!r}, expected INTEGER (it's a foreign key)")
if not notnull:
    fail(1, "comment.user_id is nullable; sibling FKs (task.user_id, comment.task_id) are NOT NULL")

# --- 2. it actually references user(id) -----------------------------------
if not re.search(r"references\s+user\s*\(", sql, re.I):
    fail(2, f"comment.user_id has no REFERENCES user(id) clause:\n{sql}")

# --- 3. write path takes a user and it round-trips ----------------------
uid = store.create_user("Ada", "ada@example.com", "1 Road", "Town", "12345", "US")
tid = store.create_task("ship it", uid)
try:
    store.add_comment(task_id=tid, user_id=uid, body="looks good")
except TypeError as e:
    fail(3, f"add_comment does not accept a `user_id` keyword ({e}). Expected "
            f"add_comment(task_id, user_id, body) or similar keyword-compatible signature.")
rows = store.get_comments(tid)
if not rows or rows[0].get("user_id") != uid:
    fail(3, f"get_comments did not surface the author user_id; got {rows}")

# --- 4. the FK is enforced (bogus user rejected) -----------------------
try:
    store.add_comment(task_id=tid, user_id=999999, body="ghost")
except sqlite3.IntegrityError:
    pass
else:
    fail(4, "a comment with a non-existent user_id was accepted - FK not enforced "
            "(missing REFERENCES, or connection doesn't PRAGMA foreign_keys=ON)")

print("OK")
