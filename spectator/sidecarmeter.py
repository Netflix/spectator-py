import re
from typing import Union

from spectator.id import MeterId
from spectator.sidecarwriter import MemoryWriter, NoopWriter, PrintWriter, UdpWriter


class SidecarMeter:
    ALLOWED_CHARS = re.compile("[^-._A-Za-z0-9~^]")

    def __init__(self, meter_id: MeterId, meter_type: str):
        """
        :param meter_id:
            Base identifier for all measurements supplied by this meter.
        :param meter_type:
            Prefix string for line to output to SpectatorD.
        """
        self._writer = None
        self.meterId = meter_id
        self.idString = self._create_id_string(meter_id, meter_type)

    def _replace_invalid_chars(self, s: str) -> str:
        return self.ALLOWED_CHARS.sub("_", s)

    def _create_id_string(self, meter_id: MeterId, meter_type: str) -> str:
        s = "{}:{}".format(meter_type, self._replace_invalid_chars(meter_id.name))

        for key, value in sorted(meter_id.tags().items()):
            k = self._replace_invalid_chars(key)
            v = self._replace_invalid_chars(value)
            s += ",{}={}".format(k, v)

        return s + ":"

    def writer(self) -> Union[MemoryWriter, NoopWriter, PrintWriter, UdpWriter]:
        if self._writer is None:
            raise NotImplementedError("use a concrete implementation")
        return self._writer
