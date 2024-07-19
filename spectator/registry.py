import logging
from typing import Optional

from spectator.config import Config
from spectator.meter.age_gauge import AgeGauge
from spectator.meter.counter import Counter
from spectator.meter.dist_summary import DistributionSummary
from spectator.meter.gauge import Gauge
from spectator.meter.max_gauge import MaxGauge
from spectator.meter.meter_id import MeterId
from spectator.meter.monotonic_counter import MonotonicCounter
from spectator.meter.monotonic_counter_uint import MonotonicCounterUint
from spectator.meter.percentile_dist_summary import PercentileDistributionSummary
from spectator.meter.percentile_timer import PercentileTimer
from spectator.meter.timer import Timer
from spectator.writer.new_writer import new_writer, WriterUnion


class Registry:
    """Registry is the main entry point for interacting with the Spectator library."""

    def __init__(self, config: Config = Config()) -> None:
        self._config = config
        self._logger = logging.getLogger(__name__)
        self._writer = new_writer(config.location)
        self._logger.info("Create Registry with extra_common_tags=%s", config.extra_common_tags)

    def writer(self) -> WriterUnion:
        return self._writer

    def close(self) -> None:
        self._logger.info("Close Registry Writer")
        try:
            self._writer.close()
        except IOError:
            self._logger.error("Error closing Registry Writer")

    def new_id(self, name: str, tags: Optional[dict] = None) -> MeterId:
        """Create a new MeterId, which applies any configured extra common tags,
        and can be used as an input to the *_with_meter_id Registry methods."""
        if tags is None:
            tags = {}

        new_meter_id = MeterId(name, tags)

        if len(self._config.extra_common_tags) > 0:
            new_meter_id = new_meter_id.with_tags(self._config.extra_common_tags)

        return new_meter_id

    def age_gauge(self, name: str, tags: Optional[dict] = None) -> AgeGauge:
        return AgeGauge(self.new_id(name, tags), self._writer)

    def age_gauge_with_meter_id(self, meter_id: MeterId) -> AgeGauge:
        return AgeGauge(meter_id, self._writer)

    def counter(self, name: str, tags: Optional[dict] = None) -> Counter:
        return Counter(self.new_id(name, tags), self._writer)

    def counter_with_meter_id(self, meter_id: MeterId) -> Counter:
        return Counter(meter_id, self._writer)

    def distribution_summary(self, name: str, tags: Optional[dict] = None) -> DistributionSummary:
        return DistributionSummary(self.new_id(name, tags), self._writer)

    def distribution_summary_with_meter_id(self, meter_id: MeterId) -> DistributionSummary:
        return DistributionSummary(meter_id, self._writer)

    def gauge(self, name: str, tags: Optional[dict] = None, ttl_seconds: Optional[int] = None) -> Gauge:
        return Gauge(self.new_id(name, tags), self._writer, ttl_seconds)

    def gauge_with_meter_id(self, meter_id: MeterId, ttl_seconds: Optional[int] = None) -> Gauge:
        return Gauge(meter_id, self._writer, ttl_seconds)

    def max_gauge(self, name: str, tags: Optional[dict] = None) -> MaxGauge:
        return MaxGauge(self.new_id(name, tags), self._writer)

    def max_gauge_with_meter_id(self, meter_id: MeterId) -> MaxGauge:
        return MaxGauge(meter_id, self._writer)

    def monotonic_counter(self, name: str, tags: Optional[dict] = None) -> MonotonicCounter:
        return MonotonicCounter(self.new_id(name, tags), self._writer)

    def monotonic_counter_with_meter_id(self, meter_id: MeterId) -> MonotonicCounter:
        return MonotonicCounter(meter_id, self._writer)

    def monotonic_counter_uint(self, name: str, tags: Optional[dict] = None) -> MonotonicCounterUint:
        return MonotonicCounterUint(self.new_id(name, tags), self._writer)

    def monotonic_counter_uint_with_meter_id(self, meter_id: MeterId) -> MonotonicCounterUint:
        return MonotonicCounterUint(meter_id, self._writer)

    def pct_distribution_summary(self, name: str, tags: Optional[dict] = None) -> PercentileDistributionSummary:
        return PercentileDistributionSummary(self.new_id(name, tags), self._writer)

    def pct_distribution_summary_with_meter_id(self, meter_id: MeterId) -> PercentileDistributionSummary:
        return PercentileDistributionSummary(meter_id, self._writer)

    def pct_timer(self, name: str, tags: Optional[dict] = None) -> PercentileTimer:
        return PercentileTimer(self.new_id(name, tags), self._writer)

    def pct_timer_with_meter_id(self, meter_id: MeterId) -> PercentileTimer:
        return PercentileTimer(meter_id, self._writer)

    def timer(self, name: str, tags: Optional[dict] = None) -> Timer:
        return Timer(self.new_id(name, tags), self._writer)

    def timer_with_meter_id(self, meter_id: MeterId) -> Timer:
        return Timer(meter_id, self._writer)
