import pytest
import rdflib
from ipyradiant import collapse_preds
from rdflib import Graph, URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph


@pytest.fixture(scope="module")
def test_graph():
    graph = Graph()
    graph.add(
        (
            rdflib.URIRef("www.testing.com/Luke"),
            rdflib.URIRef("www.testing.com/hates"),
            rdflib.URIRef("www.testing.com/TottenhamHotspur"),
        )
    )
    graph.add(
        (
            rdflib.URIRef("www.testing.com/Luke"),
            rdflib.URIRef("www.testing.com/has"),
            rdflib.Literal("scarves"),
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
    preds_to_collapse = [
        rdflib.URIRef("www.testing.com/has"),
        rdflib.URIRef("www.testing.com/goes"),
    ]
    subjects = [
        rdflib.URIRef("www.testing.com/EmiratesStadium"),
    ]
    netx_version = rdflib_to_networkx_graph(test_graph)
    assert len(netx_version) == 5
    collapsed_netx = collapse_preds(netx_version, preds_to_collapse, subjects)
    assert len(collapsed_netx) == 4


def test_node_data(test_graph):
    preds_to_collapse = [
        rdflib.URIRef("www.testing.com/has"),
        rdflib.URIRef("www.testing.com/goes"),
    ]
    subjects = [
        rdflib.URIRef("www.testing.com/EmiratesStadium"),
    ]
    netx_version = rdflib_to_networkx_graph(test_graph)
    collapsed_netx = collapse_preds(netx_version, preds_to_collapse, subjects)
    assert (
        collapsed_netx.nodes.get(URIRef("www.testing.com/Luke")).get(
            rdflib.term.URIRef("www.testing.com/has")
        )
        == "scarves"
    )
    assert collapsed_netx.nodes.get(URIRef("www.testing.com/Luke")).get(
        rdflib.term.URIRef("www.testing.com/goes")
    ) == rdflib.term.URIRef("www.testing.com/EmiratesStadium")
