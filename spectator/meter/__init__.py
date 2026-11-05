import abc

from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion
from spectator.writer.noop_writer import NoopWriter


class Meter(metaclass=abc.ABCMeta):  # noqa: B024
    def __init__(
        self, meter_id: MeterId, writer: WriterUnion | None, meter_type_symbol: str
    ) -> None:
        self._id = meter_id
        self._meter_type_symbol = meter_type_symbol
        # a meter that is given no writer discards its updates
        self._writer: WriterUnion = writer if writer is not None else NoopWriter()

    def writer(self) -> WriterUnion:
        return self._writer
