import unittest

from spectator.config import Config
from spectator.registry import Registry
from spectator.clock import ManualClock
from spectator.stopwatch import StopWatch


class StopwatchTest(unittest.TestCase):

    def test_stopwatch_with_pct_timer(self):
        r = Registry(Config("memory"))
        t = r.timer("pct_timer")
        self.assertTrue(r.writer().is_empty())

        clock = ManualClock()
        with StopWatch(t, clock):
            clock.set_monotonic_time(33)
        self.assertEqual("t:pct_timer:33", r.writer().last_line())

    def test_stopwatch_with_timer(self):
        r = Registry(Config("memory"))
        t = r.timer("timer")
        self.assertTrue(r.writer().is_empty())

        clock = ManualClock()
        with StopWatch(t, clock):
            clock.set_monotonic_time(42)
        self.assertEqual("t:timer:42", r.writer().last_line())
