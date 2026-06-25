import base64
import logging
from typing import Optional, Union

from spectator.meter import Meter
from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion
from spectator.writer.noop_writer import NoopWriter


class DistinctCountSketch(Meter):
    """Estimates the number of distinct values recorded during a step interval, such as the number
    of unique users, device ids, or source IPs, using a HyperLogLog sketch. The result is an
    estimate (~13% standard error), not an exact count.

    Values may be strings, bytes, or integers. The value is sent to SpectatorD as a base64-encoded
    byte string, and SpectatorD computes the hash. This keeps a single hash implementation shared
    across all clients, so sketches recorded by different clients merge correctly. Integers are
    encoded as their 8-byte little-endian representation and strings as their UTF-8 bytes, matching
    the other client implementations.

    Each instance publishes a fixed number of gauges, so treat any additional dimensions with the
    same diligence as percentile timers and ensure they have a small bounded cardinality."""

    def __init__(self, meter_id: MeterId, writer: Optional[WriterUnion] = None) -> None:
        if writer is None:
            writer = NoopWriter()

        super().__init__(meter_id, writer, "S")
        self._logger = logging.getLogger(__name__)

    def record(self, value: Union[int, str, bytes, bytearray]) -> None:
        if isinstance(value, str):
            # Encode as UTF-8 to match the other clients. Unpaired surrogates are replaced with
            # '?' rather than raising, both to honor the never-throw-on-instrumentation convention
            # and to match the unpaired-surrogate handling in the other client implementations.
            data = value.encode("utf-8", errors="replace")
        elif isinstance(value, (bytes, bytearray)):
            data = bytes(value)
        elif isinstance(value, int) and not isinstance(value, bool):
            # Match the other clients: hash the 8-byte little-endian representation of the value.
            # Values that do not fit in 64 bits cannot be represented consistently, so skip them
            # rather than silently truncating to a colliding value.
            if not -(2 ** 63) <= value < 2 ** 64:
                self._logger.warning("DistinctCountSketch.record ignoring out-of-range int")
                return
            data = (value & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little")
        else:
            # Follow the library convention of not throwing on instrumentation: skip the bad value
            # and warn, rather than risk disrupting the caller.
            self._logger.warning("DistinctCountSketch.record ignoring unsupported value type: %s",
                                 type(value).__name__)
            return

        encoded = base64.b64encode(data).decode("ascii")
        line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{encoded}"
        self._writer.write(line)
