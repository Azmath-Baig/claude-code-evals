# Daily Claude Code user log

_Owner: [you] · Started 2026-09-04_

A dated record of using Claude Code on real work. Purpose: (1) be able to speak concretely
about what it does well and where it fails; (2) source real gaps that become tasks in
`tasks/`.

The entries below are from building this suite (2026-09-04 to -05) — real usage, real
friction, on Windows, `claude -p` v2.1.260. Keep adding your own as you go; the value is in
the volume over time.

---

### 2026-09-04 — building the harness (`runner.py`) to invoke `claude -p` per task
**Context:** small Python project; wiring a subprocess wrapper around the `claude` CLI on Windows.
**What happened:** multi-line task prompts arrived at the model **truncated after the first
line**, with no error. The model's own output said things like *"your message got cut off
after 'I want to keep'"*. Root cause: `claude` on Windows is an npm `.cmd` shim; a multi-line
string passed as a command-line argument gets cut at the first newline by `cmd.exe`'s parser.
**Category:** failure (silent, environment-specific)
**My read:** not a model defect — a platform trap in *my* harness code, invisible without
running it in the real target environment. But it cost an hour, and anyone scripting around
`claude` on Windows (a common thing — same install path as `eslint`, `tsc`, etc.) will hit it.
**→ Task:** `030-windows-subprocess-argv-truncation` — and when given that exact task
scoped and explicit, the model produced a *more* defensive fix than my reference (stdin +
`cmd.exe /c`, self-tested with embedded quotes). The gap was process, not capability.

### 2026-09-04 — headless editing silently no-ops without the right flag
**Context:** first real harness run.
**What happened:** `claude -p` with `--permission-mode acceptEdits` didn't edit anything —
it asked for permission and, being non-interactive, effectively stalled. Needed
`--dangerously-skip-permissions`.
**Category:** friction (docs / discoverability)
**My read:** minor, but the failure mode (a run that "completes" having done nothing) looks
identical to a real 0% score. Worth a clearer headless-mode error or a doc note.
**→ n/a** (documented in `docs/RUN_IT_YOURSELF.md`)

### 2026-09-04 — vague vs anchored schema changes
**Context:** ~5-file SQLite fixtures; "add a history table" style asks.
**What happened:** on a genuinely ambiguous ask with nothing to anchor on (mirror one
specific column, or two equally valid designs), the model picks a reasonable option and
doesn't flag that it made a load-bearing choice. Add *any* anchor — a repeated codebase
convention, or a neighbouring file that consumes the schema — and it matches it every time.
**Category:** nuance
**My read:** this is the boundary. It's not "silently wrong"; it's "silently *chose*". A
one-line "I assumed X; say so if you wanted Y" would close it. Below that bar it's fine.
**→ Tasks:** `002–010` (schema-consistency family)

### 2026-09-05 — 7-turn evolving task, no reminders
**Context:** notification-preferences feature; build → refactor → optimize → bulk update →
response format → caching → fix tests, across one session.
**What happened:** re-checked all 6 original requirements at the end independently. **10/10
survived.** Backward compatibility, existing-user defaults, admin-can't-override-explicit,
no stale reads after caching, atomic bulk update.
**Category:** win
**My read:** better long-horizon constraint retention than I expected. The obvious next test
is 30 turns / hundreds of files / requirements in genuine tension.
**→ Task:** `028-longhorizon-notif-prefs`

### 2026-09-05 — pushback on directives a senior would question
**Context:** 5 one-line changes that are each a bad idea (remove retry logic, uninvalidated
global cache, drop a money-path guard, swallow sync exceptions, hardcode a live secret).
**What happened:** warned on 2, **declined 3 outright** and proposed a safer alternative.
On the money-path guard: *"charge(account, -500) does balance -= -500, i.e. it credits the
account. No error, no log — just money created."*
**Category:** win / surprising (better than the "compliant junior" hypothesis predicted)
**→ Tasks:** `031–035` (pushback family, LLM-judge graded)

### 2026-09-05 — judgment with no answer key
**Context:** "here are 3 rate-limiter implementations, which do we ship for a 6-instance
load-balanced gateway?"
**What happened:** picked one decisively **and caught the non-obvious point** — all three
keep per-instance state, so 6 instances inflate the per-key limit ~6× unless state moves to
Redis. Named the tradeoff it was accepting.
**Category:** win
**→ Task:** `036-judgment-pick-implementation`

---

## Rolling summary

**Recurring wins:** convention-matching when any anchor exists; long-horizon constraint
retention (7 turns); pushing back on harmful directives; engineering judgment on open-ended
"which should we ship" questions.

**Recurring friction:** all environment/harness, not model — Windows `.cmd`-shim argv
truncation, headless permission flags, VS Code terminal hijacking git credentials.

**Open questions to test:** horizons past 7 turns; interactive (non-headless) behaviour;
cost/latency/DX (diff size, token count) as tracked metrics; discovery with a false-positive
rate, not just a hit rate.
