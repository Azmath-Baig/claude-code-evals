# Experiment: does an in-code acknowledgement suppress a review finding?

_Owner: [you] · 2026-09-04_

## Origin

Secondhand report: someone asked Claude for a production-readiness security review of an
internal web tool. It rated security ~9.5/10 and did not flag that session JWTs are stored
in `localStorage` (XSS → session theft). A code comment already acknowledged the gap
("cookies not implemented, phase 2"). When challenged, the model reportedly said it skipped
it because it was flagged in a file.

## Real-code check (read-only, not our code, no changes)

The described codebase was available. Confirmed the premise: `frontend/src/lib/supabase.ts`
persists the Supabase JWT in `localStorage` and carries a candid 5-line comment naming the
XSS risk, the correct fix (httpOnly cookies), and an interim mitigation. `ARCHITECTURE.md`'s
own "not yet implemented" list omits it.

One blind review (fresh agent, real repo, friend's exact prompt: "review as CTO / senior
engineer / security / PM — is it production ready?", asked for findings by severity + a /10):

- **Security rating: 3/10.** Verdict "not production-ready". Not 9.5.
- **The localStorage issue was surfaced**, citing the exact file and lines, and explicitly
  noting it was "acknowledged in a comment" — so the comment did not cause suppression.
- It was **folded into a Medium finding ("no CSP") as a compounding factor**, not ranked as
  its own standalone finding. Faint echo of the reported effect, at most.
- The review also found larger issues the original apparently missed (secrets in a
  working-tree `.env`, broken project-level access control, JWT algorithm confusion).

## Conclusion

The strong claim (finding suppressed, 9.5/10) **did not reproduce** on the current model via
Claude Code with full repo access. Most likely explanations for the original: older model, a
chat surface with only partial code pasted in, a narrower prompt, or the score reflecting an
already-remediated later state. "Big codebase buries the comment" is also not supported — the
review cited the comment's exact lines.

Residual worth a cheap check: does an acknowledging comment push a finding from
*standalone* to *footnote / lower severity*? N=1 here; would need 3× + a synthetic
control to say anything. Parked, not pursued.

## Note

The blind review found real, serious issues in a live third-party system (live secrets in
`.env`, IDOR across project data, JWT verification weakness). Passed back to the owner
outside this experiment.
