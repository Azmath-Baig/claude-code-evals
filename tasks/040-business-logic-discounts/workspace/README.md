# pricing

`price_order(subtotal_cents, discounts, customer)` applies a list of stacked discounts (percent / fixed) to an order total, honouring a per-customer price floor and a lifetime discount cap. Full contract in the `price_order` docstring.
