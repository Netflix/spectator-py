import time
import unittest

from spectator.clock import Clock, SystemClock, ManualClock


class ClockTest(unittest.TestCase):
    def test_wall_time_raises(self):
        self.assertRaises(NotImplementedError, Clock().wall_time)

    def test_monotonic_raises(self):
        self.assertRaises(NotImplementedError, Clock().monotonic_time)


class SystemClockTest(unittest.TestCase):
    def test_wall_time(self):
        c = SystemClock()
        start = c.wall_time()
        time.sleep(0.01)
        end = c.wall_time()
        self.assertTrue(end > start, "{} > {}".format(end, start))

    def test_monotonic_time(self):
        c = SystemClock()
        start = c.monotonic_time()
        time.sleep(0.01)
        end = c.monotonic_time()
        self.assertTrue(end > start, "{} > {}".format(end, start))


class ManualClockTest(unittest.TestCase):
    def test_init(self):
        c1 = ManualClock()
        self.assertEqual(0, c1.wall_time())
        self.assertEqual(0, c1.monotonic_time())

        c2 = ManualClock(1, 2)
        self.assertEqual(1, c2.wall_time())
        self.assertEqual(2, c2.monotonic_time())

    def test_set_wall_time(self):
        c = ManualClock()
        c.set_wall_time(1)
        self.assertEqual(1, c.wall_time())

    def test_set_monotonic_time(self):
        c = ManualClock()
        c.set_monotonic_time(1)
        self.assertEqual(1, c.monotonic_time())
