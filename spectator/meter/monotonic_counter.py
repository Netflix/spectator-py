from spectator.meter import Meter
from spectator.meter.id import Id
from spectator.writer.new_writer import new_writer, WriterUnion


class MonotonicCounter(Meter):
    """The value is a monotonically increasing number. A minimum of two samples must be received
    in order for SpectatorD to calculate a delta value and report it to the backend."""

    def __init__(self, id: Id, writer: WriterUnion = new_writer("none")) -> None:
        super().__init__(id, writer, "C")

    def set(self, amount: float) -> None:
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{amount}"
        self._writer.write(line)
