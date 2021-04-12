""" query widgets
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

__all__ = ["QueryWidget", "SPARQLQueryFramer", "service_patch_rdflib"]

from .app import QueryWidget
from .framer import SPARQLQueryFramer
from .utils import service_patch_rdflib
