"""Verifier: ~12 scenarios, each targeting one discount rule or interaction.
Reports rules-passed / N. Pass = all."""
import copy
import os
import sys

sys.path.insert(0, os.getcwd())
import pricing  # noqa: E402

C = lambda floor, cap: {"min_total_cents": floor, "remaining_discount_cents": cap}
P = lambda v: {"type": "percent", "value": v}
F = lambda v: {"type": "fixed", "value": v}

# (name, subtotal, discounts, customer, expected_total)
SCEN = [
    ("no discounts -> subtotal unchanged", 10000, [], C(0, 10**9), 10000),
    ("single fixed", 10000, [F(1500)], C(0, 10**9), 8500),
    ("single percent, half-up rounding", 1005, [P(50)], C(0, 10**9), 502),  # round_half_up(502.5)=503
    ("percent then fixed", 10000, [P(10), F(500)], C(0, 10**9), 8500),
    ("percent is computed on the REDUCED running total (order matters)",
     10000, [F(5000), P(50)], C(0, 10**9), 2500),                          # not 0
    ("floor clamps a discount mid-sequence", 10000, [F(9000)], C(3000, 10**9), 3000),
    ("later discount is a no-op once at the floor",
     10000, [F(9000), P(50)], C(3000, 10**9), 3000),
    ("lifetime cap clamps a discount", 10000, [F(5000)], C(0, 2000), 8000),
    ("cap exhausts mid-sequence", 10000, [F(3000), F(3000)], C(0, 4000), 6000),
    ("cap and floor bite the same discount", 10000, [F(8000)], C(6000, 3000), 7000),
    ("percent 100 with a floor", 10000, [P(100)], C(2000, 10**9), 2000),
    ("percent 0 / fixed 0 no-ops", 10000, [P(0), F(0)], C(0, 10**9), 10000),
]

passed, fails = 0, []
for name, sub, disc, cust, want in SCEN:
    cust_in = copy.deepcopy(cust)
    try:
        got = pricing.price_order(sub, [dict(d) for d in disc], cust_in)
    except Exception as e:
        fails.append(f"{name}: raised {type(e).__name__}: {e}")
        continue
    if got != want:
        fails.append(f"{name}: got {got}, expected {want}")
        continue
    if cust_in != cust:
        fails.append(f"{name}: mutated the customer dict ({cust} -> {cust_in})")
        continue
    passed += 1

print(f"DISCOUNT RULES PASSED: {passed}/{len(SCEN)}")
for f in fails:
    print(f"  [FAIL] {f}")

sys.exit(0 if passed == len(SCEN) else 1)
