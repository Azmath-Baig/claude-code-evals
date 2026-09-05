# tasks slice

A thin full-stack slice of the task feature.

- **`backend/tasks_api.py`** — validates task `state`, computes allowed transitions,
  serializes a task for the API (`state` + `next_states`).
- **`backend/reporting.py`** — rollups (`state_counts`, `percent_done`).
- **`frontend/src/taskStatus.ts`** — renders each state: a display label, a colour, and
  the transition buttons to show (`nextStates`).
