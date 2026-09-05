# Experiment: test quality when asked to "add tests"

_Owner: [you] · Started 2026-09-04_

## Hypothesis

Asked to "add tests", the model writes shallow tests — happy path only, `assert x is not
None`, no edge/error cases — that pass but wouldn't catch a regression.

## Method — mutation testing

For each task: the model writes `test_*.py`. The grader then
1. runs the tests against the correct implementation → must pass;
2. swaps in each of several planted single-bug mutants of the target function → each must
   make at least one test fail ("killed"). A mutant that still passes ("survivor") means
   that behaviour was never pinned.

Pass = every mutant killed. (This is the "evaluation methodology" the JD asks for, in
miniature: mutation score as the metric, not line coverage.)

## Tasks

| Task | Target | Ask | Mutants |
|---|---|---|---|
| 018 testquality-median-natural | `median` | "add unit tests" (plain) | even-count not averaged; input not sorted; off-by-one index; empty returns None; `//` vs `/` |
| 019 testquality-parser-natural | `parse_kv` | "add unit tests" (plain) | no whitespace strip; empty segments not skipped; dup-key check dropped; malformed check dropped; empty returns None |
| 020 testquality-median-explicit | `median` | "write regression-catching tests, cover odd/even/unsorted/single/empty" (explicit) | same as 018 |

018 vs 020 = the natural-vs-explicit axis on one fixture. All three verified: FAIL with no
tests, PASS with a thorough suite, FAIL (with the exact survivors listed) on a happy-path
suite.

## Runs

Real `claude -p`, 3×.

### Round 1 — [date]

| Task | run 1 | run 2 | run 3 | survivors seen |
|---|---|---|---|---|
| 018 | | | | |
| 019 | | | | |
| 020 | | | | |

## Findings

_fill after Round 1_

- Plain "add tests" (018, 019): mutation score? which behaviours go unpinned? →
- Explicit framing (020 vs 018): does it help? →
