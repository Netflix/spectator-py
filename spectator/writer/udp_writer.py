import socket
from ipaddress import ip_address, IPv6Address
from typing import Tuple

from spectator.writer import Writer


class UdpWriter(Writer):
    """Writer that outputs data to a UDP socket."""

    def __init__(self, location: str, address: Tuple[str, int]) -> None:
        super().__init__()
        self._logger.info("initialize UdpWriter to %s", location)
        self._address = address

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
            with socket.socket(self._family, socket.SOCK_DGRAM) as s:
                s.sendto(bytes(line, encoding="utf-8"), self._address)
        except IOError:
            self._logger.error("failed to write line=%s", line)

    def close(self) -> None:
        pass
