from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from .utils import load_json


@dataclass(frozen=True)
class Question:
    exam: str
    name: str
    path: Path
    subject_path: Path
    tests_path: Path
    meta: dict

    @property
    def points(self) -> int:
        return int(self.meta.get("points", 0))

    @property
    def required_files(self) -> list[str]:
        files = self.meta.get("required_files", self.meta.get("expected_files", []))
        return [str(item) for item in files]

    @property
    def test_command(self) -> str:
        return str(self.meta.get("test_command", "bash tests/test.sh"))


class QuestionLoader:
    def __init__(self, questions_root: Path) -> None:
        self.questions_root = questions_root

    def available_exams(self) -> list[str]:
        if not self.questions_root.exists():
            return []
        return sorted(path.name for path in self.questions_root.iterdir() if path.is_dir())

    def load_exam(self, exam: str) -> list[Question]:
        exam_path = self.questions_root / exam
        if not exam_path.is_dir():
            raise ValueError(f"Exame nao encontrado: {exam}")

        questions: list[Question] = []
        for question_path in sorted(path for path in exam_path.iterdir() if path.is_dir()):
            meta_path = question_path / "meta.json"
            subject_path = question_path / "subject.txt"
            tests_path = question_path / "tests" / "test.sh"
            if not meta_path.is_file() or not subject_path.is_file() or not tests_path.is_file():
                continue
            meta = load_json(meta_path)
            name = str(meta.get("name", question_path.name))
            questions.append(
                Question(
                    exam=exam,
                    name=name,
                    path=question_path,
                    subject_path=subject_path,
                    tests_path=tests_path,
                    meta=meta,
                )
            )

        if not questions:
            raise ValueError(f"Nenhuma questao valida encontrada em questions/{exam}.")
        return questions

    def pick_random(self, questions: list[Question], used_names: set[str]) -> Question | None:
        remaining = [question for question in questions if question.name not in used_names]
        if not remaining:
            return None
        return random.choice(remaining)
