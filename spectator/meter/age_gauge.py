from typing import Optional

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion
from spectator.writer.noop_writer import NoopWriter


class AgeGauge(Meter):
    """The value is the time in seconds since the epoch at which an event has successfully
    occurred, or 0 to use the current time in epoch seconds. After an Age Gauge has been set,
    it will continue reporting the number of seconds since the last time recorded, for as long
    as the SpectatorD process runs. This meter type makes it easy to implement the Time Since
    Last Success alerting pattern."""

    def __init__(self, meter_id: MeterId, writer: Optional[WriterUnion] = None) -> None:
        if writer is None:
            writer = NoopWriter()

        super().__init__(meter_id, writer, "A")

    def now(self) -> None:
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:0"
        self._writer.write(line)

    def set(self, seconds: int) -> None:
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{seconds}"
        self._writer.write(line)
