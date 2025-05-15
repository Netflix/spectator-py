import os
import random
import socket


class UnixServer:

    def __init__(self, path: str = f"/tmp/spectatord-test-{random.randint(1, 10000)}") -> None:
        if os.path.exists(path):
            os.remove(path)
        self._path = path
        self._sock = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
        self._sock.bind(path)

    def address(self) -> str:
        return "unix://{}".format(self._path)

    def read(self) -> str:
        data, _ = self._sock.recvfrom(1024)
        return data.decode(encoding="utf-8")

    def close(self) -> None:
        self._sock.close()
        os.remove(self._path)
