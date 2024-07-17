from typing import Tuple, Type

from spectator.meter import Meter
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

# https://netflix.github.io/atlas-docs/spectator/agent/usage/#metric-types
_METER_CLASSES = {
    'A': AgeGauge,
    'c': Counter,
    'd': DistributionSummary,
    'g': Gauge,
    'm': MaxGauge,
    'C': MonotonicCounter,
    'U': MonotonicCounterUint,
    'D': PercentileDistributionSummary,
    'T': PercentileTimer,
    't': Timer,
}


def get_meter_class(symbol: str) -> Type[Meter]:
    return _METER_CLASSES.get(symbol)


def parse_protocol_line(line: str) -> Tuple[str, MeterId, str]:
    """Parse a SpectatorD protocol line into component parts. Utility exposed for testing."""
    symbol, id, value = line.split(":")
    # remove optional parts, such as gauge ttls
    symbol = symbol.split(",")[0]
    id = id.split(",")
    name = id[0]

    tags = {}
    for tag in id[1:]:
        k, v = tag.split("=")
        tags[k] = v

    return symbol, MeterId(name, tags), value
