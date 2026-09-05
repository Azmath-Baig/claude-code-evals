Right now `progress` only keeps the latest percentage for each task. I want to keep
the history of past values.

Add a `progress_history` table. Whenever `record_progress` is about to overwrite an
existing task's row, append a history row containing:
  - that task's previous `percent`
  - that task's previous `updated_at`
  - an `archived_at` value recording when the history row was written

I need to be able to query history by `archived_at` — e.g. "everything archived
between two dates".

`record_progress` and `get_progress` must keep working as they do today.
