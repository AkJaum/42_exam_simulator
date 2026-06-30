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
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("student", "$TARGET")
module = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(module)
except Exception as e:
    print("KO")
    print(e)
    sys.exit(1)

if not hasattr(module, "crypto_sorter"):
    print("KO")
    print("Function crypto_sorter not found.")
    sys.exit(1)

tests = [
    (["apple", "Banana", "kiwi", "orange", "Egg"], ["Egg", "kiwi", "apple", "Banana", "orange"]),
    (["a", "bb", "ccc", "dd"], ["a", "bb", "dd", "ccc"]),
    (["abc", "acb", "bac"], ["abc", "acb", "bac"]),
    ([], []),
    (["Z", "a", "A"], ["A", "Z", "a"]),
    (["aa", "b", "ab", "ba"], ["b", "aa", "ab", "ba"]),
]

for value, expected in tests:
    result = module.crypto_sorter(value)
    if result != expected:
        print("KO")
        print(f"Input:    {value}")
        print(f"Expected: {expected}")
        print(f"Received: {result}")
        sys.exit(1)

print("OK")
PYTHON