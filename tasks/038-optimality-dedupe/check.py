"""Verifier: dedupe must be correct AND scale ~linearly (the O(n^2) `x in list`
version is correct but fails the complexity probe)."""
import os
import random
import sys

CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CWD)
sys.path.insert(0, os.path.join(TASK_DIR, ".."))
import _optimality  # noqa: E402


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


import dedupe_util  # noqa: E402

# --- 1. correctness -------------------------------------------------
cases = [
    ([], []),
    ([1], [1]),
    ([3, 1, 3, 2, 1, 4], [3, 1, 2, 4]),
    (["a", "b", "a", "c", "b"], ["a", "b", "c"]),
    ([(1, 2), (3, 4), (1, 2)], [(1, 2), (3, 4)]),
    (list(range(100)) + list(range(100)), list(range(100))),
]
for inp, want in cases:
    try:
        got = dedupe_util.dedupe(list(inp))
    except Exception as e:
        fail(1, f"dedupe({inp!r}) raised {type(e).__name__}: {e}")
    if got != want:
        fail(1, f"dedupe({inp!r}) == {got!r}, expected {want!r}")

rnd = random.Random(7)
big = [rnd.randint(0, 5000) for _ in range(20000)]
seen, want = set(), []
for x in big:
    if x not in seen:
        seen.add(x); want.append(x)
if dedupe_util.dedupe(list(big)) != want:
    fail(1, "dedupe gave the wrong result / order on a large mixed input")

# --- 2. complexity: must scale ~linearly ---------------------------
def make_input(n):
    r = random.Random(1)
    return [r.randint(0, n // 2) for _ in range(n)]  # ~50% duplicates

verdict, detail = _optimality.classify(dedupe_util.dedupe, make_input)
print(f"complexity probe: {verdict}  |  {detail}")
if verdict == "superlinear":
    fail(2, "dedupe scales super-linearly - almost certainly an O(n^2) membership test "
            "(`x in result_list`). Use a set for seen-membership: O(n).")
if verdict == "inconclusive":
    print("  (probe inconclusive - not failing on it; re-run or widen sizes to confirm)")

print("OK")
