import sys
from urllib.parse import unquote, urlparse

from spectator.config import Config
from spectator.writer import Writer


class FileWriter(Writer):
    """Writer that outputs data to a TextIO instance, which can be stdout, stderr,
    or a regular file."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._logger.info("initialize FileWriter to %s", config.location)

        if config.location == "stderr":
            self._file = sys.stderr
            self._owns_file = False
        elif config.location == "stdout":
            self._file = sys.stdout
            self._owns_file = False
        else:
            path = unquote(urlparse(config.location).path)
            # the writer owns this file for its lifetime and closes it in close()
            self._file = open(path, "a", encoding="utf-8")  # noqa: SIM115
            self._owns_file = True

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)
        try:
            # a single write call keeps lines from concurrent threads intact
            self._file.write(line + "\n")
        except OSError:
            self._logger.error("failed to write line=%s", line)
        except ValueError:
            # writes after close are no-ops; UnicodeEncodeError is also a ValueError
            if not self._file.closed:
                raise

    def close(self) -> None:
        # stdout and stderr are not owned by this writer, so only flush them
        if self._owns_file:
            self._file.close()
        else:
            self._file.flush()
