"""Account limits."""

FREE_TIER_PROJECT_LIMIT = 10  # matches the current production config (see ops runbook)


def is_free_tier(user):
    return user.get("plan", "free") == "free"
