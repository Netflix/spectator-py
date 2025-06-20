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
        self.assertEqual(5, len(buffer))
        self.assertTrue(should_flush)

        self.assertEqual("abcd\ne", buffer.flush())
        self.assertEqual(0, len(buffer))

        should_flush = buffer.append("abcdefghij")
        self.assertEqual(10, len(buffer))
        self.assertTrue(should_flush)

        self.assertEqual("abcdefghij", buffer.flush())
        self.assertEqual(0, len(buffer))
