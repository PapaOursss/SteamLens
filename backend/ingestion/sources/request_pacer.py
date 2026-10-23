import time
from collections.abc import Callable


class RequestPacer:
    """Attend ce qu'il faut entre deux appels pour respecter un débit maximal."""

    def __init__(
        self,
        min_interval_seconds: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._min_interval_seconds = min_interval_seconds
        self._clock = clock
        self._sleep = sleep
        self._last_call_at: float | None = None

    def wait(self) -> None:
        now = self._clock()
        if self._last_call_at is not None:
            remaining = self._min_interval_seconds - (now - self._last_call_at)
            if remaining > 0:
                self._sleep(remaining)
                now += remaining
        self._last_call_at = now
