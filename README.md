[![Snapshot](https://github.com/Netflix/spectator-py/actions/workflows/snapshot.yml/badge.svg)](https://github.com/Netflix/spectator-py/actions/workflows/snapshot.yml) [![PyPI version](https://badge.fury.io/py/netflix-spectator-py.svg)](https://badge.fury.io/py/netflix-spectator-py)

## Spectator-py

Python thin-client metrics library for use with [Atlas] and [SpectatorD].

See the [Atlas Documentation] site for more details on `spectator-py`.

[Atlas]: https://netflix.github.io/atlas-docs/overview/
[SpectatorD]: https://netflix.github.io/atlas-docs/spectator/agent/usage/
[Atlas Documentation]: https://netflix.github.io/atlas-docs/spectator/lang/py/usage/

## Local Development

Install [pyenv](https://github.com/pyenv/pyenv), possibly with [Homebrew](https://brew.sh/), and
install a recent Python version.

```shell
make setup-venv
make test
make coverage
```
