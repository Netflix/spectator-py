from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from spectator.atomicnumber import AtomicNumber
from spectator.clock import SystemClock
from spectator.gauge import Gauge
from threading import Timer


class AbstractAgeGauge(with_metaclass(ABCMeta)):

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def _measure(self):
        pass


class NoopAgeGauge(AbstractAgeGauge):

    def get(self):
        return 0

    def reset(self):
        pass

    def _measure(self):
        return {}


class AgeGauge(AbstractAgeGauge):
    def __init__(self, meterId, clock=SystemClock()):
        self._gauge = Gauge(meterId, clock)
        self._clock = SystemClock()
        self._last_reset = AtomicNumber(float('nan'))
        self.reset()
        self._t = Timer(60, self._update)
        self._t.daemon = True
        self._t.start()

    def __del__(self):
        self._t.cancel()

    def get(self):
        return self._gauge.get()

    def reset(self):
        self._gauge.set(0)
        self._last_reset.set(self._clock.wall_time())

    def _update(self):
        self._gauge.set(self._clock.wall_time() - self._last_reset.get())

    def _measure(self):
        id = self._gauge.meterId.with_default_stat('gauge')
        return {id: self._gauge.get()}
