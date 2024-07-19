import abc
import time


class Clock(metaclass=abc.ABCMeta):
    def wall_time(self) -> float:
        raise NotImplementedError

    def monotonic_time(self) -> float:
        raise NotImplementedError


class SystemClock(Clock):
    def wall_time(self) -> float:
        return time.time()

    def monotonic_time(self) -> float:
        """Use `time.perf_counter()`, because it is a clock with the highest available resolution
        to measure a short duration. It does include time elapsed during sleep and is system-wide.

        See https://docs.python.org/3/library/time.html#time.perf_counter for more information."""
        return time.perf_counter()


class ManualClock(Clock):
    """Used to enable deterministic unit testing for the StopWatch class."""
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
