from spectator.writer import Writer


class NoopWriter(Writer):
    """Writer that does nothing. Used to disable output."""

    def __init__(self) -> None:
        super().__init__()
        self._logger.debug("initialize NoopWriter")

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)

    def close(self) -> None:
        pass
