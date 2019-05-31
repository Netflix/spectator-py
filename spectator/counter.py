from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from spectator.atomicnumber import AtomicNumber


class AbstractCounter(with_metaclass(ABCMeta)):

    @abstractmethod
    def increment(self, amount=1):
        pass

    @abstractmethod
    def count(self):
        pass

    @abstractmethod
    def _measure(self):
        pass


class NoopCounter(AbstractCounter):

    def increment(self, amount=1):
        pass

    def count(self):
        return 0

    def _measure(self):
        return {}


class Counter(AbstractCounter):

    def __init__(self, meterId):
        self.meterId = meterId
        self._count = AtomicNumber(0)

    def increment(self, amount=1):
        if amount > 0:
            self._count.add_and_get(amount)

    def count(self):
        return self._count.get()

    def _measure(self):
        return {
            self.meterId.with_stat('count'): self._count.get_and_set(0)
        }
