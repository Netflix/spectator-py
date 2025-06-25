import unittest

from spectator import NoopWriter


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
