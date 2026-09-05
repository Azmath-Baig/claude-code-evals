# Competitive analysis

_Owner: [you] · Run(s): [Claude Code vs …] · Suite version: [git SHA]_

Same suite, same tasks, same timeouts, run against multiple agents. Goal is not a
leaderboard — it's to convert "where do we lead / trail" into a ranked list of what to
build next.

## Agents compared

| Agent | Version | Model | Invocation | Notes |
|---|---|---|---|---|
| Claude Code | [ ] | [ ] | `agents.json:claude-code` | |
| [Aider] | [ ] | [ ] | | |
| [Codex CLI] | [ ] | [ ] | | |

## Results

Paste from `python harness/report.py --run <claude-code-run> <other-run> --out docs/_generated-results.md`.

| | Claude Code | [B] | [C] |
|---|---|---|---|
| Overall pass rate | | | |
| stacktrace-bugfix | | | |
| multi-file-refactor | | | |
| feature-spec | | | |
| ambiguous-spec | | | |
| repo-navigation | | | |
| ... | | | |
| Median wall-clock / task | | | |
| Timeout rate | | | |

## Where Claude Code leads

- **[type / behavior]** — [margin]. Likely because [ ]. Keep / defend by [ ].

## Where Claude Code trails

| Gap | Size | Task evidence | Root cause hypothesis | Fix surface |
|---|---|---|---|---|
| [ ] | [ ] | [ ] | model behavior / harness / tooling / prompt | [ ] |

## Recommended priorities

Ranked. Each = (developer impact) × (frequency) × (how clearly this suite shows it's real),
minus (cost to fix).

1. **[gap]** — [one line why it's #1].
2. ...
3. ...

## Caveats

- Every agent runs its own harness/tooling; a gap may be scaffold, not model. Note which is
  which where known.
- Small N. Treat < [X]pp differences as noise.
- Public tasks; contamination cuts both ways.
