from __future__ import annotations

import shutil
import select
import string
import sys
import termios
import threading
import time
import tty
from pathlib import Path
from typing import Callable, TypeVar

from .grader import Grader, GradeResult
from .question_loader import Question, QuestionLoader
from .terminal_launcher import TerminalLaunchResult, open_terminal
from .terminal_ui import TerminalUI
from .timer import CountdownTimer
from .utils import ensure_dir, format_seconds, now_slug, safe_slug, save_json


EXAM_DURATION_SECONDS = 3 * 60 * 60
VALIDATION_DELAY_SECONDS = 2
REAL_MODE_MAX_SCORE = 100
T = TypeVar("T")


class ExamSession:
    def __init__(self, root: Path, login: str, exam: str, mode: str) -> None:
        self.root = root
        self.login = safe_slug(login)
        self.exam = exam
        self.mode = mode
        self.loader = QuestionLoader(root / "questions")
        self.questions = self.loader.load_exam(exam)
        self.session_dir = root / f"exam_{self.login}_{now_slug()}"
        self.subjects_dir = self.session_dir / "subjects"
        self.rendu_dir = self.session_dir / "rendu"
        self.traces_dir = self.session_dir / "traces"
        self.state_path = self.session_dir / "session.json"
        self.ui = TerminalUI()
        self.timer = CountdownTimer(EXAM_DURATION_SECONDS)
        self.grader = Grader(self.session_dir)
        self.used_questions: set[str] = set()
        self.current_question: Question | None = None
        self.current_index = 0
        self.score = 0
        self.attempts = 0
        self.finished = False
        self.finish_reason = ""
        self.real_question_limit = len(self.questions)
        self.terminal_launch_result: TerminalLaunchResult | None = None

    @property
    def mode_label(self) -> str:
        return "Simulador real do exame" if self.mode == "real" else "Simulador mata-mata"

    @property
    def total_questions_target(self) -> int:
        if self.mode == "real":
            return self.real_question_limit
        return len(self.questions)

    @property
    def total_possible_score(self) -> int:
        if self.mode == "real":
            return REAL_MODE_MAX_SCORE
        return sum(question.points for question in self.questions)

    def start(self) -> None:
        ensure_dir(self.subjects_dir)
        ensure_dir(self.rendu_dir)
        ensure_dir(self.traces_dir)
        self._pick_next_question()
        self.terminal_launch_result = open_terminal(self.session_dir)
        self._save_state()

    def status_text(self) -> str:
        current = self.current_question
        question_name = current.name if current else "-"
        question_points = current.points if current else 0
        time_left = format_seconds(self.timer.remaining_seconds())
        return "\n".join(
            [
                f"{self.ui.color('Tempo restante:', self.ui.CYAN)} {self.ui.color(time_left, self.ui.BOLD, self.ui.YELLOW)}",
                f"{self.ui.color('Questao atual:', self.ui.CYAN)} {self.ui.color(question_name, self.ui.BOLD)}",
                f"{self.ui.color('Questao vale:', self.ui.CYAN)} {question_points} pontos",
                f"{self.ui.color('Score:', self.ui.CYAN)} {self.score}/{self.total_possible_score}",
            ]
        )

    def subject_path(self) -> Path | None:
        if not self.current_question:
            return None
        return self.subjects_dir / f"{self.current_question.name}.txt"

    def print_header(self) -> None:
        print(self.ui.line())
        print(self.ui.color("  42 Exam Simulator iniciado", self.ui.BOLD, self.ui.GREEN))
        print(self.ui.line())
        print()
        print(self.ui.color("Mantenha este terminal aberto durante todo o exame.", self.ui.BOLD))
        print("Use outro terminal para editar seus arquivos dentro da pasta rendu/.")
        print(f"Quando terminar uma questao, volte aqui e digite: {self.ui.color('grademe', self.ui.BOLD, self.ui.GREEN)}")
        print()
        print(self.status_text())
        self._print_terminal_launch_result()
        print()
        print(f"Digite {self.ui.color('help', self.ui.BOLD)} para ver os comandos disponiveis.")

    def grade_current(self) -> GradeResult | None:
        if self.timer.expired():
            self._finish("Tempo esgotado.")
            return None
        if not self.current_question:
            self._finish("Nenhuma questao atual.")
            return None

        self.attempts += 1
        question_name = self.current_question.name
        print()
        result = self._run_with_spinner(
            "Rodando testes",
            lambda: self._grade_with_delay(self.current_question, self.attempts),
        )

        if result.passed:
            points = self.current_question.points if self.current_question else 0
            self.score = min(self.score + points, self.total_possible_score)
            print(self.ui.color(f"Aprovado: {question_name}", self.ui.BOLD, self.ui.GREEN))
            print(f"{self.ui.color('Trace:', self.ui.CYAN)} {result.trace_path}")
            self._pick_next_question(announce=True)
        else:
            print(self.ui.color(f"Recusado: {result.reason}", self.ui.BOLD, self.ui.RED))
            print(f"{self.ui.color('Trace:', self.ui.CYAN)} {result.trace_path}")
            visible_stdout = self._visible_test_stdout(result.stdout)
            if visible_stdout:
                print()
                print(visible_stdout)
            if self.mode == "knockout":
                self._finish("Mata-mata encerrado apos falha na questao.")

        self._save_state()
        return result

    def run_command_loop(self) -> None:
        self.print_header()
        while not self.finished:
            if self.timer.expired():
                self._finish("Tempo esgotado.")
                break

            try:
                command = self._read_command()
            except (EOFError, KeyboardInterrupt):
                print()
                self._finish("Simulado encerrado manualmente.")
                break

            if not command:
                continue
            if command == "grademe":
                self.grade_current()
            elif command == "status":
                print()
                print(self.status_text())
            elif command == "subject":
                path = self.subject_path()
                print(f"\n{path if path else 'Nenhum subject atual.'}")
            elif command == "terminal":
                print()
                self.terminal_launch_result = open_terminal(self.session_dir)
                self._print_terminal_launch_result()
            elif command == "help":
                print()
                self.print_help()
            elif command == "exit":
                self._finish("Simulado encerrado manualmente.")
            else:
                print(self.ui.color("Comando desconhecido. Digite help para ver as opcoes.", self.ui.YELLOW))

        self._save_state()
        print()
        print(self.ui.line())
        print(self.ui.color("  Exame finalizado", self.ui.BOLD, self.ui.MAGENTA))
        print(self.ui.line())
        print(self.finish_reason)
        print(f"{self.ui.color('Score final:', self.ui.CYAN)} {self.score}/{self.total_possible_score}")
        print(f"{self.ui.color('Sessao:', self.ui.CYAN)} {self.session_dir}")

    def print_help(self) -> None:
        print(self.ui.color("Comandos disponiveis:", self.ui.BOLD))
        print(f"  {self.ui.color('grademe', self.ui.GREEN)}  - corrige a questao atual")
        print(f"  {self.ui.color('status', self.ui.CYAN)}   - mostra tempo, questao, pontos e score")
        print(f"  {self.ui.color('subject', self.ui.CYAN)}  - mostra o caminho do subject atual")
        print(f"  {self.ui.color('terminal', self.ui.CYAN)} - abre outro terminal na raiz da sessao")
        print(f"  {self.ui.color('help', self.ui.CYAN)}     - mostra esta ajuda")
        print(f"  {self.ui.color('exit', self.ui.RED)}     - encerra o simulado manualmente")

    def _prompt_text(self, typed: str = "") -> str:
        question = self.current_question.name if self.current_question else "-"
        remaining = format_seconds(self.timer.remaining_seconds())
        left = self.ui.color(remaining, self.ui.BOLD, self.ui.YELLOW)
        current = self.ui.color(question, self.ui.BOLD, self.ui.GREEN)
        mode = self.ui.color(self.mode, self.ui.MAGENTA)
        prompt = self.ui.color("exam>", self.ui.BOLD, self.ui.CYAN)
        return f"[{left} | {current} | {mode}] {prompt} {typed}"

    def _read_command(self) -> str:
        if sys.stdin.isatty() and sys.stdout.isatty():
            return self._read_command_live()
        return input("\n" + self._prompt_text()).strip().lower()

    def _read_command_live(self) -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        typed: list[str] = []
        last_render = 0.0
        sys.stdout.write("\n" + self.ui.hide_cursor())
        sys.stdout.flush()
        try:
            tty.setcbreak(fd)
            while True:
                if self.timer.expired():
                    return ""
                now = time.time()
                if now - last_render >= 1.0:
                    self._render_prompt("".join(typed))
                    last_render = now

                ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                if not ready:
                    continue

                char = sys.stdin.read(1)
                if char in ("\n", "\r"):
                    command = "".join(typed).strip().lower()
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return command
                if char == "\x03":
                    raise KeyboardInterrupt
                if char == "\x04" and not typed:
                    raise EOFError
                if char in ("\x7f", "\b"):
                    if typed:
                        typed.pop()
                        self._render_prompt("".join(typed))
                        last_render = time.time()
                    continue
                if char in string.printable and char not in "\r\n\t\x0b\x0c":
                    typed.append(char)
                    self._render_prompt("".join(typed))
                    last_render = time.time()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            sys.stdout.write(self.ui.show_cursor())
            sys.stdout.flush()

    def _render_prompt(self, typed: str) -> None:
        sys.stdout.write("\r" + self.ui.clear_line() + self._prompt_text(typed))
        sys.stdout.flush()

    def _run_with_spinner(self, label: str, callback: Callable[[], T]) -> T:
        if not sys.stdout.isatty():
            print(f"{label}...")
            return callback()

        result: list[T] = []
        error: list[BaseException] = []

        def target() -> None:
            try:
                result.append(callback())
            except BaseException as exc:
                error.append(exc)

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        frames = "|/-\\"
        index = 0
        sys.stdout.write(self.ui.hide_cursor())
        try:
            while thread.is_alive():
                frame = self.ui.color(frames[index % len(frames)], self.ui.CYAN)
                sys.stdout.write("\r" + self.ui.clear_line() + f"{frame} {label}...")
                sys.stdout.flush()
                index += 1
                thread.join(0.1)
            sys.stdout.write("\r" + self.ui.clear_line())
            sys.stdout.flush()
        finally:
            sys.stdout.write(self.ui.show_cursor())
            sys.stdout.flush()

        if error:
            raise error[0]
        return result[0]

    def _grade_with_delay(self, question: Question, attempt_number: int) -> GradeResult:
        time.sleep(VALIDATION_DELAY_SECONDS)
        return self.grader.grade(question, attempt_number)

    def _visible_test_stdout(self, stdout: str) -> str:
        lines = [line for line in stdout.splitlines() if not line.startswith("TRACE_CASE\t")]
        return "\n".join(line for line in lines if line.strip()).strip()

    def _pick_next_question(self, announce: bool = False) -> None:
        if self.score >= self.total_possible_score:
            self.current_question = None
            self._finish("Pontuacao maxima atingida.")
            return

        question = self.loader.pick_random(self.questions, self.used_questions)
        if question is None:
            self._finish("Nao ha mais questoes disponiveis.")
            return

        self.current_question = question
        self.used_questions.add(question.name)
        self.current_index += 1
        self._copy_subject(question)
        if announce:
            print()
            print(self.status_text())

    def _print_terminal_launch_result(self) -> None:
        result = self.terminal_launch_result
        if result is None:
            return
        print()
        if result.opened:
            print(self.ui.color(result.message, self.ui.BOLD, self.ui.GREEN))
            return
        print(self.ui.color(f"Nao consegui abrir outro terminal automaticamente: {result.message}", self.ui.YELLOW))
        print(f"Abra manualmente outro terminal e rode: cd {self.session_dir}")

    def _copy_subject(self, question: Question) -> None:
        current_path = self.subjects_dir / f"{question.name}.txt"
        shutil.copyfile(question.subject_path, current_path)

    def _finish(self, reason: str) -> None:
        self.finished = True
        self.finish_reason = reason

    def _save_state(self) -> None:
        current = self.current_question
        save_json(
            self.state_path,
            {
                "login": self.login,
                "exam": self.exam,
                "mode": self.mode,
                "session_dir": str(self.session_dir),
                "started_at": self.timer.started_at,
                "duration_seconds": self.timer.duration_seconds,
                "remaining_seconds": self.timer.remaining_seconds(),
                "current_question": current.name if current else None,
                "current_index": self.current_index,
                "total_questions_target": self.total_questions_target,
                "max_score": self.total_possible_score,
                "used_questions": sorted(self.used_questions),
                "score": self.score,
                "attempts": self.attempts,
                "finished": self.finished,
                "finish_reason": self.finish_reason,
                "updated_at": time.time(),
            },
        )
