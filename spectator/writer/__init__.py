import abc
import logging


class Writer(metaclass=abc.ABCMeta):
    def __init__(self):
        self._logger = logging.getLogger("spectator.writer")

    @abc.abstractmethod
    def write(self, line: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError
