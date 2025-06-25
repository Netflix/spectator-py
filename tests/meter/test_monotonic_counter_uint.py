import ctypes
import unittest

from spectator import MonotonicCounterUint, MemoryWriter, MeterId, NoopWriter


class MonotonicCounterUintTest(unittest.TestCase):
    tid = MeterId("monotonic_counter_uint")

    def test_noop_writer(self):
        c = MonotonicCounterUint(self.tid)
        self.assertTrue(isinstance(c.writer(), NoopWriter))

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
