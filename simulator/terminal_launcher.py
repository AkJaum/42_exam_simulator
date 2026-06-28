from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TerminalLaunchResult:
    opened: bool
    message: str
    command: list[str] | None = None


def open_terminal(cwd: Path) -> TerminalLaunchResult:
    if os.environ.get("EXAM_SIM_NO_TERMINAL") == "1":
        return TerminalLaunchResult(False, "Abertura automatica desativada por EXAM_SIM_NO_TERMINAL=1.")

    if not sys.stdin.isatty():
        return TerminalLaunchResult(False, "Entrada nao interativa detectada.")

    multiplexer_result = _try_terminal_multiplexer(cwd)
    if multiplexer_result is not None:
        return multiplexer_result

    if not _has_graphical_session():
        return TerminalLaunchResult(False, "Sessao grafica, tmux ou screen nao detectados.")

    cwd = cwd.resolve()
    candidates = _terminal_candidates(cwd)
    tried: list[str] = []

    for command in candidates:
        if not command:
            continue
        executable = command[0]
        if shutil.which(executable) is None:
            tried.append(executable)
            continue
        try:
            subprocess.Popen(
                command,
                cwd=str(cwd),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            return TerminalLaunchResult(True, f"Terminal aberto em {cwd}.", command)
        except OSError:
            tried.append(executable)

    tried_text = ", ".join(dict.fromkeys(tried)) or "nenhum"
    return TerminalLaunchResult(False, f"Nenhum terminal compativel encontrado. Tentativas: {tried_text}.")


def _has_graphical_session() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def _try_terminal_multiplexer(cwd: Path) -> TerminalLaunchResult | None:
    if os.environ.get("TMUX") and shutil.which("tmux"):
        command = ["tmux", "new-window", "-c", str(cwd), "-n", "exam-session"]
        try:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            return TerminalLaunchResult(True, f"Nova janela tmux aberta em {cwd}.", command)
        except OSError:
            return TerminalLaunchResult(False, "Falha ao abrir nova janela tmux.", command)

    if os.environ.get("STY") and shutil.which("screen"):
        shell = os.environ.get("SHELL") or "bash"
        cd_command = f"cd {shlex.quote(str(cwd))}; exec {shlex.quote(shell)}"
        command = ["screen", "-X", "screen", "-t", "exam-session", "sh", "-lc", cd_command]
        try:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            return TerminalLaunchResult(True, f"Nova janela screen aberta em {cwd}.", command)
        except OSError:
            return TerminalLaunchResult(False, "Falha ao abrir nova janela screen.", command)

    return None


def _terminal_candidates(cwd: Path) -> list[list[str]]:
    shell = os.environ.get("SHELL") or "bash"
    cd_command = f"cd {shlex.quote(str(cwd))}; exec {shlex.quote(shell)}"
    user_terminal = _user_terminal_candidate(cwd)
    candidates: list[list[str]] = []
    if user_terminal:
        candidates.append(user_terminal)

    candidates.extend(
        [
            ["xdg-terminal-exec", "sh", "-lc", cd_command],
            ["x-terminal-emulator", "-e", "sh", "-lc", cd_command],
            ["gnome-terminal", f"--working-directory={cwd}"],
            ["kgx", "--working-directory", str(cwd)],
            ["konsole", "--workdir", str(cwd)],
            ["xfce4-terminal", f"--working-directory={cwd}"],
            ["mate-terminal", f"--working-directory={cwd}"],
            ["tilix", f"--working-directory={cwd}"],
            ["terminator", f"--working-directory={cwd}"],
            ["qterminal", "--workdir", str(cwd)],
            ["lxterminal", f"--working-directory={cwd}"],
            ["kitty", "--directory", str(cwd)],
            ["alacritty", "--working-directory", str(cwd)],
            ["wezterm", "start", "--cwd", str(cwd)],
            ["foot", f"--working-directory={cwd}"],
            ["deepin-terminal", "--work-directory", str(cwd)],
            ["xterm", "-e", "sh", "-lc", cd_command],
            ["urxvt", "-e", "sh", "-lc", cd_command],
            ["rxvt", "-e", "sh", "-lc", cd_command],
        ]
    )
    return candidates


def _user_terminal_candidate(cwd: Path) -> list[str] | None:
    terminal = os.environ.get("EXAM_SIM_TERMINAL") or os.environ.get("TERMINAL")
    if not terminal:
        return None

    parts = shlex.split(terminal)
    if not parts:
        return None

    if len(parts) == 1:
        return parts

    rendered = [part.replace("{cwd}", str(cwd)) for part in parts]
    if rendered != parts:
        return rendered
    return parts
