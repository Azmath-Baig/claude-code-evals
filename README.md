# claude-code-evals

An agentic evaluation suite for AI coding agents, built to answer one question the way a
product manager has to answer it:

> **Is the coding agent actually getting better — and where is it still failing developers?**

This repo contains:

- A **task suite** (`tasks/`) of self-contained coding problems, each with an automated
  pass/fail verifier — SWE-bench-style, but designed to isolate *behaviors* (clarification,
  multi-file edits, recovery from bad tool calls) rather than just "can it code."
- A thin **harness** (`harness/`) that runs any coding agent against every task headlessly,
  captures the full transcript, and scores it.
- The **PM deliverables** (`docs/`): the evaluation spec, the findings, a launch-readiness
  scorecard, a competitive analysis, and an eval roadmap.

## Why this exists

I'm applying for **Product Manager — Claude Code Model Performance** at Anthropic. Rather than
assert that I can drive model-performance product direction, this repo demonstrates it:
task design, evaluation methodology, capability-gap analysis, prioritization, and
launch-readiness thinking, backed by reproducible runs.

## Findings so far

Full write-up in `docs/01-findings.md`. Headline: **11 categories of adversarial pressure
tested against real `claude -p`, ~100 runs, no model capability weakness held up under
inspection.**

- **Schema-change consistency** (39 runs) — matches an explicit spec (17/17), a repeated
  codebase convention (12/12), or a neighbouring dependent file (3/3). The one apparent
  "failure" was a grader encoding one of two valid designs as "correct" — resolved by a
  forcing task, not a model defect.
- **Scope adherence** (12 runs), **recovery from a bad first step** (9 runs), **mutation-tested
  test quality** (9 runs), **cross-layer completeness** (6 runs) — all null.
- **Long-horizon constraint survival** — a 7-turn task (build a feature with 6 interacting
  requirements, then 6 unrelated-sounding follow-ups with zero reminders) scored **10/10** on
  independently re-checking every original requirement at the end.
- **Conflicting sources of truth** — given 3 documents disagreeing on one rule, the model
  named all three, reasoned, documented its choice, and asked for confirmation.
- **A Windows subprocess pitfall sourced from this project's own build** (see below) — the
  model produced a more defensive fix than my own reference solution.
- Reward hacking, silent contract degradation under "optimize," and inconsistent invariant
  enforcement have verified task designs (`tasks/023–027`) not yet run to a result — the
  clearest next step.

**Verifier hygiene, caught three times.** A verifier that graded the wrong workspace copy
(`docs/00-eval-spec.md` §9); a keyword-based transcript check that missed a valid phrasing;
and — most tellingly — **the harness itself**: passing a multi-line prompt as a Windows
subprocess argument to `claude`'s npm `.cmd` shim silently truncated it, caught only by
reading real output. Turned into `tasks/030`, where the same model, given a scoped task and
a real check, produced a correct and more defensive fix than mine. **Every real miss in this
project traced to unverified process, not incorrect model reasoning once actually tested.**
That's the throughline finding.

_Next: run tasks 023–027 to completion; repeat the long-horizon and conflicting-authority
tasks 3× each; push the long-horizon test further (more turns, real tension between
requirements)._

## Quickstart

```bash
# 1. Point the harness at an agent (see agents.json)
# 2. Run every task with one agent
python harness/runner.py --agent claude-code

# 3. Grade the runs
python harness/grader.py --run latest

# 4. Print the results table
python harness/report.py --run latest
```

Requires Python 3.9+ and the agent CLI you're testing (e.g. `claude`). No third-party
packages for the harness itself; individual tasks may need `pytest` etc. inside their
workspace.

## Layout

| Path | What |
|---|---|
| `docs/00-eval-spec.md` | Methodology, scoring rubric, task taxonomy |
| `docs/01-findings.md` | Failure classes, proposed behavior changes, developer impact |
| `docs/02-launch-readiness-scorecard.md` | Gates for shipping a new model into Claude Code |
| `docs/03-competitive-analysis.md` | Claude Code vs other agents on the same suite |
| `docs/04-eval-roadmap.md` | What this suite can't measure yet, and what to build next |
| `docs/05-daily-user-log.md` | Dated friction notes from real daily use |
| `tasks/README.md` | How to author a task |
| `harness/` | runner / grader / report |
