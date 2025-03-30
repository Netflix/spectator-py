import unittest

from spectator import Counter, MemoryWriter, MeterId


class CounterTest(unittest.TestCase):
    tid = MeterId("counter")

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
