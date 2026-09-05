# Running the suite with the real Claude Code CLI

The blind runs in `_experiments/` used a general-purpose Claude agent as a stand-in.
For results you can put your name behind, run the actual `claude` CLI headless.

## Prereqs

- `claude` on your PATH (`claude --version` works)
- Python 3.9+
- `bash` available (Git Bash on Windows)

## One agent, whole suite

```bash
cd claude-code-evals
python harness/runner.py --agent claude-code --timeout 900
python harness/grader.py  --run latest
python harness/report.py  --run latest
```

`agents.json` already defines `claude-code` as
`claude -p "{prompt}" --permission-mode acceptEdits`. Adjust the flags there if your
setup needs it (e.g. a model flag, or `--dangerously-skip-permissions` in a sandbox).

## Three repeats (do this before trusting any number)

```bash
cd claude-code-evals
for i in 1 2 3; do
  python harness/runner.py --agent claude-code --timeout 900
  run=$(cat results/latest.txt)
  python harness/grader.py --run "$run"
  echo "=== repeat $i: $run ==="
  python harness/report.py --run "$run"
done
```

Look for tasks whose pass/fail flips between repeats — note them as unstable in
`_experiments/schema-consistency.md`. A task that isn't stable across 3 runs isn't
measuring anything yet.

## Just the schema-consistency family

```bash
python harness/runner.py --agent claude-code \
  --tasks 002-schema-consistency 003-schema-consistency-vague \
          004-schema-consistency-big 005-schema-consistency-forced
python harness/grader.py --run latest
python harness/report.py --run latest
```

## Reading a failure

`results/<run>/<task>/grade.json` has the verifier output (`[FAIL <n>]` tells you which
assertion broke). `results/<run>/<task>/stdout.log` is the agent transcript.
`results/<run>/<task>/workspace/` is the code it produced — diff it against
`tasks/<task>/workspace/` to see exactly what it changed.
