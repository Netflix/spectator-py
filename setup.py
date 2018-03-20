#!/usr/bin/env python

from setuptools import setup

setup(
    name='netflix-spectator-py',
    version='0.1.3',
    description='Python library for reporting metrics to Atlas.',
    author='Brian Harrington',
    author_email='netflix-atlas@googlegroups.com',
    license='Apache 2.0',
    url='https://github.com/brharrington/spectator-py/',
    packages=['spectator'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
