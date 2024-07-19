from typing import Union

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import new_writer, WriterUnion


class Counter(Meter):
    """The value is the number of increments that have occurred since the last time it was
    recorded. The value will be reported to the Atlas backend as a rate-per-second."""

    def __init__(self, meter_id: MeterId, writer: WriterUnion = new_writer("none")) -> None:
        super().__init__(meter_id, writer, "c")

    def increment(self, delta: Union[int, float] = 1) -> None:
        if delta > 0:
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{delta}"
            self._writer.write(line)
