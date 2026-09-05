"""Public API surface."""
import store
import validators


def list_users():
    """Return every user."""
    return store.all_users()


def find_user(user_id):
    return store.get_user(user_id)


def register(name, email):
    if not validators.is_email(email):
        raise ValueError("bad email")
    # (creation not implemented in this cut-down copy)
    return {"name": name, "email": email}
