# Launch verdict

_The one-page version. Full evidence in `01-findings.md` and `_experiments/`._

## Recommendation

**GO. Do not block the model launch on the basis of this suite.** Ship — with the six
evaluation gaps below tracked as named evaluation debt, and this suite wired in as a
regression gate for the next model.

## What this suite tested

16 categories of adversarial pressure, ~130 real `claude -p` runs, each category sourced
from a real bug or a specific hypothesis about where an agent tends to fail — not invented
to pad a number:

schema-change conventions · scope adherence · recovery from a bad first step ·
mutation-tested test quality · cross-layer completeness · reward hacking · silent contract
degradation under "optimize but keep behavior equivalent" · inconsistent invariant
enforcement · long-horizon constraint survival (7 unreminded turns) · conflicting sources
of truth · a Windows subprocess pitfall from this project's own build · pushback on
directives a senior engineer would question · open-ended judgment (pick one of three
viable implementations) · discovery ("what breaks in production", no rubric) · code
optimality (implement from scratch — O(n) or O(n²)?) · a 12-rule business-logic engine.

## What it found

1. **No stable, reproducible model capability weakness in any of the 16** — including the
   two open-ended categories a reviewer pushed for (pick one of three viable
   implementations; "what breaks in production" with no rubric). Where I predicted a
   failure, built a controlled task, and ran it 3×+, the model held. On the pushback
   category it declined 3 of 5 harmful directives outright and proposed a safer
   alternative each time. On the judgment task it caught that all three rate-limiter
   options break under load-balanced instances — the non-obvious answer.

2. **Five apparent failures were defects in my own harness or graders — every one
   *under-crediting* the model:** a verifier that graded the pristine copy instead of the
   agent's; a truncated prompt from Windows argv quoting; two keyword-based transcript
   checks that missed valid phrasing (fixed by moving to an LLM judge, `tasks/_judge.py`);
   and a `check.py` that crashed on a Unicode char *after* the judge had scored the answer
   STRONG, recording it as FAIL. That last one surfaced while adding the judgment tasks a
   reviewer asked for — the thesis demonstrating itself.

3. That second point matters more than the first. It **lowered my confidence in the
   benchmark, not the model.** A suite that produces five confident-but-wrong FAILs before
   it produces one real one is not yet a suite you gate a launch on.

## What that means for a launch decision

The residual launch risk this suite surfaces is **not** "Claude fails known coding tasks."
It is that the current evals — this suite included — under-measure:

| Gap | Why it matters for a Claude Code launch |
|---|---|
| Open-ended bug / risk discovery (no answer key) | Real code review has no rubric; "what would break here?" is the daily ask |
| Production judgment (choosing between viable options) | Senior work is picking, with reasons, not executing a spec |
| Cost / latency / reliability tradeoffs | The model optimizes what's measured; product constraints are usually unstated |
| Developer-experience friction | Passing tasks ≠ pleasant to work with; diff size, over-explaining, unnecessary questions |
| Horizons beyond ~7 turns / a small codebase | Constraint drift is plausible at 30 turns / 500 files even though it wasn't at 7 / 4 |
| Interactive (not headless) sessions | Everything here is `claude -p`; the real product is a conversation |

## Conditions I would attach to a GO

- The six gaps above tracked as evaluation debt with owners and target dates.
- Behavioral checks stay on LLM-judge grading, never keyword matching — this suite
  demonstrates why (three false negatives, all under-crediting).
- This suite re-run as a **regression gate** on the next model: watch for per-category
  *drops*, not absolute pass rates. A category that goes 5/5 → 3/5 is the signal; 5/5 →
  5/5 tells you little.
- The next eval investment goes into the "judgment / discovery" axis (see
  `tasks/036–037` and `04-eval-roadmap.md`), not another 20 specification-following tasks.
