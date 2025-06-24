from typing import Union

from spectator.writer.file_writer import FileWriter
from spectator.writer.memory_writer import MemoryWriter
from spectator.writer.noop_writer import NoopWriter
from spectator.writer.socket_writer import SocketWriter

WriterUnion = Union[FileWriter, MemoryWriter, NoopWriter, SocketWriter]


def is_valid_output_location(location: str) -> bool:
    if not isinstance(location, str):
        return False
    return location in ["none", "memory", "stdout", "stderr", "udp", "unix"] or \
        location.startswith("file://") or \
        location.startswith("udp://") or \
        location.startswith("unix://")


def new_writer(location: str, buffer_size: int = 0, is_global: bool = False) -> WriterUnion:
    """Create a new Writer based on an output location."""

    if location == "none":
        writer = NoopWriter()
    elif location == "memory":
        writer = MemoryWriter()
    elif location in ("stderr", "stdout"):
        writer = FileWriter(location)
    elif location == "udp":
        # default udp port for spectatord
        location = "udp://127.0.0.1:1234"
        writer = SocketWriter(location, buffer_size, is_global)
    elif location == "unix":
        # default unix domain socket for spectatord
        location = "unix:///run/spectatord/spectatord.unix"
        writer = SocketWriter(location, buffer_size)
    elif location.startswith("file://"):
        writer = FileWriter(location)
    elif location.startswith("udp://"):
        writer = SocketWriter(location, buffer_size, is_global)
    elif location.startswith("unix://"):
        writer = SocketWriter(location, buffer_size)
    else:
        raise ValueError(f"unsupported Writer location: {location}")

    return writer
