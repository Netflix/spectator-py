import socket
from typing import Tuple


class UdpServer:

    def __init__(self, address: Tuple[str, int] = ("127.0.0.1", 0)) -> None:
        self._sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self._sock.bind(address)

    def address(self) -> str:
        hostname, port = self._sock.getsockname()
        return "udp://{}:{}".format(hostname, port)

    def read(self) -> str:
        data, _ = self._sock.recvfrom(1024)
        return data.decode(encoding="utf-8")

    def close(self) -> None:
        self._sock.close()
