from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import new_writer, WriterUnion


class MaxGauge(Meter):
    """The value is a number that was sampled at a point in time, but it is reported as a maximum
    gauge value to the backend."""

    def __init__(self, meter_id: MeterId, writer: WriterUnion = new_writer("none")) -> None:
        super().__init__(meter_id, writer, "m")

    def set(self, value: float) -> None:
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value}"
        self._writer.write(line)
