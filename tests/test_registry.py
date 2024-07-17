import logging
import unittest

from spectator.registry import Registry
from spectator.config import Config
from spectator.writer.memory_writer import MemoryWriter


class RegistryTest(unittest.TestCase):

    def test_close(self):
        r = Registry(Config("memory"))

        c = r.counter("counter")
        c.increment()
        self.assertEqual("c:counter:1", r.writer().last_line())

        r.close()
        self.assertTrue(r.writer().is_empty())

    def test_age_gauge(self):
        r = Registry(Config("memory"))

        g1 = r.age_gauge("age_gauge")
        g2 = r.age_gauge("age_gauge", {"my-tags": "bar"})
        self.assertTrue(r.writer().is_empty())

        g1.set(1)
        self.assertEqual("A:age_gauge:1", r.writer().last_line())

        g2.set(2)
        self.assertEqual("A:age_gauge,my-tags=bar:2", r.writer().last_line())

    def test_age_gauge_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        g = r.age_gauge_with_meter_id(r.new_id("age_gauge", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        g.set(0)
        self.assertEqual("A:age_gauge,extra-tags=foo,my-tags=bar:0", r.writer().last_line())

    def test_counter(self):
        r = Registry(Config("memory"))

        c1 = r.counter("counter")
        c2 = r.counter("counter", {"my-tags": "bar"})
        self.assertTrue(r.writer().is_empty())

        c1.increment()
        self.assertEqual("c:counter:1", r.writer().last_line())

        c2.increment()
        self.assertEqual("c:counter,my-tags=bar:1", r.writer().last_line())

        c1.increment(2)
        self.assertEqual("c:counter:2", r.writer().last_line())

        c2.increment(2)
        self.assertEqual("c:counter,my-tags=bar:2", r.writer().last_line())

        r.counter("counter").increment(3)
        self.assertEqual("c:counter:3", r.writer().last_line())

    def test_counter_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        c = r.counter_with_meter_id(r.new_id("counter", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        c.increment()
        self.assertEqual("c:counter,extra-tags=foo,my-tags=bar:1", r.writer().last_line())

        c.increment(2)
        self.assertEqual("c:counter,extra-tags=foo,my-tags=bar:2", r.writer().last_line())

        r.counter("counter").increment(3)
        self.assertEqual("c:counter,extra-tags=foo:3", r.writer().last_line())

    def test_distribution_summary(self):
        r = Registry(Config("memory"))

        d = r.distribution_summary("distribution_summary")
        self.assertTrue(r.writer().is_empty())

        d.record(42)
        self.assertEqual("d:distribution_summary:42", r.writer().last_line())

    def test_distribution_summary_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        d = r.distribution_summary_with_meter_id(r.new_id("distribution_summary", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        d.record(42)
        self.assertEqual("d:distribution_summary,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_gauge(self):
        r = Registry(Config("memory"))

        g = r.gauge("gauge")
        self.assertTrue(r.writer().is_empty())

        g.set(42)
        self.assertEqual("g:gauge:42", r.writer().last_line())

    def test_gauge_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        g = r.gauge_with_meter_id(r.new_id("gauge", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        g.set(42)
        self.assertEqual("g:gauge,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_gauge_with_id_with_ttl_seconds(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        g = r.gauge_with_meter_id(r.new_id("gauge", {"my-tags": "bar"}), ttl_seconds=120)
        self.assertTrue(r.writer().is_empty())

        g.set(42)
        self.assertEqual("g,120:gauge,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_gauge_with_ttl_seconds(self):
        r = Registry(Config("memory"))

        g = r.gauge("gauge", ttl_seconds=120)
        self.assertTrue(r.writer().is_empty())

        g.set(42)
        self.assertEqual("g,120:gauge:42", r.writer().last_line())

    def test_max_gauge(self):
        r = Registry(Config("memory"))

        g = r.max_gauge("max_gauge")
        self.assertTrue(r.writer().is_empty())

        g.set(42)
        self.assertEqual("m:max_gauge:42", r.writer().last_line())

    def test_max_gauge_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        g = r.max_gauge_with_meter_id(r.new_id("max_gauge", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        g.set(42)
        self.assertEqual("m:max_gauge,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_monotonic_counter(self):
        r = Registry(Config("memory"))

        c = r.monotonic_counter("monotonic_counter")
        self.assertTrue(r.writer().is_empty())

        c.set(42)
        self.assertEqual("C:monotonic_counter:42", r.writer().last_line())

    def test_monotonic_counter_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        c = r.monotonic_counter_with_meter_id(r.new_id("monotonic_counter", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        c.set(42)
        self.assertEqual("C:monotonic_counter,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_new_id(self):
        r1 = Registry(Config("memory"))
        id1 = r1.new_id("id")
        self.assertEqual("Id(name=id, tags={})", str(id1))

        r2 = Registry(Config("memory", {"extra-tags": "foo"}))
        id2 = r2.new_id("id")
        self.assertEqual("Id(name=id, tags={'extra-tags': 'foo'})", str(id2))

    def test_pct_distribution_summary(self):
        r = Registry(Config("memory"))

        d = r.pct_distribution_summary("pct_distribution_summary")
        self.assertTrue(r.writer().is_empty())

        d.record(42)
        self.assertEqual("D:pct_distribution_summary:42", r.writer().last_line())

    def test_pct_distribution_summary_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        d = r.pct_distribution_summary_with_meter_id(r.new_id("pct_distribution_summary", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        d.record(42)
        self.assertEqual("D:pct_distribution_summary,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_pct_timer(self):
        r = Registry(Config("memory"))

        t = r.pct_timer("pct_timer")
        self.assertTrue(r.writer().is_empty())

        t.record(42)
        self.assertEqual("T:pct_timer:42", r.writer().last_line())

    def test_pct_timer_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        t = r.pct_timer_with_meter_id(r.new_id("pct_timer", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        t.record(42)
        self.assertEqual("T:pct_timer,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_timer(self):
        r = Registry(Config("memory"))

        t = r.timer("timer")
        self.assertTrue(r.writer().is_empty())

        t.record(42)
        self.assertEqual("t:timer:42", r.writer().last_line())

    def test_timer_with_id(self):
        r = Registry(Config("memory", {"extra-tags": "foo"}))

        t = r.timer_with_meter_id(r.new_id("timer", {"my-tags": "bar"}))
        self.assertTrue(r.writer().is_empty())

        t.record(42)
        self.assertEqual("t:timer,extra-tags=foo,my-tags=bar:42", r.writer().last_line())

    def test_writer(self):
        r = Registry(Config("memory"))
        self.assertTrue(isinstance(r.writer(), MemoryWriter))

    def test_writer_debug_logging(self):
        logging.getLogger("spectator.writer").setLevel(logging.DEBUG)
        r = Registry(Config("memory"))
        self.assertTrue(r.writer().is_empty())

        expected_messages = [
            "DEBUG:spectator.writer:write line=c:counter:1",
        ]

        with self.assertLogs("spectator.writer", level='DEBUG') as logs:
            c = r.counter("counter")
            c.increment()

        self.assertEqual(expected_messages, logs.output)
