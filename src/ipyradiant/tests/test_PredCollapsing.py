# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import pytest
import rdflib
from rdflib import Graph

from ipyradiant import CustomURIRef, collapse_predicates


@pytest.fixture(scope="module")
def test_graph():
    graph = Graph()
    graph.add(
        (
            rdflib.URIRef("www.testing.com/Luke"),
            rdflib.URIRef("www.testing.com/builds"),
            rdflib.URIRef("www.testing.com/Programs"),
        )
    )
    graph.add(
        (
            rdflib.URIRef("www.testing.com/Luke"),
            rdflib.URIRef("www.testing.com/has"),
            rdflib.Literal("one brother"),
        )
    )
    graph.add(
        (
            rdflib.URIRef("www.testing.com/Luke"),
            rdflib.URIRef("www.testing.com/wants"),
            rdflib.Literal("two jackets"),
        )
    )
    graph.add(
        (
            rdflib.URIRef("www.testing.com/Luke"),
            rdflib.URIRef("www.testing.com/goes"),
            rdflib.URIRef("www.testing.com/EmiratesStadium"),
        )
    )
    graph.add(
        (
            rdflib.URIRef("www.testing.com/Luke"),
            rdflib.URIRef("www.testing.com/has"),
            rdflib.Literal("one mother"),
        )
    )
    return graph


def test_correct_length(test_graph):
    predicates_to_collapse = [
        rdflib.URIRef("www.testing.com/has"),
        rdflib.URIRef("www.testing.com/goes"),
    ]

    collapsed_netx = collapse_predicates(
        test_graph, predicates_to_collapse=predicates_to_collapse, namespaces={}
    )
    assert len(collapsed_netx) == 3


def test_node_data(test_graph):
    predicates_to_collapse = [
        rdflib.URIRef("www.testing.com/has"),
        rdflib.URIRef("www.testing.com/goes"),
    ]

    collapsed_netx = collapse_predicates(
        test_graph,
        predicates_to_collapse=predicates_to_collapse,
        namespaces={"ts": "www.testing.com/"},
    )
    # test that the node data is indeed collapsed by trying out each key and their expected values.
    first_pred = "ts:has"
    second_pred = "ts:goes"
    subject = rdflib.URIRef("www.testing.com/Luke")
    assert len(collapsed_netx.nodes[subject][first_pred]) == 2

    assert collapsed_netx.nodes[subject][second_pred] == CustomURIRef(
        uri=rdflib.URIRef("www.testing.com/EmiratesStadium"),
        namespaces={"ts": "www.testing.com/"},
    )
    assert "one brother" in collapsed_netx.nodes[subject][first_pred]
    assert "one mother" in collapsed_netx.nodes[subject][first_pred]
