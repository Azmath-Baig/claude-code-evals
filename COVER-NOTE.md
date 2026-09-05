# Cover note

_For: Product Manager — Claude Code Model Performance. Read this first; it's the 90-second
version. Full write-up in [`docs/01-findings.md`](docs/01-findings.md), the launch call in
[`docs/LAUNCH-VERDICT.md`](docs/LAUNCH-VERDICT.md)._

---

I set out to do the core job in miniature: build an agentic eval suite, point it at Claude
Code, and find where the model fails a developer badly enough to hold a launch.

I couldn't. Across **16 categories of adversarial pressure and ~130 real `claude -p` runs**
— schema conventions, scope discipline, recovery from a bad first step, mutation-tested test
quality, cross-layer completeness, reward hacking, contract degradation under "optimize but
keep behaviour equal", invariant enforcement, 7-turn constraint survival, conflicting
sources of truth, a Windows subprocess trap from this project's own build, whether it pushes
back on bad directives, open-ended judgment/discovery with no answer key, whether it
writes the optimal algorithm from scratch, and a 12-rule business-logic engine — no model
capability weakness held up once I looked at the raw evidence.

What I found instead: **five times I thought I had a finding, and each was a defect in my
own harness or grader — every one under-crediting the model.** A verifier that graded the
pristine copy instead of the agent's. A prompt truncated by Windows argv quoting. Two
keyword-based transcript checks that missed valid phrasing (fixed by moving to an LLM
judge). A check that crashed on a Unicode character *after* the judge had scored the answer
STRONG. That last one surfaced live, while I was adding the judgment tasks a reviewer asked
for.

So my launch recommendation is **GO — do not block on this suite** — with the six things it
under-measures tracked as explicit evaluation debt (open-ended discovery, production
judgment, cost/latency tradeoffs, developer-experience friction, horizons past ~7 turns,
interactive sessions). The suite's value now is as a **regression gate** for the next model:
watch per-category drops, not absolute scores.

What I think this demonstrates for the role:

- **Hypothesis-driven task design** — every category came from a real bug or a specific
  theory of failure, not filler. See `tasks/` and `docs/_experiments/`.
- **Evaluator skepticism** — the discipline of never trusting an automated PASS/FAIL until
  the raw transcript and workspace are read. It's why the five instrument bugs got caught
  instead of shipped as "findings".
- **Methodology judgment** — keyword grading of free-text behaviour doesn't work; I learned
  that the hard way and built the LLM-judge replacement (`tasks/_judge.py`), then re-ran and
  verified the fix.
- **Willingness to invalidate my own thesis** — I came in wanting to stop a launch and
  concluded the opposite, in writing, with the reasoning shown.

The harness is ~350 lines and not the point. The interpretation is.

— built over ~2 days, `claude -p` v2.1.260, Windows.
