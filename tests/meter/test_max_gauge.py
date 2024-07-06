import unittest

from spectator.meter.max_gauge import MaxGauge
from spectator.meter.id import Id
from spectator.writer.memory_writer import MemoryWriter


class MaxGaugeTest(unittest.TestCase):
    tid = Id("max_gauge")

    def test_set(self):
        g = MaxGauge(self.tid, MemoryWriter())
        self.assertTrue(g.writer().is_empty())

        g.set(0)
        self.assertEqual("m:max_gauge:0", g.writer().last_line())
