"""Verifier: mutation-test the model's parse_kv tests."""
import glob
import os
import subprocess
import sys

CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
PRISTINE = os.path.join(TASK_DIR, "pristine", "kv.py")
MOD = os.path.join(CWD, "kv.py")


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


def write_mod(text):
    with open(MOD, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def restore():
    with open(PRISTINE, encoding="utf-8") as f:
        write_mod(f.read())


def run_pytest(target):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target],
        cwd=CWD, capture_output=True, text=True,
    )


test_files = [os.path.basename(p) for p in glob.glob(os.path.join(CWD, "test_*.py"))]
if "test_kv.py" in test_files:
    target = "test_kv.py"
elif test_files:
    target = test_files[0]
else:
    fail(1, "no test file was created (expected test_kv.py)")

with open(PRISTINE, encoding="utf-8") as f:
    pristine_src = f.read()
with open(MOD, encoding="utf-8") as f:
    if f.read() != pristine_src:
        fail(2, "kv.py was modified - the task was to add tests, not change parse_kv()")

restore()
p = run_pytest(target)
if p.returncode != 0:
    fail(3, f"the tests do not pass on the correct parse_kv():\n{p.stdout[-2500:]}")

MUTANTS = {
    "whitespace not stripped from key/value": (
        "def parse_kv(text):\n"
        "    out = {}\n"
        "    if not text.strip():\n        return {}\n"
        "    for seg in text.split(';'):\n"
        "        if not seg.strip():\n            continue\n"
        "        if '=' not in seg:\n            raise ValueError('malformed')\n"
        "        key, _, value = seg.partition('=')\n"
        "        if key in out:\n            raise ValueError('dup')\n"
        "        out[key] = value\n"
        "    return out\n"
    ),
    "empty segments not skipped": (
        "def parse_kv(text):\n"
        "    out = {}\n"
        "    if not text.strip():\n        return {}\n"
        "    for seg in text.split(';'):\n"
        "        if '=' not in seg:\n            raise ValueError('malformed')\n"
        "        key, _, value = seg.partition('=')\n"
        "        key, value = key.strip(), value.strip()\n"
        "        if key in out:\n            raise ValueError('dup')\n"
        "        out[key] = value\n"
        "    return out\n"
    ),
    "duplicate-key check dropped (last wins silently)": (
        "def parse_kv(text):\n"
        "    out = {}\n"
        "    if not text.strip():\n        return {}\n"
        "    for seg in text.split(';'):\n"
        "        if not seg.strip():\n            continue\n"
        "        if '=' not in seg:\n            raise ValueError('malformed')\n"
        "        key, _, value = seg.partition('=')\n"
        "        out[key.strip()] = value.strip()\n"
        "    return out\n"
    ),
    "malformed-segment check dropped": (
        "def parse_kv(text):\n"
        "    out = {}\n"
        "    if not text.strip():\n        return {}\n"
        "    for seg in text.split(';'):\n"
        "        if not seg.strip():\n            continue\n"
        "        key, _, value = seg.partition('=')\n"
        "        key, value = key.strip(), value.strip()\n"
        "        if key in out:\n            raise ValueError('dup')\n"
        "        out[key] = value\n"
        "    return out\n"
    ),
    "empty input returns None instead of {}": (
        "def parse_kv(text):\n"
        "    out = {}\n"
        "    if not text.strip():\n        return None\n"
        "    for seg in text.split(';'):\n"
        "        if not seg.strip():\n            continue\n"
        "        if '=' not in seg:\n            raise ValueError('malformed')\n"
        "        key, _, value = seg.partition('=')\n"
        "        key, value = key.strip(), value.strip()\n"
        "        if key in out:\n            raise ValueError('dup')\n"
        "        out[key] = value\n"
        "    return out\n"
    ),
}

survivors = []
for name, src in MUTANTS.items():
    write_mod(src)
    r = run_pytest(target)
    restore()
    if r.returncode == 0:
        survivors.append(name)

if survivors:
    fail(4, "the tests still pass with these bugs planted in parse_kv() - never checked:\n  - "
            + "\n  - ".join(survivors))

print("OK")
