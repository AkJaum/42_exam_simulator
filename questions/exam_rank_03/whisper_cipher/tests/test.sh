#!/usr/bin/env bash

set -e

EXERCISE="whisper_cipher"
FILE="whisper_cipher.py"
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
    (("Hello", 3), "Khoor"),
    (("abc", 1), "bcd"),
    (("Zebra!", 2), "Bgdtc!"),
    (("xyz", 3), "abc"),
    (("ABC", 26), "ABC"),
    (("Hello World!", 13), "Uryyb Jbeyq!"),
    (("123!", 5), "123!"),
]

sys.exit(run_cases("$TARGET", "whisper_cipher", tests))
PYTHON
