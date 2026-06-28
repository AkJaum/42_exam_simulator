#!/usr/bin/env bash

set -e

EXERCISE="twist_permutation"
FILE="twist_permutation.py"
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
    (([1, 2, 3, 4, 5], 2), [4, 5, 1, 2, 3]),
    (([1, 2, 3], 4), [3, 1, 2]),
    (([10, 20, 30, 40], 0), [10, 20, 30, 40]),
    (([1], 10), [1]),
    (([1, 2], 1), [2, 1]),
    (([1, 2, 3, 4], 8), [1, 2, 3, 4]),
]

sys.exit(run_cases("$TARGET", "twist_permutation", tests))
PYTHON
