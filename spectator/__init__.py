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
        try:
            from os import register_at_fork
            register_at_fork(before=GlobalRegistry.stop_without_publish,
                             after_in_parent=GlobalRegistry.start,
                             after_in_child=GlobalRegistry.clear_meters_and_start)
        except ImportError:
            pass

    else:
        logger.debug("module spectatorconfig auto-start is disabled - GlobalRegistry will not start")
except ImportError:
    logger.debug("module spectatorconfig is missing - GlobalRegistry will not start")
