# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import pytest
import rdflib
from ipyradiant import CustomURIRef, collapse_predicates
from rdflib import Graph


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
        test_graph, predicates_to_collapse=predicates_to_collapse, namespaces={}
    )
    # test that the node data is indeed collapsed by trying out each key and their expected values.
    first_pred = list(
        collapsed_netx.nodes[rdflib.URIRef("www.testing.com/Luke")].keys()
    )[0]
    second_pred = list(
        collapsed_netx.nodes[rdflib.URIRef("www.testing.com/Luke")].keys()
    )[1]
    assert collapsed_netx.nodes[rdflib.URIRef("www.testing.com/Luke")][
        second_pred
    ] == rdflib.term.Literal("one brother")
    assert collapsed_netx.nodes[rdflib.URIRef("www.testing.com/Luke")][
        first_pred
    ] == CustomURIRef(
        uri=rdflib.URIRef("www.testing.com/EmiratesStadium"), namespaces={}
    )
