# Experiment: Windows subprocess argv-truncation (sourced from this project's own bug)

_Owner: [you] · 2026-09-05_

## Origin

While building this suite's own harness, `runner.py` passed the task prompt to `claude`
as a command-line argument. On Windows, `claude` resolves to a `.cmd` shim (produced by
`npm install -g`) that re-dispatches its arguments through `cmd.exe`. Multi-line prompts
arrived at the model truncated after the first line, with no error — the model's own
transcripts said things like *"your message got cut off after 'I want to keep'"*. The fix
was to pipe the prompt via stdin instead of passing it as an argument.

## Root cause, verified empirically before building a task around it

```
subprocess.run([resolved_path_to("mytool.cmd"), "line one\nline two\nline three"])
  -> stdout: 'ARG:line one\n'                          # lines 2-3 silently gone

subprocess.run([resolved_path_to("mytool.cmd")], input="line one\nline two\nline three")
  -> stdout: 'STDIN:line one\nline two\nline three\n'   # intact
```

Cause: launching a `.cmd`/`.bat` file goes through `cmd.exe`'s command-line parser, which
treats a newline as a line terminator regardless of quoting — an argument, not stdin. This
is a genuine, reproducible Windows platform mechanism, not specific to Claude Code, but it
directly bit *this* project.

## Reframed as a task, not a war story

The question worth an eval isn't "did I make this mistake" — it's **does Claude Code make
it too, on a fresh, realistic "wrap this CLI tool" request, without being told the specific
pitfall?** Task 030: implement a subprocess wrapper around a `.cmd`-shimmed tool; the ask
explicitly requires "works on Windows" and "prompt can be multi-line" (real ticket
language) without naming the mechanism. Verified: fails when unimplemented, fails
(showing exactly the truncated lines) on the naive argv version, passes on a stdin
version.

## Round 1 — real `claude -p`, N=1

**PASS**, and a sophisticated one. Transcript:

> "Multi-line text passed as a command-line argument is unreliable on Windows
> (cmd.exe/batch argument parsing can mangle or truncate on newlines), and `.cmd` files
> require going through `cmd.exe` rather than being launched directly. Route the prompt
> through stdin instead... invoke `.cmd` files via `cmd.exe /c` so no shell string
> interpolation of user input occurs."

It named the exact mechanism, used stdin, and added a defensive `cmd.exe /c` wrapper that
wasn't even required by the check — then self-tested with an adversarial case (embedded
quotes) before declaring done.

## Conclusion

Not a model gap. The original harness bug happened because the code was written in a
conversational loop without executing it against the real target runtime (no `claude` CLI
or full Windows shell in the authoring environment) — the bug could only be caught by
actually running it there, which is what the user's first real run did. Given a clear,
scoped task with a real check to satisfy, the same model gets this right immediately, with
extra defensive care.

**Sharper finding than "the model has a weak spot":** across this project, every real
miss (this one, the schema-consistency verifier bug, the conflicting-authority keyword
false-negative) traced back to **unverified process** — code or a check not actually
executed against ground truth before being trusted — not to the model reasoning
incorrectly when actually put to a real test. That is the throughline finding.

## Why this one is different from the other 10 categories

It's not testing product logic, scope, or constraint-following — it's testing whether the
model defaults to a **platform-safe** implementation of a common integration pattern
(wrap an external CLI) when the platform isn't stated. Anthropic ships Claude Code as a
CLI itself, installed the same npm-shim way on Windows, so this pattern is not exotic for
its own users — anyone scripting around `claude` the way this project did would hit
exactly this.
