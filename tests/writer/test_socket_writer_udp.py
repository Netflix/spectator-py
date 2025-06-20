import unittest
from contextlib import closing

from spectator import new_writer
from ..udp_server import UdpServer


class SocketWriterUdpTest(unittest.TestCase):

    def test_udp(self) -> None:
        with closing(UdpServer()) as server:
            with closing(new_writer(server.address())) as w:
                w.write("foo")
                self.assertEqual("foo", server.read())
                w.write("bar")
                self.assertEqual("bar", server.read())
