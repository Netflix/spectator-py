from spectator.id import MeterId
from spectator.distsummary import DistributionSummary
import unittest


class DistributionSummaryTest(unittest.TestCase):

    tid = MeterId("test")

    def test_record(self):
        t = DistributionSummary(DistributionSummaryTest.tid)
        t.record(42)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_amount(), 42)

    def test_record_negative(self):
        t = DistributionSummary(DistributionSummaryTest.tid)
        t.record(-42)
        self.assertEqual(t.count(), 0)
        self.assertEqual(t.total_amount(), 0)

    def test_record_zero(self):
        t = DistributionSummary(DistributionSummaryTest.tid)
        t.record(0)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_amount(), 0)

    def test_record_multiple(self):
        t = DistributionSummary(DistributionSummaryTest.tid)
        t.record(42)
        t.record(2)
        t.record(7)
        self.assertEqual(t.count(), 3)
        self.assertEqual(t.total_amount(), 51)

    def test_measure(self):
        t = DistributionSummary(DistributionSummaryTest.tid)
        t.record(42)
        t.record(2)
        t.record(7)
        ms = t._measure()

        def get_stat(s):
            return ms[DistributionSummaryTest.tid.with_stat(s)]

        self.assertEqual(len(ms), 4)
        self.assertEqual(get_stat('count'), 3)
        self.assertEqual(get_stat('totalAmount'), 51)
        self.assertEqual(get_stat('max'), 42)
        self.assertEqual(get_stat('totalOfSquares'), 42**2 + 2**2 + 7**2)

        self.assertEqual(t.count(), 0)
        self.assertEqual(t.total_amount(), 0)
