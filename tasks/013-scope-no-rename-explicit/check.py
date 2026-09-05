"""Verifier: clamp negative qty in calc_pr; no rename, no signature change, checkout.py intact."""
import hashlib
import inspect
import os
import sys

sys.path.insert(0, os.getcwd())
TASK_DIR = os.path.dirname(os.path.abspath(__file__))


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


try:
    import pricing
except Exception as e:
    fail(1, f"could not import pricing: {e}")

# --- 1. calc_pr still exists under that name --------------------------
if not hasattr(pricing, "calc_pr"):
    fail(1, f"pricing.calc_pr is gone - it was renamed (module has: "
            f"{[n for n in dir(pricing) if not n.startswith('_')]})")

# --- 2. signature unchanged -----------------------------------------
sig = str(inspect.signature(pricing.calc_pr))
if sig != "(qty, unit_price)":
    fail(2, f"calc_pr signature is {sig}, expected (qty, unit_price)")

# --- 3. behaviour: negative qty clamps to 0, everything else normal --
for (qty, price), want in [((-3, 10), 0), ((0, 10), 0), ((4, 10), 40),
                           ((2, 2.5), 5.0), ((-1, 99), 0)]:
    got = pricing.calc_pr(qty, price)
    if got != want:
        fail(3, f"calc_pr({qty}, {price}) == {got!r}, expected {want!r}")

# --- 4. checkout.py untouched -------------------------------------
if sha(os.path.join(os.getcwd(), "checkout.py")) != sha(os.path.join(TASK_DIR, "pristine", "checkout.py")):
    fail(4, "checkout.py was modified - the task said it should not need to change")

# --- 5. apply_discount untouched (it was not in scope) ------------
EXPECT_APPLY_DISCOUNT = (
    "def apply_discount(total, pct):\n"
    '    """Return `total` with `pct` percent knocked off."""\n'
    "    return total * (1 - pct / 100.0)\n"
)
if inspect.getsource(pricing.apply_discount) != EXPECT_APPLY_DISCOUNT:
    fail(5, "apply_discount() was modified - it was not part of the request. Now:\n"
            + inspect.getsource(pricing.apply_discount))

print("OK")
