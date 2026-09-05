"""Verifier: extracting address columns should follow table/FK conventions and not break callers."""
import os
import re
import sys

sys.path.insert(0, os.getcwd())
if os.path.exists("app.db"):
    os.remove("app.db")
import store  # noqa: E402


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


ADDR = {"street", "city", "postal_code", "country"}

store.init_db()

# --- 1. callers still work: create_user(...6 args...) and get_user round-trip
try:
    uid = store.create_user("Ada", "ada@example.com", "1 Road", "Town", "12345", "DE")
except TypeError as e:
    fail(1, f"create_user no longer accepts (name, email, street, city, postal_code, country): {e}")
u = store.get_user(uid)
if u is None:
    fail(1, "get_user returned None for a freshly created user")
missing = [k for k in ("street", "city", "postal_code", "country") if u.get(k) is None]
if missing:
    fail(1, f"get_user no longer returns address field(s) {missing} - callers are broken. "
            f"get_user must join the new table. Got keys: {sorted(u)}")
if (u.get("street"), u.get("city"), u.get("postal_code"), u.get("country")) != \
   ("1 Road", "Town", "12345", "DE"):
    fail(1, f"get_user returned wrong address values: {u}")

# --- 2. the address columns are gone from `user` --------------------------
con = store.connect()
user_cols = {r[1] for r in con.execute("PRAGMA table_info(user)").fetchall()}
still_there = ADDR & user_cols
if still_there:
    fail(2, f"`user` still has address column(s) {sorted(still_there)} - they were not extracted")

# --- 3. there is a new table that holds all four address columns ---------
tables = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
).fetchall()]
addr_table = None
for t in tables:
    if t in ("user", "task", "comment"):
        continue
    tcols = {r[1] for r in con.execute(f"PRAGMA table_info({t})").fetchall()}
    if ADDR <= tcols:
        addr_table = t
        break
if not addr_table:
    con.close()
    fail(3, f"no new table contains all of {sorted(ADDR)}; tables present: {tables}")

# --- 4. the link follows the <table>_id ... REFERENCES convention -------
addr_sql = con.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (addr_table,)
).fetchone()[0]
user_sql = con.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name='user'"
).fetchone()[0]
con.close()

link_on_addr = bool(re.search(r"user_id\s+INTEGER[^,]*references\s+user\s*\(", addr_sql, re.I))
link_on_user = bool(re.search(r"\b\w+_id\s+INTEGER[^,]*references\s+" + re.escape(addr_table) + r"\s*\(",
                              user_sql, re.I))
if not (link_on_addr or link_on_user):
    fail(4, f"no conventional FK between `user` and `{addr_table}` "
            f"(expected `user_id INTEGER ... REFERENCES user(id)` on `{addr_table}`, "
            f"or `{addr_table}_id INTEGER ... REFERENCES {addr_table}(id)` on `user`).\n"
            f"{addr_table}: {addr_sql}\nuser: {user_sql}")

print("OK")
