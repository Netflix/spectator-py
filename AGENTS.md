# AGENTS.md

`netflix-spectator-py` is a stateless, stdlib-only Python thin client that turns meter updates into SpectatorD protocol lines and sends them (UDP, Unix socket, file, or memory) to SpectatorD, which aggregates and publishes to Atlas.

- Setup and releases: [README.md](README.md).
- User docs live on the Atlas site, not in this repo: https://netflix.github.io/atlas-docs/spectator/lang/py/usage/
- Protocol reference: https://netflix.github.io/atlas-docs/spectator/agent/usage/

## Commands

| Task | Command |
|---|---|
| Create venv + dev deps | `make setup-venv` (creates `./venv`, runs `pip install -e ".[dev]"`) |
| Test + coverage | `make test` → `pytest --cov=spectator tests` |
| Single test | `venv/bin/pytest tests/meter/test_counter.py::CounterTest::test_increment` |
| Lint + format check | `make lint` → `ruff check .` and `ruff format --check .` |
| Auto-fix + format | `make format` → `ruff check --fix .` and `ruff format .` |
| Type check | `make typecheck` → `mypy spectator tests` |
| Packaging check | `make check-manifest` (check-manifest, `python -m build`, `twine check --strict dist/*`) |
| Full CI gate | `make all` (clean, test, lint, typecheck, check-manifest) |
| Coverage report | `make coverage` (opens `htmlcov/index.html` on macOS) |
| Build dist | `python -m build --sdist --wheel --outdir dist/ .` |
| Clean | `make clean` |
| Migrations | None. No database or schema. |

- On macOS, every make target sources `venv/bin/activate`. Run `make setup-venv` first or the targets fail. On Linux they use the ambient Python.
- CI (`.github/workflows/pr.yml`) runs `make install-deps && make all` on Python 3.10, 3.11, 3.12 and 3.13.
- Baseline is clean: ruff check and ruff format report nothing, mypy reports no issues, all tests pass. Keep it that way.
- All packaging and tool config (ruff, mypy, pytest, check-manifest) lives in `pyproject.toml`. There is no `setup.py` or `setup.cfg`.
- Release: follow "Releasing" in `README.md`. Merge the `version` bump in `pyproject.toml` before creating the `vX.Y.Z` release. A tag on a commit with a different version fails to publish; this is why 1.2.0 never reached PyPI. `release.yml` now checks the tag against the `pyproject.toml` version (PEP 440, so `v1.3.0-rc.1` matches `1.3.0rc1`) before building. Never create `v*` tags or releases unless you are releasing.

## Architecture

```
spectator/
  __init__.py          Public API: re-exports every public class + deprecated GlobalRegistry
  config.py            Config(location, extra_common_tags, buffer_size, is_global) + env overrides
  common_tags.py       nf.container / nf.process from env; tag validation
  registry.py          Registry: two factory methods per meter type
  protocol_parser.py   Symbol -> meter class map; line parser (testing utility)
  stopwatch.py         StopWatch context manager -> Timer / PercentileTimer
  clock.py             SystemClock (perf_counter), ManualClock (tests)
  meter/               One meter class per file; all subclass Meter
    meter_id.py        MeterId: name + tags -> sanitized, sorted spectatord_id
  writer/              Writer ABC (write, close) + implementations
    new_writer.py      location -> writer factory; WriterUnion
    socket_writer.py   UDP/Unix datagram writer, optional LineBuffer + flush thread
    line_buffer.py     Byte-sized line batching
tests/                 Mirrors package layout; udp_server.py / unix_server.py helpers
```

Data flow: `Registry.counter(name, tags)` → `MeterId` (+ extra common tags) → `Counter(id, writer)` → `writer.write("c:<id>:<value>")`. Nothing is aggregated in-process; SpectatorD does that.

## Code Style & Conventions

- Python ≥ 3.10. Use built-in generics and PEP 604 unions (`dict[str, str]`, `list[str]`, `X | None`), and `typing.TypeAlias` for aliases. Never use `Optional`, `Dict`, `List` or `Union`; ruff's `UP` rules reject them. No 3.11+ features (`typing.Self`, `except*`, `tomllib`, the `type` statement).
- Formatting is `ruff format` (Black style, 88 columns). Run `make format` before committing and never hand-format. Long strings, comments and docstrings are allowed (E501 is off).
- ruff is pinned in `pyproject.toml` (`ruff==X.Y.Z`). To upgrade: bump the pin, run `make format`, commit any reformat on its own, and add that commit's full hash to `.git-blame-ignore-revs`. Never mix a reformat with other changes.
- Add a `# noqa: <code>` only when the rule is genuinely wrong for that line. Existing ones: `B024` on `Clock`/`Meter`, `SIM115` on the `FileWriter` file handle.
- Type-annotate every signature, including `-> None`. mypy checks `tests/` too, against Python 3.10. The package ships `py.typed`.
- Runtime is stdlib-only (no `dependencies`). Never add a runtime dependency. Dev tools go in `pyproject.toml` → `[project.optional-dependencies] dev`.
- Logging: `self._logger = logging.getLogger(__name__)`. Pass lazy `%s` args, never f-strings, to log calls. Log at info on construction, debug per write, error on I/O failure. GlobalRegistry paths (`config.is_global`) log at debug.
- Build protocol lines with f-strings: `f"{self._meter_type_symbol}:{self._id.spectatord_id}:{value}"`.
- Never raise from instrumentation calls (`increment`, `record`, `set`, `write`). Drop bad input, optionally with a `warning`. Writers catch `OSError` and log it. Only `Config` raises (`ValueError` on an invalid location).
- Defaults: use `X | None = None` and build the object inside the function. Never use mutable or object default args.
- Registry pattern: each meter gets `<type>(name, tags=None)` and `<type>_with_id(meter_id)`.
- Every meter class has a docstring explaining its Atlas semantics. ruff doesn't enforce this; keep doing it anyway.
- Commit subjects are short and imperative with the PR number: `Fix LineBuffer payload byte accounting (#98)`.

### Adding a meter type
1. `spectator/meter/<name>.py`: subclass `Meter`, default `writer` to `NoopWriter()`, pass the SpectatorD symbol to `super().__init__`.
2. Add both factory methods to `Registry`.
3. Register the symbol in `protocol_parser._METER_CLASSES`.
4. Import it in `spectator/__init__.py` and add it to `__all__`.
5. Add `tests/meter/test_<name>.py`, plus cases in `tests/test_registry.py` and `tests/test_protocol_parser.py`.

### Adding a writer / output location
Subclass `Writer`. Add it to `WriterUnion` and `new_writer`, add the location to `Config.is_valid_output_location`, and document it in the `Config` docstring.

### Tests
- Write `unittest.TestCase` classes; pytest runs them. Import from top-level `spectator`, and import helpers relatively (`from ..udp_server import UdpServer`).
- Assert exact protocol lines: use `Registry(Config("memory"))` or `Counter(id, MemoryWriter())`, then `writer().last_line()`.
- Socket tests: wrap `UdpServer()` (ephemeral port) or `UnixServer()` in `contextlib.closing`.
- Env vars: use `patch.dict(os.environ, {...})`. Never leave the env mutated.
- Time: use `ManualClock`, never `sleep`.
- Every bug fix ships with a regression test.

## Critical Gotchas

### Import-time state
- `GlobalRegistry` is built at `import spectator`. Its env vars (`SPECTATOR_OUTPUT_LOCATION`, `NETFLIX_CONTAINER_NAME`, `TITUS_CONTAINER_NAME`, `NETFLIX_PROCESS_NAME`) must be set before the first import.
- `Registry()` reads the env when it is constructed (#96). Never reintroduce `config: Config = Config()`, because that default is evaluated once at import. The sentence in the `Config` docstring saying `Registry()` reads config at import is stale.
- `tests/conftest.py` strips the `NETFLIX_*` / `TITUS_*` env vars before any test imports `spectator`. Keep global env scrubbing there.
- `SocketWriter` opens its socket lazily on the first `write()`, so `import spectator` never opens a socket. Keep it lazy.

### Configuration
- `SPECTATOR_OUTPUT_LOCATION` overrides any location passed in code, including `Config("memory")` in tests. Unset it in your shell before running tests.
- The env-derived `nf.container` / `nf.process` tags override `extra_common_tags` keys with the same name.
- `new_writer` mutates `config.location`: `"udp"` becomes `udp://127.0.0.1:1234` and `"unix"` becomes `unix:///run/spectatord/spectatord.unix`.
- Match locations by scheme prefix (`startswith("udp://")`), never by substring. A Unix path containing `udp` was once misrouted (#93).
- `file://` paths are percent-decoded with `unquote` (#97).
- A `MeterId(...)` built directly skips extra common tags. Use `Registry.new_id()`. The `*_with_id()` methods do not add common tags.
- `Registry.new_id()` builds the `MeterId` once, from the caller's tags merged with the extra common tags. Never go back to `MeterId(name, tags).with_tags(...)` on that path; it builds every id twice.

### Writers & threading
- `SocketWriter._lock` is an `RLock` so that `close()` called from a signal handler cannot deadlock. Never change it to a `Lock`.
- `close()` sets `_closed`, flushes the buffer, then closes the socket in `finally` (#95). Writes after `close()` are no-ops.
- `buffer_size > 0` starts a daemon thread that flushes every 5 s. In pre-fork servers (gunicorn, multiprocessing), create buffered Registries after the fork.
- `LineBuffer` counts UTF-8 bytes plus the `\n` separators (#98). Never size it with `len(str)` for non-ASCII text.
- `FileWriter.close()` only flushes stdout/stderr and must never close them (#94).
- `MemoryWriter.close()` clears the captured lines, so assert before closing.
- Writers catch only `OSError`. Anything else, such as a `UnicodeEncodeError` from lone surrogates, propagates to the caller.

### Meter semantics (wire contract with SpectatorD)
- The type symbols (`c C U g m A t T d D S`) and the `symbol:id:value` line format are a protocol contract. Changing them breaks ingestion.
- `MeterId` replaces characters outside `[-._A-Za-z0-9~^]` with `_`, drops non-str or empty tag keys/values with a warning, and sorts tags in `spectatord_id`. Expected strings in tests must list tags in sorted order.
- `Counter.increment` silently drops `delta <= 0`. Timers and distribution summaries silently drop negative values.
- `Gauge(ttl_seconds=N)` emits the symbol `g,N`. The default TTL is 900 s; SpectatorD enforces a minimum of 5 s.
- `MonotonicCounterUint.set()` takes a `ctypes.c_uint64`, not an `int`.
- Time code blocks with `with StopWatch(timer):`. There is no `timer.stopwatch()` method, despite what the `PercentileTimer` docstring says.
- `DistinctCountSketch` encoding must stay byte-identical to the other Spectator clients: UTF-8 with `errors="replace"`, 8-byte little-endian ints, `bool` rejected, then base64.
- Percentile timers and summaries (up to 300× the cost) and `DistinctCountSketch` need low, bounded tag cardinality. Never use IDs or raw user input as tag values.

### Tests & environment
- `tests/test_global_registry.py` binds UDP `127.0.0.1:1234`, the default SpectatorD port, so it fails if a local `spectatord` is running.

### Packaging & public API
- Packages are auto-discovered (`include = ["spectator*"]`). `py.typed` ships through `[tool.setuptools.package-data]`; a non-`.py` file needed at runtime must be added there too.
- Add any non-`.py` file under `spectator/` to `MANIFEST.in` or `check-manifest` fails. New top-level repo-only files (docs, configs) go in `[tool.check-manifest] ignore` in `pyproject.toml` instead.
- `__all__` in `spectator/__init__.py` defines the public API, so renaming or removing a name is a breaking change. `GlobalRegistry` is deprecated but must keep working.
- Secrets: automated releases use the `PYPI_API_TOKEN` GitHub Actions secret, and manual releases use a maintainer's local `~/.pypirc` or twine credentials. Never commit `~/.pypirc`, tokens, `dist/` or `venv/`.
