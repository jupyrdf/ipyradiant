""" Unit Tests for Query Capabilities
"""
# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.

import rdflib
from SPARQLWrapper import JSON, SPARQLWrapper

DBPEDIA_LABEL_QUERY = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
    LIMIT 5
"""

DBPEDIA_ENDPOINT = "http://dbpedia.org/sparql"

LINKEDDATA_QUERY = """
    SELECT DISTINCT ?s ?p ?o
    WHERE
    { service <http://linkeddata.uriburner.com/sparql> {SELECT ?s ?p ?oWHERE {?s ?p ?o} LIMIT 3}}
"""


def test_remote_query():
    sparql = SPARQLWrapper(DBPEDIA_ENDPOINT)
    sparql.setQuery(DBPEDIA_LABEL_QUERY)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    res = []  # cache results
    for result in results["results"]["bindings"]:
        res.append(result["label"]["value"])

    # check if results are returned and length 5 (LIMIT 5 in query)
    assert len(res) > 0 and len(res) == 5


def test_federated_query():
    graph = rdflib.Graph()
    res = graph.query(LINKEDDATA_QUERY)
    res = list(res)

    for i in res:
        assert len(i) == 3
