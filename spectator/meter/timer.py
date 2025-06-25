from typing import Optional

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion
from spectator.writer.noop_writer import NoopWriter


class Timer(Meter):
    """The value is the number of seconds that have elapsed for an event."""

    def __init__(self, meter_id: MeterId, writer: Optional[WriterUnion] = None) -> None:
        if writer is None:
            writer = NoopWriter()

        super().__init__(meter_id, writer, "t")

    def record(self, seconds: float) -> None:
        if seconds >= 0:
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{seconds}"
            self._writer.write(line)
