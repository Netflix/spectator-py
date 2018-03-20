from spectator.atomicnumber import AtomicNumber


class DistributionSummary:

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
