import unittest

from spectator import Config, new_writer, NoopWriter


class NoopWriterTest(unittest.TestCase):

    def test_noop_writer_logs(self):
        expected_messages = [
            "INFO:spectator.writer:initialize NoopWriter",
            "DEBUG:spectator.writer:write line=c:counter:1"
        ]

        with self.assertLogs("spectator.writer", level='DEBUG') as logs:
            noop_writer = NoopWriter()
            noop_writer.write("c:counter:1")
            noop_writer.close()

        self.assertEqual(expected_messages, logs.output)

    def test_global_noop_writer_logs_at_debug(self):
        expected_messages = [
            "DEBUG:spectator.writer:initialize GlobalRegistry NoopWriter",
        ]

        with self.assertLogs("spectator.writer", level='DEBUG') as logs:
            new_writer(Config("none", is_global=True))

        self.assertEqual(expected_messages, logs.output)
