import unittest

from spectator.meter.counter import Counter
from spectator.meter.gauge import Gauge
from spectator.meter.timer import Timer
from spectator.protocol_parser import get_meter_class, parse_protocol_line


class ProtocolParserTest(unittest.TestCase):

    def test_parse_invalid_lines(self):
        self.assertRaises(ValueError, parse_protocol_line, "foo")
        self.assertRaises(ValueError, parse_protocol_line, "foo:bar")
        self.assertRaises(ValueError, parse_protocol_line, "foo:bar,baz-quux")

    def test_parse_counter(self):
        symbol, id, value = parse_protocol_line("c:counter:1")
        self.assertEqual("c", symbol)
        self.assertEqual(Counter, get_meter_class(symbol))
        self.assertEqual("counter", id.name())
        self.assertEqual({}, id.tags())
        self.assertEqual("1", value)

    def test_parse_counter_with_tag(self):
        symbol, id, value = parse_protocol_line("c:counter,foo=bar:1")
        self.assertEqual("c", symbol)
        self.assertEqual(Counter, get_meter_class(symbol))
        self.assertEqual("counter", id.name())
        self.assertEqual({"foo": "bar"}, id.tags())
        self.assertEqual("1", value)

    def test_parse_counter_with_multiple_tags(self):
        symbol, id, value = parse_protocol_line("c:counter,foo=bar,baz=quux:1")
        self.assertEqual("c", symbol)
        self.assertEqual(Counter, get_meter_class(symbol))
        self.assertEqual("counter", id.name())
        self.assertEqual({"foo": "bar", "baz": "quux"}, id.tags())
        self.assertEqual("1", value)

    def test_parse_gauge(self):
        symbol, id, value = parse_protocol_line("g:gauge:1")
        self.assertEqual("g", symbol)
        self.assertEqual(Gauge, get_meter_class(symbol))
        self.assertEqual("gauge", id.name())
        self.assertEqual({}, id.tags())
        self.assertEqual("1", value)

    def test_parse_gauge_with_ttl(self):
        symbol, id, value = parse_protocol_line("g,120:gauge:1")
        self.assertEqual("g", symbol)
        self.assertEqual(Gauge, get_meter_class(symbol))
        self.assertEqual("gauge", id.name())
        self.assertEqual({}, id.tags())
        self.assertEqual("1", value)

    def test_parse_timer(self):
        symbol, id, value = parse_protocol_line("t:timer:1")
        self.assertEqual("t", symbol)
        self.assertEqual(Timer, get_meter_class(symbol))
        self.assertEqual("timer", id.name())
        self.assertEqual({}, id.tags())
        self.assertEqual("1", value)
