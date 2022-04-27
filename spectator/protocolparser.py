from typing import Tuple, Type

from spectator.counter import Counter, MonotonicCounter
from spectator.distsummary import DistributionSummary
from spectator.gauge import AgeGauge, Gauge, MaxGauge
from spectator.id import MeterId
from spectator.sidecarmeter import SidecarMeter
from spectator.timer import Timer

# https://github.com/Netflix-Skunkworks/spectatord#metric-types
_METER_CLASS_MAP = {
    'c': Counter,
    'd': DistributionSummary,
    'g': Gauge,
    'm': MaxGauge,
    't': Timer,
    'A': AgeGauge,
    'C': MonotonicCounter,
    'D': DistributionSummary,
    'T': Timer
}


def parse_protocol_line(line: str) -> Tuple[Type[SidecarMeter], MeterId, str]:
    """Parse SpectatorD protocol lines and return a Tuple of data which can be used to validate
    that the line matches expectations in tests."""
    meter_type, meter_id, value = line.split(":")

    meter_class = _METER_CLASS_MAP.get(meter_type.split(",")[0])

    meter_id = meter_id.split(",")
    name = meter_id[0]
    tags = {}

    for tag in meter_id[1:]:
        k, v = tag.split("=")
        tags[k] = v

    return meter_class, MeterId(name, tags), value
