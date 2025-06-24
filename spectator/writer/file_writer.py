import sys
from urllib.parse import urlparse

from spectator.writer import Writer


class FileWriter(Writer):
    """Writer that outputs data to a TextIO instance, which can be stdout, stderr,
    or a regular file."""

    def __init__(self, location: str) -> None:
        super().__init__()
        self._logger.info("initialize FileWriter to %s", location)

        if location == "stderr":
            self._file = sys.stderr
        elif location == "stdout":
            self._file = sys.stdout
        else:
            self._file = open(urlparse(location).path, "a", encoding="utf-8")

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)
        try:
            print(line, file=self._file)
        except IOError:
            self._logger.error("failed to write line=%s", line)

    def close(self) -> None:
        self._file.close()
