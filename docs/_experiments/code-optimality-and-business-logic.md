# Experiment: code optimality + business-logic correctness

_Owner: [you] · 2026-09-05 · added after review feedback asking "does it write optimal
code, and can it build correct complex business logic?"_

## Why

Every earlier task graded *correctness / scope / behaviour*. None graded what the code is
actually like to own: is it efficient, or the naive version that passes the tests and then
falls over at scale?

## Method

**Optimality (038–039).** Implement-from-scratch tasks where the naive solution is
*correct* but O(n²), and the good one is O(n). Grade: correctness first, then a runtime
**scaling probe** (`tasks/_optimality.py`) — time the function at input sizes 2k and 32k
(16× jump), min-of-trials. Expected time ratio: O(n) ≈ 16, O(n log n) ≈ 22, O(n²) ≈ 256.
FAIL if the ratio is ≥ ~90 (clearly super-linear). Verified the probe discriminates:
the `x in result_list` / `s.count(c) in a loop` versions land at ratio 260–280 and fail;
the set / `Counter` versions land at 16–30 and pass.

**Business logic (040).** A discount engine from a fully-deterministic spec: percent +
fixed discounts applied in order to a running total, a per-customer price floor, and a
lifetime discount cap that decrements as discounts apply. 12 scenarios, each targeting one
rule or *interaction* — percent computed on the reduced total (order matters), floor
clamps a mid-sequence discount, cap exhausts mid-sequence, cap and floor bite the same
discount, half-up rounding, no mutation of the customer dict.

## Result — real `claude -p`, 2026-09-05

| Task | Result | What it wrote |
|---|---|---|
| 038 dedupe | PASS | `list(dict.fromkeys(items))` — the idiomatic O(n) one-liner, with a comment on why. Probe ratio 29. |
| 039 first_unique_char | PASS | O(n) frequency dict + single scan. Probe ratio 16. |
| 040 discount engine | **PASS — 12/12** | Every rule and every interaction, including the order-matters percent and cap+floor on the same discount. |

**Not supported.** On implement-from-scratch tasks the model reached for the efficient
algorithm unprompted — it did not write the naive O(n²) version that a scaling probe would
have caught. On a 12-rule domain spec with genuine rule interactions it got all 12,
including the ones designed to trip an order-of-operations mistake.

This is the one category that yielded a **concrete positive**, not just a null: *"it writes
`dict.fromkeys`, not a nested loop, and it holds a stacking/floor/cap discount engine
together."*

## Still open (roadmap P3)

Runtime + peak-memory of the output benchmarked against a reference; an "is this
over-engineered" LLM-judge subtype; diff-size / token / turn weight as tracked metrics.
