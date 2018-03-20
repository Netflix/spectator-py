from spectator.id import MeterId
from spectator.timer import Timer
import unittest


class TimerTest(unittest.TestCase):

    tid = MeterId("test")

    def test_record(self):
        t = Timer(TimerTest.tid)
        t.record(42)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_time(), 42)

    def test_record_negative(self):
        t = Timer(TimerTest.tid)
        t.record(-42)
        self.assertEqual(t.count(), 0)
        self.assertEqual(t.total_time(), 0)

    def test_record_zero(self):
        t = Timer(TimerTest.tid)
        t.record(0)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_time(), 0)

    def test_record_multiple(self):
        t = Timer(TimerTest.tid)
        t.record(42)
        t.record(2)
        t.record(7)
        self.assertEqual(t.count(), 3)
        self.assertEqual(t.total_time(), 51)

    def test_measure(self):
        t = Timer(TimerTest.tid)
        t.record(42)
        t.record(2)
        t.record(7)
        ms = t._measure()

        def get_stat(s):
            return ms[TimerTest.tid.with_stat(s)]

        self.assertEqual(len(ms), 4)
        self.assertEqual(get_stat('count'), 3)
        self.assertEqual(get_stat('totalTime'), 51)
        self.assertEqual(get_stat('max'), 42)
        self.assertEqual(get_stat('totalOfSquares'), 42**2 + 2**2 + 7**2)

        self.assertEqual(t.count(), 0)
        self.assertEqual(t.total_time(), 0)
