# projects_api

A tiny in-memory project API. Callers pass their `user_id`. Each project has an
`owner_id`. Mutation entry points: `update_project`, `delete_project`, `add_task`,
`update_task`, `bulk_update`. Reads: `get_project`.
