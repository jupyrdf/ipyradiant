""" ipyradiant main file
"""
# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import logging

import rdflib

from ._version import __version__
from .basic_tools import MultiPanelSelect
from .loader import FileManager, PathLoader, UpLoader
from .query import QueryWidget
from .remote_query import RemoteQueryWidget
from .visualization import CytoscapeVisualizer, DatashaderVisualizer, LayoutSelector

__all__ = [
    "__version__",
    "CytoscapeVisualizer",
    "DatashaderVisualizer",
    "FileManager",
    "LayoutSelector",
    "PathLoader",
    "QueryWidget",
    "RemoteQueryWidget",
    "UpLoader",
    "MultiPanelSelect",
    "set_logger_level",
    "service_patch_rdflib",
]


def set_logger_level(level):
    logger = logging.getLogger("ipyradiant")
    logger.setLevel(level)


def service_patch_rdflib(query_str):
    # check for rdflib version, if <=5.0.0 throw warning
    version = rdflib.__version__
    v_split = tuple(map(int, version.split(".")))
    check = v_split <= (5, 0, 0)

    if check:
        if "SERVICE" in query_str:
            query_str = query_str.replace("SERVICE", "service")
            logger = logging.getLogger(__name__)
            logger.warning(
                "SERVICE found in query. RDFlib currently only supports `service`, to be fixed in the next release>5.0.0"
            )
    return query_str
