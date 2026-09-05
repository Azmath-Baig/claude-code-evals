"""Pricing math."""


def calc_pr(qty, unit_price):
    """Line total for `qty` units at `unit_price` each."""
    return qty * unit_price


def apply_discount(total, pct):
    """Return `total` with `pct` percent knocked off."""
    return total * (1 - pct / 100.0)
