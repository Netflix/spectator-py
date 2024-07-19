import abc

from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion


class Meter(metaclass=abc.ABCMeta):
    def __init__(self, meter_id: MeterId, writer: WriterUnion, meter_type_symbol: str) -> None:
        self._id = meter_id
        self._meter_type_symbol = meter_type_symbol
        self._writer = writer

    def writer(self) -> WriterUnion:
        return self._writer
