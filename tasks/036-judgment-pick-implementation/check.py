"""Judgment check (LLM judge): given three viable implementations and a concrete
scenario, does the model exercise engineering judgment — pick one, engage the
scenario's real constraints, and name the tradeoff — or recite textbook pros/cons?
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
    "The user asked which of three rate-limiter implementations (token bucket, fixed "
    "window, sliding log -- all in `impls/`, all in-process / per-instance) to ship for an "
    "API gateway that runs as 6 round-robin load-balanced instances, needs per-key limits "
    "(~10 req/s sustained, bursts to ~50), and has ~200k active keys. Classify the answer: "
    "STRONG = picks one clearly AND identifies that all three keep state per-instance, so "
    "6 instances multiply the effective per-key limit ~6x unless state is shared (e.g. "
    "Redis) or the config compensates, AND names what the chosen option gives up. "
    "PARTIAL = picks one with reasoning tied to THIS scenario (burst behaviour, "
    "per-key memory at 200k keys, boundary accuracy) but does not surface the "
    "distributed-state / 6x problem. "
    "WEAK = no clear pick, or generic textbook pros/cons not tied to the scenario."
)
OPTIONS = ["STRONG", "PARTIAL", "WEAK"]

verdict, info = _judge.judge(transcript, QUESTION, OPTIONS)

print(f"LLM-JUDGE VERDICT: {verdict}    votes={dict(info['votes'])}")
for r in info["reasons"]:
    print(f"  reason: {r}")
print("--- transcript (first 1800 chars) ---")
print(transcript[:1800])
print("--- end ---")

if verdict == "UNAVAILABLE":
    print("[LLM judge unavailable: `claude` not on PATH. Read the transcript by hand.]")
    sys.exit(0)
sys.exit(0 if verdict in ("STRONG", "PARTIAL") else 1)
