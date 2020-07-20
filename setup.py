#!/usr/bin/env python
"""Setuptools script for ipyradiant."""
import re

from setuptools import find_packages, setup

try:
    __version__ = re.findall(
        r"""__version__ = ["']+([0-9\.]*)["']+""", open("ipyradiant/__init__.py").read(),
    )[0]
except IndexError:
    raise RuntimeError("Could not find __version__ in 'ipyradiant/__init__.py'!")

setup(
    name="ipyradiant",
    version=__version__,
    description="A Jupyter widget for working with RDF graphs.",
    long_description=open("README.md").read(),
    keywords="ipyradiant",
    author="Zach Welz",
    author_email="welz.zachary@gmail.com",
    url="https://github.com/zwelz3/ipyradiant",
    license="BSD-3-Clause",
    package_data={},
    install_requires=[
    ],
    include_package_data=True,
    extras_require={
    },
)
