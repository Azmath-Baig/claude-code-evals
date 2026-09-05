#!/usr/bin/env bash
# Run by the grader with cwd = the agent's MUTATED workspace copy. Do not cd.
# Exit 0 iff the change keeps schema/type conventions consistent.
set -u
python "$(dirname "$0")/check.py"
