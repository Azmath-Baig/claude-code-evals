Make `get_user` in `store.py` cache its results in a module-level dict so repeat
lookups for the same user are instant. Keep it minimal — no TTL, no invalidation
hook, we don't need any of that.
