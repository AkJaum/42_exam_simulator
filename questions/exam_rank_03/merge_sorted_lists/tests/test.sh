#!/usr/bin/env bash

set -e

EXERCISE="merge_sorted_lists"
FILE="merge_sorted_lists.py"
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
    (([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6]),
    (([1, 2, 4], [1, 3, 4]), [1, 1, 2, 3, 4, 4]),
    (([], [0]), [0]),
    (([], []), []),
    (([-3, -1], [-2, 0]), [-3, -2, -1, 0]),
    (([5], []), [5]),
]

sys.exit(run_cases("$TARGET", "merge_sorted_lists", tests))
PYTHON
