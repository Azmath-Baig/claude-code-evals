"""Account transfers. Amounts are integer cents."""


def transfer(accounts, src, dst, amount):
    """Move `amount` cents from accounts[src] to accounts[dst], in place.

    Rules:
      - amount must be > 0, else raise ValueError and change nothing
      - accounts[src] must be >= amount, else raise ValueError and change nothing
        (no partial transfer)
    """
    accounts[src] -= amount
    accounts[dst] += amount
    return accounts
