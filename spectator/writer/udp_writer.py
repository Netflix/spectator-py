import socket
import threading
from ipaddress import ip_address, IPv6Address
from typing import Tuple

from spectator.writer import Writer


class UdpWriter(Writer):
    """Writer that outputs data to a UDP socket."""

    def __init__(self, location: str, address: Tuple[str, int]) -> None:
        super().__init__()
        self._logger.debug("initialize UdpWriter to %s", location)
        self._address = address
        self._lock = threading.Lock()
        self._sock = None

        try:
            if type(ip_address(self._address[0])) is IPv6Address:
                self._family = socket.AF_INET6
            else:
                self._family = socket.AF_INET
        except ValueError:
            # anything that does not appear to be an IPv4 or IPv6 address (i.e. hostnames)
            self._family = socket.AF_INET

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)

        try:
            # lazily instantiate the socket, in a thread-safe manner. this is necessary, because
            # the legacy GlobalRegistry will configure a UdpWriter upon `import spectator`.
            if self._sock is None:
                with self._lock:
                    if self._sock is None:
                        self._sock = socket.socket(family=self._family, type=socket.SOCK_DGRAM)

            self._sock.sendto(bytes(line, encoding="utf-8"), self._address)
        except IOError:
            self._logger.error("failed to write line=%s", line)
        except Exception as e:
            self._logger.error("exception during write: %s", e)

    def close(self) -> None:
        self._sock.close()
