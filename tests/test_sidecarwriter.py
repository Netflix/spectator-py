import io
import unittest
from contextlib import closing, redirect_stderr, redirect_stdout
from tempfile import TemporaryDirectory
import os
from spectator.sidecarwriter import PrintWriter, SidecarWriter


class SidecarWriterTest(unittest.TestCase):

    def test_invalid_location(self):
        with self.assertRaises(ValueError):
            SidecarWriter.create("foo")

    def test_write_impl_requires_concrete_class(self):
        with self.assertRaises(NotImplementedError):
            SidecarWriter("foo").write_impl("bar")

    def test_close_requires_concrete_class(self):
        with self.assertRaises(NotImplementedError):
            SidecarWriter("foo").close()

    def test_noop_writer(self):
        noop = SidecarWriter.create("none")
        try:
            noop.write_impl("foo")
            noop.close()
        except NotImplementedError:
            self.fail("NoopWriter raised NotImplementedError unexpectedly!")

    def test_print_writer_custom(self):
        with TemporaryDirectory() as tmpdir:
            tmpfile = os.path.join(tmpdir, "print-writer.txt")
            writer = SidecarWriter.create("file://{}".format(tmpfile))

            with closing(writer) as w:  # type: PrintWriter
                w.write_line("foo")

            with open(tmpfile, encoding="utf-8") as f:
                line = f.read()
                self.assertEqual("foo\n", line)

    def test_print_writer_stderr(self):
        f = io.StringIO()
        with redirect_stderr(f):
            with closing(SidecarWriter.create("stderr")) as w:  # type: PrintWriter
                w.write_line("foo")
                self.assertEqual("foo\n", f.getvalue())

    def test_print_writer_stdout(self):
        f = io.StringIO()
        with redirect_stdout(f):
            with closing(SidecarWriter.create("stdout")) as w:  # type: PrintWriter
                w.write_line("foo")
                self.assertEqual("foo\n", f.getvalue())

    def test_memory_writer_get_clear(self):
        memory = SidecarWriter.create("memory")
        self.assertEqual([], memory.get())
        memory.write("c:test:", 1)
        self.assertEqual(["c:test:1"], memory.get())
        memory.clear()
        self.assertEqual([], memory.get())
