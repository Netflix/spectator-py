import socket
import threading
import time
from ipaddress import ip_address, IPv6Address
from typing import Optional, Tuple, TypeAlias, Union
from urllib.parse import urlparse

from spectator.config import Config
from spectator.writer import Writer
from spectator.writer.line_buffer import LineBuffer

InetFamily: TypeAlias = Tuple[Union[str, None], Union[int, None]]
UnixFamily: TypeAlias = str
SocketAddress: TypeAlias = Union[InetFamily, UnixFamily]


class SocketWriter(Writer):
    """Writer that outputs data to either a UDP socket or a Unix Domain socket."""

    def __init__(self, config: Config) -> None:
        super().__init__()

        if config.is_global:
            self._logger.debug("initialize GlobalRegistry SocketWriter to %s (buffer_size=%s)",
                               config.location, config.buffer_size)
        else:
            self._logger.info("initialize SocketWriter to %s (buffer_size=%s)",
                              config.location, config.buffer_size)

        self._buffer: Optional[LineBuffer] = LineBuffer(config.buffer_size) if config.buffer_size > 0 else None
        self._lock = threading.Lock()
        self._sock: Optional[socket.socket] = None

        if "udp" in config.location:
            self._init_udp(config.location)
        else:
            self._init_unix(config.location)

        if self._buffer is not None:
            self._thread = threading.Thread(target=self._background_flush, daemon=True)
            self._logger.info("start SocketWriter background flush, every 5 seconds")
            self._thread.start()

    def _init_udp(self, location: str):
        parsed = urlparse(location)
        self._address: SocketAddress = (parsed.hostname, parsed.port)
        try:
            if self._address[0] is not None and type(ip_address(self._address[0])) is IPv6Address:
                self._family = socket.AF_INET6
            else:
                self._family = socket.AF_INET
        except ValueError:
            # anything that does not appear to be an IPv4 or IPv6 address (i.e. hostnames)
            self._family = socket.AF_INET

    def _init_unix(self, location: str):
        self._address = urlparse(location).path
        self._family = socket.AF_UNIX

    def _background_flush(self) -> None:
        while True:
            time.sleep(5)
            if self._buffer is None or self._sock is None:
                continue
            if len(self._buffer) > 0:
                with self._lock:
                    try:
                        self._sock.sendto(bytes(self._buffer.flush(), encoding="utf-8"), self._address)
                    except IOError:
                        self._logger.error("failed to write buffer from background flush")

    def _acquire_socket(self) -> None:
        # lazily instantiate the socket, in a thread-safe manner. this is necessary, because
        # the legacy GlobalRegistry will configure a SocketWriter (udp) upon `import spectator`.
        if self._sock is None:
            try:
                with self._lock:
                    if self._sock is None:
                        self._sock = socket.socket(family=self._family, type=socket.SOCK_DGRAM)
            except Exception as e:
                self._logger.error("exception during socket acquire: %s", e)

    def _write_buffer(self, line: str) -> None:
        if self._buffer is None or self._sock is None:
            return
        with self._lock:
            if self._buffer.append(line):
                try:
                    self._sock.sendto(bytes(self._buffer.flush(), encoding="utf-8"), self._address)
                except IOError:
                    self._logger.error("failed to write buffer, including line=%s", line)

    def _write_socket(self, line: str) -> None:
        if self._sock is None:
            return
        try:
            self._sock.sendto(bytes(line, encoding="utf-8"), self._address)
        except IOError:
            self._logger.error("failed to write line=%s", line)

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)
        self._acquire_socket()

        if self._buffer is not None:
            self._write_buffer(line)
        else:
            self._write_socket(line)

    def close(self) -> None:
        if self._sock is None:
            return
        self._sock.close()
