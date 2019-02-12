from spectator import Registry
from spectator import ManualClock
from spectator.histogram import PercentileBuckets
from spectator.histogram import PercentileDistributionSummary
from spectator.histogram import PercentileTimer
import random
import unittest


class PercentileBucketsTest(unittest.TestCase):

    _max_value = 9223372036854775807

    def test_index_of(self):
        self.assertEqual(0, PercentileBuckets.index_of(-1))
        self.assertEqual(0, PercentileBuckets.index_of(0))
        self.assertEqual(1, PercentileBuckets.index_of(1))
        self.assertEqual(2, PercentileBuckets.index_of(2))
        self.assertEqual(3, PercentileBuckets.index_of(3))
        self.assertEqual(4, PercentileBuckets.index_of(4))

        self.assertEqual(25, PercentileBuckets.index_of(87))

        self.assertEqual(
            PercentileBuckets.length() - 1,
            PercentileBuckets.index_of(self._max_value))

    def test_index_of_sanity_check(self):
        random.seed(42)
        for i in range(10000):
            v = random.randint(-self._max_value, self._max_value)
            if v < 0:
                self.assertEqual(0, PercentileBuckets.index_of(v))
            else:
                b = PercentileBuckets.get(PercentileBuckets.index_of(v))
                self.assertTrue(v <= b)

    def test_bucket_sanity_check(self):
        random.seed(42)
        for i in range(10000):
            v = random.randint(-self._max_value, self._max_value)
            if v < 0:
                self.assertEqual(1, PercentileBuckets.bucket(v))
            else:
                b = PercentileBuckets.bucket(v)
                self.assertTrue(v <= b)

    def __assert_equals(self, vs1, vs2, threshold):
        self.assertEqual(len(vs1), len(vs2))
        for i in range(len(vs1)):
            v1 = vs1[i]
            v2 = vs2[i]
            self.assertAlmostEqual(v1, v2, delta=threshold)

    def test_percentiles(self):
        counts = [0] * PercentileBuckets.length()
        for i in range(100000):
            counts[PercentileBuckets.index_of(i)] += 1

        pcts = [0.0, 25.0, 50.0, 75.0, 90.0, 95.0, 98.0, 99.0, 99.5, 100.0]
        results = [0.0] * len(pcts)

        PercentileBuckets.percentiles(counts, pcts, results)

        expected = [
            0.0, 25e3, 50e3, 75e3, 90e3, 95e3, 98e3, 99e3, 99.5e3, 100e3
        ]
        threshold = 0.1 * 100000  # quick check, should be within 10% of total
        self.__assert_equals(expected, results, threshold)

        # Further check each value is within 10% of actual percentile
        for i in range(len(results)):
            threshold = 0.1 * expected[i] + 1e-12
            self.assertAlmostEqual(expected[i], results[i], delta=threshold)

    def test_percentile(self):
        counts = [0] * PercentileBuckets.length()
        for i in range(100000):
            counts[PercentileBuckets.index_of(i)] += 1

        pcts = [0.0, 25.0, 50.0, 75.0, 90.0, 95.0, 98.0, 99.0, 99.5, 100.0]
        for p in pcts:
            expected = p * 1e3
            threshold = 0.1 * expected + 1e-12
            self.assertAlmostEqual(
                expected,
                PercentileBuckets.percentile(counts, p),
                delta=threshold)


class PercentileTimerTest(unittest.TestCase):

    def _check_percentiles(self, t, start):
        for i in range(100000):
            t.record(i / 1e3)
        for i in range(start, 100):
            expected = float(i)
            threshold = 0.15 * expected + 1e-12
            self.assertAlmostEqual(expected, t.percentile(i), delta=threshold)

    def test_percentile(self):
        r = Registry()
        t = PercentileTimer(r, "test", min=0, max=PercentileBuckets._max_value)
        self._check_percentiles(t, 0)

    def test_with_threshold(self):
        r = Registry()
        t = PercentileTimer(r, "test", min=10, max=100)
        self._check_percentiles(t, 10)

    def test_with_threshold_2(self):
        r = Registry()
        t = PercentileTimer(r, "test", min=0, max=100)
        self._check_percentiles(t, 0)

    def test_stopwatch(self):
        clock = ManualClock()
        r = Registry(clock=clock)
        t = PercentileTimer(r, "test", min=0, max=100)
        with t.stopwatch():
            clock.set_monotonic_time(1.0)
        self._check_percentiles(t, 0)


class PercentileDistributionSummaryTest(unittest.TestCase):

    def _check_percentiles(self, t, start):
        for i in range(100000):
            t.record(i)
        for i in range(start, 100):
            expected = i * 1e3
            threshold = 0.15 * expected + 1e-12
            self.assertAlmostEqual(expected, t.percentile(i), delta=threshold)

    def test_percentile(self):
        r = Registry()
        t = PercentileDistributionSummary(r, "test")
        self._check_percentiles(t, 0)

    def test_with_threshold(self):
        r = Registry()
        t = PercentileDistributionSummary(r, "test", min=25e3, max=100e3)
        self._check_percentiles(t, 25)
