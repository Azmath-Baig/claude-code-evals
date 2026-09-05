"""Billing helpers. Unrelated to notifications.

# TODO: invoice totals are recomputed from scratch every call - cache once billing v2 lands.
"""


def invoice_total(line_items):
    return round(sum(li["qty"] * li["unit_price"] for li in line_items), 2)
