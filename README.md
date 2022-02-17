[![Snapshot](https://github.com/Netflix/spectator-py/actions/workflows/snapshot.yml/badge.svg)](https://github.com/Netflix/spectator-py/actions/workflows/snapshot.yml)

## Introduction

Python port of the [Spectator] library for Java.

See the Spectator [documentation] for an overview of core concepts and details on [usage].

Supports Python >= 3.5, which is the oldest system Python 3 available on our commonly used OSes.

Note that there is a risk of deadlock if you are running Python 3.6 or lower and using 
`os.fork()` or using a library that will fork the process 
(see [this section](#concurrent-usage-under-older-python) for workarounds),
so **we recommend using Python >= 3.7**

[Spectator]: https://github.com/Netflix/spectator/
[documentation]: https://netflix.github.io/atlas-docs/spectator/
[usage]: https://netflix.github.io/atlas-docs/spectator/lang/py/usage/

## Local Development

* Install [pyenv](https://github.com/pyenv/pyenv), possibly with [Homebrew](https://brew.sh/).
* Install Python versions: 3.5, 3.6, 3.7, and 3.8. Enable all versions globally.
* Make changes and add tests.
* `tox`

## Usage

## Installing

The `netflix-spectator-py` package alone is not sufficient to report data to an Atlas backend -
a configuration package must also be installed.

At Netflix, the internal configuration package is named `netflix-spectator-pyconf` and it declares
a dependency on this client package.

```
pip3 install netflix-spectator-pyconf
```

## Importing

### Standard Usage

At Netflix, your initialization script should load the environment, to ensure that the standard
variables are available to the Python application.

```bash
source /etc/nflx/environment
```

Importing the `GlobalRegistry` configures common tags based on environment variables, sets the
Atlas Aggregator URL, and starts a background thread which reports metrics data every five seconds.

```python
from spectator import GlobalRegistry
```

Once the `GlobalRegistry` is imported, it is used to create and manage Meters.

### Concurrent Usage Under Older Python

> :warning: **Use Python 3.7+ if possible**: But if you can't, here's a workaround to prevent deadlocks

There is a known issue in Python where forking a process after a thread is started can lead to
deadlocks. This is commonly seen when using the `multiprocessing` module with default settings.
The root cause of the deadlocks is that `fork()` copies everything in memory, including globals
that have been set in imported modules, but it does not copy threads - any threads started in
the parent process will not exist in the child process. The possibility of deadlocks occurs when
global state sets a lock and it then depends upon a thread to remove the lock.

Under the standard usage model for `spectator-py`, it starts a background publishing thread when
the module is imported, which is responsible for manipulating a lock. Below, there are a couple of
options described for working around this issue.

#### Gunicorn

If you are using `spectator-py` while running under [Gunicorn], then do not use the `--preload`
flag, which loads application code before worker processes are forked. Preloading triggers the
conditions that allow deadlocks to occur in the background publish thread.

At Netflix, you can set the following flag in `/etc/default/ezconfig` to achieve this configuration
for Gunicorn:

```bash
WSGI_GUNICORN_PRELOAD = undef
```

[Gunicorn]: https://gunicorn.org/

#### Task Worker Forking

> :warning: **Use Python 3.7+ if possible**: But if you can't, here's a workaround to prevent deadlocks

For other pre-fork worker processing frameworks, such as [huey], you need to be careful about how
and when you start the `GlobalRegistry` to avoid deadlocks in the background publish thread. You
should set the `SPECTATOR_PY_DISABLE_AUTO_START_GLOBAL` environment variable to disable automatic
startup of the Registry, so that you can plan to start it manually after all of the workers have
been forked.

You can set the variable as a part of your initialization script:

```bash
export SPECTATOR_PY_DISABLE_AUTO_START_GLOBAL=1
```

You can set the variable in Python code, as long as it is at the top of the module where you plan
to use `spectator-py`:

```python
import os

os.environ["SPECTATOR_PY_DISABLE_AUTO_START_GLOBAL"] = "1"
```

After your workers have started, you can then start the `GlobalRegistry` as follows:

```python
from spectator import GlobalRegistry

GlobalRegistry.start()
```

It is often best to have the `import` and `start()` within an initialization function for the
workers, to help ensure that it is not started when the module is loaded.

[huey]: https://github.com/coleifer/huey

#### Generic Multiprocessing

> :warning: **Use Python 3.7+ if possible**: But if you can't, here's a workaround to prevent deadlocks

In Python 3, you can configure the start method to `spawn` for `multiprocessing`. This will cause
the module to do a `fork()` followed by an `execve()` to start a brand new Python process.

To configure this option globally:

```python
from multiprocessing import set_start_method
set_start_method("spawn")
```

To configure this option within a context:

```python
from multiprocessing import get_context

def your_func():
    with get_context("spawn").Pool() as pool:
        pass
```

### Logging

This package provides three loggers:

* `spectator.init`
* `spectator.HttpClient`
* `spectator.Registry`

When troubleshooting metrics collection and reporting, you should set `Registry` logging to the
`DEBUG` level. For example:

```python
import logging

# record the human-readable time, name of the logger, logging level, thread id and message
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(message)s'
)

# silence the HttpClient logger output, to minimize confusion while reading logs
logging.getLogger('spectator.HttpClient').setLevel(logging.ERROR)

# set the Registry logger to INFO or ERROR when done troubleshooting
logging.getLogger('spectator.Registry').setLevel(logging.DEBUG)
```

### Detecting Deadlocks

If you need to detect whether or not your application is affected by deadlocks, then you can use
[sys._current_frames] to collect stack frames periodically and check them. A common pattern is
to run this on a background thread every 10 seconds.

[sys._current_frames]: https://docs.python.org/3/library/sys.html#sys._current_frames

## Working with IDs

The IDs used for looking up a meter in the `GlobalRegistry` consist of a name and a set of tags.
IDs will be consumed by users many times after the data has been reported, so they should be
chosen thoughtfully, while considering how they will be used. See the [naming conventions] page
for general guidelines.

IDs are immutable, so they can be freely passed around and used in a concurrent context. Tags can
be added to an ID when it is created, to track the dimensionality of the metric. **All tag keys
and values must be strings.** For example, if you want to keep track of the number of successful
requests, you must cast integers to strings.

```python
requests_id = GlobalRegistry.counter('server.numRequests', {'statusCode': str(200)})
requests_id.increment()
```

[naming conventions]: https://netflix.github.io/spectator/en/latest/intro/conventions/

## Meter Types

### Counters

A Counter is used to measure the rate at which an event is occurring. Considering an API
endpoint, a Counter could be used to measure the rate at which it is being accessed.

Counters are reported to the backend as a rate-per-second. In Atlas, the `:per-step` operator
can be used to convert them back into a value-per-step on a graph.

Call `increment()` when an event occurs:

```python
GlobalRegistry.counter('server.numRequests').increment()
```

You can also pass a value to `increment()`. This is useful when a collection of events happens
together:

```python
GlobalRegistry.counter('queue.itemsAdded').increment(10)
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
GlobalRegistry.distribution_summary('server.requestSize').record(10)
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
GlobalRegistry.gauge('server.queueSize').set(10)
```

Gauges are designed to report the last set value for 15 minutes. This done so that updates to the
values do not need to be collected on a tight 1-minute schedule to ensure that Atlas shows
unbroken lines in graphs.

If you wish to no longer report a Gauge value, then set it to `float('nan')`. This is a separate
and distinct value from `'nan'` or `'NaN'`, which are strings.

### Age Gauges

A gauge which reports the number of seconds since it was last reset. The starting value of the
gauge is zero.

Age gauges are intended to be used with the Time Since Last Success alerting pattern, where a
static threshold in number of seconds is set for a given task. Whenever this value is exceeded,
an alert will fire. The gauge should be reset whenever a task is successful. The gauge will
update its value every minute with the number of seconds that have elapsed since the last
reset.

```python
last_success = GlobalRegistry.age_gauge('last_success', {'id': 'cache_refresh'})

# periodically scheduled work
while True:
    refresh_cache()
    if refresh_successful():
        last_success.reset()
    sleep(300)
```

### Timers

A Timer is used to measure how long (in seconds) some event is taking.

Call `record()` with a value:

```python
GlobalRegistry.timer('server.requestLatency').record(0.01)
```

Timers will keep track of the following statistics as they are used:

* `count`
* `totalTime`
* `totalOfSquares`
* `max`
