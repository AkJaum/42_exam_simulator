#!/usr/bin/env bash

set -e

EXERCISE="permutation_checker"
FILE="permutation_checker.py"
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
    (("anagram", "nagaram"), True),
    (("rat", "car"), False),
    (("Listen", "Silent"), True),
    (("", ""), True),
    (("abc", "cab"), True),
    (("abc", "abcd"), False),
    (("aaa", "aab"), False),
]

sys.exit(run_cases("$TARGET", "permutation_checker", tests))
PYTHON
