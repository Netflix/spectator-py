from spectator.id import MeterId
from spectator.counter import Counter
import unittest


class CounterTest(unittest.TestCase):

    tid = MeterId("test")

    def test_increment(self):
        c = Counter(CounterTest.tid)
        self.assertEqual(c.count(), 0)
        c.increment()
        self.assertEqual(c.count(), 1)

    def test_increment_negative(self):
        c = Counter(CounterTest.tid)
        c.increment(-1)
        self.assertEqual(c.count(), 0)

    def test_measure(self):
        c = Counter(CounterTest.tid)
        c.increment()
        ms = c._measure()
        self.assertEqual(len(ms), 1)
        self.assertEqual(ms[CounterTest.tid.with_stat('count')], 1)
        self.assertEquals(c.count(), 0)
