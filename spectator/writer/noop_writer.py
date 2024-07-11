from spectator.writer import Writer


class NoopWriter(Writer):
    """Writer that does nothing. Used to disable output."""

    def __init__(self) -> None:
        super().__init__()
        self._logger.info("initialize NoopWriter")

    def write(self, line: str) -> None:
        pass

    def close(self) -> None:
        pass
