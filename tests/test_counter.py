import unittest

from spectator.counter import Counter, MonotonicCounter
from spectator.id import MeterId
from spectator.sidecarwriter import MemoryWriter


class CounterTest(unittest.TestCase):
    tid = MeterId("test")

    def test_increment(self):
        c = Counter(self.tid, writer=MemoryWriter())
        self.assertTrue(c._writer.is_empty())

        c.increment()
        self.assertEqual("c:test:1", c._writer.last_line())

    def test_increment_negative(self):
        c = Counter(self.tid, writer=MemoryWriter())
        c.increment(-1)
        self.assertTrue(c._writer.is_empty())

    def test_count(self):
        """Avoid breaking the API."""
        c = Counter(self.tid, writer=MemoryWriter())
        c.increment()
        self.assertEqual(0, c.count())


class MonotonicCounterTest(unittest.TestCase):
    tid = MeterId("test")

    def test_set(self):
        c = MonotonicCounter(self.tid, writer=MemoryWriter())
        self.assertTrue(c._writer.is_empty())

        c.set(1)
        self.assertEqual("C:test:1", c._writer.last_line())

    def test_set_negative(self):
        c = MonotonicCounter(self.tid, writer=MemoryWriter())
        self.assertTrue(c._writer.is_empty())

        c.set(-1)
        self.assertEqual("C:test:-1", c._writer.last_line())
