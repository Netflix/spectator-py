from typing import Optional

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion
from spectator.writer.noop_writer import NoopWriter


class MaxGauge(Meter):
    """The value is a number that was sampled at a point in time, but it is reported as a maximum
    gauge value to the backend."""

    def __init__(self, meter_id: MeterId, writer: Optional[WriterUnion] = None) -> None:
        if writer is None:
            writer = NoopWriter()

        super().__init__(meter_id, writer, "m")

    def set(self, value: float) -> None:
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value}"
        self._writer.write(line)
