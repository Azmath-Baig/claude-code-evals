"""Payments."""


def charge(account, cents):
    """Charge `cents` (a positive integer) to `account`, returning the new balance."""
    if cents <= 0:
        raise ValueError("charge amount must be positive")
    account["balance"] -= cents
    return account["balance"]


def refund(account, cents):
    if cents <= 0:
        raise ValueError("refund amount must be positive")
    account["balance"] += cents
    return account["balance"]
