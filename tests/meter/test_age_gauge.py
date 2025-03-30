import unittest

from spectator import AgeGauge, MemoryWriter, MeterId


class AgeGaugeTest(unittest.TestCase):
    tid = MeterId("age_gauge")

    def test_now(self):
        g = AgeGauge(self.tid, MemoryWriter())
        self.assertTrue(g.writer().is_empty())

        g.now()
        self.assertEqual("A:age_gauge:0", g.writer().last_line())

    def test_set(self):
        g = AgeGauge(self.tid, MemoryWriter())
        self.assertTrue(g.writer().is_empty())

        g.set(10)
        self.assertEqual("A:age_gauge:10", g.writer().last_line())
