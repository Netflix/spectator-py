import abc
from ctypes import c_uint64
from typing import Union

from spectator.meter.meter_id import MeterId
from spectator.writer.new_writer import WriterUnion


class Meter(metaclass=abc.ABCMeta):
    def __init__(self, meter_id: MeterId, writer: WriterUnion, meter_type_symbol: str) -> None:
        self._id = meter_id
        self._meter_type_symbol = meter_type_symbol
        self._writer = writer

    def writer(self) -> WriterUnion:
        return self._writer

    def update(self, value: Union[c_uint64, float, int]) -> None:
        """General-purpose meter update method, to assist with meta-programming."""
        if self._meter_type_symbol == "c":
            # counter
            if value > 0:
                line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value}"
                self._writer.write(line)
        elif self._meter_type_symbol in ["d", "D", "t", "T"]:
            # dist_summary, percentile_dist_summary, percentile_timer, timer
            if value >= 0:
                line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value}"
                self._writer.write(line)
        elif self._meter_type_symbol == "U":
            # monotonic_counter_uint
            if isinstance(value, c_uint64):
                line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value.value}"
                self._writer.write(line)
        elif self._meter_type_symbol in ["A", "g", "m", "C"]:
            # age_gauge, gauge, max_gauge, monotonic_counter
            line = f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value}"
            self._writer.write(line)
