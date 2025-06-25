import unittest

from spectator import DistributionSummary, MemoryWriter, MeterId, NoopWriter


class DistributionSummaryTest(unittest.TestCase):
    tid = MeterId("dist_summary")

    def test_noop_writer(self):
        d = DistributionSummary(self.tid)
        self.assertTrue(isinstance(d.writer(), NoopWriter))

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
