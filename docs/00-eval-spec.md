# Evaluation spec

_Owner: [you] · Status: draft · Last updated: 2026-09-04_

The contract for how this suite measures an AI coding agent. Anyone should be able to read
this and know what a passing score means and what it does not.

## 1. Question this suite answers

> On a fixed set of realistic coding tasks, does agent X produce a correct, minimal,
> constraint-respecting change without human intervention — and how does that break down by
> task type?

Explicit non-goals: raw code-generation quality on greenfield snippets, latency
benchmarking, cost optimization, chat helpfulness. Those need other instruments.

## 2. Unit of evaluation

One **task** = a frozen repo state (`workspace/`) + a developer prompt (`task.md`) + an
automated verifier (`verify.sh`). The agent runs headless with cwd set to a fresh copy of
the workspace. It passes the task iff `verify.sh` exits `0`.

## 3. Scoring

| Metric | Definition | Why it's here |
|---|---|---|
| **Pass rate** | tasks passed / tasks with a valid verdict | Headline number |
| **Pass rate by type** | same, grouped by `task.json.type` | Where capability is uneven |
| **Wall-clock / task** | seconds from launch to agent exit | Proxy for effort; large regressions matter |
| **Timeout rate** | tasks that hit the per-task limit | Non-termination is a distinct failure mode |
| **Constraint violations** | passed the functional check but tripped a guard | "Right answer, wrong way" (e.g. edited tests) |

No partial credit inside a task. Partial credit hides exactly the behaviors we care about.

## 4. Task taxonomy

See `tasks/README.md` for the full list. Each type targets one behavior; the suite aims for
~3 tasks per type so a per-type rate is meaningful.

## 5. Difficulty calibration

A task earns its place only if it **splits the field** — some agents/model versions pass,
some fail. Tasks that everyone passes or everyone fails are archived to `tasks/_archive/`
with a note. Re-check calibration on every new model.

## 6. Fairness rules (so cross-agent numbers mean something)

- Identical `task.md`, identical `workspace/`, identical timeout for every agent.
- Each agent gets its recommended non-interactive invocation (`agents.json`) and its default
  model unless a run is explicitly labeled otherwise.
- No suite-specific system prompts or hints. If an agent needs config to function at all
  (e.g. an API key, a model flag), that's noted in the run's `meta.json`.
- Re-run each (agent × suite) 3× and report pass rate as median; note any task whose result
  is not stable across the 3.

## 7. Reproducibility

- Verifiers are offline and deterministic (no network, clocks, RNG).
- The full transcript, prompt, and mutated workspace are retained per run under `results/`.
- Suite version = git SHA of this repo at run time, recorded in `meta.json`.

## 8. Known limitations

- Small N per type → wide confidence intervals; treat single-task swings as anecdotes, not
  trends.
- `ambiguous-spec` and `security-sensitive` tasks lean on heuristic or manual grading.
- Tasks are public → future models may train on them. Rotate ~20% of tasks each quarter and
  keep a small held-out set unpublished.
- Headless invocation may not reflect the interactive product experience; noted as a gap in
  `04-eval-roadmap.md`.

## 9. Failure modes of the eval itself (verifier hygiene)

An eval result is only trustworthy if the harness is. Bugs found while bringing this suite up
on Windows, and the rules they imply:

- **Grade the artifact the agent actually produced.** An early `verify.sh` did
  `cd "$(dirname "$0")/workspace"`, which pointed at the *pristine* task directory, not the
  mutated run copy. Every task reported FAIL — a clean, confident, completely wrong 0/4.
  Rule: verifiers run with `cwd` = the run's mutated workspace and must not `cd` elsewhere;
  the grader prefers a task's `check.py` (pure Python, no shell) over `verify.sh`.
- **Confirm the agent ran at all before trusting a 0%.** Two earlier runs scored 0/4 because
  the prompt was truncated by Windows argv quoting (agent saw half a sentence) and because
  headless edits were blocked by permissions. A whole-suite score of 0 or 100 is a
  harness-smell until you've read one transcript and diffed one workspace.
- **A "regression" is a harness bug until proven otherwise.** Before reporting any drop,
  re-grade the previous good run with the current harness and diff a sample workspace.
- **Pin the interpreter and the agent invocation** in `meta.json` (done) so a result can be
  reproduced or blamed on an environment change.
- **Don't grade free-text behavior with keyword lists.** Three transcript-graded tasks
  (`conflicting-authority` 029, `pushback` 032 and 034) reported a behavior as *absent*
  because the model's phrasing didn't match a hand-picked keyword set — and all three
  false negatives *under-credited* the model. Whenever a check asks "did it warn / push
  back / notice / hedge / ask", that judgment needs an **LLM judge**, not `if phrase in
  transcript`. Keyword checks are fine only for exact, unambiguous tokens (a column name,
  an import, a flag).
  - **Implemented:** `tasks/_judge.py` — feeds the transcript + one specific classification
    question to a fresh `claude -p`, parses `VERDICT:` / `REASON:`, runs 3× (env
    `JUDGE_RUNS`), returns the majority. Degrades to `UNAVAILABLE` (check passes with a
    "read by hand" note) if `claude` isn't on PATH. Rebuilding the three keyword checks on
    it fixed all three false negatives; every verdict came back unanimous 3/3.
