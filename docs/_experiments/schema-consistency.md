# Experiment: schema-consistency (timestamp type/format drift)

_Owner: [you] · Started 2026-09-04_

## Origin

Real usage: asked Claude Code to add a history table capturing a progress value over
time. Data later stopped flowing between the two tables; root cause was a date
type/format mismatch between the new table and the existing one. Symptom (progress not
updating) was several steps removed from the cause.

## Hypothesis

When creating a new table meant to mirror an existing one, the agent does not always
carry the existing timestamp convention (ISO-8601 string, tz-aware) into the new schema,
and instead introduces a silent mismatch (`CURRENT_TIMESTAMP` default → `"YYYY-MM-DD
HH:MM:SS"`, naive `datetime.now()`, or unix epoch int). The mismatch is invisible at
write time and breaks at read time.

## Design

| Task | Prompt | Schema | Isolates |
|---|---|---|---|
| 002 | explicit: "same columns … copy … unchanged" | 1 table | base rate with a tight spec |
| 003 | vague: "store the history … so I can look back" | 1 table (same as 002) | prompt quality effect (002 vs 003) |
| 004 | explicit (same as 002) | 11 tables, 3 timestamp conventions present | schema-size / distractor effect (002 vs 004) |

Verifier `check.py` (shared), 7 assertions:
1. `progress_history` created with `task_name, percent, updated_at`
2–3. `record_progress` / `get_progress` unchanged; one latest row per task
4. prior percents captured in history
5. **history `updated_at` is an ISO string that `parse_ts` accepts and is tz-aware**
6. **archived row keeps the original `updated_at` (not re-stamped)**
7. **date-range query over history with ISO bounds returns the rows**

Failure of 5, 6, or 7 = the mismatch reproduced.

## Runs

Method: blind Claude agent, no access to `check.py`, isolated workspace copy,
non-interactive (cannot ask clarifying questions — states assumptions and proceeds).
N = 1 per variant for this first pass; repeat 3× before treating any number as real.

### Round 1 — 2026-09-04 (N=1 each, blind general-purpose Claude agent, not `claude` CLI headless)

| Task | Result | Which assertions failed | What the agent did |
|---|---|---|---|
| 002 crisp/small | **PASS 7/7** | none | `INSERT INTO progress_history (…) SELECT … FROM progress WHERE task_name=?` — copies the row in SQL, structurally cannot reformat or re-stamp. |
| 003 vague/small | **FAIL** | #1 only | Chose a *different design*: append-only log, one row **per call** (not snapshot-before-overwrite), column named `recorded_at` not `updated_at`, added `get_progress_history()`. **Timestamp format was correct** — ISO-8601 string, tz-aware (`now_iso()`). |
| 004 crisp/big | **PASS 7/7** | none | Same `INSERT … SELECT` as 002. Docstring explicitly noted the 3 competing timestamp conventions and deliberately matched `progress`'s ISO string. |

## Findings — Round 1

- **Does the timestamp type/format mismatch reproduce with an explicit prompt?** No, in 2/2
  explicit runs (small and big schema). The model chose `INSERT … SELECT`, which can't drift.
- **Is it mostly a prompt problem?** The vague run (003) did *not* produce a format mismatch
  either — but it did produce a **schema-shape divergence**: different column name, different
  semantics for what a "history row" means. In a real codebase with existing readers expecting
  `updated_at` and snapshot semantics, that divergence is a plausible cause of "data stops
  flowing between the two tables" — closer to the real-world symptom than a pure date-format bug.
- **Does big schema make it worse?** Not in this single run — the model surfaced the competing
  conventions and picked correctly. Needs the harder variant (below) and more repeats.
- **Failure mode actually observed:** on an underspecified schema request, the model makes
  reasonable-but-divergent modeling choices (naming, "log every call" vs "snapshot before
  overwrite") that won't match what surrounding code / the developer assumed.

### Reframed hypothesis for Round 2

The developer-relevant risk is **schema-shape / semantics divergence on underspecified
schema-change requests**, not date-format mangling specifically. The original real-world bug
was likely some mix of: a vaguer prompt, a much larger/older real codebase, long-session
context drift, a follow-up edit (not the initial table creation), or an earlier model version.

### Round 2 — 2026-09-04 (blind general-purpose Claude agent; N=3 for 003 and 005)

| Task | Runs | Result | Notes |
|---|---|---|---|
| 005 forced/explicit (fresh `archived_at`, no `INSERT..SELECT` escape hatch) | a,b,c | **PASS 3/3** | All three used `now_iso()` for `archived_at` — matched the ISO/tz-aware convention exactly. Removing the escape hatch did **not** produce timestamp drift. |
| 003 vague/small | R1, b, c | **FAIL 3/3, identical divergence** | Every run: append-on-every-write (not snapshot-before-overwrite), history column named `recorded_at` (not `updated_at`), extra `get_history()` helper. Timestamps always correct ISO/tz-aware. |

Combined across both rounds:
- **Explicit prompt (002, 004, 005 ×3): 5/5 PASS.** The model matches the existing timestamp
  convention reliably, even with distractor conventions (004) and even when it must generate a
  new timestamp itself (005).
- **Vague prompt (003 ×3): 3/3 the SAME divergence.** Not random — a stable set of unprompted
  modeling decisions.

### Round 3 — 2026-09-04 (REAL `claude -p` CLI, headless, N=1 each)

First run void: harness bugs (prompt truncated by Windows argv; no edit permission; verifier
`cd`'d to the pristine task dir so it graded unmodified code). After fixes (prompt via stdin,
`--dangerously-skip-permissions`, verifier runs in the mutated workspace):

| Task | Prompt | Result | Notes |
|---|---|---|---|
| 002 | explicit / small | **PASS** | `INSERT INTO progress_history … SELECT … FROM progress` |
| 003 | vague | **FAIL** | `progress_history` has `recorded_at`, not `updated_at`; append-on-every-write. Timestamp format fine (ISO, tz-aware). |
| 004 | explicit / big schema | **PASS** | same `INSERT … SELECT` |
| 005 | explicit / forced fresh timestamp | **PASS** | used `now_iso()` for `archived_at` |

**The real CLI reproduces the blind-run result exactly.** Explicit prompt 3/3 pass; vague
prompt fails with the identical divergence (`recorded_at`, log-not-snapshot).

### Round 3b — 2026-09-04 (real `claude -p`, 3× repeat)

Three consecutive full runs: **every run identical** — 002 PASS, 003 FAIL, 004 PASS, 005 PASS.
All three 003 failures are byte-for-byte the same: `progress_history(id, task_name, percent,
recorded_at)`, append-on-every-write, `progress` upsert left untouched. Zero variance.

### Total evidence

| | Explicit prompt (002, 004, 005) | Vague prompt (003) |
|---|---|---|
| Blind general-purpose agent | 5/5 PASS | 3/3 same divergence |
| Real `claude -p` CLI (4 runs: 1 + 3× repeat) | **12/12 PASS** | **4/4 same divergence** |
| **Combined** | **17/17 PASS** | **7/7 identical divergence** |

## Findings — CONFIRMED (stable across 3× real-CLI repeat)

**The original "date-format drift" hypothesis is not supported.** The model is genuinely good
at carrying timestamp type/format across when the request is clear.

**What reproduces instead:** on an underspecified "add history" request, the model reliably
(3/3) makes the same load-bearing modeling choices without flagging them:
1. **append-on-every-write** instead of snapshot-the-old-row-before-overwrite;
2. a **new column name (`recorded_at`)** instead of mirroring the existing `updated_at`.

It never surfaces that these were choices, and never asks. Because the failure disappears
entirely with an explicit prompt, this is **not a capability gap — it's a
clarification/assumption-surfacing gap.**

### Why a developer cares

If surrounding code, queries, or migrations expect `updated_at` and snapshot semantics, the
new table silently doesn't integrate — the same class as the real-world bug that started this
("data not flowing between the two tables"). The cost lands later, far from the change.

### Proposed behavior change (draft for 01-findings.md)

When a schema-change request is underspecified on a dimension that determines whether the new
schema integrates with existing code — e.g. whether to mirror an existing column's name/type,
or snapshot-vs-log semantics — the agent should either ask one targeted question or state the
assumption prominently in its summary (not buried), rather than silently picking.

### Caveats

- N=3, blind general-purpose agent (not `claude -p`), single model version. "3/3 identical"
  may partly reflect the subagent harness or the framing of my run prompt. **Confirm with the
  real CLI** (`docs/RUN_IT_YOURSELF.md`) before treating as a finding rather than a candidate.
- The run prompt told the agent to "state your assumption and proceed" — so this measures what
  it does when it *can't* ask. A separate task should test whether it asks when it can.

## Would a developer care?

Yes — silent, delayed, cause far from symptom, common bug class, erodes trust in
agent-authored schema changes. See `01-findings.md` for the write-up.

## Next

- [x] Re-run with the real `claude` CLI headless (`claude -p`) — Round 3, reproduces
- [x] Repeat the CLI run 3× — Round 3b, byte-identical every run
- [x] Build the `underspecified-schema` family — tasks 006-009 (see below)
- [ ] Run 006-009 with the real CLI ×3; fill the results table

## Family: `underspecified-schema` (tasks 006-009)

Shared fixture `tasks/_family_base/store.py` — a task tracker with visible conventions
(singular table names; `<table>_id INTEGER NOT NULL REFERENCES <table>(id)`;
`created_at`/`updated_at` ISO-8601 UTC; `state` columns with a `*_STATES` tuple + `CHECK`).
Each task is a vague request; the check grades convention-adherence, not just functionality.

| Task | Vague ask | Convention-following answer | Divergence it catches |
|---|---|---|---|
| 006 status-enum | "let me mark a task archived" | extend `state` domain + `TASK_STATES` + `CHECK` | adds a boolean `archived`/`is_archived` column → two sources of truth |
| 007 foreign-key | "tie each comment to a user" | `user_id INTEGER NOT NULL REFERENCES user(id)` | `author`/`user` naming, TEXT, nullable, no `REFERENCES` |
| 008 table-split | "pull address fields into their own table" | singular-named table + conventional FK + `get_user` joins | plural/odd name, non-conventional link, callers silently lose fields |
| 009 naming-mirror | "log every user login" | new table, `created_at` (ISO tz-aware), `user_id` FK | timestamp named `time`/`logged_at`; naive/`CURRENT_TIMESTAMP`; FK not `user_id` |

All four: verified to FAIL on the untouched fixture and PASS with a conventional reference fix.

### Family results — real `claude -p`, 3× (2026-09-04)

| Task | run 1 | run 2 | run 3 | notes |
|---|---|---|---|---|
| 006 status-enum | PASS | PASS | PASS | extended `state` + `TASK_STATES` + `CHECK`; added a migration; no boolean column |
| 007 foreign-key | PASS | PASS | PASS | `user_id INTEGER NOT NULL REFERENCES user(id)` |
| 008 table-split | PASS | PASS | PASS | singular `address` table, conventional FK, `get_user` joins, callers intact |
| 009 naming-mirror | PASS | PASS | PASS | `login` table, `created_at` via `now_iso()`, `user_id` FK |

**12/12.** In 006, 008, 009 the model's own summary explicitly says it is "following the
codebase conventions" and names them (singular table names, `<table>_id` FK, `created_at`
via `now_iso()`, matching `add_comment`'s style).

## Interpretation — the finding shrank

The broad claim ("on underspecified schema changes the model silently makes bad
assumptions") **is not supported.** Given visible, repeated codebase conventions, the model
follows them reliably on vague requests.

What is left is narrow and partly an artifact of the grader:

- **003 is not a convention-following task.** It asks to mirror *one specific existing
  column* (`progress.updated_at`) into a new table. There is no repeated pattern forcing the
  name, and `recorded_at` is a defensible — arguably better — name for "when this history
  row was recorded."
- **003 has a real design fork** (snapshot-before-overwrite vs append-every-write) with two
  legitimate answers. `check.py` encodes one of them as "correct."
- So the 003 "failure" is mostly: a genuinely ambiguous ask + an opinionated verifier. The
  model's output is a reasonable history-table design, not a bug.

The only residue worth keeping: *when a request is genuinely ambiguous between two good
designs and there's no convention to anchor on, the model picks one without flagging it as a
judgment call.* 003 as currently built does not cleanly prove even this, because its output
is defensible on its own terms.

## Task 010 (sharpened 003) — real `claude -p`, 3×

Workspace now ships `report.py`: real SQL against `progress_history(task_name, percent,
updated_at)`, a docstring stating snapshot-before-overwrite semantics, "DO NOT CHANGE THIS
FILE". task.md points at it.

| run 1 | run 2 | run 3 |
|---|---|---|
| PASS | PASS | PASS |

The model's summary: *"the ordered lookups `report.py` does … Verified against both
`report.py` functions."* It opened the dependent file, named the column `updated_at` to
match, used snapshot-before-overwrite (`INSERT … SELECT … FROM progress`), and preserved the
original timestamps. The exact opposite of the 003 behaviour — because this time there was
something concrete to anchor on.

## Conclusion — line closed, hypothesis not supported

| Situation | Runs | Result |
|---|---|---|
| Explicit prompt names the columns (002, 004, 005) | 17 | all pass |
| Vague prompt, but visible repeated conventions (006–009) | 12 | all pass, model names the conventions it's matching |
| Vague prompt, visible dependent code (010) | 3 | all pass, model consults `report.py` |
| Vague prompt, **nothing to anchor on**, two equally valid designs (003) | 7 | "fails" `check.py`, which encodes one of the two designs |

**Claude Code matches whatever context exists** — a convention, a spec, or a neighbouring
file. The only "divergence" we could produce was 003, where there genuinely was no anchor
and `recorded_at` + append-log is a legitimate design. That's a property of the task + an
opinionated verifier, not a model defect.

003 is retained in the suite as a documented example (see `00-eval-spec.md` §9): a verifier
that grades one of several valid designs manufactures a false signal.

**Next: a different capability area.** This one is done.
- [ ] **Harder variant:** existing code writes timestamps via `CURRENT_TIMESTAMP` default;
      ask to add a column that must be queried alongside an ISO column — force the choice
- [ ] **Long-context variant:** precede the task with several unrelated edits in one session,
      see if convention-matching degrades
- [ ] **Underspecified-schema family** (the reframed hypothesis): 3–4 vague schema-change asks,
      grade on "does the new schema match existing naming + semantics conventions"
- [ ] Add sibling tasks: nullability mismatch, id type mismatch, enum/text value mismatch
- [ ] If it reproduces: draft the proposed behavior change for `01-findings.md`
