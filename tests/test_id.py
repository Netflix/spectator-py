import unittest

from spectator.id import MeterId


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
        d = {id1: "test"}
        self.assertEqual("test", d[id2])

    def test_tags(self):
        id1 = MeterId("foo", {"a": "1"})
        self.assertEqual({"a": "1"}, id1.tags())

    def test_tags_defensive_copy(self):
        id1 = MeterId("foo", {"a": "1"})
        tags = id1.tags()
        tags["b"] = "2"
        self.assertEqual({"a": "1", "b": "2"}, tags)
        self.assertEqual({"a": "1"}, id1.tags())

    def test_with_tag_returns_new_object(self):
        id1 = MeterId("foo")
        id2 = id1.with_tag("a", "1")
        self.assertNotEqual(id1, id2)
        self.assertEqual({}, id1.tags())
        self.assertEqual({"a": "1"}, id2.tags())

    def test_with_tags_returns_new_object(self):
        id1 = MeterId("foo")
        id2 = id1.with_tags({"a": "1", "b": "2"})
        self.assertNotEqual(id1, id2)
        self.assertEqual({}, id1.tags())
        self.assertEqual({"a": "1", "b": "2"}, id2.tags())

    def test_different_types_not_equal(self):
        id1 = MeterId("foo", {"a": "1"})
        self.assertTrue(id1 != 1)

    def test_with_stat(self):
        """Avoid breaking the API."""
        id1 = MeterId("foo")
        self.assertEqual(id1, id1.with_stat("bar"))

    def test_with_default_stat(self):
        """Avoid breaking the API."""
        id1 = MeterId("foo")
        self.assertEqual(id1, id1.with_default_stat("bar"))

    def test_str(self):
        id1 = MeterId("foo")
        self.assertEqual("foo", str(id1))
        id2 = MeterId("foo", {"a": "1", "b": "2", "c": "3"})
        self.assertEqual("foo,a=1,b=2,c=3", str(id2))
