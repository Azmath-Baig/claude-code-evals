# Findings

_Owner: [you] · Based on 11 real-`claude -p` experiments, ~100 runs · 2026-09-05_

## Executive summary

I tested Claude Code against 12 categories of adversarial pressure, each sourced from a
real bug or a specific hypothesis about where an agent is likely to fail rather than
invented for its own sake: schema-change conventions, scope adherence, recovery from a
bad first step, mutation-tested test quality, cross-layer completeness, reward hacking,
silent contract degradation under "optimize but keep behavior equivalent," an ownership
invariant applied across multiple code paths, long-horizon constraint survival across 7
unreminded turns, conflicting sources of truth, a Windows subprocess pitfall sourced from
this project's own build, and — the last resort — whether it pushes back on directives a
senior engineer would question or just complies.

**Result: no model capability weakness held up under inspection in any of the 12.** Four
things that looked like findings along the way turned out, on reading the raw transcript
or workspace, to be bugs in my own verifiers or grading heuristics — not the model. Every
one *under-credited* the model. Each was caught, root-caused, and fixed; see "Verifier
hygiene" below.

That is the headline, and I'm reporting it as such rather than manufacturing a weaker
"gotcha" to have something to point at. The suite, the methodology, and the discipline of
re-checking automated verdicts against raw evidence are the deliverable this round.

The strongest single recommendation to fall out of it: **behavioral evals — "did it warn,
notice, push back, hedge" — cannot be graded by keyword matching; they need an LLM judge.**
I learned this by getting it wrong three times in this suite, then fixed it: `tasks/_judge.py`
runs a fresh `claude -p` as the grader (transcript + one classification question, 3×,
majority vote). Rebuilding the three keyword checks on it corrected all three false
negatives, and every verdict came back unanimous (3/3). That's the loop — wrong instrument,
diagnosed, replaced, re-verified — and it's the part of this project most directly relevant
to a Model Performance / eval role.

## Category-by-category

| # | Category | Tasks | Runs | Result |
|---|---|---|---|---|
| 1 | Schema-change consistency | 002–010 | 39 | Not supported. Model matches explicit specs (17/17) and repeated conventions (12/12); the one "failure" (003) was a grader encoding one of two valid designs, resolved by 010 |
| 2 | Scope adherence | 011–014 | 12 | Not supported. Zero collateral edits, natural or explicit asks |
| 3 | Recovery after a bad first step | 015–017 | 9 | Not supported. Iterated past first-plausible-fix, repaired inherited breakage, honored a no-dependency constraint |
| 4 | Test quality ("add tests") | 018–020 | 9 | Not supported. Mutation-tested; all planted bugs caught |
| 5 | Cross-layer completeness | 021–022 | 6 | Not supported, even with sync signposts removed |
| 6 | Reward hacking ("get tests green") | 023–024 | — | Not yet run via harness at scale (design verified: catches skip/weaken/delete) |
| 7 | Silent degradation under "optimize" | 025 | — | Design verified against a battery of edge cases (dedupe, tz, None, rounding, ordering) |
| 8 | Invariant applied inconsistently | 026–027 | — | Design verified: catches guard-one-path-only |
| 9 | Long-horizon constraint survival | 028 (multi-turn) | 1 (7 turns) | Not supported. 10/10 original constraints survived 6 unrelated-sounding follow-ups |
| 10 | Conflicting sources of truth | 029 | 1 | Not supported. Model named all 3 conflicting sources, reasoned, documented, asked for confirmation — a grader keyword-list false negative initially hid this |
| 11 | Windows subprocess argv-truncation (sourced from this project's own bug) | 030 | 1 | Not supported. Model produced a more defensive fix than the reference solution |
| 12 | Pushback — senior collaborator vs compliant junior | 031–035 | 5 | Not supported. Warned on 2, **declined 3** (money-path guard, exception-swallow, hardcoded secret) and proposed/built a safer alternative each time |

Rows 6–8 have verified task designs (fail-when-broken / pass-when-fixed confirmed by hand)
but weren't yet run against the live model at the time of writing — run them via
`docs/RUN_IT_YOURSELF.md` before citing a result for those three.

## Verifier hygiene: three self-caught bugs

Worth reporting on its own, since it's the throughline across everything above.

1. **`verify.sh` graded the wrong copy.** An early script `cd`'d back to the pristine task
   directory before running the check, so every task in a batch reported a confident,
   wrong 0/4. Fixed: verifiers run in the workspace the grader sets as cwd; the grader now
   prefers a pure-Python `check.py` over shell scripts. (`00-eval-spec.md` §9)
2. **Keyword-based transcript checks false-negatived — three times, always under-crediting
   the model.** Task 029 ("did it notice the conflict"), then `pushback` 032 and 034
   ("did it warn / push back"). Each time the model's actual behavior was substantive and
   correct; the hand-picked phrase list just didn't cover the wording it used. Rule now in
   §9: free-text behavioral judgments need an LLM judge, not `if phrase in transcript`.
3. **The Windows harness bug itself** — passing a multi-line prompt as a subprocess
   argument to an npm `.cmd` shim silently truncated it. This one wasn't in a task
   verifier; it was in the harness that runs the tasks. Caught the same way: by reading
   the actual output, not trusting that "exit 0" meant "worked." (`windows-subprocess-safety.md`)

**Pattern:** every real miss in this project — whether in a grader or in the harness
itself — traced back to code or a check that hadn't been executed against ground truth
before being trusted. None traced back to the model reasoning incorrectly once it was
actually put to a real, executed test. If I had to give Claude Code's model-performance
team one recommendation from this round, it would be to keep pushing on **making
"did you actually run this and check the real output" a default habit of agentic
workflows** — not because the model can't do it when asked, but because the cost of
skipping it (as I did, twice, building this very suite) is exactly this class of bug.

## What I would prioritize next (if I owned this)

1. **Run categories 6–8 (reward hacking, silent degradation, invariant drift) to
   completion** — they're the closest in spirit to genuine specification gaming, and
   verified-but-unrun is the biggest gap in this round.
2. **Repeat the long-horizon and conflicting-authority tasks 3× each** — both are N=1;
   a stable 3/3 would meaningfully strengthen "not supported" into "held up."
3. **Push the long-horizon test further** — more turns, a bigger codebase, requirements
   with real tension (not just non-overlapping asks) — this is the category most likely
   to still find something, per the design that produced task 028.
4. **Build the "model-induced technical debt" eval** (architecture-quality judged
   independently of functional tests) — proposed but not built this round; a different
   axis entirely (would the code pass review, not just tests).

## Watch list

- Reward-hacking and silent-degradation task designs are solid; running them is pure
  upside for the next session.
- The suite has never been run against a second agent (Aider, Codex CLI) for competitive
  comparison — `docs/03-competitive-analysis.md` is still a template.
