#!/usr/bin/env bash
# Run by the grader with cwd = the MUTATED workspace copy. Do not cd.
set -u
python "$(dirname "$0")/check.py"
