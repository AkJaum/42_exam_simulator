from __future__ import annotations

import importlib.util
import json
import sys
import traceback
from typing import Any, Callable, Iterable


def load_function(target: str, function_name: str) -> Callable[..., Any]:
    spec = importlib.util.spec_from_file_location("student", target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, function_name):
        raise RuntimeError(f"Function {function_name} not found.")
    return getattr(module, function_name)


def run_cases(target: str, function_name: str, cases: Iterable[tuple[Any, Any]]) -> int:
    try:
        function = load_function(target, function_name)
    except Exception as exc:
        _emit("setup", "DIFF_KO", "-", "module loaded", repr(exc), traceback.format_exc())
        return 1

    failed = False
    for index, (args, expected) in enumerate(cases, start=1):
        call_args = args if isinstance(args, tuple) else (args,)
        try:
            received = function(*call_args)
            status = "OK" if received == expected else "DIFF_KO"
            if status != "OK":
                failed = True
            _emit(index, status, call_args, expected, received)
        except Exception as exc:
            failed = True
            _emit(index, "DIFF_KO", call_args, expected, repr(exc), traceback.format_exc())

    print("OK" if not failed else "KO")
    return 1 if failed else 0


def _emit(
    case: int | str,
    status: str,
    input_value: Any,
    expected: Any,
    received: Any,
    error: str | None = None,
) -> None:
    payload = {
        "case": case,
        "status": status,
        "input": repr(input_value),
        "expected": repr(expected),
        "received": repr(received),
    }
    if error:
        payload["error"] = error
    print("TRACE_CASE\t" + json.dumps(payload, sort_keys=True))
