import socket
import threading

from spectator.writer import Writer


class UnixWriter(Writer):
    """Writer that outputs data to a Unix Domain Socket."""

    def __init__(self, location: str) -> None:
        super().__init__()
        self._logger.debug("initialize UnixWriter to %s", location)
        self._location = location
        self._lock = threading.Lock()
        self._sock = None

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)

        try:
            # lazily instantiate the socket, in a thread-safe manner
            if self._sock is None:
                with self._lock:
                    if self._sock is None:
                        self._sock = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)

            self._sock.sendto(bytes(line, encoding="utf-8"), self._location)
        except IOError:
            self._logger.error("failed to write line=%s", line)
        except Exception as e:
            self._logger.error("exception during write: %s", e)

    def close(self) -> None:
        self._sock.close()
