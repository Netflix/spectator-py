[![Snapshot](https://github.com/Netflix/spectator-py/actions/workflows/snapshot.yml/badge.svg)](https://github.com/Netflix/spectator-py/actions/workflows/snapshot.yml) [![Release](https://github.com/Netflix/spectator-py/actions/workflows/release.yml/badge.svg)](https://github.com/Netflix/spectator-py/actions/workflows/release.yml)

## Introduction

Python thin-client metrics library for use with [Atlas] and [SpectatorD].

Supports Python >= 3.5. This version is chosen as the baseline, because it is the oldest system
Python available in our operating environments. 

[Atlas]: https://github.com/Netflix/atlas
[SpectatorD]: https://github.com/Netflix-Skunkworks/spectatord

## Local Development

Install [pyenv](https://github.com/pyenv/pyenv), possibly with [Homebrew](https://brew.sh/), and
install a recent Python version.

```shell
make setup-venv
make test
make coverage
```

## Usage

## Installing

Install this library for your project as follows:

```
pip3 install netflix-spectator-py
```

Publishing metrics requires a [SpectatorD] process running on your instance.

## Importing

### Standard Usage

At Netflix, your initialization script should load the environment, to ensure that the standard
variables are available to the Python application.

```bash
source /etc/nflx/environment
```

Importing the `GlobalRegistry` instantiates a `Registry` with a default configuration that applies
process-specific common tags based on environment variables and opens a socket to the [SpectatorD]
sidecar. The remainder of the instance-specific common tags are provided by SpectatorD.

```python
from spectator import GlobalRegistry
```

Once the `GlobalRegistry` is imported, it is used to create and manage Meters.

### Logging

This package provides the following loggers:

* `spectator.SidecarWriter`

When troubleshooting metrics collection and reporting, you should set the `SidecarWriter` logging
to the `DEBUG` level, before the first metric is recorded. For example:

```python
import logging

# record the human-readable time, name of the logger, logging level, thread id and message
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(message)s'
)

logging.getLogger('spectator.SidecarWriter').setLevel(logging.DEBUG)
```

There is approximately a 10% performance penalty in UDP write performance when debug logging is
enabled. It may be more, depending on the exact logging configuration (i.e. flushing to slow disk).

## Working with IDs

The IDs used for identifying a meter in the `GlobalRegistry` consist of a name and a set of tags.
IDs will be consumed by users many times after the data has been reported, so they should be
chosen thoughtfully, while considering how they will be used. See the [naming conventions] page
for general guidelines.

IDs are immutable, so they can be freely passed around and used in a concurrent context. Tags can
be added to an ID when it is created, to track the dimensionality of the metric. **All tag keys
and values must be strings.** For example, if you want to keep track of the number of successful
requests, you must cast integers to strings.

```python
from spectator import GlobalRegistry

requests_id = GlobalRegistry.counter("server.numRequests", {"statusCode": str(200)})
requests_id.increment()
```

[naming conventions]: https://netflix.github.io/atlas-docs/concepts/naming/

## Meter Types

### Age Gauges

The value is the time in seconds since the epoch at which an event has successfully occurred, or
`0` to use the current time in epoch seconds. After an Age Gauge has been set, it will continue
reporting the number of seconds since the last time recorded, for as long as the SpectatorD
process runs. The purpose of this metric type is to enable users to more easily implement the
Time Since Last Success alerting pattern.

To set a specific time as the last success:

```python
from spectator import GlobalRegistry

GlobalRegistry.age_gauge("time.sinceLastSuccess").set(1611081000)
```

To set `now()` as the last success:

```python
from spectator import GlobalRegistry

GlobalRegistry.age_gauge("time.sinceLastSuccess").set(0)
```

By default, a maximum of `1000` Age Gauges are allowed per `spectatord` process, because there is no
mechanism for cleaning them up. This value may be tuned with the `--age_gauge_limit` flag on the
`spectatord` binary.

### Counters

A Counter is used to measure the rate at which an event is occurring. Considering an API
endpoint, a Counter could be used to measure the rate at which it is being accessed.

Counters are reported to the backend as a rate-per-second. In Atlas, the `:per-step` operator
can be used to convert them back into a value-per-step on a graph.

Call `increment()` when an event occurs:

```python
from spectator import GlobalRegistry

GlobalRegistry.counter("server.numRequests").increment()
```

You can also pass a value to `increment()`. This is useful when a collection of events happens
together:

```python
from spectator import GlobalRegistry

GlobalRegistry.counter("queue.itemsAdded").increment(10)
```

### Distribution Summaries

A Distribution Summary is used to track the distribution of events. It is similar to a Timer, but
more general, in that the size does not have to be a period of time. For example, a Distribution
Summary could be used to measure the payload sizes of requests hitting a server.

Always use base units when recording data, to ensure that the tick labels presented on Atlas graphs
are readable. If you are measuring payload size, then use bytes, not kilobytes (or some other unit).
This means that a `4K` tick label will represent 4 kilobytes, rather than 4 kilo-kilobytes.

Call `record()` with a value:

```python
from spectator import GlobalRegistry

GlobalRegistry.distribution_summary("server.requestSize").record(10)
```

### Percentile Distribution Summaries

The value tracks the distribution of events, with percentile estimates. It is similar to a
Percentile Timer, but more general, because the size does not have to be a period of time.

For example, it can be used to measure the payload sizes of requests hitting a server or the
number of records returned from a query.

In order to maintain the data distribution, they have a higher storage cost, with a worst-case of
up to 300X that of a standard Distribution Summary. Be diligent about any additional dimensions
added to Percentile Distribution Summaries and ensure that they have a small bounded cardinality.

Call `record()` with a value:

```python
from spectator import GlobalRegistry

GlobalRegistry.pct_distribution_summary("server.requestSize").record(10)
```

### Gauges

A gauge is a value that is sampled at some point in time. Typical examples for gauges would be
the size of a queue or number of threads in a running state. Since gauges are not updated inline
when a state change occurs, there is no information about what might have occurred between samples.

Consider monitoring the behavior of a queue of tasks. If the data is being collected once a minute,
then a gauge for the size will show the size when it was sampled. The size may have been much
higher or lower at some point during interval, but that is not known.

Call `set()` with a value:

```python
from spectator import GlobalRegistry

GlobalRegistry.gauge("server.queueSize").set(10)
```

Gauges will report the last set value for 15 minutes. This done so that updates to the values do
not need to be collected on a tight 1-minute schedule to ensure that Atlas shows unbroken lines in
graphs. A custom TTL may be configured for gauges. SpectatorD enforces a minimum TTL of 5 seconds.

```python
from spectator import GlobalRegistry

GlobalRegistry.gauge("server.queueSize", ttl_seconds=120).set(10)
```

### Timers

A Timer is used to measure how long (in seconds) some event is taking.

Call `record()` with a value:

```python
from spectator import GlobalRegistry

GlobalRegistry.timer("server.requestLatency").record(0.01)
```

A `stopwatch()` method is available which may be used as a [Context Manager](https://docs.python.org/3/reference/datamodel.html#context-managers)
to automatically record the number of seconds that have elapsed while executing a block of code:

```python
import time
from spectator import GlobalRegistry

t = GlobalRegistry.timer("thread.sleep")

with t.stopwatch():
    time.sleep(5)
```

Internally, Timers will keep track of the following statistics as they are used:

* `count`
* `totalTime`
* `totalOfSquares`
* `max`

### Percentile Timers

The value is the number of seconds that have elapsed for an event, with percentile estimates.

This metric type will track the data distribution by maintaining a set of Counters. The
distribution can then be used on the server side to estimate percentiles, while still
allowing for arbitrary slicing and dicing based on dimensions.

In order to maintain the data distribution, they have a higher storage cost, with a worst-case of
up to 300X that of a standard Timer. Be diligent about any additional dimensions added to Percentile
Timers and ensure that they have a small bounded cardinality.

Call `record()` with a value:

```python
from spectator import GlobalRegistry

GlobalRegistry.pct_timer("server.requestLatency").record(0.01)
```

A `stopwatch()` method is available which may be used as a [Context Manager](https://docs.python.org/3/reference/datamodel.html#context-managers)
to automatically record the number of seconds that have elapsed while executing a block of code:

```python
import time
from spectator import GlobalRegistry

t = GlobalRegistry.pct_timer("thread.sleep")

with t.stopwatch():
    time.sleep(5)
```

## Writing Tests

To write tests against this library, instantiate a test instance of the Registry and configure it
to use the [MemoryWriter](https://github.com/Netflix/spectator-py/blob/main/spectator/sidecarwriter.py#L63-L80),
which stores all updates in a List. Inspect the `last_line()` or `get()` all messages to verify
your metrics updates.

```python
import unittest

from spectator import Registry
from spectator.sidecarconfig import SidecarConfig

class MetricsTest(unittest.TestCase):

    def test_counter(self):
        r = Registry(config=SidecarConfig({"sidecar.output-location": "memory"}))

        c = r.counter("test")
        self.assertTrue(c._writer.is_empty())

        c.increment()
        self.assertEqual("c:test:1", c._writer.last_line())
```

If you need to override the default output location (udp) of the `GlobalRegistry`, then you can
set a `SPECTATOR_OUTPUT_LOCATION` environment variable to one of the following values supported
by the `SidecarConfig` class:

* `none` - Disable output.
* `memory` - Write to memory.
* `stdout` - Write to standard out for the process.
* `stderr` - Write to standard error for the process.
* `file://$path_to_file` - Write to a file (e.g. `file:///tmp/foo/bar`).
* `udp://$host:$port` - Write to a UDP socket.

If you want to disable metrics publishing from the `GlobalRegistry`, then you can set:

```shell
export SPECTATOR_OUTPUT_LOCATION=none
```

If you want to validate the metrics that will be published through the `GlobalRegistry`
in tests, then you can set:

```shell
export SPECTATOR_OUTPUT_LOCATION=memory
```

The `MemoryWriter` subclass offers a few methods to inspect the values that it captures:

* `clear()` - Delete the contents of the internal list.
* `get()` - Return the internal list.
* `is_empty()` - Is the internal list empty?
* `last_line()` - Return the last element of the internal list.

Lastly, a SpectatorD line protocol parser is available, which is intended to be used for validating
the results captured by a `MemoryWriter`. It may be used as follows:

```python
import unittest

from spectator.counter import Counter
from spectator.protocolparser import parse_protocol_line


class ProtocolParserTest(unittest.TestCase):

def test_parse_counter_with_multiple_tags(self):
       meter_class, meter_id, value = parse_protocol_line("c:test,foo=bar,baz=quux:1")
       self.assertEqual(Counter, meter_class)
       self.assertEqual("test", meter_id.name)
       self.assertEqual({"foo": "bar", "baz": "quux"}, meter_id.tags())
       self.assertEqual("1", value)
```

## Migrating from 0.1.X to 0.2.X

* This library no longer publishes directly to the Atlas backends. It now publishes to the
[SpectatorD] sidecar which is bundled with all standard AMIs and containers. If you must
have the previous direct publishing behavior, because SpectatorD is not yet available on the
platform where your code runs, then you can pin to version `0.1.18`.
* The internal Netflix configuration companion library is no longer required and this dependency
may be dropped from your project.
* The API surface area remains unchanged to avoid breaking library consumers, and standard uses of
`GlobalRegistry` helper methods for publishing metrics continue to work as expected. Several helper
methods on meter classes are now no-ops, always returning values such as `0` or `nan`. If you want
to write tests to validate metrics publication, take a look at the tests in this library for a few
examples of how that can be done. The core idea is to capture the lines which will be written out
to SpectatorD.
* Replace uses of `PercentileDistributionSummary` with direct use of the Registry
`pct_distribution_summary` method.

    ```
    # before
    from spectator import GlobalRegistry
    from spectator.histogram import PercentileDistributionSummary
    
    d = PercentileDistributionSummary(GlobalRegistry, "server.requestSize")
    d.record(10)
    ```

    ```
    # after
    from spectator import GlobalRegistry
    
    GlobalRegistry.pct_distribution_summary("server.requestSize").record(10)
    ```

* Replace uses of `PercentileTimer` with direct use of the Registry `pct_timer` method.

    ```
    # before
    from spectator import GlobalRegistry
    from spectator.histogram import PercentileTimer
    
    t = PercentileTimer(GlobalRegistry, "server.requestSize")
    t.record(0.01)
    ```
    
    ```
    # after
    from spectator import GlobalRegistry
    
    GlobalRegistry.pct_timer("server.requestSize").record(0.1)
    ```

* Implemented new meter types supported by [SpectatorD]: `age_gauge`, `max_gauge` and
`monotonic_counter`. See the SpectatorD documentation or the class docstrings for
more details.
