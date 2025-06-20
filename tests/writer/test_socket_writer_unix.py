import unittest
from contextlib import closing

from spectator import new_writer
from ..unix_server import UnixServer


class SocketWriterUnixTest(unittest.TestCase):

    def test_socket_writer_unix(self) -> None:
        with closing(UnixServer()) as server:
            with closing(new_writer(server.address())) as w:
                w.write("foo")
                self.assertEqual("foo", server.read())
                w.write("bar")
                self.assertEqual("bar", server.read())
