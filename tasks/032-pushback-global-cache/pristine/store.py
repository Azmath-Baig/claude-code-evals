"""User lookups (pretend this is a thin wrapper over a database)."""

_USERS = {
    1: {"id": 1, "name": "Ada", "role": "admin"},
    2: {"id": 2, "name": "Bo", "role": "user"},
}


def get_user(user_id):
    """Fetch a user's current record."""
    row = _USERS.get(user_id)
    return dict(row) if row else None


def set_role(user_id, role):
    """Change a user's role. Takes effect immediately."""
    _USERS[user_id]["role"] = role
