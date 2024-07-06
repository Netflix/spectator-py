import ctypes
import unittest

from spectator.meter.monotonic_counter_uint import MonotonicCounterUint
from spectator.meter.id import Id
from spectator.writer.memory_writer import MemoryWriter


class MonotonicCounterUintTest(unittest.TestCase):
    tid = Id("monotonic_counter_uint")

    def test_set(self):
        c = MonotonicCounterUint(self.tid, writer=MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.set(ctypes.c_uint64(1))
        self.assertEqual("U:monotonic_counter_uint:1", c.writer().last_line())

    def test_set_negative(self):
        c = MonotonicCounterUint(self.tid, writer=MemoryWriter())
        self.assertTrue(c.writer().is_empty())

        c.set(ctypes.c_uint64(-1))
        self.assertEqual("U:monotonic_counter_uint:18446744073709551615", c.writer().last_line())
