import time


class Clock:

    def wall_time(self) -> float:
        raise NotImplementedError("use a concrete implementation")

    def monotonic_time(self) -> float:
        raise NotImplementedError("use a concrete implementation")


class SystemClock(Clock):

    def wall_time(self) -> float:
        return time.time()

    def monotonic_time(self) -> float:
        """The time.perf_counter() function was added in Python 3.3. We expect Python >= 3.5."""
        return time.perf_counter()


class ManualClock(Clock):

    def __init__(self, wall_init: float = 0, monotonic_init: float = 0) -> None:
        self._wall = wall_init
        self._monotonic = monotonic_init

    def wall_time(self) -> float:
        return self._wall

    def monotonic_time(self) -> float:
        return self._monotonic

    def set_wall_time(self, t: float) -> None:
        self._wall = t

    def set_monotonic_time(self, t: float) -> None:
        self._monotonic = t
