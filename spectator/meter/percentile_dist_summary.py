from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import new_writer, WriterUnion


class PercentileDistributionSummary(Meter):
    """The value tracks the distribution of events. It is similar to a Timer, but more general,
    because the size does not have to be a period of time. For example, it can be used to
    measure the payload sizes of requests hitting a server or the number of records returned
    from a query.

    In order to maintain the data distribution, Percentile Distribution Summaries have a higher
    storage cost, with a worst-case of up to 300X that of a standard Distribution Summary. Be
    diligent about any additional dimensions added to Percentile Distribution Summaries and ensure
    that they have a small bounded cardinality."""

    def __init__(self, meter_id: MeterId, writer: WriterUnion = new_writer("none")) -> None:
        super().__init__(meter_id, writer, "D")

    def record(self, amount: int) -> None:
        if amount >= 0:
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{amount}"
            self._writer.write(line)
