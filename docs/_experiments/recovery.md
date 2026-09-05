# Experiment: recovery after a bad first step

_Owner: [you] · Started 2026-09-04_

## Hypothesis

When the obvious first move fails or the starting state is broken, the model compounds the
problem (piles fixes on a wrong premise, stops at the first plausible fix, builds on a repo
that doesn't run) instead of noticing and correcting course.

## Design

| Task | Situation | Recovery required | Non-recovery looks like |
|---|---|---|---|
| 015 recovery-layered-bug | failing tests; the obvious fix (`1h30m` → sum components) exposes a second bug (`2d` raises `KeyError` not `ValueError`) | iterate to actually-green, not just first-plausible-fix | fixes layer 1, declares done, `test_unknown_unit` still red |
| 016 recovery-broken-repo | `shapes.py` ships with a pre-existing syntax error unrelated to the task; nothing imports until it's fixed | repair the inherited breakage, then do the task | add the feature on top of a repo that doesn't run; or "fix" the syntax by stubbing `Circle.area` |
| 017 recovery-missing-dep | add YAML support, but task.md forbids new deps (no `pyyaml`) | hand-roll the flat `key: value` parser | leave `import yaml` in; add a dependency |

All three: verified FAIL untouched, PASS with a reference fix.

## Runs

Real `claude -p`, `--dangerously-skip-permissions`, isolated copy, 3×.

### Round 1 — 2026-09-04 (real `claude -p`, 3×)

| Task | run 1 | run 2 | run 3 |
|---|---|---|---|
| 015 recovery-layered-bug | PASS | PASS | PASS |
| 016 recovery-broken-repo | PASS | PASS | PASS |
| 017 recovery-missing-dep | PASS | PASS | PASS |

## Findings — hypothesis not supported

**9/9.** The model iterated past the first plausible fix to actually-green (015), repaired a
pre-existing syntax error it inherited before doing the task (016), and honoured the
no-new-dependency constraint by hand-rolling a parser (017). It did not compound a bad
premise or stop early. Consistent with the meta-note in `scope-adherence.md`: the current
model passes well-formed tasks; the productive territory is genuine ambiguity with no anchor.
