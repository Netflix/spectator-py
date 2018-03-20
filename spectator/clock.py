import time


class Clock:

    def wall_time(self):
        raise NotImplementedError("use a concrete implementation")

    def monotonic_time(self):
        raise NotImplementedError("use a concrete implementation")


class SystemClock(Clock):

    def __init__(self):
        try:
            # perf_counter was added in 3.3, use the higher resolution timer
            # if available, otherwise fallback to the `time.time()`
            time.perf_counter()
            self._monotonic_timer = lambda: time.perf_counter()
        except AttributeError:
            self._monotonic_timer = lambda: time.time()

    def wall_time(self):
        return time.time()

    def monotonic_time(self):
        return self._monotonic_timer()


class ManualClock(Clock):

    def __init__(self, wallInit=0, monotonicInit=0):
        self._wall = wallInit
        self._monotonic = monotonicInit

    def wall_time(self):
        return self._wall

    def monotonic_time(self):
        return self._monotonic

    def set_wall_time(self, t):
        self._wall = t

    def set_monotonic_time(self, t):
        self._monotonic = t
