# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from rdflib import URIRef
from rdflib.namespace import RDF

from ipyradiant.rdf2nx import RDF2NX


def test_rdf2nx(example_ns, SCHEMA, simple_rdf_graph):
    """A simple test for the rdf2nx converter.

    TODO expand as part of #67
    TODO test strict=True
    """
    KNOWN_EDGE = (URIRef(example_ns.Protagonist), URIRef(example_ns.Antagonist))
    namespaces = {"schema": SCHEMA, "ex": example_ns, "base": example_ns}
    nx_graph = RDF2NX.convert(rdf_graph=simple_rdf_graph, namespaces=namespaces)

    try:
        protagonist = nx_graph.nodes[example_ns.Protagonist]
    except KeyError:
        raise KeyError("Protagonist node not found in fixture graph.")

    p_height = protagonist.get("ex:height", None)
    assert (
        type(p_height) == float
    ), "XSD Datatype failed to map to python type correctly."

    p_type = type(protagonist.get("type", None))
    assert not isinstance(
        p_type, type(None)
    ), f"Failed to get type of node from node keys: {protagonist.keys()}"
    assert p_type == URIRef, "URIRef node attribute is not URI."

    assert KNOWN_EDGE in nx_graph.edges(data=False) and KNOWN_EDGE[
        ::-1
    ] in nx_graph.edges(data=False), "Known relations missing in the networkx graph."

    # Run once more with rdf namespace and check type
    namespaces = {"rdf": RDF, **namespaces}
    nx_graph = RDF2NX.convert(rdf_graph=simple_rdf_graph, namespaces=namespaces)

    try:
        protagonist = nx_graph.nodes[example_ns.Protagonist]
    except KeyError:
        raise KeyError("Protagonist node not found in fixture graph.")

    p_type = type(protagonist.get("rdf:type", None))
    assert not isinstance(
        p_type, type(None)
    ), f"Failed to get rdf:type of node from node keys: {protagonist.keys()}"
