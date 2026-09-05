"""In-memory user store. Pretend this is a thin wrapper over a real database."""

_USERS = [
    {"id": 1, "name": "Ada",    "email": "ada@example.com"},
    {"id": 2, "name": "Bo",     "email": "bo@example.com"},
    {"id": 3, "name": "Cy",     "email": "cy@example.com"},
    {"id": 4, "name": "Di",     "email": "di@example.com"},
    {"id": 5, "name": "Ez",     "email": "ez@example.com"},
    {"id": 6, "name": "Fi",     "email": "fi@example.com"},
    {"id": 7, "name": "Gil",    "email": "gil@example.com"},
]


def all_users():
    return [dict(u) for u in _USERS]


def get_user(user_id):
    for u in _USERS:
        if u["id"] == user_id:
            return dict(u)
    return None


def user_count():
    # TODO: this recomputes the whole list just to count it - do it directly
    return len(all_users())
