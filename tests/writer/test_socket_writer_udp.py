import threading
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

    def test_udp_with_buffer_flushes_on_close(self) -> None:
        with closing(UdpServer()) as server:
            w = SocketWriter(Config(server.address(), buffer_size=1024))
            w.write("foo")
            w.write("bar")
            w.close()
            self.assertEqual("foo\nbar", server.read())

    def test_udp_close_closes_socket_on_encode_error(self) -> None:
        with closing(UdpServer()) as server:
            w = SocketWriter(Config(server.address(), buffer_size=1024))
            w.write("\ud800")
            sock = w._sock  # pylint: disable=protected-access
            assert sock is not None
            self.assertRaises(UnicodeEncodeError, w.close)
            self.assertEqual(-1, sock.fileno())
            w.write("foo")
            self.assertIsNone(w._sock)  # pylint: disable=protected-access

    def test_udp_close_while_lock_is_held_by_same_thread(self) -> None:
        # a signal handler may call close() while the interrupted thread holds the lock
        with closing(UdpServer()) as server:
            w = SocketWriter(Config(server.address(), buffer_size=1024))
            w.write("foo")

            def close_holding_lock() -> None:
                with w._lock:  # pylint: disable=protected-access
                    w.close()

            t = threading.Thread(target=close_holding_lock, daemon=True)
            t.start()
            t.join(5)
            self.assertFalse(t.is_alive())
            self.assertEqual("foo", server.read())
