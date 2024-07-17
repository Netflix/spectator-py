from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import new_writer, WriterUnion


class PercentileTimer(Meter):
    """The value is the number of seconds that have elapsed for an event. A stopwatch method
    is available, which provides a context manager that can be used to automate recording the
    timing for a block of code using the `with` statement.

    In order to maintain the data distribution, Percentile Timers have a higher storage cost,
    with a worst-case of up to 300X that of a standard Timer. Be diligent about any additional
    dimensions added to Percentile Timers and ensure that they have a small bounded cardinality."""

    def __init__(self, meter_id: MeterId, writer: WriterUnion = new_writer("none")) -> None:
        super().__init__(meter_id, writer, "T")

    def record(self, seconds: float) -> None:
        if seconds >= 0:
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{seconds}"
            self._writer.write(line)
