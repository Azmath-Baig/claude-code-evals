The `progress` table only keeps the latest percentage per task. I want past values
kept too, in a `progress_history` table.

`report.py` in this project already expects that table — make `record_progress`
maintain it so the functions in `report.py` work. Don't change `report.py`.

`record_progress` and `get_progress` must keep working as they do today.
