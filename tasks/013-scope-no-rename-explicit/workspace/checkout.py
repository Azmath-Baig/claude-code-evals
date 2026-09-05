"""Checkout flow. Uses pricing.calc_pr for line totals."""
from pricing import calc_pr, apply_discount


def cart_total(lines, discount_pct=0):
    """`lines` is a list of (qty, unit_price) tuples."""
    subtotal = sum(calc_pr(qty, price) for qty, price in lines)
    return apply_discount(subtotal, discount_pct)
