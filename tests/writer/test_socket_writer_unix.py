import random
import socket
import unittest
from contextlib import closing
from urllib.parse import quote

from spectator import Config, SocketWriter
from ..unix_server import UnixServer


class SocketWriterUnixTest(unittest.TestCase):

    def test_socket_writer_unix_escaped_address(self) -> None:
        w = SocketWriter(Config("unix:///run/spectatord/my%20service/spectatord.unix"))
        self.assertEqual("/run/spectatord/my service/spectatord.unix", w._address)  # pylint: disable=protected-access

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "requires AF_UNIX support")
    def test_socket_writer_unix(self) -> None:
        with closing(UnixServer()) as server:
            with closing(SocketWriter(Config(server.address()))) as w:
                w.write("foo")
                self.assertEqual("foo", server.read())
                w.write("bar")
                self.assertEqual("bar", server.read())

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "requires AF_UNIX support")
    def test_socket_writer_unix_path_containing_udp(self) -> None:
        with closing(UnixServer("/tmp/udp-spectatord-test")) as server:
            with closing(SocketWriter(Config(server.address()))) as w:
                w.write("foo")
                self.assertEqual("foo", server.read())

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "requires AF_UNIX support")
    def test_socket_writer_unix_escaped_path(self) -> None:
        path = f"/tmp/spectatord test {random.randint(1, 10000)}.unix"
        with closing(UnixServer(path)) as server:
            with closing(SocketWriter(Config(f"unix://{quote(path)}"))) as w:
                w.write("foo")
                self.assertEqual("foo", server.read())
