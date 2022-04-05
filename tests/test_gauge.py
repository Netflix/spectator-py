import unittest

from spectator.gauge import AgeGauge, Gauge, MaxGauge
from spectator.id import MeterId
from spectator.sidecarwriter import MemoryWriter


class GaugeTest(unittest.TestCase):
    tid = MeterId("test")

    def test_set(self):
        g = Gauge(self.tid, writer=MemoryWriter())
        self.assertTrue(g._writer.is_empty())

        g.set(1)
        self.assertEqual("g:test:1", g._writer.last_line())

    def test_custom_ttl(self):
        g = Gauge(self.tid, ttl_seconds=120, writer=MemoryWriter())
        g.set(42)
        self.assertEqual("g,120:test:42", g._writer.last_line())

    def test_get(self):
        """Avoid breaking the API."""
        g = Gauge(self.tid, writer=MemoryWriter())
        g.set(1)
        self.assertEqual(0, g.get())


class AgeGaugeTest(unittest.TestCase):
    tid = MeterId("test")

    def test_set(self):
        g = AgeGauge(self.tid, writer=MemoryWriter())
        self.assertTrue(g._writer.is_empty())

        g.set(0)
        self.assertEqual("A:test:0", g._writer.last_line())


class MaxGaugeTest(unittest.TestCase):
    tid = MeterId("test")

    def test_set(self):
        g = MaxGauge(self.tid, writer=MemoryWriter())
        self.assertTrue(g._writer.is_empty())

        g.set(0)
        self.assertEqual("m:test:0", g._writer.last_line())
