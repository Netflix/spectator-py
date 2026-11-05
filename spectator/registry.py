import logging

from spectator.common_tags import validate_tags
from spectator.config import Config
from spectator.meter.age_gauge import AgeGauge
from spectator.meter.counter import Counter
from spectator.meter.dist_summary import DistributionSummary
from spectator.meter.distinct_count_sketch import DistinctCountSketch
from spectator.meter.gauge import Gauge
from spectator.meter.max_gauge import MaxGauge
from spectator.meter.meter_id import MeterId
from spectator.meter.monotonic_counter import MonotonicCounter
from spectator.meter.monotonic_counter_uint import MonotonicCounterUint
from spectator.meter.percentile_dist_summary import PercentileDistributionSummary
from spectator.meter.percentile_timer import PercentileTimer
from spectator.meter.timer import Timer
from spectator.writer.new_writer import WriterUnion, new_writer


class Registry:
    """Registry is the main entry point for interacting with the Spectator library."""

    def __init__(self, config: Config | None = None) -> None:
        if config is None:
            config = Config()
        self._logger = logging.getLogger(__name__)
        self._config = config
        if config.is_global:
            self._logger.debug(
                "Create GlobalRegistry with extra_common_tags=%s",
                config.extra_common_tags,
            )
        else:
            self._logger.info(
                "Create Registry with extra_common_tags=%s", config.extra_common_tags
            )

        self._writer = new_writer(config)

    def writer(self) -> WriterUnion:
        return self._writer

    def close(self) -> None:
        self._logger.debug("Close Registry Writer")
        try:
            self._writer.close()
        except OSError:
            self._logger.error("Error closing Registry Writer")

    def new_id(self, name: str, tags: dict | None = None) -> MeterId:
        """Create a new MeterId, which applies any configured extra common tags,
        and can be used as an input to the *_with_id Registry methods."""
        common_tags = self._config.extra_common_tags
        if not common_tags:
            return MeterId(name, tags)
        if tags is None:
            return MeterId(name, common_tags)

        merged_tags = validate_tags(tags)
        if merged_tags == tags:
            # nothing is dropped from tags, so add the common tags and build the id once
            merged_tags.update(common_tags)
            return MeterId(name, merged_tags)

        # MeterId warns about the tags it drops, and that warning names only the caller's tags
        return MeterId(name, tags).with_tags(common_tags)

    def age_gauge(self, name: str, tags: dict | None = None) -> AgeGauge:
        return AgeGauge(self.new_id(name, tags), self._writer)

    def age_gauge_with_id(self, meter_id: MeterId) -> AgeGauge:
        return AgeGauge(meter_id, self._writer)

    def counter(self, name: str, tags: dict | None = None) -> Counter:
        return Counter(self.new_id(name, tags), self._writer)

    def counter_with_id(self, meter_id: MeterId) -> Counter:
        return Counter(meter_id, self._writer)

    def distribution_summary(
        self, name: str, tags: dict | None = None
    ) -> DistributionSummary:
        return DistributionSummary(self.new_id(name, tags), self._writer)

    def distribution_summary_with_id(self, meter_id: MeterId) -> DistributionSummary:
        return DistributionSummary(meter_id, self._writer)

    def distinct_count_sketch(
        self, name: str, tags: dict | None = None
    ) -> DistinctCountSketch:
        return DistinctCountSketch(self.new_id(name, tags), self._writer)

    def distinct_count_sketch_with_id(self, meter_id: MeterId) -> DistinctCountSketch:
        return DistinctCountSketch(meter_id, self._writer)

    def gauge(
        self, name: str, tags: dict | None = None, ttl_seconds: int | None = None
    ) -> Gauge:
        return Gauge(self.new_id(name, tags), self._writer, ttl_seconds)

    def gauge_with_id(self, meter_id: MeterId, ttl_seconds: int | None = None) -> Gauge:
        return Gauge(meter_id, self._writer, ttl_seconds)

    def max_gauge(self, name: str, tags: dict | None = None) -> MaxGauge:
        return MaxGauge(self.new_id(name, tags), self._writer)

    def max_gauge_with_id(self, meter_id: MeterId) -> MaxGauge:
        return MaxGauge(meter_id, self._writer)

    def monotonic_counter(
        self, name: str, tags: dict | None = None
    ) -> MonotonicCounter:
        return MonotonicCounter(self.new_id(name, tags), self._writer)

    def monotonic_counter_with_id(self, meter_id: MeterId) -> MonotonicCounter:
        return MonotonicCounter(meter_id, self._writer)

    def monotonic_counter_uint(
        self, name: str, tags: dict | None = None
    ) -> MonotonicCounterUint:
        return MonotonicCounterUint(self.new_id(name, tags), self._writer)

    def monotonic_counter_uint_with_id(self, meter_id: MeterId) -> MonotonicCounterUint:
        return MonotonicCounterUint(meter_id, self._writer)

    def pct_distribution_summary(
        self, name: str, tags: dict | None = None
    ) -> PercentileDistributionSummary:
        return PercentileDistributionSummary(self.new_id(name, tags), self._writer)

    def pct_distribution_summary_with_id(
        self, meter_id: MeterId
    ) -> PercentileDistributionSummary:
        return PercentileDistributionSummary(meter_id, self._writer)

    def pct_timer(self, name: str, tags: dict | None = None) -> PercentileTimer:
        return PercentileTimer(self.new_id(name, tags), self._writer)

    def pct_timer_with_id(self, meter_id: MeterId) -> PercentileTimer:
        return PercentileTimer(meter_id, self._writer)

    def timer(self, name: str, tags: dict | None = None) -> Timer:
        return Timer(self.new_id(name, tags), self._writer)

    def timer_with_id(self, meter_id: MeterId) -> Timer:
        return Timer(meter_id, self._writer)
