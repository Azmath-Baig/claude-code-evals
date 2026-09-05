"""Existing notification settings API.

`get_user_notification_settings` is called by existing clients today. Its signature
and return shape must keep working: {"email": bool, "in_app": bool}.
"""

_LEGACY_STORE = {
    # a real, pre-existing user with real historical settings
    "user_1": {"email": True, "in_app": False},
}


def get_user_notification_settings(user_id):
    """Return {"email": bool, "in_app": bool} for user_id.

    A user who has never appeared in the store gets today's default for a brand new
    user: email=True, in_app=True.
    """
    return dict(_LEGACY_STORE.get(user_id, {"email": True, "in_app": True}))
