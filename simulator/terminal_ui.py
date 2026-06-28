from __future__ import annotations

import os
import sys


class TerminalUI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    CLEAR_LINE = "\033[2K"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"

    def __init__(self) -> None:
        self.enabled = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

    def color(self, text: str, *styles: str) -> str:
        if not self.enabled:
            return text
        return "".join(styles) + text + self.RESET

    def line(self) -> str:
        return self.color("=" * 52, self.DIM)

    def clear_line(self) -> str:
        return self.CLEAR_LINE if self.enabled else ""

    def hide_cursor(self) -> str:
        return self.HIDE_CURSOR if self.enabled else ""

    def show_cursor(self) -> str:
        return self.SHOW_CURSOR if self.enabled else ""
