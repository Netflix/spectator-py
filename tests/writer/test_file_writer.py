import io
import os
import unittest
from contextlib import closing, redirect_stderr, redirect_stdout
from tempfile import TemporaryDirectory

from spectator import Config, FileWriter


class FileWriterTest(unittest.TestCase):

    def test_file_writer_custom(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file = os.path.join(tmpdir, "file-writer.txt")
            writer = FileWriter(Config(f"file://{tmp_file}"))

            with closing(writer) as w:
                w.write("foo")

            with open(tmp_file, encoding="utf-8") as f:
                line = f.read()
                self.assertEqual("foo\n", line)

    def test_file_writer_stderr(self):
        f = io.StringIO()
        with redirect_stderr(f):
            with closing(FileWriter(Config("stderr"))) as w:
                w.write("foo")
                self.assertEqual("foo\n", f.getvalue())

    def test_file_writer_stdout(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with closing(FileWriter(Config("stdout"))) as w:
                w.write("foo")
                self.assertEqual("foo\n", f.getvalue())
