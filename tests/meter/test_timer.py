import unittest

from spectator import MemoryWriter, MeterId, Timer


class TimerTest(unittest.TestCase):
    tid = MeterId("timer")

    def test_record(self):
        t = Timer(self.tid, MemoryWriter())
        self.assertTrue(t.writer().is_empty())

        t.record(42)
        self.assertEqual("t:timer:42", t.writer().last_line())

    def test_record_negative(self):
        t = Timer(self.tid, MemoryWriter())
        t.record(-42)
        self.assertTrue(t.writer().is_empty())

    def test_record_zero(self):
        t = Timer(self.tid, MemoryWriter())
        t.record(0)
        self.assertEqual("t:timer:0", t.writer().last_line())
