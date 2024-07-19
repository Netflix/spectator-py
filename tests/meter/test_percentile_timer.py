import unittest

from spectator.meter.meter_id import MeterId
from spectator.meter.percentile_timer import PercentileTimer
from spectator.writer.memory_writer import MemoryWriter


class PercentileTimerTest(unittest.TestCase):
    tid = MeterId("percentile_timer")

    def test_record(self):
        t = PercentileTimer(self.tid, MemoryWriter())
        self.assertTrue(t.writer().is_empty())

        t.record(42)
        self.assertEqual("T:percentile_timer:42", t.writer().last_line())

    def test_record_negative(self):
        t = PercentileTimer(self.tid, MemoryWriter())
        t.record(-42)
        self.assertTrue(t.writer().is_empty())

    def test_record_zero(self):
        t = PercentileTimer(self.tid, MemoryWriter())
        t.record(0)
        self.assertEqual("T:percentile_timer:0", t.writer().last_line())
