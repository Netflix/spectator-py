import unittest

from spectator.meter.dist_summary import DistributionSummary
from spectator.meter.id import Id
from spectator.writer.memory_writer import MemoryWriter


class DistributionSummaryTest(unittest.TestCase):
    tid = Id("dist_summary")

    def test_record(self):
        d = DistributionSummary(self.tid, MemoryWriter())
        self.assertTrue(d.writer().is_empty())

        d.record(42)
        self.assertEqual("d:dist_summary:42", d.writer().last_line())

    def test_record_negative(self):
        d = DistributionSummary(self.tid, MemoryWriter())
        d.record(-42)
        self.assertTrue(d.writer().is_empty())

    def test_record_zero(self):
        d = DistributionSummary(self.tid, MemoryWriter())
        d.record(0)
        self.assertEqual("d:dist_summary:0", d.writer().last_line())
