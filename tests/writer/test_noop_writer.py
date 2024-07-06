import unittest

from spectator.writer.new_writer import new_writer


class NoopWriterTest(unittest.TestCase):

    def test_noop_writer_logs(self):
        expected_messages = [
            "INFO:spectator.writer:initialize NoopWriter",
        ]

        with self.assertLogs("spectator.writer", level='INFO') as logs:
            noop_writer = new_writer("none")
            noop_writer.write("c:counter:1")
            noop_writer.close()

        self.assertEqual(expected_messages, logs.output)
