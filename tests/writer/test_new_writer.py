import os
import unittest
from tempfile import TemporaryDirectory

from spectator import Config, new_writer, NoopWriter, MemoryWriter, FileWriter, SocketWriter


class NewWriterTest(unittest.TestCase):

    def test_none(self):
        w = new_writer(Config("none"))
        self.assertTrue(isinstance(w, NoopWriter))

    def test_memory(self):
        w = new_writer(Config("memory"))
        self.assertTrue(isinstance(w, MemoryWriter))

    def test_stderr_stdout_file(self):
        w = new_writer(Config("stderr"))
        self.assertTrue(isinstance(w, FileWriter))
        w = new_writer(Config("stdout"))
        self.assertTrue(isinstance(w, FileWriter))

        with TemporaryDirectory() as tmpdir:
            tmp_file = os.path.join(tmpdir, "file-writer.txt")
            w = new_writer(Config(f"file://{tmp_file}"))
            self.assertTrue(isinstance(w, FileWriter))

    def test_udp_unix(self):
        w = new_writer(Config("udp"))
        self.assertTrue(isinstance(w, SocketWriter))
        w = new_writer(Config("udp://"))
        self.assertTrue(isinstance(w, SocketWriter))

        w = new_writer(Config("unix"))
        self.assertTrue(isinstance(w, SocketWriter))
        w = new_writer(Config("unix://"))
        self.assertTrue(isinstance(w, SocketWriter))

    def test_invalid(self):
        config = Config("none")
        config.location = "invalid"
        self.assertRaises(ValueError, new_writer, config)
