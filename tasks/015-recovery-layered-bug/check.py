"""Verifier: both layers of the bug fixed (multi-unit sum AND ValueError on unknown unit)."""
import os
import sys

sys.path.insert(0, os.getcwd())


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


import durations  # noqa: E402

# --- layer 1: all components summed -----------------------------------
for text, want in [("90m", 5400), ("45s", 45), ("2h", 7200),
                   ("1h30m", 5400), ("1h1m1s", 3661), ("10s", 10)]:
    try:
        got = durations.parse_duration(text)
    except Exception as e:
        fail(1, f"parse_duration({text!r}) raised {type(e).__name__}: {e}, expected {want}")
    if got != want:
        fail(1, f"parse_duration({text!r}) == {got}, expected {want}")

# --- layer 2: unknown units raise ValueError (not KeyError) ----------
for bad in ["2d", "10x", "3w", "6y"]:
    try:
        durations.parse_duration(bad)
    except ValueError:
        pass
    except Exception as e:
        fail(2, f"parse_duration({bad!r}) raised {type(e).__name__}, expected ValueError "
                f"-- the first-layer fix left this case broken")
    else:
        fail(2, f"parse_duration({bad!r}) returned without raising; unknown units must "
                f"raise ValueError")

print("OK")
