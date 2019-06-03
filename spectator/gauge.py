from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from spectator.atomicnumber import AtomicNumber


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

    def __init__(self, meterId):
        self.meterId = meterId
        self._value = AtomicNumber(float('nan'))

    def get(self):
        return self._value.get()

    def set(self, value):
        self._value.set(value)

    def _measure(self):
        id = self.meterId.with_stat('gauge')
        v = self._value.get_and_set(float('nan'))
        return {id: v}
