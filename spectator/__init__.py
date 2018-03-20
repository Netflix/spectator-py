import atexit

from .clock import Clock        # noqa: F401
from .clock import ManualClock  # noqa: F401
from .clock import SystemClock  # noqa: F401
from .registry import Registry

GlobalRegistry = Registry()

try:
    from spectatorconfig import auto_start_global
    if auto_start_global():
        GlobalRegistry.start()
        atexit.register(GlobalRegistry.stop)
except:
    pass
