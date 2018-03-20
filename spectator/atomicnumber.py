import threading


class AtomicNumber:

    def __init__(self, init):
        self._value = init
        self._lock = threading.RLock()

    def set(self, v):
        with self._lock:
            self._value = v

    def get(self):
        with self._lock:
            return self._value

    def get_and_set(self, v):
        with self._lock:
            tmp = self._value
            self._value = v
            return tmp

    def get_and_increment(self):
        return self.get_and_add(1)

    def increment_and_get(self):
        return self.add_and_get(1)

    def get_and_add(self, amount):
        with self._lock:
            tmp = self._value
            self._value += amount
            return tmp

    def add_and_get(self, amount):
        with self._lock:
            self._value += amount
            return self._value

    def max(self, amount):
        with self._lock:
            self._value = max(self._value, amount)
            return self._value

    def __str__(self):
        with self._lock:
            return "AtomicLong({})".format(self._value)
