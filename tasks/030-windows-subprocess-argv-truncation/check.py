"""Verifier: call_tool must deliver a multi-line prompt to `mytool` intact."""
import os
import sys

sys.path.insert(0, os.getcwd())


def fail(n, msg):
    print(f"[FAIL {n}] {msg}")
    sys.exit(1)


try:
    import caller
except Exception as e:
    fail(0, f"could not import caller.py: {type(e).__name__}: {e}")

# --- 1. a simple single-line call round-trips --------------------------
try:
    out = caller.call_tool("hello")
except Exception as e:
    fail(1, f"call_tool('hello') raised {type(e).__name__}: {e}")
if "hello" not in out:
    fail(1, f"call_tool('hello') -> {out!r}; expected it to contain 'hello'")

# --- 2. a multi-line prompt must arrive at the tool INTACT -------------
prompt = "line one\nline two\nline three"
try:
    out = caller.call_tool(prompt)
except Exception as e:
    fail(2, f"call_tool() with a multi-line prompt raised {type(e).__name__}: {e}")

missing = [line for line in ("line one", "line two", "line three") if line not in out]
if missing:
    fail(2, f"the multi-line prompt was NOT passed to mytool intact - missing {missing} "
            f"from its output ({out!r}). This is the classic Windows .cmd-shim argv-"
            f"truncation bug: a multi-line string passed as a command-line ARGUMENT gets "
            f"silently cut at the first newline (no error). Pass it via stdin instead.")

print("OK")
