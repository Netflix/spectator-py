import os

from setuptools import setup


def read(fname):
    """Utility function to read a file, for publishing the README with the package."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="netflix-spectator-py",
    version="1.0.0rc2",
    python_requires=">3.9",
    description="Python library for reporting metrics to SpectatorD and the Netflix Atlas Timeseries Database.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Netflix Telemetry Engineering",
    author_email="netflix-atlas@googlegroups.com",
    license="Apache 2.0",
    url="https://github.com/Netflix/spectator-py",
    packages=["spectator", "spectator.meter", "spectator.writer"],
    install_requires=[],
    extras_require={
        "dev": [
            "check-manifest",
            "pylint",
            "pytest-cov",
            "pytest"
        ]
    }
)
