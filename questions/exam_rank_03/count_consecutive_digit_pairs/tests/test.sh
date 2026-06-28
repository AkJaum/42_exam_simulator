#!/usr/bin/env bash

set -e

EXERCISE="count_consecutive_digit_pairs"
FILE="count_consecutive_digit_pairs.py"
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
    ("1112233335", 2),
    ("1234", 3),
    ("1111", 0),
    ("", 0),
    ("1", 0),
    ("0123456789", 9),
    ("121212", 3),
    ("989898", 0),
    ("789012", 3),
]

sys.exit(run_cases("$TARGET", "count_consecutive_digit_pairs", tests))
PYTHON
