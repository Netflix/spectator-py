from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from spectator.atomicnumber import AtomicNumber
from spectator.clock import SystemClock


class AbstractGauge(with_metaclass(ABCMeta)):

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self, value):
        pass

    @abstractmethod
    def _measure(self):
        pass


class NoopGauge(AbstractGauge):

    def get(self):
        return 0

    def set(self, value):
        pass

    def _measure(self):
        return {}


class Gauge(AbstractGauge):
    ttl = 15 * 60

    def __init__(self, meterId, clock=SystemClock()):
        self.meterId = meterId
        self._clock = clock
        self._last_update = AtomicNumber(float('nan'))
        self._value = AtomicNumber(float('nan'))

    def get(self):
        return self._value.get()

    def set(self, value):
        self._last_update.set(self._clock.wall_time())
        self._value.set(value)

    def _has_expired(self):
        return (self._clock.wall_time() - self._last_update.get()) > self.ttl

    def _measure(self):
        id = self.meterId.with_stat('gauge')

        if self._has_expired():
            v = self._value.get_and_set(float('nan'))
        else:
            v = self._value.get()

        return {id: v}
