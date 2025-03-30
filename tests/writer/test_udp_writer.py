import threading
import unittest
from contextlib import closing

from spectator import new_writer
from ..udp_server import UdpServer


class UdpWriterTest(unittest.TestCase):

    def test_udp(self) -> None:
        with closing(UdpServer()) as server:
            with closing(new_writer(server.address())) as w:
                w.write("foo")
                self.assertEqual("foo", server.read())
                w.write("bar")
                self.assertEqual("bar", server.read())

    @unittest.skip("unreliable on ci servers")
    def test_concurrent_writes(self) -> None:
        """When running with four writer threads and one reader thread, there appears to
        be an upper limit of 18,000 +/- 500 messages. This can be observed by increasing
        the messages_per_thread to 10000. We may need to investigate performance here. The
        current value for messages_per_thread is the largest value that allows the test to
        complete successfully in most cases. Even adding a debug log line to the UdpWriter
        class can impact the number of messages received."""

        messages_per_thread = 2500
        writer_thread_count = 4
        lines = []

        with closing(UdpServer()) as server:
            with closing(new_writer(server.address())) as w:
                def reader_target() -> None:
                    while True:
                        line = server.read()
                        if line != "done":
                            lines.append(line)
                        else:
                            break

                reader = threading.Thread(target=reader_target)
                reader.start()

                def writer_target(n: int) -> None:
                    base = n * messages_per_thread
                    for i in range(0, messages_per_thread):
                        w.write("{}".format(base + i))

                threads = []
                for j in range(0, writer_thread_count):
                    thread = threading.Thread(target=writer_target, args=[j])
                    threads.append(thread)
                    thread.start()

                for t in threads:
                    t.join()

                w.write("done")
                reader.join()

        m = writer_thread_count * messages_per_thread
        self.assertEqual(m, len(lines))
        self.assertEqual(m * (m - 1) / 2, sum(map(int, lines)))
