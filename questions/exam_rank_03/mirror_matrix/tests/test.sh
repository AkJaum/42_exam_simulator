#!/usr/bin/env bash

set -e

EXERCISE="mirror_matrix"
FILE="mirror_matrix.py"
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
    ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[3, 2, 1], [6, 5, 4], [9, 8, 7]]),
    ([["a", "b"], ["c", "d"]], [["b", "a"], ["d", "c"]]),
    ([[42]], [[42]]),
    ([], []),
    ([[1, 2], [], [3, 4, 5]], [[2, 1], [], [5, 4, 3]]),
]

sys.exit(run_cases("$TARGET", "mirror_matrix", tests))
PYTHON
