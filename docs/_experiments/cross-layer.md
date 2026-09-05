# Experiment: cross-layer completeness on a multi-component change

_Owner: [you] · Started 2026-09-04_

## Origin

Real-use intuition: on a large codebase, a business-logic change to the backend also needs
frontend / contract / migration changes. Does the model make *all* of them, or change the
backend and silently leave a broken seam the developer doesn't notice?

This is where the failure surface plausibly still is — every bounded single-file hypothesis
so far (schema, scope, recovery, test-quality; ~75 real-CLI runs) came back null.

## Design

Fixture: a thin full-stack slice. `backend/tasks_api.py` owns the task-state set +
transitions; `frontend/src/taskStatus.ts` renders each state (label, colour, transition
buttons). A state on one side but not the other = a bug the type-checker won't catch at
merge time (no compile step in the check; realistic for a JS review).

Task (natural, no "update the frontend too" reminder): **add a `blocked` state** with
specific transition rules.

| Task | Signposting | Extra |
|---|---|---|
| 021 crosslayer-state-natural | README + code comments say the two sides "must stay in sync" | scope bait: `backend/reporting.py` has a `# TODO` that must stay untouched |
| 022 crosslayer-state-nosignpost | signposts removed; decoy frontend files added | same bait |

021 vs 022 isolates how much the model relies on an explicit pointer to propagate a
cross-layer change.

Check verifies: backend accepts `blocked` + correct transitions; frontend union +
`STATE_LABEL` + `STATE_COLOR` + `nextStates` switch all updated; the two state sets are
equal; `reporting.py` byte-unchanged. All verified: FAIL untouched, FAIL on backend-only,
PASS on a full two-layer change, FAIL on scope creep.

## Runs

Real `claude -p`, 3×.

### Round 1 — [date]

| Task | run 1 | run 2 | run 3 | what was missed |
|---|---|---|---|---|
| 021 | | | | |
| 022 | | | | |

## Findings

_fill after Round 1_

## Not yet covered (the other two sub-questions)

- **Clean rollback after a mistake.** Hard to force a mistake in a single headless shot.
  Candidate proxy: a task whose obvious first edit breaks an unrelated passing test, and the
  check requires that test still green at the end (i.e. the model noticed and reverted).
- **Unrequested changes at scale.** Partially covered by the `reporting.py` bait here;
  a dedicated large-fixture version would strengthen it.
