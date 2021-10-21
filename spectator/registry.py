import logging
import math
import sys
import threading

from spectator.clock import SystemClock
from spectator.counter import Counter, NoopCounter
from spectator.distsummary import DistributionSummary, NoopDistributionSummary
from spectator.gauge import Gauge, NoopGauge
from spectator.http import HttpClient
from spectator.id import MeterId
from spectator.timer import Timer, NoopTimer


logger = logging.getLogger("spectator.Registry")

try:
    from spectatorconfig import default_config
    defaultConfig = default_config()
    logger.info("loaded default config: %s", defaultConfig)
except:
    defaultConfig = {}


class Registry:
    noopGauge = NoopGauge()
    noopCounter = NoopCounter()
    noopDistributionSummary = NoopDistributionSummary()
    noopTimer = NoopTimer()
    addOp = 0
    maxOp = 10
    counterStats = {"count", "totalAmount", "totalTime",
                    "totalOfSquares", "percentile"}

    def __init__(self, clock=SystemClock()):
        self._clock = clock
        self._lock = threading.RLock()
        self._meters = {}
        self._started = False

    def clock(self):
        return self._clock

    def _new_meter(self, name, tags, meterFactory, meterCls, defaultIns):
        with self._lock:
            if tags is None:
                tags = {}
            meterId = MeterId(name, tags)
            meter = self._meters.get(meterId, None)
            if meter is None:
                meter = meterFactory(meterId)
                self._meters[meterId] = meter
            elif not isinstance(meter, meterCls):
                logger.warning("Meter is already defined as type %s. "
                               "Please use a unique name or tags",
                               meter.__class__.__name__)
                return defaultIns
            return meter

    def counter(self, name, tags=None):
        return self._new_meter(name, tags, lambda id: Counter(id), Counter,
                               self.noopCounter)

    def timer(self, name, tags=None):
        return self._new_meter(name, tags, lambda id: Timer(id, self._clock),
                               Timer, self.noopTimer)

    def distribution_summary(self, name, tags=None):
        return self._new_meter(name, tags, lambda id: DistributionSummary(id),
                               DistributionSummary,
                               self.noopDistributionSummary)

    def gauge(self, name, tags=None):
        return self._new_meter(name, tags, lambda id: Gauge(id, self._clock), Gauge,
                               self.noopGauge)

    def __iter__(self):
        with self._lock:
            return RegistryIterator(self._meters.values())

    def start(self, config=None):
        if self._started:
            logger.debug("registry already started")
            return RegistryStopper(None)
        else:
            self._started = True
            logger.info("starting registry")
            if config is None:
                logger.info("config not specified, using default")
                config = defaultConfig
            elif type(config) is not dict:
                logger.warning("invalid config specified, using default")
                config = defaultConfig
            frequency = config.get("frequency", 5.0)
            self._uri = config.get("uri", None)
            self._batch_size = config.get("batch_size", 10000)
            self._common_tags = config.get("common_tags", {})
            self._client = HttpClient(self, config.get("timeout", 1))
            self._timer = RegistryTimer(frequency, self._publish)
            self._timer.start()
            logger.debug("registry started with config: %s", config)
            return RegistryStopper(self)

    def clear_meters_and_start(self):
        """
        This is called after a fork in the child process
        to clear the cloned `_meters` and prevent duplicates
        (the `_meters` are copied with the process
        during the forking)
        """
        self._meters = {}
        self.start()

    def stop_without_publish(self):
        """
        This is called before a fork to prevent a potential deadlock.
        It cancels the background timer thread. After the fork, the timer
        thread is restarted in the main and cloned processes.
        """
        if self._started:
            logger.debug("stopping log registry")
            self._timer.cancel()
            self._started = False

    def stop(self):
        self.stop_without_publish()
        # Even if not started, attempt to flush data to minimize risk
        # of data loss
        self._publish()

    def _get_measurements(self):
        """
        If there are no references in user code, then we expect four references to a meter:

            1) meters map,
            2) local variable in the for loop,
            3) internal to ref count method, and
            4) internal to the garbage collector.

        """
        snapshot = []

        with self._lock:
            for k, m in list(self._meters.items()):
                if sys.getrefcount(m) == 4:
                    if m.__class__.__name__ == 'Gauge':
                        if m._has_expired():
                            del self._meters[k]
                    else:
                        del self._meters[k]

                ms = m._measure()

                for id, value in ms.items():
                    if self._should_send(id, value):
                        snapshot.append((id, value))

        return snapshot

    def _send_batch(self, batch):
        json = self._measurements_to_json(batch)
        self._client.post_json(self._uri, json)

    def _publish(self):
        snapshot = self._get_measurements()

        if logger.isEnabledFor(logging.DEBUG):
            for id, value in snapshot:
                logger.debug("reporting: %s => %f", id, value)

        if self._uri is not None:
            i = 0
            while i < len(snapshot):
                end = min(i + self._batch_size, len(snapshot))
                self._send_batch(snapshot[i:end])
                i += self._batch_size

    def _should_send(self, id, value):
        max_op = 10
        op = self._operation(id.tags())
        return not math.isnan(value) and (value > 0 or op == max_op)

    def _build_string_table(self, payload, data):
        strings = {'name': 0}
        for k, v in self._common_tags.items():
            strings[k] = 0
            strings[v] = 0

        for id, _ in data:
            strings[id.name] = 0
            for k, v in id.tags().items():
                strings[k] = 0
                strings[v] = 0
        keys = list(strings.keys())
        keys.sort()
        payload.append(len(keys))
        payload.extend(keys)
        for i, k in enumerate(keys):
            strings[k] = i
        return strings

    def _measurements_to_json(self, data):
        payload = []
        strings = self._build_string_table(payload, data)
        for id, v in data:
            self._append_measurement(strings, payload, id, v)
        return payload

    def _append_measurement(self, strings, payload, id, value):
        tags = id.tags()
        op = self._operation(tags)
        common_tags = self._common_tags
        payload.append(len(tags) + 1 + len(common_tags))
        for k, v in common_tags.items():
            payload.append(strings[k])
            payload.append(strings[v])
        for k, v in tags.items():
            payload.append(strings[k])
            payload.append(strings[v])
        payload.append(strings["name"])
        payload.append(strings[id.name])
        payload.append(op)
        payload.append(value)

    def _operation(self, tags):
        if tags.get('statistic') in self.counterStats:
            return self.addOp
        else:
            return self.maxOp


class RegistryTimer:

    def __init__(self, frequency, function):
        self._frequency = frequency
        self._function = function
        self._cancelled = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True

    def _run(self):
        while not self._cancelled.wait(self._frequency):
            try:
                self._function()
            except:
                e = sys.exc_info()[0]
                logger.exception("registry polling failed: %s", e)

    def start(self):
        self._thread.start()

    def cancel(self):
        self._cancelled.set()
        self._thread.join()


class RegistryStopper:

    def __init__(self, registry):
        self._registry = registry

    def __enter__(self):
        pass

    def __exit__(self, typ, value, traceback):
        if self._registry is not None:
            self._registry.stop()


class RegistryIterator:

    def __init__(self, meters):
        self._meters = list(meters)
        self._pos = 0

    def next(self):
        # needed to work on 2.7
        return self.__next__()

    def __next__(self):
        if self._pos < len(self._meters):
            pos = self._pos
            self._pos += 1
            return self._meters[pos]
        else:
            raise StopIteration
