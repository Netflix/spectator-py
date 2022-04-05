from spectator.id import MeterId
from spectator.sidecarmeter import SidecarMeter
from spectator.sidecarwriter import SidecarWriter


class DistributionSummary(SidecarMeter):
    """The value tracks the distribution of events. It is similar to a Timer, but more general,
    because the size does not have to be a period of time. For example, it can be used to
    measure the payload sizes of requests hitting a server or the number of records returned
    from a query.

    Two types are available: (1) standard distribution summaries, with a meter type of "d", and (2)
    percentile distribution summaries, with a meter type of "D". The standard distribution summaries
    are the default.

    In order to maintain the data distribution, Percentile Distribution Summaries have a higher
    storage cost, with a worst-case of up to 300X that of a standard Distribution Summary. Be
    diligent about any additional dimensions added to Percentile Distribution Summaries and ensure
    that they have a small bounded cardinality."""

    def __init__(self, meter_id: MeterId, meter_type: str = "d",
                 writer: SidecarWriter = SidecarWriter.create("none")) -> None:
        if meter_type not in ["d", "D"]:
            raise ValueError("Distribution Summaries must have a meter type of 'd' or 'D'.")
        super().__init__(meter_id, meter_type)
        self._writer = writer

    def record(self, amount: int) -> None:
        if amount >= 0:
            self._writer.write(self.idString, amount)

    @staticmethod
    def count() -> int:
        """Avoid breaking the API."""
        return 0

    @staticmethod
    def total_amount() -> int:
        """Avoid breaking the API."""
        return 0
