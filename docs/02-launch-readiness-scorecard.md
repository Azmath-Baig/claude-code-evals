# Launch-readiness scorecard — new model into Claude Code

_Owner: [you] · Template — instantiate one per candidate model._

A PM-owned gate. The question at launch is not "is the model good" but "is it ready to be
the default coding model for every Claude Code user, and do we know the risks we're
accepting." This scorecard is how that decision gets made with evidence instead of vibes.

## Candidate: [model id] · Target date: [ ] · Decision owner: [you]

### 1. Capability gates (from this suite)

| Gate | Threshold | Current model | Candidate | Verdict |
|---|---|---|---|---|
| Overall pass rate | ≥ [prev − 2pp] | [ ] | [ ] | ⬜ |
| No task type regresses > 10pp | — | — | [ ] | ⬜ |
| Timeout / non-termination rate | ≤ [ ]% | [ ] | [ ] | ⬜ |
| Constraint-violation rate (right answer, wrong way) | ≤ [ ]% | [ ] | [ ] | ⬜ |
| Held-out task set (not public) pass rate | ≥ [ ] | [ ] | [ ] | ⬜ |

### 2. Behavior-change review

New model behaviors that are *different* even if not worse. Each needs an explicit accept /
mitigate / block call.

| Behavior delta | Evidence (task / transcript) | Risk | Call |
|---|---|---|---|
| [ ] | [ ] | [ ] | ⬜ |

### 3. Known regressions accepted

| Regression | Size | Why acceptable now | Follow-up + owner |
|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] |

### 4. Cross-functional sign-off

| Area | Owner | Status | Notes |
|---|---|---|---|
| Model behavior / research | | ⬜ | |
| Claude Code eng | | ⬜ | |
| Evals (this suite) | [you] | ⬜ | |
| Docs / changelog | | ⬜ | |
| Support / DevRel briefed | | ⬜ | |

### 5. Rollout plan

- [ ] Staged rollout: [%] → [%] → 100%, gate metric = [ ], min soak = [ ]
- [ ] Rollback trigger defined and tested: [ ]
- [ ] Live telemetry dashboard for [gate metrics] ready
- [ ] Changelog entry drafted, capability changes called out

### 6. Decision

**GO / GO-WITH-MITIGATIONS / NO-GO** — [date], [owner]

Rationale: [ ]
