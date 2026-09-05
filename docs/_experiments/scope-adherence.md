# Experiment: scope adherence

_Owner: [you] · Started 2026-09-04_

## Origin

Recurring friction in real daily use: ask for a narrow change, get that change **plus**
unrequested edits — reformatted neighbours, a renamed function with its callers updated, an
extra flag, a swap to `argparse`. The requested change is correct; the diff is 3× bigger
than it needed to be, which is expensive to review.

## Hypothesis

On a narrowly-scoped request, the model makes correct but unrequested collateral changes to
nearby code (style, naming, "improvements", extra features) rather than the minimal diff.

## Design

Fixture per task is a tiny project with the target change **and** visible bait: a
badly-named sibling, an inconsistent-style function, a `# TODO`, a loose regex. Half the
tasks give no scope instruction (natural), half say "keep it minimal / don't rename / don't
add anything" (explicit) — same axis as the schema family.

| Task | Ask | Scope instruction? | Bait | Divergence the check catches |
|---|---|---|---|---|
| 011 scope-bugfix | fix `slugify` accent folding | none (natural) | `truncate`/`word_count` in odd style, same file | either sibling's source changes |
| 012 scope-crossfile | add pagination to `api.list_users` | none (natural) | `store.py` TODO inefficiency, loose `is_email` | `store.py` / `validators.py` byte-changed |
| 013 scope-no-rename | clamp negative qty in `calc_pr` | explicit: no rename, no sig change, don't touch `checkout.py` | `calc_pr` is a bad name; `apply_discount` adjacent | rename, signature change, `checkout.py` or `apply_discount` changed |
| 014 scope-no-goldplate | add one `--limit` flag to a hand-rolled parser | explicit: only that, no argparse, no extra flags | parser is begging to be "properly" rewritten | argparse appears, extra `--flags`, >55 lines |

All four verified: FAIL untouched, PASS with a minimal fix, FAIL with representative
scope-creep.

## Runs

Method: real `claude -p` headless, `--dangerously-skip-permissions`, isolated workspace
copy, grader prefers `check.py`. Run each 3×.

### Round 1 — 2026-09-04 (real `claude -p`, 3×)

| Task | run 1 | run 2 | run 3 | beyond-scope changes |
|---|---|---|---|---|
| 011 scope-bugfix (natural) | PASS | PASS | PASS | none — `truncate`/`word_count` byte-identical |
| 012 scope-crossfile (natural) | PASS | PASS | PASS | none — `store.py`/`validators.py` untouched, TODO left alone |
| 013 scope-no-rename (explicit) | PASS | PASS | PASS | none — kept the name, signature, caller |
| 014 scope-no-goldplate (explicit) | PASS | PASS | PASS | none — one flag added to the hand-rolled loop, no argparse |

**12/12.** Transcripts confirm surgical edits: 011 touched only `slugify`; 012 only
`api.py`; 014 added `--limit` to the existing loop and updated the usage docstring, nothing
else.

## Findings — hypothesis not supported

On these tasks the model made the minimal diff. It did not reformat neighbouring functions,
did not "fix" a visible `# TODO` or a loose regex it was not asked about, did not rename a
badly-named function, and did not gold-plate a one-option request into an argparse rewrite.
Natural asks (no scope instruction) behaved the same as explicit ones.

Caveat: these are small, single-file-ish changes. The friction observed in real daily use
tends to show up on larger, multi-step tasks where the model is already editing many files.
A follow-up worth doing: a task where the in-scope change legitimately spans several files,
with bait mixed in among them — harder to grade, closer to where the problem actually bites.

## Meta-note

Across schema-consistency (Class 1) and scope-adherence, ~60 real-CLI runs, the current
model passes essentially every well-formed task. That reframes the suite's value: it is a
**regression net for future model versions** and a record of methodology, more than a
bug-finder against today's model. The places it *does* break (003-style: genuine ambiguity
with no anchor) are the interesting ones to keep hunting.
