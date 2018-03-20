from spectator.id import MeterId
from spectator.gauge import Gauge
import math
import unittest


class GaugeTest(unittest.TestCase):

    tid = MeterId("test")

    def test_set(self):
        g = Gauge(GaugeTest.tid)
        self.assertTrue(math.isnan(g.get()))
        g.set(1)
        self.assertEqual(g.get(), 1)

    def test_measure(self):
        g = Gauge(GaugeTest.tid)
        g.set(42)
        ms = g._measure()
        self.assertTrue(math.isnan(g.get()))
        self.assertEqual(len(ms), 1)
        self.assertEqual(ms[GaugeTest.tid.with_stat('gauge')], 42)
