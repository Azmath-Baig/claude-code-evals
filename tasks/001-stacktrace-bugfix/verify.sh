#!/usr/bin/env bash
# Run by the grader with cwd = the agent's MUTATED workspace copy. Do not cd.
# Passes (exit 0) iff every test passes AND the tests/ dir is untouched.
set -u

if [ -f .verify/tests.sha256 ]; then
  if ! sha256sum -c .verify/tests.sha256 >/dev/null 2>&1; then
    echo "FAIL: files under tests/ were modified"
    exit 3
  fi
fi

python -m pytest -q
