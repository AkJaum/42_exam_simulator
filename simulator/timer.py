from __future__ import annotations

import time


class CountdownTimer:
    def __init__(self, duration_seconds: int, started_at: float | None = None) -> None:
        self.duration_seconds = duration_seconds
        self.started_at = started_at if started_at is not None else time.time()

    def remaining_seconds(self) -> int:
        elapsed = time.time() - self.started_at
        return max(0, int(self.duration_seconds - elapsed))

    def expired(self) -> bool:
        return self.remaining_seconds() <= 0
