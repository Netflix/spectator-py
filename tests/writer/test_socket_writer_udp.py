import unittest
from contextlib import closing

from spectator import Config, SocketWriter
from ..udp_server import UdpServer


class SocketWriterUdpTest(unittest.TestCase):

    def test_udp(self) -> None:
        with closing(UdpServer()) as server:
            with closing(SocketWriter(Config(server.address()))) as w:
                w.write("foo")
                self.assertEqual("foo", server.read())
                w.write("bar")
                self.assertEqual("bar", server.read())

    def test_udp_with_buffer(self) -> None:
        with closing(UdpServer()) as server:
            with closing(SocketWriter(Config(server.address(), buffer_size=5))) as w:
                w.write("foo")
                w.write("bar")
                self.assertEqual("foo\nbar", server.read())
