from spectator.config import Config
from spectator.registry import Registry

from spectator.clock import Clock, SystemClock, ManualClock
from spectator.protocol_parser import get_meter_class, parse_protocol_line
from spectator.stopwatch import StopWatch

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId

from spectator.meter.age_gauge import AgeGauge
from spectator.meter.counter import Counter
from spectator.meter.dist_summary import DistributionSummary
from spectator.meter.gauge import Gauge
from spectator.meter.max_gauge import MaxGauge
from spectator.meter.monotonic_counter import MonotonicCounter
from spectator.meter.monotonic_counter_uint import MonotonicCounterUint
from spectator.meter.percentile_dist_summary import PercentileDistributionSummary
from spectator.meter.percentile_timer import PercentileTimer
from spectator.meter.timer import Timer

from spectator.writer import Writer
from spectator.writer.new_writer import new_writer, WriterUnion

from spectator.writer.file_writer import FileWriter
from spectator.writer.memory_writer import MemoryWriter
from spectator.writer.noop_writer import NoopWriter
from spectator.writer.udp_writer import UdpWriter

# DEPRECATED: The GlobalRegistry construct is no longer necessary, since this library became a thin
# client implementation, but it was kept to help minimize the work associated with adopting the new
# version of this library. The previous advice for using this library offered many examples like the
# following:
#
#   from spectator import GlobalRegistry
#
#   GlobalRegistry.counter("server.numRequests").increment()
#
# Now, with the thin client version, this library is stateless. You can have one or more Registry
# objects in your code, and the preferred method of using it is as follows:
#
#   from spectator import Registry
#
#   r = Registry()
#   r.counter("server.numRequests").increment()
#
# Using this method of instantiating the Registry offers you the opportunity to provide an alternate
# configuration, to supply a different output location or a set of extra common tags. Or, keep the
# defaults and use the Registry as-is.

GlobalRegistry = Registry()
