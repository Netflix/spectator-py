import unittest
from contextlib import closing

from spectator import GlobalRegistry
from .udp_server import UdpServer


class GlobalRegistryTest(unittest.TestCase):

    def test_counter(self):
        with closing(UdpServer(("127.0.0.1", 1234))) as server:
            c = GlobalRegistry.counter("counter")
            c.increment()
            self.assertEqual("c:counter:1", server.read())
            c.increment(2)
            self.assertEqual("c:counter:2", server.read())
