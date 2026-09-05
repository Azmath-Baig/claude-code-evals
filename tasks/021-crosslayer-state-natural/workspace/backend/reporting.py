"""Backend: rollups over tasks. Unrelated to state validation.

# TODO: state_counts recomputes the full list on every call - cache it later.
"""
from collections import Counter

from tasks_api import validate_state


def state_counts(rows):
    counts = Counter(validate_state(r["state"]) for r in rows)
    return dict(counts)


def percent_done(rows):
    if not rows:
        return 0.0
    done = sum(1 for r in rows if r["state"] == "done")
    return round(100 * done / len(rows), 1)
