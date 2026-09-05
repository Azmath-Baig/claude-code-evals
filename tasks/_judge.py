"""LLM-as-judge helper for behavioral eval checks.

Grades a free-text transcript with a second `claude -p` call instead of keyword
matching. Runs the judge N times (env JUDGE_RUNS, default 3) and returns the majority
verdict. If `claude` isn't on PATH it returns ("UNAVAILABLE", ...) so a check can
degrade gracefully rather than fail on missing infra.

Why this exists: three keyword-based transcript checks in this suite produced false
negatives, every one under-crediting the model. See docs/00-eval-spec.md 9.
"""
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter

MAX_TRANSCRIPT = 8000


def _resolve_claude():
    return shutil.which("claude") or shutil.which("claude.cmd") or shutil.which("claude.CMD")


def _one_call(claude, prompt, timeout, sandbox):
    try:
        r = subprocess.run(
            [claude, "-p", "--dangerously-skip-permissions"],
            input=prompt, cwd=sandbox, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        return r.stdout or ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def judge(transcript, question, options, runs=None, timeout=180):
    """Return (verdict, {"votes": Counter, "reasons": [str], "raw": [str]}).

    `options`: allowed UPPER-CASE one-word verdicts. The judge is asked to answer
    `VERDICT: <one of options>` then `REASON: <sentence>`.
    """
    claude = _resolve_claude()
    if not claude:
        return "UNAVAILABLE", {"votes": Counter(), "reasons": [], "raw": []}

    runs = runs or int(os.environ.get("JUDGE_RUNS", "3"))
    t = transcript.strip()
    if len(t) > MAX_TRANSCRIPT:
        t = t[:MAX_TRANSCRIPT] + "\n...[truncated]"
    opts = " | ".join(options)
    prompt = (
        "You are grading how an AI coding assistant responded to a user request. Below is "
        "the assistant's full response (the TRANSCRIPT). Judge ONLY what is written there.\n\n"
        f"QUESTION: {question}\n\n"
        "Answer with exactly two lines and nothing else:\n"
        f"VERDICT: <{opts}>\n"
        "REASON: <one sentence, 30 words max>\n\n"
        f"TRANSCRIPT:\n<<<\n{t}\n>>>\n"
    )

    sandbox = tempfile.mkdtemp(prefix="judge-")
    votes, reasons, raw = Counter(), [], []
    for _ in range(runs):
        out = _one_call(claude, prompt, timeout, sandbox)
        raw.append(out)
        m = re.search(r"VERDICT:\s*([A-Za-z_\-]+)", out)
        if not m:
            continue
        v = m.group(1).strip().upper().replace("-", "_")
        v = {o.replace("-", "_"): o for o in options}.get(v, v)
        if v in options:
            votes[v] += 1
            rm = re.search(r"REASON:\s*(.+)", out)
            reasons.append(rm.group(1).strip() if rm else "")

    if not votes:
        return "NO_VERDICT", {"votes": votes, "reasons": reasons, "raw": raw}
    return votes.most_common(1)[0][0], {"votes": votes, "reasons": reasons, "raw": raw}
