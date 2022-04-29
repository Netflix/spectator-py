import unittest

from spectator import Registry, ManualClock
from spectator.histogram.percentiles import PercentileBuckets
from spectator.histogram.percentiles import PercentileDistributionSummary
from spectator.histogram.percentiles import PercentileTimer
from spectator.sidecarconfig import SidecarConfig


class PercentileBucketsTest(unittest.TestCase):
    """Avoid breaking the API."""

    def test_empty_api_methods(self):
        b = PercentileBuckets()
        self.assertEqual(0, b.get(1))
        self.assertEqual(0, b.length())
        self.assertEqual(0, b.index_of(1))
        self.assertEqual(0, b.bucket(1))
        self.assertEqual(None, b.percentiles(1, 1, 1))
        self.assertEqual(0, b.percentile(1, 1))


class PercentileTimerTest(unittest.TestCase):
    """Avoid breaking the API."""

    def test_record(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        t = PercentileTimer(r, "test")
        self.assertTrue(r.writer().is_empty())

        t.record(42)
        self.assertEqual("T:test:42", r.writer().last_line())

    def test_stopwatch(self):
        clock = ManualClock()
        r = Registry(clock=clock, config=SidecarConfig({"sidecar.output-location": "memory"}))

        t = PercentileTimer(r, "test")
        with t.stopwatch():
            clock.set_monotonic_time(42)
        self.assertEqual("T:test:42", r.writer().last_line())

    def test_empty_api_methods(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))
        t = PercentileTimer(r, "test")
        self.assertEqual(0, t.count())
        self.assertEqual(0, t.total_time())
        self.assertEqual(0, t.percentile(1))


class PercentileDistributionSummaryTest(unittest.TestCase):
    """Avoid breaking the API."""

    def test_record(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        t = PercentileDistributionSummary(r, "test")
        self.assertTrue(r.writer().is_empty())

        t.record(42)
        self.assertEqual("D:test:42", r.writer().last_line())

    def test_empty_api_methods(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))
        t = PercentileDistributionSummary(r, "test")
        self.assertEqual(0, t.count())
        self.assertEqual(0, t.total_amount())
        self.assertEqual(0, t.percentile(1))
