""" Unit Tests for Service Patch
"""
# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import unittest

import ipyradiant


class ServicePatchTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ServicePatchTest, self).__init__(*args, **kwargs)

    # Remote Query Test
    def test1(self):
        query_str = """
            SELECT DISTINCT ?s ?p ?o
            WHERE
            { SERVICE <http://linkeddata.uriburner.com/sparql> {SELECT ?s ?p ?oWHERE {?s ?p ?o}               }}
        """
        query_str = ipyradiant.service_patch_rdflib(query_str)
        self.assertEqual(
            query_str,
            """SELECT DISTINCT ?s ?p ?o
                                        WHERE
                                        { service <http://linkeddata.uriburner.com/sparql> {SELECT ?s ?p ?oWHERE {?s ?p ?o}               }}
                                        """,
        )
