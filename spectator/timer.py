from spectator.clock import Clock, SystemClock
from spectator.id import MeterId
from spectator.sidecarmeter import SidecarMeter
from spectator.sidecarwriter import SidecarWriter


class Timer(SidecarMeter):
    """The value is the number of seconds that have elapsed for an event. A stopwatch method
    is available, which provides a context manager that can be used to automate recording the
    timing for a block of code using the `with` statement.

    Two types are available: (1) standard timers, with a meter type of "t", and (2) percentile
    timers, with a meter type of "T". The standard timers are the default.

    In order to maintain the data distribution, Percentile Timers have a higher storage cost,
    with a worst-case of up to 300X that of a standard Timer. Be diligent about any additional
    dimensions added to Percentile Timers and ensure that they have a small bounded cardinality."""

    def __init__(self, meter_id: MeterId, clock: Clock = SystemClock(), meter_type: str = "t",
                 writer: SidecarWriter = SidecarWriter.create("none")) -> None:
        if meter_type not in ["t", "T"]:
            raise ValueError("Timers must have a meter type of 't' or 'T'.")

        super().__init__(meter_id, meter_type)
        self._clock = clock
        self._writer = writer

    def record(self, seconds: float) -> None:
        if seconds >= 0:
            self._writer.write(self.idString, seconds)

    def stopwatch(self) -> "StopWatch":
        return StopWatch(self)

    def clock(self) -> Clock:
        return self._clock

    @staticmethod
    def count() -> int:
        """Avoid breaking the API."""
        return 0

    @staticmethod
    def total_time() -> float:
        """Avoid breaking the API."""
        return 0


class StopWatch:
    """Context Manager that records the duration of a with-statement block in a Timer or
    PercentileTimer. The type annotation for the init parameter is skipped to avoid circular
    imports."""

    def __init__(self, timer) -> None:
        self._timer = timer

    def __enter__(self) -> None:
        self._start = self._timer.clock().monotonic_time()

    def __exit__(self, type_, value, traceback) -> None:
        self._timer.record(self.duration())

    def duration(self) -> float:
        now = self._timer.clock().monotonic_time()
        return now - self._start
