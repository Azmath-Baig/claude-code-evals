"""Task-tracker store (SQLite).

Conventions used throughout this codebase:
  * table names are singular:  user, task, comment
  * every table starts with:   id INTEGER PRIMARY KEY AUTOINCREMENT
  * foreign keys are:          <table>_id INTEGER NOT NULL REFERENCES <table>(id)
  * timestamps are:            created_at / updated_at, TEXT, ISO-8601 UTC
                               (use now_iso(); read back with parse_ts())
  * status columns are named `state`, TEXT, restricted to a module-level
    <THING>_STATES tuple AND a matching CHECK (state IN (...)) constraint
  * booleans, when needed, are is_<adj> INTEGER 0/1
"""
import sqlite3
from datetime import datetime, timezone

DB = "app.db"

TASK_STATES = ("open", "in_progress", "done")


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def parse_ts(s):
    """Every timestamp in this app is an ISO-8601 string. Parse one back to a datetime."""
    return datetime.fromisoformat(s)


def init_db():
    con = connect()
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS user (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            street      TEXT NOT NULL,
            city        TEXT NOT NULL,
            postal_code TEXT NOT NULL,
            country     TEXT NOT NULL,
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS task (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            state       TEXT NOT NULL DEFAULT 'open'
                        CHECK (state IN ('open', 'in_progress', 'done')),
            user_id     INTEGER NOT NULL REFERENCES user(id),
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS comment (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id     INTEGER NOT NULL REFERENCES task(id),
            body        TEXT NOT NULL,
            created_at  TEXT NOT NULL
        );
        """
    )
    con.commit()
    con.close()


def create_user(name, email, street, city, postal_code, country):
    con = connect()
    ts = now_iso()
    cur = con.execute(
        "INSERT INTO user (name, email, street, city, postal_code, country, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, email, street, city, postal_code, country, ts),
    )
    con.commit()
    uid = cur.lastrowid
    con.close()
    return uid


def get_user(user_id):
    con = connect()
    row = con.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    con.close()
    return dict(row) if row else None


def create_task(title, user_id):
    con = connect()
    ts = now_iso()
    cur = con.execute(
        "INSERT INTO task (title, user_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (title, user_id, ts, ts),
    )
    con.commit()
    tid = cur.lastrowid
    con.close()
    return tid


def get_task(task_id):
    con = connect()
    row = con.execute("SELECT * FROM task WHERE id = ?", (task_id,)).fetchone()
    con.close()
    return dict(row) if row else None


def set_task_state(task_id, state):
    con = connect()
    con.execute(
        "UPDATE task SET state = ?, updated_at = ? WHERE id = ?",
        (state, now_iso(), task_id),
    )
    con.commit()
    con.close()


def add_comment(task_id, body):
    con = connect()
    cur = con.execute(
        "INSERT INTO comment (task_id, body, created_at) VALUES (?, ?, ?)",
        (task_id, body, now_iso()),
    )
    con.commit()
    cid = cur.lastrowid
    con.close()
    return cid


def get_comments(task_id):
    con = connect()
    rows = con.execute(
        "SELECT * FROM comment WHERE task_id = ? ORDER BY created_at, id", (task_id,)
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]
