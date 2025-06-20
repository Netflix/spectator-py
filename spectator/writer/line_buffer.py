from typing import List


class LineBuffer:
    """Line buffer for Writers."""

    def __init__(self, max_size: int) -> None:
        self._size: int = 0
        self._max_size: int = max_size
        self._lines: List[str] = []

    def __len__(self) -> int:
        return self._size

    def append(self, line: str) -> bool:
        """Return value indicates whether the buffer should be flushed."""
        self._lines.append(line)
        self._size += len(line)
        return self._size >= self._max_size

    def flush(self) -> str:
        lines = "\n".join(self._lines)
        self._lines = []
        self._size = 0
        return lines
