import abc
import logging

from spectator.meter.id import Id
from spectator.writer.new_writer import WriterUnion


class Meter(metaclass=abc.ABCMeta):
    def __init__(self, id: Id, writer: WriterUnion, meter_type_symbol: str) -> None:
        self._id = id
        self._logger = logging.getLogger("spectator.meter")
        self._meter_type_symbol = meter_type_symbol
        self._writer = writer

    def writer(self) -> WriterUnion:
        return self._writer
