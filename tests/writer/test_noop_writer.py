import unittest

from spectator import new_writer


class NoopWriterTest(unittest.TestCase):

    def test_noop_writer_logs(self):
        expected_messages = [
            "DEBUG:spectator.writer:initialize NoopWriter",
            "DEBUG:spectator.writer:write line=c:counter:1"
        ]

        with self.assertLogs("spectator.writer", level='DEBUG') as logs:
            noop_writer = new_writer("none")
            noop_writer.write("c:counter:1")
            noop_writer.close()

        self.assertEqual(expected_messages, logs.output)
