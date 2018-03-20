from spectator import ManualClock
from spectator import Registry
import unittest


class RegistryTest(unittest.TestCase):

    def test_counter(self):
        r = Registry()
        c = r.counter("test")
        self.assertEqual(c.count(), 0)
        c.increment()
        self.assertEqual(c.count(), 1)

    def test_counter_get(self):
        r = Registry()
        r.counter("test").increment()
        self.assertEqual(r.counter("test").count(), 1)

    def test_timer(self):
        r = Registry()
        t = r.timer("test")
        self.assertEqual(t.count(), 0)
        t.record(42)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_time(), 42)

    def test_timer_with(self):
        clock = ManualClock()
        r = Registry(clock)
        t = r.timer("test")
        with t.stopwatch():
            clock.set_monotonic_time(42)
        self.assertEqual(t.count(), 1)
        self.assertEqual(t.total_time(), 42)

    def test_iterate_empty(self):
        r = Registry()
        for m in r:
            self.fail("registry should be empty")

    def test_iterate(self):
        r = Registry()
        r.counter("counter")
        r.timer("timer")
        meters = 0
        for m in r:
            meters += 1
        self.assertEqual(2, meters)

    def test_duplicate_start(self):
        r = Registry()
        r.start()
        t1 = r._timer
        r.start()
        self.assertEqual(r._timer, t1)

    def test_publish_cleanup_noref(self):
        r = Registry()
        with r.start():
            id = r.counter('test').meterId
            r.counter('test').increment()
            self.assertTrue(id in r._meters)
            r._publish()
            self.assertFalse(id in r._meters)

    def test_publish_cleanup_ref(self):
        r = Registry()
        with r.start():
            id = r.counter('test').meterId
            c = r.counter('test')
            c.increment()
            self.assertTrue(id in r._meters)
            r._publish()
            self.assertTrue(id in r._meters)
