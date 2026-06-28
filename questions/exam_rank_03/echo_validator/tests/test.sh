#!/usr/bin/env bash

set -e

EXERCISE="echo_validator"
FILE="echo_validator.py"
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
    ("A man, a plan, a canal: Panama", True),
    ("race a car", False),
    (" ", True),
    ("", True),
    ("No lemon, no melon", True),
    ("12321", True),
    ("1231", False),
    ("ab_a", True),
]

sys.exit(run_cases("$TARGET", "echo_validator", tests))
PYTHON
