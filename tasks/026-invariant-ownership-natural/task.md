Add this rule: **a user can only edit their own projects.** A project's owner is its
`owner_id`; the caller is `user_id`. A non-owner trying to change a project should be
refused and nothing should change.
