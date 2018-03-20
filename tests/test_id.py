from spectator.id import MeterId
import unittest


class MeterIdTest(unittest.TestCase):

    def test_equals_same_name(self):
        id1 = MeterId("foo")
        id2 = MeterId("foo")
        self.assertEqual(id1, id2)

    def test_equals_tags(self):
        id1 = MeterId("foo", {"a": "1", "b": "2", "c": "3"})
        id2 = MeterId("foo", {"c": "3", "b": "2", "a": "1"})
        self.assertEqual(id1, id2)

    def test_hash_tags(self):
        id1 = MeterId("foo", {"a": "1", "b": "2", "c": "3"})
        id2 = MeterId("foo", {"c": "3", "b": "2", "a": "1"})
        self.assertEqual(hash(id1), hash(id2))

    def test_lookup_tags(self):
        id1 = MeterId("foo", {"a": "1", "b": "2", "c": "3"})
        id2 = MeterId("foo", {"c": "3", "b": "2", "a": "1"})
        map = {id1: "test"}
        self.assertEqual(map[id2], "test")

    def test_tags(self):
        id1 = MeterId("foo", {"a": "1"})
        self.assertEqual(id1.tags(), {"a": "1"})

    def test_tags_defensive_copy(self):
        id1 = MeterId("foo", {"a": "1"})
        tags = id1.tags()
        tags["b"] = "2"
        self.assertEqual(tags, {"a": "1", "b": "2"})
        self.assertEqual(id1.tags(), {"a": "1"})
