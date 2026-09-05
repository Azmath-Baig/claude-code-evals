`list_users()` returns the whole list, which is getting big. Add pagination to it:
a `limit` and an `offset` argument, so callers can ask for one page at a time.
Default behaviour (no arguments) should still return everyone.
