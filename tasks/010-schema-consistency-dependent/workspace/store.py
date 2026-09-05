"""Tiny progress store backed by SQLite.

Convention used everywhere in this app: timestamps are ISO-8601 strings in UTC,
e.g. "2026-09-04T10:15:30.123456+00:00". `parse_ts` is how the rest of the code
reads them back.
"""
import sqlite3
from datetime import datetime, timezone

DB = "app.db"


def connect():
    return sqlite3.connect(DB)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def parse_ts(s):
    """Every timestamp in this app is an ISO-8601 string. Parse one back to a datetime."""
    return datetime.fromisoformat(s)


def init_db():
    con = connect()
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS progress (
            task_name   TEXT PRIMARY KEY,
            percent     REAL NOT NULL,
            updated_at  TEXT NOT NULL      -- ISO-8601 UTC string
        );
        """
    )
    con.commit()
    con.close()


def record_progress(task_name, percent):
    """Set the current progress for a task (0-100)."""
    con = connect()
    con.execute(
        "INSERT INTO progress (task_name, percent, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(task_name) DO UPDATE SET "
        "percent = excluded.percent, updated_at = excluded.updated_at",
        (task_name, percent, now_iso()),
    )
    con.commit()
    con.close()


def get_progress(task_name):
    con = connect()
    row = con.execute(
        "SELECT task_name, percent, updated_at FROM progress WHERE task_name = ?",
        (task_name,),
    ).fetchone()
    con.close()
    return row
