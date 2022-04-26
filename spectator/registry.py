from typing import Optional

from spectator.clock import Clock, SystemClock
from spectator.counter import Counter, MonotonicCounter
from spectator.distsummary import DistributionSummary
from spectator.gauge import AgeGauge, Gauge, MaxGauge
from spectator.id import MeterId
from spectator.sidecarconfig import SidecarConfig
from spectator.sidecarwriter import SidecarWriter
from spectator.timer import Timer


class Registry:
    """Registry for reporting data to SpectatorD."""

    def __init__(self, clock: Clock = SystemClock(),
                 config: SidecarConfig = SidecarConfig()) -> None:
        self._clock = clock
        self._common_tags = config.common_tags()
        self._writer = SidecarWriter.create(config.output_location())

    def _merge_common_tags(self, meter_id: MeterId) -> MeterId:
        return meter_id if len(self._common_tags) == 0 else meter_id.with_tags(self._common_tags)

    def _new_meter(self, name: str, tags: Optional[dict] = None) -> MeterId:
        if tags is None:
            tags = {}
        return self._merge_common_tags(MeterId(name, tags))

    def clock(self) -> Clock:
        return self._clock

    def close(self) -> None:
        self._writer.close()

    def age_gauge(self, name: str, tags: Optional[dict] = None) -> AgeGauge:
        return AgeGauge(self._new_meter(name, tags), writer=self._writer)

    def counter(self, name: str, tags: Optional[dict] = None) -> Counter:
        return Counter(self._new_meter(name, tags), writer=self._writer)

    def distribution_summary(self, name: str, tags: Optional[dict] = None) -> DistributionSummary:
        return DistributionSummary(self._new_meter(name, tags), writer=self._writer)

    def pct_distribution_summary(self, name: str,
                                 tags: Optional[dict] = None) -> DistributionSummary:
        return DistributionSummary(self._new_meter(name, tags), meter_type="D", writer=self._writer)

    def gauge(self, name: str, tags: Optional[dict] = None,
              ttl_seconds: Optional[int] = None) -> Gauge:
        return Gauge(self._new_meter(name, tags), ttl_seconds=ttl_seconds, writer=self._writer)

    def max_gauge(self, name: str, tags: Optional[dict] = None) -> MaxGauge:
        return MaxGauge(self._new_meter(name, tags), writer=self._writer)

    def monotonic_counter(self, name: str, tags: Optional[dict] = None) -> MonotonicCounter:
        return MonotonicCounter(self._new_meter(name, tags), writer=self._writer)

    def timer(self, name: str, tags: Optional[dict] = None) -> Timer:
        return Timer(self._new_meter(name, tags), clock=self._clock, writer=self._writer)

    def pct_timer(self, name: str, tags: Optional[dict] = None) -> Timer:
        return Timer(self._new_meter(name, tags), clock=self._clock, meter_type="T",
                     writer=self._writer)

    def start(self, config: Optional[dict] = None) -> None:
        """Avoid breaking the API."""

    def clear_meters_and_start(self) -> None:
        """Avoid breaking the API."""

    def stop(self) -> None:
        """Avoid breaking the API."""

    def stop_without_publish(self) -> None:
        """Avoid breaking the API."""

    def __iter__(self) -> "RegistryIterator":
        """Avoid breaking the API."""
        return RegistryIterator([])


class RegistryIterator:
    """Avoid breaking the API."""

    def __init__(self, meters):
        pass

    def __next__(self):
        raise StopIteration
