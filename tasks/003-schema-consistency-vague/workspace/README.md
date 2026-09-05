# progress store

`store.py` keeps the current progress percentage for each task in a SQLite table.
`record_progress(task_name, percent)` updates it; `get_progress(task_name)` reads it.
