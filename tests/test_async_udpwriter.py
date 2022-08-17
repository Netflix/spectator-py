from contextlib import closing

import pytest
from spectator.sidecarwriter import AsyncUdpWriter
from .udpserver import UdpServer


@pytest.mark.asyncio
async def test_async() -> None:
    with closing(UdpServer()) as server:  # type: UdpServer
        with closing(AsyncUdpWriter.create(server.address().replace("udp", "udp-async"))) as w:
            await w.connect()

            await w.write_line("foo")
            assert "foo" == server.read()
            await w.write_line("bar")
            assert "bar" == server.read()
