import unittest

from spectator import ManualClock
from spectator.id import MeterId
from spectator.timer import Timer
from spectator.sidecarwriter import MemoryWriter


class TimerTest(unittest.TestCase):
    tid = MeterId("test")

    def test_invalid_meter_type(self):
        with self.assertRaises(ValueError):
            Timer(self.tid, meter_type='x')

    def test_record(self):
        t = Timer(self.tid, writer=MemoryWriter())
        self.assertTrue(t.writer().is_empty())

        t.record(42)
        self.assertEqual("t:test:42", t.writer().last_line())

    def test_record_negative(self):
        t = Timer(self.tid, writer=MemoryWriter())
        t.record(-42)
        self.assertTrue(t.writer().is_empty())

    def test_record_zero(self):
        t = Timer(self.tid, writer=MemoryWriter())
        t.record(0)
        self.assertEqual("t:test:0", t.writer().last_line())

    def test_stopwatch(self):
        clock = ManualClock()
        t = Timer(self.tid, clock=clock, writer=MemoryWriter())
        with t.stopwatch():
            clock.set_monotonic_time(42)
        self.assertEqual("t:test:42", t.writer().last_line())

    def test_count_and_total_time(self):
        """Avoid breaking the API."""
        t = Timer(self.tid, writer=MemoryWriter())
        self.assertTrue(t.writer().is_empty())

        t.record(42)
        self.assertEqual(0, t.count())
        self.assertEqual(0, t.total_time())


class PercentileTimerTest(unittest.TestCase):
    tid = MeterId("test")

    def test_invalid_meter_type(self):
        with self.assertRaises(ValueError):
            Timer(self.tid, meter_type='x')

    def test_record(self):
        t = Timer(self.tid, meter_type="T", writer=MemoryWriter())
        self.assertTrue(t.writer().is_empty())

        t.record(42)
        self.assertEqual("T:test:42", t.writer().last_line())

    def test_record_negative(self):
        t = Timer(self.tid, meter_type="T", writer=MemoryWriter())
        t.record(-42)
        self.assertTrue(t.writer().is_empty())

    def test_record_zero(self):
        t = Timer(self.tid, meter_type="T", writer=MemoryWriter())
        t.record(0)
        self.assertEqual("T:test:0", t.writer().last_line())

    def test_stopwatch(self):
        clock = ManualClock()
        t = Timer(self.tid, clock=clock, meter_type="T", writer=MemoryWriter())
        with t.stopwatch():
            clock.set_monotonic_time(42)
        self.assertEqual("T:test:42", t.writer().last_line())
