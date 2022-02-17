import unittest

from spectator import ManualClock
from spectator.id import MeterId
from spectator.patterns.agegauge import AgeGauge


class AgeGaugeTest(unittest.TestCase):

    tid = MeterId("test")

    def test_init(self):
        g = AgeGauge(self.tid)
        self.assertEqual(0, g.get())

    def test_update(self):
        clock = ManualClock()
        g = AgeGauge(self.tid, clock=clock)
        clock.set_wall_time(g._last_reset.get() + 1)
        g._update()
        self.assertTrue(1, g.get())

    def test_measure(self):
        g = AgeGauge(self.tid)
        ms = g._measure()
        self.assertEqual(0, g.get())
        self.assertEqual(1, len(ms))
        self.assertEqual(0, ms[AgeGaugeTest.tid.with_stat('gauge')])

    def test_user_statistic(self):
        g = AgeGauge(self.tid.with_stat('duration'))
        for id in g._measure().keys():
            self.assertEqual('duration', id.tags()['statistic'])
