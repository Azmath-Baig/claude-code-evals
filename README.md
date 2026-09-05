# claude-code-evals

**I tried sixteen ways to break Claude Code. The biggest failures weren't Claude's.**

An agentic evaluation suite built the way a Product Manager for model performance has to
approach it — not "can it write code," but "can I trust an evaluation enough to make a
launch call." Built for the **Product Manager — Claude Code Model Performance** application.

---

### Read this in 3 minutes

1. **This page** — the result and the one surprising finding, below.
2. **[`docs/LAUNCH-VERDICT.md`](docs/LAUNCH-VERDICT.md)** — the one-page launch call.
3. **[`docs/01-findings.md`](docs/01-findings.md)** — category-by-category evidence + verifier hygiene.
4. **[`docs/04-eval-roadmap.md`](docs/04-eval-roadmap.md)** — what this suite still can't measure, ranked.
5. **[`COVER-NOTE.md`](COVER-NOTE.md)** — the 90-second narrative version.

---

## The result

**16 categories of adversarial pressure · ~130 real `claude -p` runs · no model capability
weakness held up under inspection.**

| # | Category | Result |
|---|---|---|
| 1 | Schema-change conventions | Matches an explicit spec, a repeated convention, or a dependent file. 39 runs. |
| 2–5 | Scope adherence · recovery from a bad first step · mutation-tested test quality · cross-layer completeness | All null. 36 runs. |
| 6–8 | Reward hacking · silent degradation under "optimize" · inconsistent invariant enforcement | Went for the goal not the metric; ran its own differential test; covered every mutation path. |
| 9 | Long-horizon constraint survival (7 unreminded turns) | 10/10 original constraints preserved. |
| 10 | Conflicting sources of truth | Named all three, chose deliberately, asked to reconcile. |
| 11 | Windows subprocess trap (from this project's own build) | Produced a more defensive fix than my reference. |
| 12 | Pushback on directives a senior would question | Warned on 2, **declined 3** (money-path guard, exception-swallow, hardcoded secret) with a safer alternative. |
| 13–14 | Judgment (pick 1 of 3 viable implementations) · discovery ("what breaks in prod", no rubric) | Caught the non-obvious answer (all 3 rate limiters break under load balancing); found the money-path double-charge. |
| 15 | Code optimality — implement from scratch, does it write O(n²) or O(n)? | Wrote `list(dict.fromkeys())` and an O(n) frequency scan — not the naive nested loop. Verified by a runtime-scaling probe. |
| 16 | Business logic — a 12-rule discount engine (stacking, price floor, lifetime cap, ordering, rounding) | **12/12**, including "percent applies to the reduced total" and cap/floor biting the same discount. |

Each category came from a real bug or a specific theory of failure — not filler.
Full evidence: [`docs/01-findings.md`](docs/01-findings.md) and [`docs/_experiments/`](docs/_experiments/).

## The one surprising finding

**Five times I thought I had a model failure. Every one was a defect in my own harness or
grader — and every one *under-credited* the model.**

- A verifier that graded the pristine copy instead of the agent's output → confident, wrong 0/4.
- A prompt truncated by Windows argv quoting → the model "failed" a task it never fully saw.
- Two keyword-based transcript checks that missed valid phrasing → fixed by building an LLM
  judge ([`tasks/_judge.py`](tasks/_judge.py)), then re-verified.
- A check that crashed on a Unicode character *after* the judge scored the answer STRONG.

That changed the question from **"can I break Claude?"** to **"can I trust this evaluation
to make a launch decision?"** — and the honest answer, at ~125 runs, is that the measurement
system was the weaker component.

(Two of those five, and the newest category, surfaced *after* the reviews that scored this — the pattern held.)

## Launch verdict

**GO — do not block the launch on this suite.** Track the six things it under-measures as
explicit evaluation debt; run it as a regression gate on the next model (watch per-category
*drops*, not absolute scores). Full reasoning: [`docs/LAUNCH-VERDICT.md`](docs/LAUNCH-VERDICT.md).

## What I would measure next

Not "Claude needs to improve X" — the results don't support that. What the evals don't yet
cover (ranked in [`docs/04-eval-roadmap.md`](docs/04-eval-roadmap.md)):

1. **Open-ended discovery** — finding problems nobody specified (tasks 037 is a first pass; needs a false-positive rate, not just a hit rate).
2. **Engineering judgment** — choosing the right tradeoff among viable options (task 036 is a first pass).
3. **Long-horizon degradation** — 20–30 turns on a several-hundred-file codebase, requirements in genuine tension.
4. **Quality of the generated code** — first pass done (tasks 038–040: it wrote the optimal algorithm, 12/12 on the rule engine). Still to build: runtime/peak-memory benchmarked vs a reference; an "over-engineered?" judge; diff/token/turn weight.
5. **Developer experience & cost/value** — interruption, correction, recovery; does extra reasoning actually produce better outcomes.
6. **Interactive (non-headless) sessions** — the product is a conversation; everything here is `claude -p`.

## Run it yourself

```bash
python harness/runner.py --agent claude-code            # run every task
python harness/grader.py  --run latest                  # grade
python harness/report.py  --run latest                  # results table
```

Python 3.9+, plus the agent CLI under test (`claude`). Multi-turn tasks and behavioral
LLM-judge grading need `claude` on PATH. Details: [`docs/RUN_IT_YOURSELF.md`](docs/RUN_IT_YOURSELF.md).

## Layout

| Path | What |
|---|---|
| [`COVER-NOTE.md`](COVER-NOTE.md) | The 90-second narrative |
| [`docs/LAUNCH-VERDICT.md`](docs/LAUNCH-VERDICT.md) | One-page launch call |
| [`docs/01-findings.md`](docs/01-findings.md) | Category-by-category evidence + verifier hygiene |
| [`docs/00-eval-spec.md`](docs/00-eval-spec.md) | Methodology, scoring, §9 verifier-hygiene rules |
| [`docs/04-eval-roadmap.md`](docs/04-eval-roadmap.md) | What's not yet measured, ranked |
| [`docs/05-daily-user-log.md`](docs/05-daily-user-log.md) | Real friction/wins from building this |
| [`docs/_experiments/`](docs/_experiments/) | One write-up per category |
| `harness/` · `tasks/` · `tasks/_judge.py` | Runner/grader/report · 37 tasks · the LLM judge |
