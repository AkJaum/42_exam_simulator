from __future__ import annotations

import os
import json
import hashlib
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .question_loader import Question


@dataclass
class GradeResult:
    passed: bool
    reason: str
    trace_path: Path
    stdout: str
    stderr: str
    returncode: int


class Grader:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.rendu_dir = session_dir / "rendu"
        self.traces_dir = session_dir / "traces"

    def grade(self, question: Question, attempt_number: int) -> GradeResult:
        answer_dir = self.rendu_dir / question.name
        trace_path = self._trace_path(question, attempt_number)

        missing_files = [
            required for required in question.required_files if not (answer_dir / required).is_file()
        ]
        if missing_files:
            reason = "Arquivos obrigatorios ausentes: " + ", ".join(missing_files)
            result = GradeResult(False, reason, trace_path, "", "", 1)
            self._write_trace(question, answer_dir, result)
            return result

        env = os.environ.copy()
        env["RENDU_DIR"] = str(self.rendu_dir)
        env["ANSWER_DIR"] = str(answer_dir)
        env["QUESTION_NAME"] = question.name
        env["PYTHONPATH"] = str(self.session_dir.parent) + os.pathsep + env.get("PYTHONPATH", "")

        try:
            completed = subprocess.run(
                shlex.split(question.test_command),
                cwd=question.path,
                env=env,
                text=True,
                capture_output=True,
                timeout=int(question.meta.get("timeout_seconds", 10)),
                check=False,
            )
            passed = completed.returncode == 0
            reason = "OK" if passed else "Os testes retornaram KO."
            result = GradeResult(
                passed=passed,
                reason=reason,
                trace_path=trace_path,
                stdout=completed.stdout,
                stderr=completed.stderr,
                returncode=completed.returncode,
            )
        except subprocess.TimeoutExpired as exc:
            result = GradeResult(
                passed=False,
                reason="Tempo limite dos testes excedido.",
                trace_path=trace_path,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                returncode=124,
            )

        self._write_trace(question, answer_dir, result)
        return result

    def _trace_path(self, question: Question, attempt_number: int) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{attempt_number:03d}_{question.name}_{timestamp}.log"
        return self.traces_dir / filename

    def _write_trace(self, question: Question, answer_dir: Path, result: GradeResult) -> None:
        trace_cases, stdout = self._parse_trace_cases(result.stdout)
        lines = [
            f"question: {question.name}",
            f"answer_dir: {answer_dir}",
            f"required_files: {', '.join(question.required_files) or '-'}",
            f"test_command: {question.test_command}",
            f"returncode: {result.returncode}",
            f"passed: {result.passed}",
            f"reason: {result.reason}",
            "",
            "----- test cases -----",
            *trace_cases,
            "",
            "----- stdout -----",
            stdout.rstrip(),
            "",
            "----- stderr -----",
            result.stderr.rstrip(),
            "",
        ]
        result.trace_path.write_text("\n".join(lines), encoding="utf-8")

    def _parse_trace_cases(self, stdout: str) -> tuple[list[str], str]:
        cases: list[str] = []
        remaining: list[str] = []

        for line in stdout.splitlines():
            if not line.startswith("TRACE_CASE\t"):
                remaining.append(line)
                continue

            try:
                payload = json.loads(line.split("\t", 1)[1])
            except json.JSONDecodeError:
                remaining.append("TRACE_CASE <invalid>")
                continue

            case = payload.get("case", "?")
            status = payload.get("status", "UNKNOWN")
            if status == "OK":
                cases.append(f"case {case}: OK")
                continue

            input_hash = self._mask(payload.get("input", ""))
            expected_hash = self._mask(payload.get("expected", ""))
            received_hash = self._mask(payload.get("received", ""))
            cases.extend(
                [
                    f"case {case}: DIFF_KO",
                    f"  input_hash:    {input_hash}",
                    f"  expected_hash: {expected_hash}",
                    f"  received_hash: {received_hash}",
                ]
            )
            if payload.get("error"):
                cases.append(f"  error_hash:    {self._mask(payload['error'])}")

        if not cases:
            cases.append("No structured test cases reported by test.sh.")

        return cases, "\n".join(remaining)

    def _mask(self, value: object) -> str:
        normalized = str(value).encode("utf-8", errors="replace")
        return hashlib.sha256(normalized).hexdigest()[:16]
