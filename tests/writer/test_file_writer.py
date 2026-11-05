import io
import os
import unittest
from contextlib import closing, redirect_stderr, redirect_stdout
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import quote

from spectator import Config, FileWriter


class FileWriterTest(unittest.TestCase):
    def test_file_writer_escaped_path(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file = os.path.join(tmpdir, "metrics space #%25.txt")
            with closing(FileWriter(Config(f"file://{quote(tmp_file)}"))) as writer:
                writer.write("foo")
            with open(tmp_file, encoding="utf-8") as source:
                self.assertEqual("foo\n", source.read())
            self.assertEqual(["metrics space #%25.txt"], os.listdir(tmpdir))

    def test_file_writer_custom(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file = os.path.join(tmpdir, "file-writer.txt")
            writer = FileWriter(Config(f"file://{tmp_file}"))

            with closing(writer) as w:
                w.write("foo")

            with open(tmp_file, encoding="utf-8") as f:
                line = f.read()
                self.assertEqual("foo\n", line)

    def test_file_writer_write_after_close_is_noop(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file = os.path.join(tmpdir, "file-writer.txt")
            writer = FileWriter(Config(f"file://{tmp_file}"))
            writer.write("foo")
            writer.close()
            writer.write("bar")

            with open(tmp_file, encoding="utf-8") as f:
                self.assertEqual("foo\n", f.read())

    def test_file_writer_write_to_closed_std_stream_is_noop(self):
        f = io.StringIO()
        with redirect_stdout(f):
            writer = FileWriter(Config("stdout"))
        f.close()
        writer.write("foo")

    def test_file_writer_write_keeps_raising_encode_errors(self):
        stream = io.TextIOWrapper(io.BytesIO(), encoding="ascii")
        with redirect_stdout(stream):
            writer = FileWriter(Config("stdout"))
        with self.assertRaises(UnicodeEncodeError):
            writer.write("caf\u00e9")

    def test_file_writer_stderr(self):
        f = io.StringIO()
        with redirect_stderr(f), closing(FileWriter(Config("stderr"))) as w:
            w.write("foo")
            self.assertEqual("foo\n", f.getvalue())

    def test_file_writer_close_leaves_std_streams_open(self):
        f = io.StringIO()
        with redirect_stdout(f), patch.object(f, "flush") as flush:
            FileWriter(Config("stdout")).close()
        with redirect_stderr(f):
            FileWriter(Config("stderr")).close()
        self.assertFalse(f.closed)
        flush.assert_called_once()

    def test_file_writer_stdout(self):
        f = io.StringIO()
        with redirect_stdout(f), closing(FileWriter(Config("stdout"))) as w:
            w.write("foo")
            self.assertEqual("foo\n", f.getvalue())

    def test_file_writer_writes_each_line_in_one_call(self):
        f = io.StringIO()
        with (
            redirect_stdout(f),
            patch.object(f, "write", wraps=f.write) as write,
            closing(FileWriter(Config("stdout"))) as w,
        ):
            w.write("foo")
        write.assert_called_once_with("foo\n")
