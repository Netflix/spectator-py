from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import new_writer, WriterUnion


class Timer(Meter):
    """The value is the number of seconds that have elapsed for an event."""

    def __init__(self, meter_id: MeterId, writer: WriterUnion= new_writer("none")) -> None:
        super().__init__(meter_id, writer, "t")

    def record(self, seconds: float) -> None:
        if seconds >= 0:
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{seconds}"
            self._writer.write(line)
