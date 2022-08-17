from spectator.id import MeterId
from spectator.sidecarmeter import SidecarMeter
from spectator.sidecarwriter import AsyncUdpWriter, SidecarWriter


class Counter(SidecarMeter):
    """The value is the number of increments that have occurred since the last time it was
    recorded. The value will be reported to the Atlas backend as a rate-per-second."""

    def __init__(self, meter_id: MeterId,
                 writer: SidecarWriter = SidecarWriter.create("none")) -> None:
        super().__init__(meter_id, "c")
        self._writer = writer

    def increment(self, delta: int = 1) -> None:
        if delta > 0:
            self._writer.write(self.idString, delta)

    @staticmethod
    def count() -> int:
        """Avoid breaking the API."""
        return 0


class MonotonicCounter(SidecarMeter):
    """The value is a monotonically increasing number. A minimum of two samples must be received
    in order for SpectatorD to calculate a delta value and report it to the backend."""

    def __init__(self, meter_id: MeterId,
                 writer: SidecarWriter = SidecarWriter.create("none")) -> None:
        super().__init__(meter_id, "C")
        self._writer = writer

    def set(self, amount: int) -> None:
        self._writer.write(self.idString, amount)


class AsyncCounter(Counter):
    _writer: AsyncUdpWriter

    def __init__(self, meter_id: MeterId, writer: AsyncUdpWriter) -> None:
        if not isinstance(writer, AsyncUdpWriter):
            raise Exception("The Async* classes can only be used with `AsyncUdpWriter`.")
        super().__init__(meter_id, writer)

    async def increment(self, delta: int = 1) -> None:
        if delta > 0:
            await self._writer.write(self.idString, delta)
