Add this rule: a user can only edit their own projects (owner = `owner_id`, caller =
`user_id`). A non-owner's attempt must be refused with nothing changed.

Apply it to every way a project can be mutated — `update_project`, `delete_project`,
`add_task`, `update_task`, and `bulk_update` — not just the obvious one.
