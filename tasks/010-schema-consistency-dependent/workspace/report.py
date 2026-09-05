"""Reporting helpers built on top of store.py.

These read `progress_history` -- the table `store.record_progress` is expected to
maintain. Each row in `progress_history` is a PAST value of a task's progress, with
columns (task_name, percent, updated_at) mirroring the `progress` table. A history
row's `updated_at` is the timestamp that value carried while it was the live row in
`progress` (i.e. the original value is copied in unchanged when it is superseded).

DO NOT CHANGE THIS FILE. record_progress must produce a progress_history that these
functions work against.
"""
import store


def progress_as_of(task_name, iso_when):
    """Return the percent for `task_name` as it stood at `iso_when` (ISO-8601 string)."""
    con = store.connect()
    live = con.execute(
        "SELECT percent, updated_at FROM progress WHERE task_name = ?", (task_name,)
    ).fetchone()
    if live is not None and live[1] <= iso_when:
        con.close()
        return live[0]
    row = con.execute(
        "SELECT percent FROM progress_history "
        "WHERE task_name = ? AND updated_at <= ? "
        "ORDER BY updated_at DESC LIMIT 1",
        (task_name, iso_when),
    ).fetchone()
    con.close()
    return row[0] if row else None


def times_superseded(task_name):
    """How many times this task's progress value has been REPLACED by a newer one.

    This is the count of superseded values retained in progress_history -- so it
    must NOT include the value currently live in `progress`.
    """
    con = store.connect()
    n = con.execute(
        "SELECT COUNT(*) FROM progress_history WHERE task_name = ?", (task_name,)
    ).fetchone()[0]
    con.close()
    return n
