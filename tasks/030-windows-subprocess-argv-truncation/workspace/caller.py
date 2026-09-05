"""Wraps calling the local `mytool` CLI utility."""
import os

TOOL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "tools",
    "mytool.cmd" if os.name == "nt" else "mytool",
)


def call_tool(prompt: str) -> str:
    """Invoke `mytool` with `prompt` and return exactly what it printed.

    Must work on Windows. `prompt` may be several lines long.
    """
    raise NotImplementedError
