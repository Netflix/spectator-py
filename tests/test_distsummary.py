import unittest

from spectator.distsummary import DistributionSummary
from spectator.id import MeterId
from spectator.sidecarwriter import MemoryWriter


class DistributionSummaryTest(unittest.TestCase):
    tid = MeterId("test")

    def test_invalid_meter_type(self):
        with self.assertRaises(ValueError):
            DistributionSummary(self.tid, meter_type='x')

    def test_record(self):
        d = DistributionSummary(self.tid, writer=MemoryWriter())
        self.assertTrue(d.writer().is_empty())

        d.record(42)
        self.assertEqual("d:test:42", d.writer().last_line())

    def test_record_negative(self):
        d = DistributionSummary(self.tid, writer=MemoryWriter())
        d.record(-42)
        self.assertTrue(d.writer().is_empty())

    def test_record_zero(self):
        d = DistributionSummary(self.tid, writer=MemoryWriter())
        d.record(0)
        self.assertEqual("d:test:0", d.writer().last_line())

    def test_count_and_total_amount(self):
        """Avoid breaking the API."""
        d = DistributionSummary(self.tid, writer=MemoryWriter())
        self.assertTrue(d.writer().is_empty())

        d.record(42)
        self.assertEqual(0, d.count())
        self.assertEqual(0, d.total_amount())


class PercentileDistributionSummaryTest(unittest.TestCase):
    tid = MeterId("test")

    def test_invalid_meter_type(self):
        with self.assertRaises(ValueError):
            DistributionSummary(self.tid, meter_type="x")

    def test_record(self):
        d = DistributionSummary(self.tid, meter_type="D", writer=MemoryWriter())
        self.assertTrue(d.writer().is_empty())

        d.record(42)
        self.assertEqual("D:test:42", d.writer().last_line())

    def test_record_negative(self):
        d = DistributionSummary(self.tid, meter_type="D", writer=MemoryWriter())
        d.record(-42)
        self.assertTrue(d.writer().is_empty())

    def test_record_zero(self):
        d = DistributionSummary(self.tid, meter_type="D", writer=MemoryWriter())
        d.record(0)
        self.assertEqual("D:test:0", d.writer().last_line())
