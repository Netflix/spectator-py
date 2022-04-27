import unittest

from spectator.counter import Counter
from spectator.gauge import Gauge
from spectator.protocolparser import parse_protocol_line
from spectator.timer import Timer


class ProtocolParserTest(unittest.TestCase):

    def test_parse_invalid_lines(self):
        with self.assertRaises(ValueError):
            parse_protocol_line("foo")
        with self.assertRaises(ValueError):
            parse_protocol_line("foo:bar")
        with self.assertRaises(ValueError):
            parse_protocol_line("foo:bar,baz-quux")

    def test_parse_counter(self):
        meter_class, meter_id, value = parse_protocol_line("c:test:1")
        self.assertEqual(Counter, meter_class)
        self.assertEqual("test", meter_id.name)
        self.assertEqual({}, meter_id.tags())
        self.assertEqual("1", value)

    def test_parse_counter_with_tag(self):
        meter_class, meter_id, value = parse_protocol_line("c:test,foo=bar:1")
        self.assertEqual(Counter, meter_class)
        self.assertEqual("test", meter_id.name)
        self.assertEqual({"foo": "bar"}, meter_id.tags())
        self.assertEqual("1", value)

    def test_parse_counter_with_multiple_tags(self):
        meter_class, meter_id, value = parse_protocol_line("c:test,foo=bar,baz=quux:1")
        self.assertEqual(Counter, meter_class)
        self.assertEqual("test", meter_id.name)
        self.assertEqual({"foo": "bar", "baz": "quux"}, meter_id.tags())
        self.assertEqual("1", value)

    def test_parse_gauge(self):
        meter_class, meter_id, value = parse_protocol_line("g:test:1")
        self.assertEqual(Gauge, meter_class)
        self.assertEqual("test", meter_id.name)
        self.assertEqual({}, meter_id.tags())
        self.assertEqual("1", value)

    def test_parse_gauge_with_ttl(self):
        meter_class, meter_id, value = parse_protocol_line("g,120:test:1")
        self.assertEqual(Gauge, meter_class)
        self.assertEqual("test", meter_id.name)
        self.assertEqual({}, meter_id.tags())
        self.assertEqual("1", value)

    def test_parse_timer(self):
        meter_class, meter_id, value = parse_protocol_line("t:test:1")
        self.assertEqual(Timer, meter_class)
        self.assertEqual("test", meter_id.name)
        self.assertEqual({}, meter_id.tags())
        self.assertEqual("1", value)
