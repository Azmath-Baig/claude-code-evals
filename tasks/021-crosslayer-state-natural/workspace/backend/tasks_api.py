"""Backend: task state validation + serialization.

The set of valid states here MUST stay in sync with the frontend
(frontend/src/taskStatus.ts) — the UI renders a label, a colour and the allowed
transitions for every state this returns.
"""

TASK_STATES = ("open", "in_progress", "done")

# allowed forward transitions, keyed by current state
TRANSITIONS = {
    "open": ["in_progress"],
    "in_progress": ["done", "open"],
    "done": [],
}


def validate_state(state):
    if state not in TASK_STATES:
        raise ValueError(f"invalid task state: {state!r}")
    return state


def can_transition(current, target):
    validate_state(current)
    validate_state(target)
    return target in TRANSITIONS[current]


def serialize_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "state": validate_state(row["state"]),
        "next_states": list(TRANSITIONS[validate_state(row["state"])]),
    }
