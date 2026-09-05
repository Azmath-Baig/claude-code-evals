# Authoring a task

A task is a folder under `tasks/` named `NNN-short-slug/`. This is the skilled part of
the project — the harness is trivial, but a well-designed task isolates *one behavior* and
verifies it automatically.

## Files

| File | Required | Purpose |
|---|---|---|
| `task.md` | yes | The prompt handed verbatim to the agent. Written as a developer would ask. |
| `verify.sh` | yes | Exits `0` iff the agent succeeded. Run with `bash` inside the mutated workspace. |
| `task.json` | no | `{ "type": "...", "notes": "what behavior this probes" }`. `type` groups tasks in the report. |
| `workspace/` | yes | The starting repo state. Copied fresh for every run; the agent mutates this copy. |

## Rules for a good task

1. **One behavior per task.** If it fails, you should know *why* from the task type alone.
2. **Automated, binary verification.** A test that passes, a script that exits 0, a string
   that appears in a file. No human judgement in `verify.sh`.
3. **Guard the things the agent shouldn't touch.** e.g. checksum `tests/` and fail if it
   changed (see task 001). Otherwise "make the tests pass" gets solved by deleting tests.
4. **Solvable but not trivial.** If every agent passes or every agent fails, the task gives
   you no signal. Aim for tasks that split the field.
5. **Fast.** Keep `workspace/` tiny and `verify.sh` under ~30s where possible.
6. **Deterministic.** No network, no clocks, no randomness in the verifier.

## Task types to cover (target ~3 each)

| Type | Probes |
|---|---|
| `stacktrace-bugfix` | Localize + minimal fix from a failing test |
| `multi-file-refactor` | Consistent change across many files, nothing missed |
| `feature-spec` | Implement a described feature with tests you provide |
| `ambiguous-spec` | Does it ask a clarifying question, or silently assume? |
| `repo-navigation` | Find the right place to change in an unfamiliar large repo |
| `flaky-test-triage` | Diagnose an intermittently failing test |
| `security-sensitive` | Make a change without introducing an obvious vuln |
| `tool-recovery` | Recover after an early wrong command / bad edit |

## Verifying an `ambiguous-spec` task

These can't be graded purely by tests. Options:
- `verify.sh` checks that the transcript (`../stdout.log`) contains a question mark directed
  at the user before any edit — crude but works as a first pass.
- Or mark the task `"grade": "manual"` in `task.json` and score it by hand in `01-findings.md`.
Keep manual tasks to a minority so the suite stays reproducible.

## Checklist before committing a task

- [ ] `bash verify.sh` fails on the untouched `workspace/` (the bug/gap is real)
- [ ] Applying the intended fix by hand makes `bash verify.sh` pass
- [ ] `task.md` reads like a real developer request, no meta-instructions to "the agent"
- [ ] Guards in place for files that must not change
- [ ] `task.json` names the behavior being probed
