import threading


class AtomicNumber:

    def __init__(self, init: float) -> None:
        self._value = init
        self._lock = threading.RLock()

    def set(self, v: float) -> None:
        with self._lock:
            self._value = v

    def get(self) -> float:
        with self._lock:
            return self._value

    def get_and_set(self, v: float) -> float:
        with self._lock:
            tmp = self._value
            self._value = v
            return tmp

    def get_and_increment(self) -> float:
        return self.get_and_add(1)

    def increment_and_get(self) -> float:
        return self.add_and_get(1)

    def get_and_add(self, amount: float) -> float:
        with self._lock:
            tmp = self._value
            self._value += amount
            return tmp

    def add_and_get(self, amount: float) -> float:
        with self._lock:
            self._value += amount
            return self._value

    def max(self, amount: float) -> float:
        with self._lock:
            self._value = max(self._value, amount)
            return self._value

    def __str__(self) -> str:
        with self._lock:
            return "AtomicLong({})".format(self._value)
