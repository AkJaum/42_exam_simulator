#!/usr/bin/env bash

set -e

EXERCISE="number_base_converter"
FILE="number_base_converter.py"
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
    (("1011", 2, 10), "11"),
    (("1A", 16, 2), "11010"),
    (("FF", 16, 10), "255"),
    (("255", 10, 36), "73"),
    (("Z", 36, 10), "35"),
    (("10", 10, 2), "1010"),
    (("102", 2, 10), "ERROR"),
    (("ABC", 10, 2), "ERROR"),
    (("10", 1, 10), "ERROR"),
    (("10", 10, 37), "ERROR"),
]

sys.exit(run_cases("$TARGET", "number_base_converter", tests))
PYTHON
