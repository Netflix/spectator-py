import unittest

from spectator import DistinctCountSketch, MemoryWriter, MeterId, NoopWriter


class DistinctCountSketchTest(unittest.TestCase):
    tid = MeterId("distinct_count_sketch")

    def test_noop_writer(self):
        d = DistinctCountSketch(self.tid)
        self.assertTrue(isinstance(d.writer(), NoopWriter))

    def test_record_str(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        self.assertTrue(d.writer().is_empty())

        # "a" -> base64 "YQ=="; SpectatorD decodes and hashes the bytes.
        d.record("a")
        self.assertEqual("S:distinct_count_sketch:YQ==", d.writer().last_line())

    def test_record_bytes(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        d.record(b"\xde\xad\xbe\xef")
        self.assertEqual("S:distinct_count_sketch:3q2+7w==", d.writer().last_line())

    def test_record_int(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        # Integers are encoded as their 8-byte little-endian representation. The literal pins the
        # wire format so it cannot drift from the Java/C++ clients.
        d.record(42)
        self.assertEqual("S:distinct_count_sketch:KgAAAAAAAAA=", d.writer().last_line())

    def test_record_negative_int(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        # -1 wraps to the all-ones 64-bit pattern, matching a signed long in the other clients.
        d.record(-1)
        self.assertEqual("S:distinct_count_sketch://////////8=", d.writer().last_line())

    def test_record_out_of_range_int_is_ignored(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        d.record(2 ** 70)  # does not fit in 64 bits; skipped rather than silently truncated
        self.assertTrue(d.writer().is_empty())

    def test_record_bool_is_ignored(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        d.record(True)  # bool is excluded from the int path; skipped rather than recorded as 1
        self.assertTrue(d.writer().is_empty())

    def test_record_str_with_unpaired_surrogate(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        # An unpaired surrogate must not raise; it is replaced with '?' (0x3F) to match the other
        # client implementations. base64("?") == "Pw==".
        d.record("\ud800")
        self.assertEqual("S:distinct_count_sketch:Pw==", d.writer().last_line())

    def test_record_unsupported_type_is_ignored(self):
        d = DistinctCountSketch(self.tid, MemoryWriter())
        d.record(1.5)  # float is not supported; should be skipped, not raise
        self.assertTrue(d.writer().is_empty())


if __name__ == "__main__":
    unittest.main()
