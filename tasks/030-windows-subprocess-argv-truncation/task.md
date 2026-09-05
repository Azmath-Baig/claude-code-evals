Implement `call_tool(prompt)` in `caller.py`. It should invoke the `mytool` CLI utility
(path given by the `TOOL` constant) with `prompt`, and return exactly what it printed.

This needs to work reliably on Windows, and `prompt` can be several lines long.
