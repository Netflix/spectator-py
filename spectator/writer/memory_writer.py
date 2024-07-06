from spectator.writer import Writer
from typing import List


class MemoryWriter(Writer):
    """Writer that stores lines in a list, to support unit testing."""

    def __init__(self) -> None:
        super().__init__()
        self._logger.info("initialize MemoryWriter")
        self._messages = []

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)
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
