import unittest

from spectator.meter.counter import Counter
from spectator.meter.id import Id
from spectator.writer.memory_writer import MemoryWriter


class CounterTest(unittest.TestCase):
    tid = Id("counter")

    def test_increment(self):
        c = Counter(self.tid, MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.increment()
        self.assertEqual("c:counter:1", c.writer().last_line())

        c.increment(2)
        self.assertEqual("c:counter:2", c.writer().last_line())

    def test_increment_negative(self):
        c = Counter(self.tid, MemoryWriter())
        c.increment(-1)
        self.assertTrue(c.writer().is_empty())
