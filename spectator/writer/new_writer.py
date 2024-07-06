import sys
from typing import Union
from urllib.parse import urlparse

from spectator.writer.file_writer import FileWriter
from spectator.writer.memory_writer import MemoryWriter
from spectator.writer.noop_writer import NoopWriter
from spectator.writer.udp_writer import UdpWriter

WriterUnion = Union[FileWriter, MemoryWriter, NoopWriter, UdpWriter]


def is_valid_output_location(location: str) -> bool:
    if not isinstance(location, str):
        return False
    return location in ["none", "memory", "stdout", "stderr", "udp", "unix"] or \
        location.startswith("file://") or \
        location.startswith("udp://")


def new_writer(location: str) -> WriterUnion:
    """Create a new Writer based on an output location."""

    if location == "none":
        writer = NoopWriter()
    elif location == "memory":
        writer = MemoryWriter()
    elif location == "stderr":
        writer = FileWriter(location, sys.stderr)
    elif location == "stdout":
        writer = FileWriter(location, sys.stdout)
    elif location == "udp":
        # default udp port for spectatord
        location = "udp://127.0.0.1:1234"
        parsed = urlparse(location)
        address = (parsed.hostname, parsed.port)
        writer = UdpWriter(location, address)
    elif location == "unix":
        # default unix domain socket for spectatord
        location = "file:///run/spectatord/spectatord.unix"
        file = open(urlparse(location).path, "a", encoding="utf-8")
        writer = FileWriter(location, file)
    elif location.startswith("file://"):
        file = open(urlparse(location).path, "a", encoding="utf-8")
        writer = FileWriter(location, file)
    elif location.startswith("udp://"):
        parsed = urlparse(location)
        address = (parsed.hostname, parsed.port)
        writer = UdpWriter(location, address)
    else:
        raise ValueError(f"unsupported Writer location: {location}")

    return writer
