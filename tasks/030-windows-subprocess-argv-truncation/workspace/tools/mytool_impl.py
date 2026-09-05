"""Implementation behind the `mytool` CLI (invoked via tools/mytool.cmd on Windows,
tools/mytool on Mac/Linux). Prints back whatever it was given, prefixed so a caller can
tell whether it arrived as a command-line argument or via stdin."""
import sys

if len(sys.argv) > 1:
    print("ARG:" + sys.argv[1])
else:
    print("STDIN:" + sys.stdin.read())
