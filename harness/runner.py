#!/usr/bin/env python3
"""Run a coding agent against every task in tasks/ and save transcripts.

Usage:
    python harness/runner.py --agent claude-code
    python harness/runner.py --agent aider --tasks 001-stacktrace-bugfix 002-...
    python harness/runner.py --agent claude-code --timeout 600

Each run creates results/<timestamp>-<agent>/ with one subdir per task containing:
    workspace/     a fresh copy of the task's workspace, mutated by the agent
    prompt.txt     the exact prompt handed to the agent
    stdout.log     agent stdout (usually the transcript)
    stderr.log     agent stderr
    run.json       {agent, task, seconds, exit_code, timed_out}
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
RESULTS_DIR = ROOT / "results"


def load_agents():
    with open(ROOT / "agents.json", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def discover_tasks(only):
    tasks = []
    for d in sorted(TASKS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if not (d / "task.md").exists() and not (d / "turns").is_dir():
            continue
        if only and d.name not in only:
            continue
        tasks.append(d)
    return tasks


def build_cmd(template, prompt, prompt_file):
    out = []
    for part in template:
        out.append(part.replace("{prompt}", prompt).replace("{prompt_file}", str(prompt_file)))
    return out


def run_one(agent_name, agent_cfg, task_dir, run_dir, timeout):
    task_name = task_dir.name
    dest = run_dir / task_name
    dest.mkdir(parents=True, exist_ok=True)

    workspace = dest / "workspace"
    shutil.copytree(task_dir / "workspace", workspace)

    prompt = (task_dir / "task.md").read_text(encoding="utf-8")
    (dest / "prompt.txt").write_text(prompt, encoding="utf-8")
    prompt_file = dest / "prompt.txt"

    prompt_via = agent_cfg.get("prompt_via", "arg")
    arg_prompt = "" if prompt_via == "stdin" else prompt
    cmd = build_cmd(agent_cfg["cmd"], arg_prompt, prompt_file)
    # On Windows the executable is often a .cmd/.bat shim; CreateProcess won't
    # resolve it from a bare name the way the shell does. shutil.which honours
    # PATHEXT, so resolve the program to a full path here.
    resolved = shutil.which(cmd[0])
    if resolved:
        cmd[0] = resolved

    stdin_text = prompt if prompt_via == "stdin" else None

    print(f"  [{task_name}] $ {' '.join(cmd[:3])} ...", flush=True)
    start = time.time()
    timed_out = False
    try:
        proc = subprocess.run(
            cmd,
            cwd=workspace,
            input=stdin_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        exit_code = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        exit_code = None
        stdout = (e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else e.stdout) or ""
        stderr = ((e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else e.stderr) or "") + \
            f"\n[runner] timed out after {timeout}s\n"
    except FileNotFoundError:
        sys.exit(f"agent command not found: {cmd[0]!r}. Is it installed / on PATH?")

    seconds = round(time.time() - start, 1)
    (dest / "stdout.log").write_text(stdout, encoding="utf-8")
    (dest / "stderr.log").write_text(stderr, encoding="utf-8")
    (dest / "run.json").write_text(json.dumps({
        "agent": agent_name,
        "task": task_name,
        "seconds": seconds,
        "exit_code": exit_code,
        "timed_out": timed_out,
    }, indent=2), encoding="utf-8")
    print(f"  [{task_name}] done in {seconds}s (exit {exit_code}, timeout={timed_out})", flush=True)


def _invoke(cmd, cwd, stdin_text, timeout):
    """Run one agent process; return (stdout, stderr, exit_code, timed_out)."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, input=stdin_text, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        return proc.stdout, proc.stderr, proc.returncode, False
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else e.stdout) or ""
        stderr = ((e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else e.stderr) or "") + \
            f"\n[runner] timed out after {timeout}s\n"
        return stdout, stderr, None, True
    except FileNotFoundError:
        sys.exit(f"agent command not found: {cmd[0]!r}. Is it installed / on PATH?")


def run_multiturn(agent_name, agent_cfg, task_dir, run_dir, timeout):
    """A task with turns/001.md, 002.md, ... run as a SEQUENCE of prompts against the
    same workspace, using the agent's session-continuation flag from turn 2 onward, so
    later turns can see and build on what earlier turns did -- without the runner ever
    repeating the earlier prompts."""
    task_name = task_dir.name
    dest = run_dir / task_name
    dest.mkdir(parents=True, exist_ok=True)

    workspace = dest / "workspace"
    shutil.copytree(task_dir / "workspace", workspace)

    turn_files = sorted((task_dir / "turns").glob("*.md"))
    if not turn_files:
        sys.exit(f"{task_name}: turns/ has no .md files")

    prompt_via = agent_cfg.get("prompt_via", "arg")
    continue_flag = agent_cfg.get("continue_flag", "--continue")
    base_cmd = list(agent_cfg["cmd"])
    resolved = shutil.which(base_cmd[0])
    if resolved:
        base_cmd[0] = resolved

    total_seconds = 0.0
    any_timeout = False
    any_nonzero = False

    for i, tf in enumerate(turn_files, start=1):
        prompt = tf.read_text(encoding="utf-8")
        prompt_file = dest / f"prompt_{i:03d}.txt"
        prompt_file.write_text(prompt, encoding="utf-8")

        cmd = list(base_cmd)
        if i > 1:
            cmd.append(continue_flag)
        arg_prompt = "" if prompt_via == "stdin" else prompt
        cmd = build_cmd(cmd, arg_prompt, prompt_file)
        stdin_text = prompt if prompt_via == "stdin" else None

        print(f"  [{task_name}] turn {i}/{len(turn_files)} ({tf.name}) ...", flush=True)
        start = time.time()
        stdout, stderr, exit_code, timed_out = _invoke(cmd, workspace, stdin_text, timeout)
        seconds = round(time.time() - start, 1)
        total_seconds += seconds
        any_timeout = any_timeout or timed_out
        any_nonzero = any_nonzero or (exit_code not in (0, None))

        (dest / f"stdout_{i:03d}.log").write_text(stdout, encoding="utf-8")
        (dest / f"stderr_{i:03d}.log").write_text(stderr, encoding="utf-8")
        (dest / f"turn_{i:03d}.json").write_text(json.dumps({
            "turn": i, "file": tf.name, "seconds": seconds,
            "exit_code": exit_code, "timed_out": timed_out,
        }, indent=2), encoding="utf-8")
        print(f"    turn {i} done in {seconds}s (exit {exit_code}, timeout={timed_out})", flush=True)

        if timed_out:
            break  # no point continuing a broken session

    (dest / "run.json").write_text(json.dumps({
        "agent": agent_name,
        "task": task_name,
        "seconds": round(total_seconds, 1),
        "exit_code": 1 if (any_timeout or any_nonzero) else 0,
        "timed_out": any_timeout,
        "turns": len(turn_files),
    }, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True, help="key from agents.json")
    ap.add_argument("--tasks", nargs="*", default=None, help="task dir names; default = all")
    ap.add_argument("--timeout", type=int, default=900, help="per-task seconds")
    args = ap.parse_args()

    agents = load_agents()
    if args.agent not in agents:
        sys.exit(f"unknown agent {args.agent!r}. Known: {', '.join(agents)}")

    tasks = discover_tasks(args.tasks)
    if not tasks:
        sys.exit("no tasks found")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RESULTS_DIR / f"{stamp}-{args.agent}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "meta.json").write_text(json.dumps({
        "agent": args.agent,
        "started": stamp,
        "tasks": [t.name for t in tasks],
    }, indent=2), encoding="utf-8")

    # keep a stable pointer to the newest run
    latest = RESULTS_DIR / "latest.txt"
    latest.write_text(run_dir.name, encoding="utf-8")

    print(f"run: {run_dir.name}  ({len(tasks)} tasks)")
    for t in tasks:
        if (t / "turns").is_dir():
            run_multiturn(args.agent, agents[args.agent], t, run_dir, args.timeout)
        else:
            run_one(args.agent, agents[args.agent], t, run_dir, args.timeout)

    print(f"\ndone. next: python harness/grader.py --run {run_dir.name}")


if __name__ == "__main__":
    main()
