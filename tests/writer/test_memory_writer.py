import unittest

from spectator import new_writer


class MemoryWriterTest(unittest.TestCase):

    def test_all_methods(self):
        memory_writer = new_writer("memory")
        self.assertTrue(memory_writer.is_empty())

        memory_writer.write("c:counter:1")
        memory_writer.write("g:gauge:2")
        self.assertEqual(["c:counter:1", "g:gauge:2"], memory_writer.get())
        self.assertEqual("g:gauge:2", memory_writer.last_line())

        memory_writer.clear()
        self.assertTrue(memory_writer.is_empty())

        memory_writer.write("c:counter:1")
        memory_writer.write("g:gauge:2")
        memory_writer.close()
        self.assertTrue(memory_writer.is_empty())
