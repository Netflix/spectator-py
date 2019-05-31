from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from spectator.atomicnumber import AtomicNumber
from spectator.clock import SystemClock


class AbstractTimer(with_metaclass(ABCMeta)):

    @abstractmethod
    def record(self, amount):
        pass

    @abstractmethod
    def stopwatch(self):
        pass

    @abstractmethod
    def count(self):
        pass

    @abstractmethod
    def total_time(self):
        pass

    @abstractmethod
    def _measure(self):
        pass


class NoopTimer(AbstractTimer):

    def record(self, amount):
        pass

    def stopwatch(self):
        return StopWatch(self)

    def count(self):
        return 0

    def total_time(self):
        return 0

    def _measure(self):
        return {}


class Timer(AbstractTimer):

    def __init__(self, meterId, clock=SystemClock()):
        self.meterId = meterId
        self._clock = clock
        self._count = AtomicNumber(0)
        self._totalTime = AtomicNumber(0)
        self._totalOfSquares = AtomicNumber(0)
        self._max = AtomicNumber(0)

    def record(self, amount):
        if amount >= 0:
            self._count.increment_and_get()
            self._totalTime.add_and_get(amount)
            self._totalOfSquares.add_and_get(amount * amount)
            self._max.max(amount)

    def stopwatch(self):
        return StopWatch(self)

    def count(self):
        return self._count.get()

    def total_time(self):
        return self._totalTime.get()

    def _measure(self):
        ms = {}
        for stat in ['count', 'totalTime', 'totalOfSquares', 'max']:
            v = getattr(self, "_{}".format(stat)).get_and_set(0)
            ms[self.meterId.with_stat(stat)] = v
        return ms


class StopWatch:

    def __init__(self, timer):
        self._timer = timer

    def __enter__(self):
        self._start = self._timer._clock.monotonic_time()

    def __exit__(self, typ, value, traceback):
        self._timer.record(self.duration())

    def duration(self):
        now = self._timer._clock.monotonic_time()
        return now - self._start
