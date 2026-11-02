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

## Releasing

Releases are published to [PyPI] by the [Release workflow], which runs when a `vX.Y.Z` tag is
created in `Netflix/spectator-py`. The workflow builds the tagged commit without running the tests,
so only release a commit that has passed CI.

1. **Bump the version** in `pyproject.toml` in a pull request ([example][bump-example]). Use
   [semantic versioning]: patch for fixes, minor for new features, major for breaking changes to the
   public API (`__all__` in `spectator/__init__.py`). Merge it and wait for the [Snapshot] build on
   `main` to pass.

2. **Check that `main` has the new version.** The tag must point at a commit whose version matches
   it, or the publish fails.

   ```shell
   git fetch origin
   git show origin/main:pyproject.toml | grep '^version'
   ```

3. **Create the release.** This creates the tag, which starts the Release workflow, and generates the
   release notes from the merged pull requests.

   ```shell
   gh release create vX.Y.Z --repo Netflix/spectator-py --target main --title vX.Y.Z --generate-notes
   ```

   Or on GitHub: **Releases** > **Draft a new release**, create the tag `vX.Y.Z` on `main`, and click
   **Generate release notes**.

4. **Confirm the publish.** Check that the [Release workflow] run succeeded and that `X.Y.Z` appears
   on [PyPI].

### If the publish fails

- If `X.Y.Z` did not reach PyPI, delete the release and its tag, fix the problem, and create the
  release again:

  ```shell
  gh release delete vX.Y.Z --repo Netflix/spectator-py --cleanup-tag --yes
  ```

- PyPI never accepts the same version twice, even after it is deleted there. If `X.Y.Z` reached
  PyPI, release the next version instead.
- An authentication error at the publish step means the `PYPI_API_TOKEN` repository secret needs to
  be replaced.

### Release candidates

Set the version to `X.Y.ZrcN` (for example `1.3.0rc1`), tag it `vX.Y.Z-rc.N` (for example
`v1.3.0-rc.1`), and add `--prerelease` to `gh release create`. pip only installs release candidates
when asked, for example with `pip install --pre netflix-spectator-py`.

### Manual release

Only if GitHub Actions is unavailable. You need maintainer access to the PyPI project and an API
token for it. Follow steps 1 to 3, then upload from the tag:

```shell
git checkout vX.Y.Z
make setup-venv
make check-manifest                                    # builds dist/ and runs twine check
TWINE_USERNAME=__token__ venv/bin/twine upload dist/*  # paste the API token when prompted
```

[PyPI]: https://pypi.org/project/netflix-spectator-py/
[Release workflow]: https://github.com/Netflix/spectator-py/actions/workflows/release.yml
[Snapshot]: https://github.com/Netflix/spectator-py/actions/workflows/snapshot.yml
[bump-example]: https://github.com/Netflix/spectator-py/pull/100
[semantic versioning]: https://semver.org/
