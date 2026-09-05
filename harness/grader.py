#!/usr/bin/env python3
"""Grade a run: execute each task's verify script against the agent's workspace.

Usage:
    python harness/grader.py --run latest
    python harness/grader.py --run 20260904T101500Z-claude-code

A task passes iff its verify script exits 0. Verify scripts live at
tasks/<name>/verify.sh and are run with `bash` inside the mutated workspace.
Results are written to results/<run>/<task>/grade.json and a run-level
results/<run>/grades.json summary.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
RESULTS_DIR = ROOT / "results"


def find_bash():
    """Locate a bash interpreter. On Windows it is usually Git's, often not on PATH."""
    found = shutil.which("bash")
    if found:
        return found
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ]
    import os
    lad = os.environ.get("LOCALAPPDATA")
    if lad:
        candidates.append(str(Path(lad) / "Programs" / "Git" / "bin" / "bash.exe"))
    git = shutil.which("git")  # derive bash from a git on PATH
    if git:
        candidates.append(str(Path(git).resolve().parent.parent / "bin" / "bash.exe"))
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def resolve_run(name):
    if name == "latest":
        p = RESULTS_DIR / "latest.txt"
        if not p.exists():
            sys.exit("no latest run recorded; run runner.py first")
        name = p.read_text(encoding="utf-8").strip()
    run_dir = RESULTS_DIR / name
    if not run_dir.exists():
        sys.exit(f"no such run: {name}")
    return run_dir


def load_task_meta(task_name):
    """Optional tasks/<name>/task.json for {type, notes}. Falls back to name prefix."""
    p = TASKS_DIR / task_name / "task.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def grade_one(run_dir, task_name, timeout):
    task_dir = TASKS_DIR / task_name
    verify = task_dir / "verify.sh"
    workspace = run_dir / task_name / "workspace"
    if not verify.exists():
        return {"task": task_name, "passed": None, "reason": "no verify.sh"}
    if not workspace.exists():
        return {"task": task_name, "passed": None, "reason": "no workspace (runner skipped it?)"}

    # Prefer a task's check.py: pure Python, no bash dependency, and it always
    # runs against `workspace` (the mutated copy) because that is the cwd we set.
    # Fall back to verify.sh via bash only when there is no check.py (e.g. task 001).
    check_py = task_dir / "check.py"
    try:
        if check_py.exists():
            proc = subprocess.run(
                [sys.executable, str(check_py)],
                cwd=workspace, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
            )
        else:
            bash = find_bash()
            if not bash:
                sys.exit(f"{task_name} has no check.py and no `bash` was found for verify.sh. "
                         "Install Git for Windows, or add its bin/ to PATH.")
            proc = subprocess.run(
                [bash, str(verify)],
                cwd=workspace, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
            )
        passed = proc.returncode == 0
        out = (proc.stdout or "")[-4000:] + (proc.stderr or "")[-4000:]
    except subprocess.TimeoutExpired:
        passed, out = False, f"verify timed out after {timeout}s"
    except FileNotFoundError:
        sys.exit(f"could not execute verifier for {task_name}")

    (run_dir / task_name / "grade.json").write_text(
        json.dumps({"task": task_name, "passed": passed, "verify_output": out}, indent=2),
        encoding="utf-8",
    )
    return {"task": task_name, "passed": passed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="latest")
    ap.add_argument("--timeout", type=int, default=300, help="per-verify seconds")
    args = ap.parse_args()

    run_dir = resolve_run(args.run)
    task_dirs = sorted(d.name for d in run_dir.iterdir() if d.is_dir())

    rows = []
    for task_name in task_dirs:
        run_meta_p = run_dir / task_name / "run.json"
        run_meta = json.loads(run_meta_p.read_text(encoding="utf-8")) if run_meta_p.exists() else {}
        g = grade_one(run_dir, task_name, args.timeout)
        g["seconds"] = run_meta.get("seconds")
        g["timed_out"] = run_meta.get("timed_out")
        g["type"] = load_task_meta(task_name).get("type", task_name.split("-", 2)[-1])
        rows.append(g)
        mark = {True: "PASS", False: "FAIL", None: "N/A "}[g["passed"]]
        print(f"  {mark}  {task_name}")

    passed = sum(1 for r in rows if r["passed"] is True)
    total = sum(1 for r in rows if r["passed"] is not None)
    summary = {"run": run_dir.name, "passed": passed, "total": total, "rows": rows}
    (run_dir / "grades.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n{passed}/{total} passed.  next: python harness/report.py --run {run_dir.name}")


if __name__ == "__main__":
    main()
