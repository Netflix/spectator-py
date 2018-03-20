from spectator.atomicnumber import AtomicNumber


class Counter:

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
