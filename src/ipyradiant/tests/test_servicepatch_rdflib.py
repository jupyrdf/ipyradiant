""" Unit Tests for Service Patch
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import rdflib

import ipyradiant

LINKEDDATA_QUERY = """
    SELECT DISTINCT ?s ?p ?o
        WHERE {
            SERVICE <http://linkeddata.uriburner.com/sparql>
            {
                SELECT ?s ?p ?o
                WHERE {?s ?p ?o}
            }
        }
"""

PATCHED_LINKEDDATA_QUERY = """
    SELECT DISTINCT ?s ?p ?o
        WHERE {
            service <http://linkeddata.uriburner.com/sparql>
            {
                SELECT ?s ?p ?o
                WHERE {?s ?p ?o}
            }
        }
"""


def test_service_fix():
    query_str = ipyradiant.service_patch_rdflib(LINKEDDATA_QUERY)
    assert query_str == PATCHED_LINKEDDATA_QUERY


def test_rdflib_version():
    version = rdflib.__version__
    v_split = tuple(map(int, version.split(".")))
    assert v_split <= (5, 0, 0)
