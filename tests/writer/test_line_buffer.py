import unittest

from spectator import LineBuffer


class LineBufferTest(unittest.TestCase):

    def test_all_methods(self):
        buffer = LineBuffer(5)
        self.assertEqual(0, len(buffer))

        should_flush = buffer.append("abcd")
        self.assertEqual(4, len(buffer))
        self.assertFalse(should_flush)

        should_flush = buffer.append("e")
        self.assertEqual(6, len(buffer))
        self.assertTrue(should_flush)

        self.assertEqual("abcd\ne", buffer.flush())
        self.assertEqual(0, len(buffer))

        should_flush = buffer.append("abcdefghij")
        self.assertEqual(10, len(buffer))
        self.assertTrue(should_flush)

        self.assertEqual("abcdefghij", buffer.flush())
        self.assertEqual(0, len(buffer))

    def test_flush_threshold_includes_newline_separators(self):
        buffer = LineBuffer(7)
        self.assertFalse(buffer.append("abc"))
        self.assertTrue(buffer.append("def"))
        self.assertEqual(7, len(buffer))
        self.assertEqual("abc\ndef", buffer.flush())

    def test_size_matches_utf8_payload(self):
        buffer = LineBuffer(6)
        self.assertFalse(buffer.append("é"))
        self.assertEqual(2, len(buffer))
        self.assertTrue(buffer.append("€"))
        self.assertEqual(6, len(buffer))
        payload = buffer.flush()
        self.assertEqual(6, len(payload.encode("utf-8")))
        self.assertEqual(0, len(buffer))
        self.assertFalse(buffer.append("abc"))
        self.assertEqual(3, len(buffer))

    def test_empty_lines_include_separators(self):
        buffer = LineBuffer(1)
        self.assertFalse(buffer.append(""))
        self.assertTrue(buffer.append(""))
        self.assertEqual(1, len(buffer))
        self.assertEqual("\n", buffer.flush())

    def test_invalid_utf8_leaves_buffer_unchanged(self):
        buffer = LineBuffer(10)
        self.assertFalse(buffer.append("foo"))
        with self.assertRaises(UnicodeEncodeError):
            buffer.append("\ud800")
        self.assertEqual(3, len(buffer))
        self.assertFalse(buffer.append("bar"))
        self.assertEqual(7, len(buffer))
        self.assertEqual("foo\nbar", buffer.flush())
