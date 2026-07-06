#!/usr/bin/env bash

set -e

EXERCISE="pattern_tracker"
FILE="pattern_tracker.py"
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
    ("1234", 3),
    ("a1b2c3", 2),
    ("9876", 0),
    ("135", 0),
    ("abc", 0),
    ("", 0),
    ("1", 0),
    ("0123456789", 9),
    ("1a2b3c4", 3),
    ("112233", 3),
]

sys.exit(run_cases("$TARGET", "pattern_tracker", tests))
PYTHON