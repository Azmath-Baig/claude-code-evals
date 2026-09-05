# progress store

`store.py` keeps the current progress percentage for each task.
`record_progress(task_name, percent)` updates it; `get_progress(task_name)` reads it.

`report.py` provides point-in-time reporting on top of a `progress_history` table.
