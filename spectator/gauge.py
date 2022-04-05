from typing import Optional

from spectator.id import MeterId
from spectator.sidecarmeter import SidecarMeter
from spectator.sidecarwriter import SidecarWriter


class Gauge(SidecarMeter):
    """The value is a number that was sampled at a point in time. The default time-to-live (TTL)
    for gauges is 900 seconds (15 minutes) - they will continue reporting the last value set for
    this duration of time. An optional ttl_seconds may be set to control the lifespan of these
    values. SpectatorD enforces a minimum ttl of 5 seconds."""

    def __init__(self, meter_id: MeterId, ttl_seconds: Optional[int] = None,
                 writer: SidecarWriter = SidecarWriter.create("none")) -> None:
        if ttl_seconds is None:
            meter_type = "g"
        else:
            meter_type = "g,{}".format(ttl_seconds)
        super().__init__(meter_id, meter_type)
        self._writer = writer

    def set(self, value: float) -> None:
        self._writer.write(self.idString, value)

    @staticmethod
    def get() -> float:
        """Avoid breaking the API."""
        return 0


class AgeGauge(SidecarMeter):
    """The value is the time in seconds since the epoch at which an event has successfully
    occurred, or 0 to use the current time in epoch seconds. After an Age Gauge has been set,
    it will continue reporting the number of seconds since the last time recorded, for as long
    as the SpectatorD process runs. This meter type makes it easy to implement the Time Since
    Last Success alerting pattern."""

    def __init__(self, meter_id: MeterId,
                 writer: SidecarWriter = SidecarWriter.create("none")) -> None:
        super().__init__(meter_id, "A")
        self._writer = writer

    def set(self, seconds: int) -> None:
        self._writer.write(self.idString, seconds)


class MaxGauge(SidecarMeter):
    """The value is a number that was sampled at a point in time, but it is reported as a maximum
    gauge value to the backend."""

    def __init__(self, meter_id: MeterId,
                 writer: SidecarWriter = SidecarWriter.create("none")) -> None:
        super().__init__(meter_id, "m")
        self._writer = writer

    def set(self, value: float) -> None:
        self._writer.write(self.idString, value)
