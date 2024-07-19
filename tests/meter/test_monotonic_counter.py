import unittest

from spectator.meter.monotonic_counter import MonotonicCounter
from spectator.meter.meter_id import MeterId
from spectator.writer.memory_writer import MemoryWriter


class MonotonicCounterTest(unittest.TestCase):
    tid = MeterId("monotonic_counter")

    def test_set(self):
        c = MonotonicCounter(self.tid, writer=MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.set(1)
        self.assertEqual("C:monotonic_counter:1", c.writer().last_line())

    def test_set_negative(self):
        c = MonotonicCounter(self.tid, writer=MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.set(-1)
        self.assertEqual("C:monotonic_counter:-1", c.writer().last_line())

    def test_update(self):
        c = MonotonicCounter(self.tid, writer=MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.update(1)
        self.assertEqual("C:monotonic_counter:1", c.writer().last_line())
