"""Time one meter update, optionally side by side with another git revision of the library.

    make benchmark                                       # the working tree on its own
    make benchmark BASELINE=main                         # main next to the working tree
    make benchmark BASELINE=main CANDIDATE=some-branch   # two revisions, nothing checked out

Each row is one statement, such as `registry.counter(name, tags).increment()`, run in batches of
1000 updates. The reported time is the median batch, in nanoseconds per update. With two columns,
the change is the second measured against the first: negative is a performance gain (less time
per update) and positive is a performance decrease.

A revision is read from the git object database and imported under its own package name, so
nothing is checked out. Both columns are timed in the same process and take turns to go first,
so that neither drift in the machine's speed nor a warm cache favors one of them.

The socket rows send to receivers that this script starts in separate processes: UDP on an
ephemeral loopback port and a Unix datagram socket in a temporary directory. They never use the
SpectatorD port.

This is not part of the test suite or of `make all`. Timings depend on the machine and on the
Python version, so compare the columns of one run, never two runs. On the no-op writer a
difference below about 5% is noise, and on the unbuffered sockets below about 15%.
"""

import argparse
import contextlib
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import logging
import multiprocessing
import os
import platform
import re
import socket
import statistics
import subprocess
import sys
import tempfile
import timeit
import types
from collections.abc import Sequence
from dataclasses import dataclass, field
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
BATCH = 1000
# half of the 2 KB that the Config docstring suggests, because macOS limits a Unix datagram to
# 2048 bytes and a flushed buffer is slightly larger than its size
BUFFER_SIZE = 1024
NAME = "server.numRequests"
COMMON_TAGS = {"nf.container": "main", "nf.process": "python"}
UPDATES = [
    ("per call, no tags", "registry.counter(NAME).increment()"),
    (
        "per call, 2 tags",
        'registry.counter(NAME, {"status": "200", "method": "GET"}).increment()',
    ),
    (
        "per call, 4 tags",
        'registry.counter(NAME, {"status": "200", "method": "GET", "country": "US", "device": "tv"}).increment()',
    ),
    ("reused meter", "counter.increment()"),
]


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout


class RevisionFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Imports the spectator package of a git revision under another top-level name."""

    def __init__(self, revision: str, package: str) -> None:
        # module name -> (source, whether it is a package, origin)
        self._sources: dict[str, tuple[str, bool, str]] = {}
        paths = _git("ls-tree", "-r", "--name-only", revision, "--", "spectator")
        for path in paths.splitlines():
            if not path.endswith(".py"):
                continue
            # the copy has to import its own modules, not those of the working tree
            source = re.sub(
                r"^([ \t]*)(from|import) spectator(?=[. ]|$)",
                rf"\1\2 {package}",
                _git("show", f"{revision}:{path}"),
                flags=re.MULTILINE,
            )
            module = path[: -len(".py")].replace("/", ".")
            is_package = module.endswith(".__init__")
            if is_package:
                module = module[: -len(".__init__")]
            name = package + module[len("spectator") :]
            self._sources[name] = (source, is_package, f"{revision}:{path}")

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        if fullname not in self._sources:
            return None
        is_package = self._sources[fullname][1]
        return importlib.util.spec_from_loader(fullname, self, is_package=is_package)

    def create_module(
        self, spec: importlib.machinery.ModuleSpec
    ) -> types.ModuleType | None:
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        source, _, origin = self._sources[module.__name__]
        exec(compile(source, origin, "exec"), module.__dict__)


def load(revision: str | None, package: str) -> types.ModuleType:
    """Import the library from the working tree, or from a git revision under another name."""
    if revision is None:
        sys.path.insert(0, str(REPO_ROOT))
        return importlib.import_module("spectator")
    sys.meta_path.insert(0, RevisionFinder(revision, package))
    return importlib.import_module(package)


def _receive(kind: str, path: str, ready: Connection) -> None:
    """Runs in a child process: bind a datagram socket, report its location and discard
    whatever arrives."""
    if kind == "unix":
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.bind(path)
        location = f"unix://{path}"
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 0))
        location = f"udp://127.0.0.1:{sock.getsockname()[1]}"
    # room for a burst, so that a sender is neither slowed down nor refused while this
    # process waits for its turn to run
    with contextlib.suppress(OSError):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
    ready.send(location)
    while True:
        sock.recv(65536)


class Receiver:
    """Stands in for SpectatorD: a separate process that discards the datagrams it is sent."""

    def __init__(self, kind: str) -> None:
        self.kind = kind
        # where the Unix receiver binds its socket: under /tmp, because the path of a Unix
        # socket is limited to about 100 bytes
        self._directory = tempfile.TemporaryDirectory(
            prefix="spectator-benchmark-", dir="/tmp" if os.path.isdir("/tmp") else None
        )
        path = os.path.join(self._directory.name, "spectatord.unix")
        ours, theirs = multiprocessing.Pipe()
        self._process = multiprocessing.Process(
            target=_receive, args=(kind, path, theirs), daemon=True
        )
        self._process.start()
        theirs.close()
        try:
            self.location: str = ours.recv()
        except EOFError:
            self.close()
            raise RuntimeError(f"the {kind} receiver did not start") from None

    def close(self) -> None:
        self._process.terminate()
        self._process.join()
        self._directory.cleanup()


class ErrorCounter(logging.Handler):
    """Counts what the library logs at warning and above: a failed send voids a timing."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.count = 0

    def emit(self, record: logging.LogRecord) -> None:
        if record.name.startswith("spectator"):
            self.count += 1


@dataclass
class Row:
    writer: str
    update: str
    common_tags: bool
    # one timer and one list of samples per column
    timers: list[timeit.Timer]
    samples: list[list[float]] = field(init=False)

    def __post_init__(self) -> None:
        self.samples = [[] for _ in self.timers]


def build_rows(
    packages: Sequence[types.ModuleType], writers: Sequence[tuple[str, str, int]]
) -> tuple[list[Row], list[Any]]:
    rows: list[Row] = []
    registries: list[Any] = []
    for common_tags in (False, True):
        for writer, location, buffer_size in writers:
            scopes = []
            for package in packages:
                config = package.Config(
                    location,
                    extra_common_tags=dict(COMMON_TAGS) if common_tags else None,
                    buffer_size=buffer_size,
                )
                registry = package.Registry(config)
                registries.append(registry)
                scopes.append(
                    {
                        "registry": registry,
                        "counter": registry.counter(NAME),
                        "NAME": NAME,
                    }
                )
            for update, statement in UPDATES:
                timers = [timeit.Timer(statement, globals=scope) for scope in scopes]
                rows.append(Row(writer, update, common_tags, timers))
    return rows, registries


def time_rows(rows: Sequence[Row], rounds: int) -> None:
    for row in rows:  # warm up, which also opens the sockets
        for timer in row.timers:
            timer.timeit(BATCH // 10)
    for round_number in range(rounds):
        for row in rows:
            columns = list(range(len(row.timers)))
            if round_number % 2 == 1:
                columns.reverse()
            for column in columns:
                seconds = row.timers[column].timeit(BATCH)
                row.samples[column].append(seconds / BATCH * 1e9)


def report(rows: Sequence[Row], labels: Sequence[str], rounds: int) -> None:
    width = max(14, *(len(label) + 2 for label in labels))
    print(
        f"ns per update, median of {rounds} rounds of {BATCH} "
        f"({platform.python_implementation()} {platform.python_version()}, {sys.platform})"
    )
    if len(labels) == 2:
        print(
            f"change: {labels[1]} against {labels[0]}. "
            "Negative is a performance gain, positive a performance decrease."
        )
    for common_tags in (False, True):
        print(
            f"\nextra common tags: {', '.join(COMMON_TAGS) if common_tags else 'none'}"
        )
        header = f"{'writer':<16}{'update':<19}"
        header += "".join(f"{label:>{width}}" for label in labels)
        print(header + (f"{'change':>9}" if len(labels) == 2 else ""))
        for row in rows:
            if row.common_tags != common_tags:
                continue
            medians = [statistics.median(samples) for samples in row.samples]
            line = f"{row.writer:<16}{row.update:<19}"
            line += "".join(f"{median:>{width}.0f}" for median in medians)
            if len(medians) == 2:
                line += f"{100 * (medians[1] / medians[0] - 1):>+8.0f}%"
            print(line)
    print(
        "\nA difference below about 5% (no-op writer) or 15% (unbuffered sockets) is noise."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Time one meter update, optionally side by side with another git revision."
    )
    parser.add_argument(
        "--baseline",
        metavar="REVISION",
        help="a git revision to time next to the candidate, such as main",
    )
    parser.add_argument(
        "--candidate",
        metavar="REVISION",
        help="a git revision to time instead of the working tree",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=40,
        help=f"batches of {BATCH} updates per row (default: 40)",
    )
    parser.add_argument(
        "--no-sockets", action="store_true", help="time the no-op writer only"
    )
    args = parser.parse_args()

    # the library reads these when it is imported and whenever a Config is created
    for key in (
        "SPECTATOR_OUTPUT_LOCATION",
        "NETFLIX_CONTAINER_NAME",
        "NETFLIX_PROCESS_NAME",
        "TITUS_CONTAINER_NAME",
    ):
        os.environ.pop(key, None)

    errors = ErrorCounter()
    logging.getLogger().addHandler(errors)

    # the receivers come first: where processes are forked, that has to happen before the
    # buffered writers start their flush threads
    receivers: list[Receiver] = []
    try:
        if not args.no_sockets:
            receivers.append(Receiver("udp"))
            if hasattr(socket, "AF_UNIX"):
                receivers.append(Receiver("unix"))

        columns: list[tuple[str, types.ModuleType]] = []
        try:
            if args.baseline is not None:
                package = load(args.baseline, "spectator_baseline")
                columns.append((args.baseline, package))
            package = load(args.candidate, "spectator_candidate")
            columns.append((args.candidate or "working tree", package))
        except subprocess.CalledProcessError as e:
            parser.error(e.stderr.strip())

        writers = [("no-op", "none", 0)]
        for receiver in receivers:
            writers.append((receiver.kind, receiver.location, 0))
            writers.append(
                (f"{receiver.kind}, buffered", receiver.location, BUFFER_SIZE)
            )

        rows, registries = build_rows([package for _, package in columns], writers)
        time_rows(rows, args.rounds)
        for registry in registries:
            registry.close()
    finally:
        for receiver in receivers:
            receiver.close()

    report(rows, [label for label, _ in columns], args.rounds)
    if errors.count > 0:
        print(
            f"\nThe library logged {errors.count} warnings or errors, so these timings are not valid."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
