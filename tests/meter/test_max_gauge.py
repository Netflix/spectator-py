import unittest

from spectator import MaxGauge, MemoryWriter, MeterId


class MaxGaugeTest(unittest.TestCase):
    tid = MeterId("max_gauge")

    def test_set(self):
        g = MaxGauge(self.tid, MemoryWriter())
        self.assertTrue(g.writer().is_empty())

        g.set(0)
        self.assertEqual("m:max_gauge:0", g.writer().last_line())
