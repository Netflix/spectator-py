import math
import unittest

from spectator import ManualClock
from spectator.gauge import Gauge
from spectator.id import MeterId


class GaugeTest(unittest.TestCase):

    tid = MeterId("test")

    def test_set(self):
        g = Gauge(GaugeTest.tid)
        self.assertTrue(math.isnan(g.get()))
        g.set(1)
        self.assertEqual(1, g.get())

    def test_measure(self):
        g = Gauge(GaugeTest.tid)
        g.set(42)
        ms = g._measure()
        self.assertEqual(42, g.get())
        self.assertEqual(1, len(ms))
        self.assertEqual(42, ms[GaugeTest.tid.with_stat('gauge')])

    def test_ttl_reset(self):
        clock = ManualClock()
        g = Gauge(GaugeTest.tid, clock=clock)
        g.set(42)
        clock.set_wall_time(g.ttl + 1)
        ms = g._measure()
        self.assertTrue(math.isnan(g.get()))
        self.assertEqual(1, len(ms))
        self.assertEqual(42, ms[GaugeTest.tid.with_stat('gauge')])

    def test_user_statistic(self):
        g = Gauge(GaugeTest.tid.with_stat('duration'))
        g.set(42)
        for id in g._measure().keys():
            self.assertEqual('duration', id.tags()['statistic'])
