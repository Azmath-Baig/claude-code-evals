# Eval roadmap

_Owner: [you] · Last updated: 2026-09-04_

What this suite measures today, what it can't, and the order I'd build the missing
instruments in. This is the "what should the engineering team measure next" artifact.

## Today (v0)

- ~[N] tasks across [M] types, automated binary verification.
- Single-agent and cross-agent runs, per-type pass rates, wall-clock, timeout rate.
- Headless invocation only.

## Gaps, ranked

### P0 — [ ]

**Gap.** _e.g. No long-horizon tasks. Everything here resolves in < 20 turns; real
developer work spans hours and many files._
**Why it matters.** _[ ]_
**What to build.** _[ ] — e.g. 5 multi-hour tasks with checkpointed sub-verifiers._
**Effort.** _[ ]_

### P1 — [ ]

**Gap.** _e.g. Interactive experience unmeasured — clarifying questions, mid-task
correction, permission prompts._
**What to build.** _[ ] — scripted-user simulator that replies to agent questions from a
rubric._

### P2 — [ ]

**Gap.** _e.g. No signal on tool-call recovery: what happens after a bad edit or a failed
command._
**What to build.** _[ ]_

### P3 — [ ]

**Gap.** _e.g. Security-sensitive changes graded only heuristically._
**What to build.** _[ ] — static-analysis gate in `verify.sh` for a set of planted-vuln
tasks._

## Suite hygiene (ongoing)

- Rotate ~20% of tasks per quarter; maintain an unpublished held-out set.
- Re-calibrate difficulty on every new model; archive tasks that stop splitting the field.
- Track per-task result stability across repeats; flag flaky verifiers.

## Instrumentation wishlist (needs Anthropic-internal data)

- Join eval results to real usage: do the failure classes here match where users actually
  retry / abandon / thumbs-down?
- Transcript mining at scale to source new tasks from real capability gaps.
