import io
import os
import unittest
from contextlib import closing, redirect_stderr, redirect_stdout
from tempfile import TemporaryDirectory

from spectator.writer.new_writer import new_writer


class FileWriterTest(unittest.TestCase):

    def test_file_writer_custom(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file = os.path.join(tmpdir, "print-writer.txt")
            writer = new_writer(f"file://{tmp_file}")

            with closing(writer) as w:
                w.write("foo")

            with open(tmp_file, encoding="utf-8") as f:
                line = f.read()
                self.assertEqual("foo\n", line)

    def test_file_writer_stderr(self):
        f = io.StringIO()
        with redirect_stderr(f):
            with closing(new_writer("stderr")) as w:
                w.write("foo")
                self.assertEqual("foo\n", f.getvalue())

    def test_file_writer_stdout(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with closing(new_writer("stdout")) as w:
                w.write("foo")
                self.assertEqual("foo\n", f.getvalue())
