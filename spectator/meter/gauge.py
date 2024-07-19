from typing import Optional

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import new_writer, WriterUnion


class Gauge(Meter):
    """The value is a number that was sampled at a point in time. The default time-to-live (TTL)
    for gauges is 900 seconds (15 minutes) - they will continue reporting the last value set for
    this duration of time. An optional ttl_seconds may be set to control the lifespan of these
    values. SpectatorD enforces a minimum TTL of 5 seconds."""

    def __init__(self, meter_id: MeterId, writer: WriterUnion = new_writer("none"),
                 ttl_seconds: Optional[int] = None) -> None:
        if ttl_seconds is None:
            meter_type_symbol = "g"
        else:
            meter_type_symbol = f"g,{ttl_seconds}"
        super().__init__(meter_id, writer, meter_type_symbol)

    def set(self, value: float) -> None:
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value}"
        self._writer.write(line)
