# Daily Claude Code user log

_Owner: [you] · Started: 2026-09-04_

A dated record of using Claude Code on real work. Purpose:
1. Be able to speak concretely, with examples, about what it does well and where it fails.
2. Source real capability gaps that become tasks in `tasks/`.

Log every session, even good ones. One entry per notable moment. Keep transcript quotes
short and strip anything private.

## Template

```
### 2026-09-DD — [what I was doing]
Context: [repo type, size, task]
What happened: [1–3 sentences]
Category: win | friction | failure | surprising
Transcript snippet: > "..."
My read: [why it did this; what better behavior looks like]
→ Task idea: [type + one line]  (or: n/a)
```

---

### 2026-09-04 — [example — replace]
Context: mid-size Python repo, adding a CLI flag
What happened: asked it to "add a --json flag"; it added the flag and output but also
reformatted an unrelated function, inflating the diff.
Category: friction
Transcript snippet: > "I also cleaned up the formatting in `format_row` while I was here."
My read: unprompted scope expansion. For a reviewer, a tight diff matters more than
opportunistic cleanup. Better: stay within the requested change unless asked.
→ Task idea: `multi-file-refactor` variant that fails if files outside the target set are modified.

---

## Rolling summary (update weekly)

**Recurring wins:** [ ]
**Recurring friction:** [ ]
**Open questions to test in the suite:** [ ]
