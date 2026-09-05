"""Verifier: load_config handles JSON and a simple YAML subset, with no missing dependency."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.getcwd())


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


try:
    import config
except Exception as e:
    fail(1, f"could not import config: {type(e).__name__}: {e}")

# --- constraint: standard library only, no yaml dependency -----------
src = open(os.path.join(os.getcwd(), "config.py"), encoding="utf-8").read()
import re as _re
if _re.search(r"^\s*(import|from)\s+(yaml|pyyaml|ruamel)", src, _re.M):
    fail(1, "config.py imports a YAML package - the task said standard library only, "
            "no new dependency")

tmp = tempfile.mkdtemp()

# --- JSON still works exactly as before ------------------------------
jp = os.path.join(tmp, "a.json")
with open(jp, "w", encoding="utf-8") as f:
    json.dump({"x": 1, "y": "hi", "z": True}, f)
try:
    d = config.load_config(jp)
except Exception as e:
    fail(2, f"load_config on a .json file raised {type(e).__name__}: {e}")
if d != {"x": 1, "y": "hi", "z": True}:
    fail(2, f"load_config(a.json) == {d!r}, expected {{'x': 1, 'y': 'hi', 'z': True}}")

# --- YAML subset works, WITHOUT an unavailable dependency -----------
YAML = "name: test\ncount: 3\nratio: 1.5\nenabled: true\ndisabled: false\nnote: hello world\n"
for ext in (".yaml", ".yml"):
    yp = os.path.join(tmp, "c" + ext)
    with open(yp, "w", encoding="utf-8") as f:
        f.write(YAML)
    try:
        d = config.load_config(yp)
    except ModuleNotFoundError as e:
        fail(3, f"load_config on {ext} needs a missing package ({e}). Expected a hand-rolled "
                f"parser for the flat key:value subset described in the task.")
    except Exception as e:
        fail(3, f"load_config on a {ext} file raised {type(e).__name__}: {e}")

    if str(d.get("name")) != "test":
        fail(3, f"{ext}: name == {d.get('name')!r}, expected 'test'")
    if str(d.get("count")).strip() not in ("3", "3.0"):
        fail(3, f"{ext}: count == {d.get('count')!r}, expected 3")
    try:
        if float(d.get("ratio")) != 1.5:
            raise ValueError
    except (TypeError, ValueError):
        fail(3, f"{ext}: ratio == {d.get('ratio')!r}, expected 1.5")
    if d.get("enabled") not in (True, "true", "True"):
        fail(3, f"{ext}: enabled == {d.get('enabled')!r}, expected boolean true")
    if d.get("disabled") not in (False, "false", "False"):
        fail(3, f"{ext}: disabled == {d.get('disabled')!r}, expected boolean false")
    if str(d.get("note")) != "hello world":
        fail(3, f"{ext}: note == {d.get('note')!r}, expected 'hello world'")

print("OK")
