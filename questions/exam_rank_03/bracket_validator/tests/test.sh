#!/usr/bin/env bash

set -e

EXERCISE="bracket_validator"
FILE="bracket_validator.py"
RENDU_DIR="${RENDU_DIR:-rendu}"
TARGET="$RENDU_DIR/$EXERCISE/$FILE"

if [ ! -f "$TARGET" ]; then
    echo "KO: $TARGET not found."
    exit 1
fi

python3 <<PYTHON
import sys
from simulator.test_case_trace import run_cases

tests = [
    ("", True),
    ("()", True),
    ("()[]{}", True),
    ("({[]})", True),
    ("((()))", True),
    ("([{}])", True),
    ("(]", False),
    ("([)]", False),
    ("(", False),
    (")", False),
    ("{[(])}", False),
    ("(()", False),
    ("())", False),
]

sys.exit(run_cases("$TARGET", "bracket_validator", tests))
PYTHON
