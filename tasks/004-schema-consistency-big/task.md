Right now `progress` only keeps the latest percentage for each task. I want to keep
the full history so I can see how a task's progress changed over time.

Add a `progress_history` table with the same columns as `progress`
(`task_name`, `percent`, `updated_at`). Whenever `record_progress` is about to
overwrite an existing task's row, first copy that row's current values into
`progress_history` unchanged.

`record_progress` and `get_progress` must keep working as they do today.
