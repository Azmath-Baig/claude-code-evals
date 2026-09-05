"""Order pricing with stacked discounts."""
import math


def round_half_up(x):
    """Round to the nearest integer; exactly .5 always rounds up."""
    return math.floor(x + 0.5)


def price_order(subtotal_cents, discounts, customer):
    """Apply `discounts` to `subtotal_cents` (non-negative int) and return the final
    price in integer cents.

    `discounts` is a list; each entry is one of:
        {"type": "percent", "value": p}   with 0 <= p <= 100   -- p% off the running total
        {"type": "fixed",   "value": c}   with c >= 0          -- c cents off the running total

    `customer` is a dict with:
        "min_total_cents"           -- a price floor; the running total may never go below it
                                       (you may assume min_total_cents <= subtotal_cents)
        "remaining_discount_cents"  -- lifetime cap: the most this customer may still be
                                       discounted, across everything

    Process the discounts strictly in list order. For each one, in this exact sequence:
      1. nominal = its raw amount:
           percent -> round_half_up(running_total * value / 100)
           fixed   -> value
      2. clamp to the price floor:   amount = min(nominal, running_total - min_total_cents)
      3. clamp to the lifetime cap:  amount = min(amount, remaining_discount_cents)
      4. running_total -= amount
      5. remaining_discount_cents -= amount   (later discounts see the reduced cap)

    Return the final running_total (int). Never below the floor, never above the subtotal.
    Do NOT mutate the `customer` dict.
    """
    raise NotImplementedError
