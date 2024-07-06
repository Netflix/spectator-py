from spectator.meter import Meter
from spectator.meter.id import Id
from spectator.writer.new_writer import new_writer, WriterUnion


class Timer(Meter):
    """The value is the number of seconds that have elapsed for an event. A stopwatch method
    is available, which provides a context manager that can be used to automate recording the
    timing for a block of code using the `with` statement."""

    def __init__(self, id: Id, writer: WriterUnion= new_writer("none")) -> None:
        super().__init__(id, writer, "t")

    def record(self, seconds: float) -> None:
        if seconds >= 0:
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{seconds}"
            self._writer.write(line)
