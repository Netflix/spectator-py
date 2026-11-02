from spectator.clock import Clock, SystemClock
from spectator.meter.percentile_timer import PercentileTimer
from spectator.meter.timer import Timer


class StopWatch:
    """Context Manager that records the duration of a with-statement block in a Timer or
    PercentileTimer. It uses a custom Clock implementation to assist with unit testing."""

    def __init__(
        self, timer: PercentileTimer | Timer, clock: Clock | None = None
    ) -> None:
        self._clock = clock if clock is not None else SystemClock()
        self._timer = timer

    def __enter__(self) -> None:
        self._start = self._clock.monotonic_time()

    def __exit__(self, type_, value, traceback) -> None:
        self._timer.record(self.duration())

    def duration(self) -> float:
        return self._clock.monotonic_time() - self._start
