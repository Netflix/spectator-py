from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from spectator.atomicnumber import AtomicNumber


class AbstractDistributionSummary(with_metaclass(ABCMeta)):

    @abstractmethod
    def record(self, amount):
        pass

    @abstractmethod
    def count(self):
        pass

    @abstractmethod
    def total_amount(self):
        pass

    @abstractmethod
    def _measure(self):
        pass


class NoopDistributionSummary(AbstractDistributionSummary):

    def record(self, amount):
        pass

    def count(self):
        return 0

    def total_amount(self):
        return 0

    def _measure(self):
        return {}


class DistributionSummary(AbstractDistributionSummary):

    def __init__(self, meterId):
        self.meterId = meterId
        self._count = AtomicNumber(0)
        self._totalAmount = AtomicNumber(0)
        self._totalOfSquares = AtomicNumber(0)
        self._max = AtomicNumber(0)

    def record(self, amount):
        if amount >= 0:
            self._count.increment_and_get()
            self._totalAmount.add_and_get(amount)
            self._totalOfSquares.add_and_get(amount * amount)
            self._max.max(amount)

    def count(self):
        return self._count.get()

    def total_amount(self):
        return self._totalAmount.get()

    def _measure(self):
        ms = {}
        for stat in ['count', 'totalAmount', 'totalOfSquares', 'max']:
            v = getattr(self, "_{}".format(stat)).get_and_set(0)
            ms[self.meterId.with_stat(stat)] = v
        return ms
