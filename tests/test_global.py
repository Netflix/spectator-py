import unittest
from contextlib import closing

from spectator import GlobalRegistry
from .udpserver import UdpServer


class GlobalTest(unittest.TestCase):

    def test_counter(self):
        with closing(UdpServer(("127.0.0.1", 1234))) as server:  # type: UdpServer
            c = GlobalRegistry.counter("test")
            c.increment()
            self.assertEqual("c:test:1", server.read())
