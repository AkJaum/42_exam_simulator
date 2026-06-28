#!/usr/bin/env bash

set -e

EXERCISE="crypto_sorter"
FILE="crypto_sorter.py"
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
    (["apple", "Banana", "kiwi", "orange", "Egg"], ["Egg", "kiwi", "apple", "Banana", "orange"]),
    (["a", "bb", "ccc", "dd"], ["a", "bb", "dd", "ccc"]),
    (["abc", "acb", "bac"], ["abc", "acb", "bac"]),
    ([], []),
    (["Z", "a", "A"], ["A", "Z", "a"]),
    (["aa", "b", "ab", "ba"], ["b", "aa", "ab", "ba"]),
]

sys.exit(run_cases("$TARGET", "crypto_sorter", tests))
PYTHON
