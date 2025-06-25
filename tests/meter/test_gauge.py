import unittest

from spectator import Gauge, MemoryWriter, MeterId, NoopWriter


class GaugeTest(unittest.TestCase):
    tid = MeterId("gauge")

    def test_noop_writer(self):
        g = Gauge(self.tid)
        self.assertTrue(isinstance(g.writer(), NoopWriter))

    def test_set(self):
        g = Gauge(self.tid, MemoryWriter())
        self.assertTrue(g.writer().is_empty())

        g.set(1)
        self.assertEqual("g:gauge:1", g.writer().last_line())

    def test_ttl_seconds(self):
        g = Gauge(self.tid, MemoryWriter(), 120)
        g.set(42)
        self.assertEqual("g,120:gauge:42", g.writer().last_line())
