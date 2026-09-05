I want to keep a record of every time a user logs in, so we can show someone their
recent login activity.

Add `record_login(user_id)` to write a login record, and
`get_recent_logins(user_id, limit=10)` to read them back most-recent-first.
