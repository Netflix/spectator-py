from spectator import Clock
from spectator.timer import StopWatch
from spectator.registry import Registry

from typing import Dict, Optional


class PercentileBuckets:
    """Avoid breaking the API."""

    @staticmethod
    def get(i) -> int:
        return 0

    @staticmethod
    def length() -> int:
        return 0

    @staticmethod
    def index_of(v) -> int:
        return 0

    @staticmethod
    def bucket(v) -> int:
        return 0

    @staticmethod
    def percentiles(counts, pcts, results) -> None:
        pass

    @staticmethod
    def percentile(counts, p) -> float:
        return 0


class PercentileTimer:
    """
    This class is deprecated, but it is retained to avoid breaking the API.

    Uses of this class should be replaced with direct use of the Registry helper method:

    from spectator import GlobalRegistry

    GlobalRegistry.pct_timer("server.requestLatency").record(0.01)
    """

    def __init__(self, registry: Registry, name: str, tags: Optional[Dict[str, str]] = None,
                 min: float = 0, max: float = 0) -> None:
        if tags is None:
            tags = {}
        self._clock = registry.clock()
        self._pct_timer = registry.pct_timer(name, tags)

    def record(self, amount: float) -> None:
        self._pct_timer.record(amount)

    def stopwatch(self) -> StopWatch:
        return StopWatch(self)

    def clock(self) -> Clock:
        return self._clock

    @staticmethod
    def count() -> int:
        return 0

    @staticmethod
    def total_time() -> float:
        return 0

    @staticmethod
    def percentile(p) -> float:
        return 0


class PercentileDistributionSummary:
    """
    This class is deprecated, but it is retained to avoid breaking the API.

    Uses of this class should be replaced with direct use of the Registry helper method:

    from spectator import GlobalRegistry

    GlobalRegistry.pct_distribution_summary("server.requestSize").record(10)
    """

    def __init__(self, registry: Registry, name: str, tags: Optional[Dict[str, str]] = None,
                 min: int = 0, max: int = 0) -> None:
        if tags is None:
            tags = {}
        self._pct_distsummary = registry.pct_distribution_summary(name, tags)

    def record(self, amount) -> None:
        self._pct_distsummary.record(amount)

    @staticmethod
    def count() -> int:
        return 0

    @staticmethod
    def total_amount() -> int:
        return 0

    @staticmethod
    def percentile(p) -> int:
        return 0
