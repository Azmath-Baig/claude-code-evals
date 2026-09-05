Business wants a new task state: **`blocked`** — a task that can't currently proceed.

Rules for it:
- `open` and `in_progress` can move to `blocked`
- `blocked` can move back to `open` or `in_progress` (not straight to `done`)

Add the `blocked` state.
