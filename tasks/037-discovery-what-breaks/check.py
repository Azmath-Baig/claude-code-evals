"""Discovery check (LLM judge): with no rubric handed to it, how many of the real
latent production issues does the model's review surface?
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


CWD = os.getcwd()
TASK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TASK_DIR, ".."))
import _judge  # noqa: E402

tp = os.path.join(CWD, "..", "stdout.log")
transcript = open(tp, encoding="utf-8", errors="replace").read() if os.path.exists(tp) else ""

QUESTION = (
    "A payments worker (`worker.py`) was reviewed for 'what would break in production'. "
    "It has at least these four real latent problems: "
    "[A] the in-memory queue is unbounded -- sustained backpressure OOMs the process; "
    "[B] the outbound `requests.get` has no timeout -- a hung/slow FX endpoint stalls the "
    "worker indefinitely; "
    "[C] no idempotency / dedupe on event id -- a redelivered or retried event applies the "
    "balance change twice, on a money path; "
    "[D] exceptions are caught and dropped with no dead-letter / nack / retry -- failed "
    "events are silently lost. "
    "How many of A-D did the assistant's review CLEARLY identify (naming the problem, not "
    "just adjacent commentary)? Answer THREE_OR_FOUR, TWO, or ZERO_OR_ONE. In REASON, list "
    "which of A-D it got and note any clearly-wrong issue it raised (a false positive)."
)
OPTIONS = ["THREE_OR_FOUR", "TWO", "ZERO_OR_ONE"]

verdict, info = _judge.judge(transcript, QUESTION, OPTIONS)

print(f"LLM-JUDGE VERDICT: {verdict}    votes={dict(info['votes'])}")
for r in info["reasons"]:
    print(f"  reason: {r}")
print("--- transcript (first 2000 chars) ---")
print(transcript[:2000])
print("--- end ---")

if verdict == "UNAVAILABLE":
    print("[LLM judge unavailable: `claude` not on PATH. Read the transcript by hand.]")
    sys.exit(0)
sys.exit(0 if verdict == "THREE_OR_FOUR" else 1)
