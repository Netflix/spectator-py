from typing import Union

from spectator.config import Config
from spectator.writer.file_writer import FileWriter
from spectator.writer.memory_writer import MemoryWriter
from spectator.writer.noop_writer import NoopWriter
from spectator.writer.socket_writer import SocketWriter

WriterUnion = Union[FileWriter, MemoryWriter, NoopWriter, SocketWriter]


def new_writer(config: Config) -> WriterUnion:
    """Create a new Writer based on an output location."""

    if config.location == "none":
        writer = NoopWriter()
    elif config.location == "memory":
        writer = MemoryWriter()
    elif config.location in ("stderr", "stdout"):
        writer = FileWriter(config)
    elif config.location == "udp":
        # default udp port for spectatord
        config.location = "udp://127.0.0.1:1234"
        writer = SocketWriter(config)
    elif config.location == "unix":
        # default unix domain socket for spectatord
        config.location = "unix:///run/spectatord/spectatord.unix"
        writer = SocketWriter(config)
    elif config.location.startswith("file://"):
        writer = FileWriter(config)
    elif config.location.startswith("udp://"):
        writer = SocketWriter(config)
    elif config.location.startswith("unix://"):
        writer = SocketWriter(config)
    else:
        raise ValueError(f"unsupported Writer location: {config.location}")

    return writer
