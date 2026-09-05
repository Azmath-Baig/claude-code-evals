"""Verifier: first_unique_char must be correct AND scale ~linearly. The
`for c in s: if s.count(c) == 1` version is correct but O(n^2)."""
import os
import random
import sys
from collections import Counter

CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CWD)
sys.path.insert(0, os.path.join(TASK_DIR, ".."))
import _optimality  # noqa: E402


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


import textscan  # noqa: E402


def ref(s):
    c = Counter(s)
    for ch in s:
        if c[ch] == 1:
            return ch
    return None


CASES = [
    ("", None),
    ("a", "a"),
    ("aabb", None),
    ("aabbc", "c"),
    ("leetcode", "l"),
    ("loveleetcode", "v"),
    ("  x  ", "x"),          # spaces repeat, x is unique
    ("abcabd", "c"),
]
for s, want in CASES:
    try:
        got = textscan.first_unique_char(s)
    except Exception as e:
        fail(1, f"first_unique_char({s!r}) raised {type(e).__name__}: {e}")
    if got != want:
        fail(1, f"first_unique_char({s!r}) == {got!r}, expected {want!r}")

rnd = random.Random(5)
alpha = "abcdefghij"
blob = "".join(rnd.choice(alpha) for _ in range(30000)) + "Z" + "".join(rnd.choice(alpha) for _ in range(30000))
if textscan.first_unique_char(blob) != ref(blob):
    fail(1, "first_unique_char disagrees with a reference on a large input")

# --- complexity: must scale ~linearly ----------------------------
def make_input(n):
    r = random.Random(2)
    # all characters repeat -> worst case: the fn must scan everything
    half = "".join(r.choice("abcdefgh") for _ in range(n // 2))
    return half + half[::-1]

verdict, detail = _optimality.classify(textscan.first_unique_char, make_input, small=2000, big=32000)
print(f"complexity probe: {verdict}  |  {detail}")
if verdict == "superlinear":
    fail(2, "first_unique_char scales super-linearly - almost certainly `s.count(c)` inside "
            "the loop (O(n) per char -> O(n^2)). Build a frequency map once (Counter/dict), "
            "then a single scan: O(n).")
if verdict == "inconclusive":
    print("  (probe inconclusive - not failing on it)")

print("OK")
