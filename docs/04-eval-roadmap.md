# Eval roadmap

_Owner: [you] · Last updated: 2026-09-05_

What this suite measures today, what it can't, and the order to build the missing
instruments — the "what should the engineering team measure next" artifact. This is the
half of the project I'd argue matters most: after ~110 runs the model held on everything
that had an answer key, so the frontier of *this* work is measuring the parts that don't.

## Today (v1)

- 37 tasks across ~15 types; automated verification (pure-Python `check.py` preferred over
  shell). Single-shot and **multi-turn** (`turns/NNN.md`, same session via `--continue`).
- Behavioral / open-ended tasks graded by an **LLM judge** (`tasks/_judge.py`), 3× majority
  — after keyword grading produced three false negatives.
- Headless (`claude -p`) only.

## Gaps, ranked

### P0 — Open-ended discovery and production judgment (no answer key)

**Gap.** Almost every task hands the model a target. Real senior work is "review this, what
breaks?" and "three options, which ship?" — no rubric. `tasks/036–037` are a first pass
(pick-an-implementation, what-breaks-in-prod), judge-graded. Two tasks isn't a category.
**What to build.** 8–10 discovery/judgment tasks with planted-issue rubrics and
tradeoff scenarios; a false-positive rate alongside the hit rate; a "product tradeoff"
subtype ("make this faster without raising cost or lowering reliability" — the naive fix
violates a constraint the prompt didn't state).
**Why it matters.** This is where the "is it a senior collaborator" question actually
lives, and it's invisible to pass/fail benchmarks. Frameworks like ECC exist to bolt
plan→test→review discipline onto agents — evidence the base behavior here is worth
measuring directly.

### P1 — Long horizon at real scale

**Gap.** The long-horizon test (task 028) was 7 turns on a ~4-file codebase and held 10/10.
Constraint drift is still plausible at 30 turns / hundreds of files.
**What to build.** A 20–30-turn task on a several-hundred-file fixture, requirements with
genuine tension (not just non-overlapping asks), checkpointed sub-verifiers, constraint
survival tracked per turn.

### P2 — Interactive (non-headless) behavior

**Gap.** Everything is `claude -p`. The product is a conversation — clarifying questions,
mid-task correction, permission prompts, the user changing their mind.
**What to build.** A scripted-user simulator that answers the agent's questions from a
rubric; measure whether the agent asks the *right* questions and integrates the answers.

### P3 — Quality of the code produced, not just its correctness

**Gap.** Every task here is graded on "is the output correct / minimal / constraint-
respecting." Nothing scores what the code is actually *like*:
- **Algorithmic complexity of generated code.** On an implement-from-scratch task, does the
  model reach for the naive O(n²) version or the efficient one? (Task 025 shows it optimizes
  well *when told to*; it's never been checked unprompted.)
- **Runtime latency and memory** of the generated code, benchmarked against a reference
  solution — not the agent's wall-clock, the *output's*.
- **Weight** — over-abstraction, unnecessary layers, added dependencies, diff size, tokens,
  turn count, over-explaining.

**What to build.** For a set of tasks with a known-good reference: `pytest-benchmark` (or a
timed harness) comparing the agent's solution to the reference on wall-time and peak memory;
a complexity-class check (does runtime scale ~linearly or ~quadratically over growing
inputs); per-task diff-size / token / turn metrics with regression thresholds; a "minimal
diff" and a "is this over-engineered" LLM-judge subtype.
**Why it matters.** "Passes the tests" and "code you'd want to own and pay to run" are
different bars, and only the first is currently measured.

## Suite hygiene (ongoing)

- Re-run as a **regression gate** on each new model: watch per-category *drops*, not
  absolute pass rates.
- Behavioral checks stay on the LLM judge, never keyword lists.
- Rotate ~20% of tasks per quarter; keep an unpublished held-out set; re-calibrate
  difficulty per model; flag flaky verifiers via repeat-stability.

## Needs Anthropic-internal data

- Join eval results to real usage: do the (absence of) failure classes here match where
  users actually retry / abandon / thumbs-down?
- Mine real transcripts to source discovery/judgment tasks from genuine capability gaps.
