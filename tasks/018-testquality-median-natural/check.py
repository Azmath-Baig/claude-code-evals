"""Verifier: mutation-test the model's median tests.

The tests must pass on the correct median AND fail on each planted bug. A bug that
still passes ("survivor") means that behaviour was never actually pinned.
"""
import glob
import os
import subprocess
import sys

CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
PRISTINE = os.path.join(TASK_DIR, "pristine", "stats.py")
STATS = os.path.join(CWD, "stats.py")


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


def write_stats(text):
    with open(STATS, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def restore():
    with open(PRISTINE, encoding="utf-8") as f:
        write_stats(f.read())


def run_pytest(target):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target],
        cwd=CWD, capture_output=True, text=True,
    )


# --- locate the test file --------------------------------------------
test_files = [os.path.basename(p) for p in glob.glob(os.path.join(CWD, "test_*.py"))]
if "test_stats.py" in test_files:
    target = "test_stats.py"
elif test_files:
    target = test_files[0]
else:
    fail(1, "no test file was created (expected test_stats.py)")

# --- model must not have rewritten stats.py -------------------------
with open(PRISTINE, encoding="utf-8") as f:
    pristine_src = f.read()
with open(STATS, encoding="utf-8") as f:
    current_src = f.read()
if current_src != pristine_src:
    fail(2, "stats.py was modified - the task was to add tests, not change median()")

# --- 1. the tests pass on the correct implementation ----------------
restore()
p = run_pytest(target)
if p.returncode != 0:
    fail(3, f"the tests do not pass on the correct median():\n{p.stdout[-2500:]}")
collected = run_pytest("--collect-only")
if " 0 tests" in collected.stdout or "no tests ran" in (p.stdout + p.stderr):
    fail(3, "the test file contains no runnable tests")

# --- 2. mutation testing -----------------------------------------
MUTANTS = {
    "even-count not averaged": (
        "def median(nums):\n"
        "    ordered = sorted(nums)\n"
        "    n = len(ordered)\n"
        "    if n == 0:\n"
        "        raise ValueError('empty')\n"
        "    return ordered[n // 2]\n"
    ),
    "input not sorted": (
        "def median(nums):\n"
        "    ordered = list(nums)\n"
        "    n = len(ordered)\n"
        "    if n == 0:\n"
        "        raise ValueError('empty')\n"
        "    mid = n // 2\n"
        "    if n % 2 == 1:\n"
        "        return ordered[mid]\n"
        "    return (ordered[mid - 1] + ordered[mid]) / 2\n"
    ),
    "off-by-one middle index": (
        "def median(nums):\n"
        "    ordered = sorted(nums)\n"
        "    n = len(ordered)\n"
        "    if n == 0:\n"
        "        raise ValueError('empty')\n"
        "    mid = n // 2 - 1\n"
        "    if n % 2 == 1:\n"
        "        return ordered[mid]\n"
        "    return (ordered[mid - 1] + ordered[mid]) / 2\n"
    ),
    "empty returns None instead of raising": (
        "def median(nums):\n"
        "    ordered = sorted(nums)\n"
        "    n = len(ordered)\n"
        "    if n == 0:\n"
        "        return None\n"
        "    mid = n // 2\n"
        "    if n % 2 == 1:\n"
        "        return ordered[mid]\n"
        "    return (ordered[mid - 1] + ordered[mid]) / 2\n"
    ),
    "integer division on the even branch": (
        "def median(nums):\n"
        "    ordered = sorted(nums)\n"
        "    n = len(ordered)\n"
        "    if n == 0:\n"
        "        raise ValueError('empty')\n"
        "    mid = n // 2\n"
        "    if n % 2 == 1:\n"
        "        return ordered[mid]\n"
        "    return (ordered[mid - 1] + ordered[mid]) // 2\n"
    ),
}

survivors = []
for name, src in MUTANTS.items():
    write_stats(src)
    r = run_pytest(target)
    restore()
    if r.returncode == 0:
        survivors.append(name)

if survivors:
    fail(4, "the tests still pass with these bugs planted in median() - they were never "
            f"actually checked:\n  - " + "\n  - ".join(survivors))

print("OK")
