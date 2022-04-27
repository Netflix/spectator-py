import logging
import socket
import sys
from typing import List, TextIO, Tuple, Union
from urllib.parse import urlparse


class SidecarWriter:
    """Base type for a writer that accepts the SpectatorD line protocol. The concrete
    implementations must exist in this module to avoid circular imports."""

    def __init__(self, location: str):
        self._location = location
        self._logger = logging.getLogger("spectator.SidecarWriter")
        self._debug = None

    @staticmethod
    def create(location: str) -> "SidecarWriter":
        """Create a new writer based on a location string."""
        if location == "none":
            return NoopWriter()
        elif location == "memory":
            return MemoryWriter()
        elif location == "stderr":
            return PrintWriter(location, sys.stderr)
        elif location == "stdout":
            return PrintWriter(location, sys.stdout)
        elif location.startswith("file://"):
            # expects: file:///path/to/file
            file = open(urlparse(location).path, "a", encoding="utf-8")
            return PrintWriter(location, file)
        elif location.startswith("udp://"):
            parsed = urlparse(location)
            address = (parsed.hostname, int(parsed.port))
            return UdpWriter(location, address)
        else:
            raise ValueError("unsupported location: {}".format(location))

    def write_impl(self, line: str) -> None:
        """Custom writers should override this method."""
        raise NotImplementedError("use a concrete implementation")

    def write_line(self, line: str) -> None:
        if self._debug is None:
            # on the first write, cache the log level to speed up later comparisons
            self._debug = self._logger.isEnabledFor(logging.DEBUG)
        try:
            if self._debug:
                # when enabled, this log line reduces udp socket performance by 10%
                self._logger.debug("writing to %s: %s", self._location, line)
            self.write_impl(line)
        except IOError:
            self._logger.warning("write to %s failed: %s", self._location, line)

    def write(self, prefix: str, value: Union[int, float]) -> None:
        self.write_line(prefix + str(value))

    def close(self) -> None:
        """Custom writers should override this method."""
        raise NotImplementedError("use a concrete implementation")


class MemoryWriter(SidecarWriter):
    """Writer that stores data in a list, to support unit testing."""

    def __init__(self) -> None:
        super().__init__("memory")
        self._messages = []

    def write_impl(self, line: str) -> None:
        self._messages.append(line)

    def close(self) -> None:
        self._messages.clear()

    def get(self) -> List[str]:
        return self._messages

    def clear(self) -> None:
        self._messages.clear()

    def is_empty(self) -> bool:
        return len(self._messages) == 0

    def last_line(self) -> str:
        return self._messages[-1]


class NoopWriter(SidecarWriter):
    """Writer that does nothing. Used to disable output."""

    def __init__(self):
        super().__init__("none")

    def write_impl(self, line: str) -> None:
        pass

    def close(self) -> None:
        pass


class PrintWriter(SidecarWriter):
    """Writer that outputs data to a TextIO instance."""

    def __init__(self, location: str, file: TextIO) -> None:
        super().__init__(location)
        self._file = file

    def write_impl(self, line: str) -> None:
        print(line, file=self._file)

    def close(self) -> None:
        self._file.close()


class UdpWriter(SidecarWriter):
    """Writer that outputs data to UDP socket."""

    def __init__(self, location: str, address: Tuple[str, int]) -> None:
        super().__init__(location)
        self._address = address
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.connect(self._address)

    def write_impl(self, line: str) -> None:
        self._sock.send(bytes(line, encoding="utf-8"))

    def close(self) -> None:
        self._sock.close()
