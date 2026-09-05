# app data store

`store.py` defines the full application schema (accounts, projects, tasks, labels,
comments, attachments, sessions, audit log, settings) plus a `progress` table that
holds the current progress percentage per task.

`record_progress(task_name, percent)` updates progress; `get_progress(task_name)` reads it.
