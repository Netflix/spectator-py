import atexit
import logging

from .clock import Clock        # noqa: F401
from .clock import ManualClock  # noqa: F401
from .clock import SystemClock  # noqa: F401
from .registry import Registry

GlobalRegistry = Registry()

logger = logging.getLogger("spectator.init")

try:
    from spectatorconfig import auto_start_global

    if auto_start_global():
        GlobalRegistry.start()
        atexit.register(GlobalRegistry.stop)
    else:
        logger.debug("module spectatorconfig auto-start is disabled - GlobalRegistry will not start")
except ImportError:
    logger.debug("module spectatorconfig is missing - GlobalRegistry will not start")
