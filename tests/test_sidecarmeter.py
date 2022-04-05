import unittest

from spectator.id import MeterId
from spectator.sidecarmeter import SidecarMeter


class SidecarMeterTest(unittest.TestCase):

    def test_id(self):
        tid = MeterId("test")
        m = SidecarMeter(tid, "g,120")
        self.assertEqual("g,120:test:", m.idString)

    def test_id_with_tags(self):
        tid = MeterId("test", {"foo": "bar", "baz": "quux"})
        m = SidecarMeter(tid, "g,120")
        self.assertEqual("g,120:test,baz=quux,foo=bar:", m.idString)

    def test_id_with_illegal_chars(self):
        tid = MeterId("test`!@#$%^&*()-=~_+[]{}\\|;:'\",<.>/?foo")
        m = SidecarMeter(tid, "g,120")
        self.assertEqual("g,120:test______^____-_~______________.___foo:", m.idString)
