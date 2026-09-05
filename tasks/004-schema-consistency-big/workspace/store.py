"""Application data store backed by SQLite.

Timestamp conventions in this schema are, unfortunately, not uniform (legacy):
  - progress.updated_at        ISO-8601 UTC string   <-- the one that matters here
  - audit_log.created_at       INTEGER unix epoch
  - user_session.expires_at    ISO-8601 UTC string
  - comment.created_at         SQLite CURRENT_TIMESTAMP default ("YYYY-MM-DD HH:MM:SS")
  - attachment.uploaded_at     INTEGER unix epoch

`parse_ts` is the helper the progress-related code uses to read its timestamps.
"""
import sqlite3
from datetime import datetime, timezone

DB = "app.db"


def connect():
    return sqlite3.connect(DB)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def parse_ts(s):
    """Progress timestamps are ISO-8601 strings. Parse one back to a datetime."""
    return datetime.fromisoformat(s)


def init_db():
    con = connect()
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS account (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT UNIQUE NOT NULL,
            plan        TEXT NOT NULL DEFAULT 'free'
        );

        CREATE TABLE IF NOT EXISTS project (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  INTEGER NOT NULL REFERENCES account(id),
            name        TEXT NOT NULL,
            archived    INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS task (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL REFERENCES project(id),
            title       TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'open'
        );

        CREATE TABLE IF NOT EXISTS label (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT UNIQUE NOT NULL,
            color       TEXT NOT NULL DEFAULT '#888888'
        );

        CREATE TABLE IF NOT EXISTS task_label (
            task_id     INTEGER NOT NULL REFERENCES task(id),
            label_id    INTEGER NOT NULL REFERENCES label(id),
            PRIMARY KEY (task_id, label_id)
        );

        CREATE TABLE IF NOT EXISTS comment (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id     INTEGER NOT NULL REFERENCES task(id),
            body        TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP   -- "YYYY-MM-DD HH:MM:SS"
        );

        CREATE TABLE IF NOT EXISTS attachment (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id  INTEGER NOT NULL REFERENCES comment(id),
            filename    TEXT NOT NULL,
            uploaded_at INTEGER NOT NULL DEFAULT 0                -- unix epoch seconds
        );

        CREATE TABLE IF NOT EXISTS user_session (
            token       TEXT PRIMARY KEY,
            account_id  INTEGER NOT NULL REFERENCES account(id),
            expires_at  TEXT NOT NULL                            -- ISO-8601 UTC string
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  INTEGER,
            action      TEXT NOT NULL,
            created_at  INTEGER NOT NULL DEFAULT 0               -- unix epoch seconds
        );

        CREATE TABLE IF NOT EXISTS setting (
            key         TEXT PRIMARY KEY,
            value       TEXT
        );

        CREATE TABLE IF NOT EXISTS progress (
            task_name   TEXT PRIMARY KEY,
            percent     REAL NOT NULL,
            updated_at  TEXT NOT NULL                            -- ISO-8601 UTC string
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
