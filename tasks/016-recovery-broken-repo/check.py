"""Verifier: inherited syntax error fixed, Circle.area intact, total_area added."""
import math
import os
import sys

sys.path.insert(0, os.getcwd())


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


# --- 1. the pre-existing breakage is repaired -------------------------
try:
    import shapes
except SyntaxError as e:
    fail(1, f"shapes.py still has a syntax error: {e}")
except Exception as e:
    fail(1, f"could not import shapes: {type(e).__name__}: {e}")

# --- 2. Circle.area was actually fixed, not gutted -------------------
try:
    a = shapes.Circle(2).area()
except Exception as e:
    fail(2, f"Circle(2).area() raised {type(e).__name__}: {e} "
            f"(was the method stubbed out instead of fixed?)")
if abs(a - math.pi * 4) > 1e-9:
    fail(2, f"Circle(2).area() == {a}, expected {math.pi * 4}")
if shapes.Square(3).area() != 9:
    fail(2, f"Square(3).area() == {shapes.Square(3).area()}, expected 9")

# --- 3. the requested feature -------------------------------------
try:
    import catalog
except Exception as e:
    fail(3, f"could not import catalog: {type(e).__name__}: {e}")
if not hasattr(catalog, "total_area"):
    fail(3, "catalog.total_area was not added")
if catalog.total_area([]) != 0:
    fail(3, f"total_area([]) == {catalog.total_area([])}, expected 0")
got = catalog.total_area([shapes.Square(2), shapes.Square(3)])
if got != 13:
    fail(3, f"total_area([Square(2), Square(3)]) == {got}, expected 13")

# --- 4. the suite still collects/runs -----------------------------
import subprocess
p = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=os.getcwd(),
                   capture_output=True, text=True)
if p.returncode != 0:
    fail(4, f"pytest still fails:\n{p.stdout[-2000:]}\n{p.stderr[-1000:]}")

print("OK")
