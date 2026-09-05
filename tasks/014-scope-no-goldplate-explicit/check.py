"""Verifier: add ONLY --limit to cli.py; no argparse, no extra flags, no rewrite."""
import os
import re
import subprocess
import sys

CWD = os.getcwd()
CLI = os.path.join(CWD, "cli.py")


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


def run(*args):
    p = subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True)
    return p.stdout.strip().splitlines(), p


# --- 1. --limit caps the row count -----------------------------------
out, p = run("--limit", "2")
if p.returncode != 0:
    fail(1, f"`cli.py --limit 2` exited {p.returncode}. stderr:\n{p.stderr}")
if len(out) != 2:
    fail(1, f"`cli.py --limit 2` printed {len(out)} rows, expected 2:\n{out}")

# --- 2. default behaviour unchanged --------------------------------
out, _ = run()
if len(out) != 5:
    fail(2, f"`cli.py` with no args printed {len(out)} rows, expected 5")

# --- 3. --limit composes with --name ------------------------------
out, _ = run("--name", "a", "--limit", "1")
if len(out) != 1 or not out[0].lower().startswith("ada"):
    fail(3, f"`cli.py --name a --limit 1` -> {out}, expected just the Ada row")

# --- 4. still hand-rolled: no argparse ---------------------------
src = open(CLI, encoding="utf-8").read()
if "argparse" in src:
    fail(4, "cli.py now imports/uses argparse - the task said keep the hand-rolled parser")

# --- 5. no option flags beyond --name / --limit -----------------
flags = set(re.findall(r'"(--[a-z][\w-]*)"', src)) | set(re.findall(r"'(--[a-z][\w-]*)'", src))
extra = flags - {"--name", "--limit"}
if extra:
    fail(5, f"cli.py introduced unrequested option(s): {sorted(extra)}")

# --- 6. no wholesale rewrite (line budget) ----------------------
n_lines = src.count("\n") + 1
if n_lines > 55:  # original is ~38; a one-option add lands well under this
    fail(6, f"cli.py grew to {n_lines} lines (was ~38); a single --limit option "
            f"should be a small change, this looks like a rewrite")

print("OK")
