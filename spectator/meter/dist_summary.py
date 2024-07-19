from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import new_writer, WriterUnion


class DistributionSummary(Meter):
    """The value tracks the distribution of events. It is similar to a Timer, but more general,
    because the size does not have to be a period of time. For example, it can be used to
    measure the payload sizes of requests hitting a server or the number of records returned
    from a query."""

    def __init__(self, meter_id: MeterId, writer: WriterUnion = new_writer("none")) -> None:
        super().__init__(meter_id, writer, "d")

    def record(self, amount: int) -> None:
        if amount >= 0:
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{amount}"
            self._writer.write(line)
