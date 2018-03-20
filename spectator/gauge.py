from spectator.atomicnumber import AtomicNumber


class Gauge:

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
