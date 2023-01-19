import os

from setuptools import setup


def read(fname):
    """Utility function to read a file, for publishing the README with the package."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="netflix-spectator-py",
    version="0.2.10",
    python_requires=">3.5",
    description="Python library for reporting metrics to the Netflix Atlas Timeseries Database.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Netflix Telemetry Engineering",
    author_email="netflix-atlas@googlegroups.com",
    license="Apache 2.0",
    url="https://github.com/Netflix/spectator-py",
    packages=["spectator", "spectator.histogram"],
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
