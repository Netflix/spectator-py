from spectator.writer import Writer
from typing import TextIO


class FileWriter(Writer):
    """Writer that outputs data to a TextIO instance, which can be stdout, stderr, a unix domain
    socket, or a regular file."""

    def __init__(self, location: str, file: TextIO) -> None:
        super().__init__()
        self._logger.info("initialize FileWriter to %s", location)
        self._file = file

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)
        try:
            print(line, file=self._file)
        except IOError:
            self._logger.error("failed to write line=%s", line)

    def close(self) -> None:
        self._file.close()
