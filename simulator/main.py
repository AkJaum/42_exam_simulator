from __future__ import annotations

import argparse
from pathlib import Path

from simulator.exam_session import ExamSession


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="42 terminal exam simulator")
    parser.add_argument("--root", required=True, help="Project root directory")
    parser.add_argument("--login", required=True, help="Student login")
    parser.add_argument("--exam", required=True, help="Exam directory name")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["real", "knockout"],
        help="Simulation mode",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session = ExamSession(
        root=Path(args.root).resolve(),
        login=args.login,
        exam=args.exam,
        mode=args.mode,
    )
    session.start()
    session.run_command_loop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
