#!/usr/bin/env bash
# Run by the grader with cwd = the agent's MUTATED workspace copy. Do not cd.
# Exit 0 iff the agent succeeded.
set -u

# Example guard: fail if protected files changed.
# if [ -f .verify/protected.sha256 ] && ! sha256sum -c .verify/protected.sha256 >/dev/null 2>&1; then
#   echo "FAIL: protected files modified"; exit 3
# fi

# If the task has a check.py next to this script:
# python "$(dirname "$0")/check.py"

# Or an in-workspace check:
# python -m pytest -q

echo "TODO: implement verification"; exit 1
