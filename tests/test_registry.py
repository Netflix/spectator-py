import unittest

from spectator import ManualClock, Registry
from spectator.sidecarconfig import SidecarConfig


class RegistryTest(unittest.TestCase):

    def test_age_gauge(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        g = r.age_gauge("test")
        self.assertTrue(g._writer.is_empty())

        g.set(0)
        self.assertEqual("A:test:0", g._writer.last_line())

    def test_counter(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        c = r.counter("test")
        self.assertTrue(c._writer.is_empty())

        c.increment()
        self.assertEqual("c:test:1", c._writer.last_line())

    def test_counter_without_reference(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))
        self.assertTrue(r.counter("test")._writer.is_empty())

        r.counter("test").increment()
        self.assertEqual("c:test:1", r.counter("test")._writer.last_line())

    def test_distsummary(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        d = r.distribution_summary("test")
        self.assertTrue(d._writer.is_empty())

        d.record(42)
        self.assertEqual("d:test:42", d._writer.last_line())

    def test_gauge(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        g = r.gauge("test")
        self.assertTrue(g._writer.is_empty())

        g.set(42)
        self.assertEqual("g:test:42", g._writer.last_line())

    def test_gauge_ttl_seconds(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        g = r.gauge("test", ttl_seconds=120)
        self.assertTrue(g._writer.is_empty())

        g.set(42)
        self.assertEqual("g,120:test:42", g._writer.last_line())

    def test_max_gauge(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        g = r.max_gauge("test")
        self.assertTrue(g._writer.is_empty())

        g.set(42)
        self.assertEqual("m:test:42", g._writer.last_line())

    def test_monotonic_counter(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        c = r.monotonic_counter("test")
        self.assertTrue(c._writer.is_empty())

        c.set(42)
        self.assertEqual("C:test:42", c._writer.last_line())

    def test_pct_distsummary(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        d = r.pct_distribution_summary("test")
        self.assertTrue(d._writer.is_empty())

        d.record(42)
        self.assertEqual("D:test:42", d._writer.last_line())

    def test_pct_timer(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        t = r.pct_timer("test")
        self.assertTrue(t._writer.is_empty())

        t.record(42)
        self.assertEqual("T:test:42", t._writer.last_line())

    def test_pct_timer_stopwatch(self):
        clock = ManualClock()
        r = Registry(clock=clock, config=SidecarConfig({"sidecar.output-location": "memory"}))

        t = r.pct_timer("test")
        with t.stopwatch():
            clock.set_monotonic_time(42)
        self.assertEqual("T:test:42", t._writer.last_line())

    def test_timer(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        t = r.timer("test")
        self.assertTrue(t._writer.is_empty())

        t.record(42)
        self.assertEqual("t:test:42", t._writer.last_line())

    def test_timer_stopwatch(self):
        clock = ManualClock()
        r = Registry(clock=clock, config=SidecarConfig({"sidecar.output-location": "memory"}))

        t = r.timer("test")
        with t.stopwatch():
            clock.set_monotonic_time(42)
        self.assertEqual("t:test:42", t._writer.last_line())

    def test_close(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))
        c = r.counter("test")
        c.increment()
        self.assertEqual("c:test:1", c._writer.last_line())
        r.close()
        self.assertTrue(c._writer.is_empty())

    def test_iterate(self):
        """Avoid breaking the API."""
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        for _ in r:
            self.fail("registry should be empty")

        r.counter("counter")
        r.timer("timer")

        for _ in r:
            self.fail("registry no longer holds references to MeterIds")
