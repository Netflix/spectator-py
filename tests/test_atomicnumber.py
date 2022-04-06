import unittest

from spectator.atomicnumber import AtomicNumber


class AtomicNumberTest(unittest.TestCase):

    def test_init(self):
        v = AtomicNumber(42)
        self.assertEqual(42, v.get())
        v.set(44)
        self.assertEqual(44, v.get())

    def test_get_and_set(self):
        v = AtomicNumber(42)
        self.assertEqual(42, v.get_and_set(44))
        self.assertEqual(44, v.get())

    def test_get_and_increment(self):
        v = AtomicNumber(42)
        self.assertEqual(42, v.get_and_increment())
        self.assertEqual(43, v.get())

    def test_increment_and_get(self):
        v = AtomicNumber(42)
        self.assertEqual(43, v.increment_and_get())
        self.assertEqual(43, v.get())

    def test_get_and_add(self):
        v = AtomicNumber(42)
        self.assertEqual(42, v.get_and_add(2))
        self.assertEqual(44, v.get())

    def test_add_and_get(self):
        v = AtomicNumber(42)
        self.assertEqual(44, v.add_and_get(2))
        self.assertEqual(44, v.get())

    def test_max(self):
        v = AtomicNumber(42)
        self.assertEqual(42, v.max(2))
        self.assertEqual(46, v.max(46))

    def test_str(self):
        v = AtomicNumber(42)
        self.assertEqual("AtomicLong(42)", str(v))
