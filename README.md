
[![Build Status](https://travis-ci.org/Netflix/spectator-py.svg)](https://travis-ci.org/Netflix/spectator-py/builds)

## Introduction

Python port of the [Spectator] library for Java.

See the Spectator [documentation] for an overview of core concepts and details on [usage].

Supports Python >= 2.7, with Python >= 3.6 recommended.

[Spectator]: https://github.com/Netflix/spectator/
[documentation]: https://netflix.github.io/atlas-docs/spectator/
[usage]: https://netflix.github.io/atlas-docs/spectator/lang/py/usage/

## Local Development

* Install [pyenv](https://github.com/pyenv/pyenv), possibly with [Homebrew](https://brew.sh/).
* Install Python versions: 2.7, 3.6, 3.7, and 3.8. Enable all versions globally.
* Make changes and add tests.
* `tox`

## Release Process

1. Pre-Requisites.

    1. Install packaging tools.

            pip3 install setuptools wheel twine

    1. Configure [PyPI] username.

            cat >~/.pypirc <<EOF
            [distutils]
            index-servers = pypi

            [pypi]
            repository: https://pypi.python.org/pypi
            username: $PYPI_USERNAME
            EOF

1. Bump the version number in [setup.py](./setup.py).

1. Tag the repo and write release notes. The goal is for the [releases] page to be readable.

    1. Clone the upstream project.

    1. Create a new tag.

            git tag v0.1.X

    1. Push the tags to the origin.

            git push origin --tags

    1. Project > Releases > Tags > Select Tag > Create Release

            Primary changes:

            - #<PR number>, <short description>.

            A comprehensive list of changes can be found in the commit log: https://github.com/Netflix/spectator-py/compare/v0.1.<N-1>...v0.1.<N>

1. On your local machine, checkout the tag and run the following command, which will build the
package and upload it to [PyPI].

        git checkout $TAG
        python3.6 setup.py sdist bdist_wheel
        twine check dist/*
        twine upload dist/*

Example release commits:

* [#23](https://github.com/Netflix/spectator-py/commit/5f8ed9dc14ff97315bf579c8d431a00a17037fc0)
* [#24](https://github.com/Netflix/spectator-py/commit/10bf2d0345175f014035d36adb15e2d6ae69e10c)

[PyPI]: https://pypi.org/project/netflix-spectator-py/
[releases]: https://github.com/Netflix/spectator-py/releases
