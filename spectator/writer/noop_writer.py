from typing import Optional

from spectator.config import Config
from spectator.writer import Writer


class NoopWriter(Writer):
    """Writer that does nothing. Used to disable output."""

    def __init__(self, config: Optional[Config] = None) -> None:
        super().__init__()
        if config is not None and config.is_global:
            self._logger.debug("initialize GlobalRegistry NoopWriter")
        else:
            self._logger.info("initialize NoopWriter")

    def write(self, line: str) -> None:
        self._logger.debug("write line=%s", line)

    def close(self) -> None:
        pass
