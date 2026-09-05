"""Shared complexity probe for the optimality tasks.

Times a single-argument function at growing input sizes and classifies how its
runtime scales. Uses min-of-trials (least noisy) and a wide size ratio so O(n) vs
O(n^2) is unmistakable even with OS jitter.
"""
import time


def measure(fn, make_input, sizes, trials=3):
    """Return {size: best_seconds}."""
    out = {}
    for n in sizes:
        data = make_input(n)
        best = float("inf")
        for _ in range(trials):
            d = list(data) if isinstance(data, list) else data
            t0 = time.perf_counter()
            fn(d)
            best = min(best, time.perf_counter() - t0)
        out[n] = best
    return out


def classify(fn, make_input, small=2000, big=32000, trials=4):
    """Scale `small` -> `big` (16x). Return (verdict, detail).

    Expected time ratio for the 16x size jump:
      O(n)        ~16      O(n log n)  ~22      O(n^2)  ~256
    verdict in {"linear-ish", "superlinear", "inconclusive"}.
    """
    sizes = [small, big]
    # if big is too fast to time reliably, scale everything up once
    t = measure(fn, make_input, sizes, trials)
    if t[big] < 0.004:
        sizes = [small * 4, big * 4]
        t = measure(fn, make_input, sizes, trials)
        small, big = sizes
    if t[small] <= 0:
        return "inconclusive", f"small size too fast to time ({t})"
    ratio = t[big] / t[small]
    detail = f"t[{small}]={t[small]*1e3:.1f}ms  t[{big}]={t[big]*1e3:.1f}ms  ratio={ratio:.1f} (16x input)"
    if ratio <= 40:
        return "linear-ish", detail
    if ratio >= 90:
        return "superlinear", detail
    return "inconclusive", detail
