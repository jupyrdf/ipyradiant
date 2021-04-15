# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from rdflib import URIRef
from rdflib.namespace import RDF

from ipyradiant.query.framer import SPARQLQueryFramer
from ipyradiant.rdf2nx import RDF2NX


class CustomNodeIRIs1(SPARQLQueryFramer):
    sparql = """
    PREFIX ex: <https://www.example.org/test/>
    PREFIX schema: <https://schema.org/>

    SELECT DISTINCT ?iri
    WHERE {
        ?iri a schema:Person .

        VALUES (?iri) {
            (ex:Protagonist)
        }
    }
    """


class CustomNodeIRIs2(SPARQLQueryFramer):
    sparql = """
    PREFIX ex: <https://www.example.org/test/>
    PREFIX schema: <https://schema.org/>

    SELECT DISTINCT ?iri
    WHERE {
        ?iri a schema:Person .

        VALUES (?iri) {
            (ex:Antagonist)
        }
    }
    """


class CustomNodeProperties(SPARQLQueryFramer):
    sparql = """
    PREFIX ex: <https://www.example.org/test/>
    PREFIX schema: <https://schema.org/>

    SELECT DISTINCT ?iri ?predicate ?value
    WHERE {
        ?iri a schema:Person ;
            ex:hasItem/rdfs:label ?value

        BIND (ex:hasItem_label AS ?predicate)
    }
    """


def test_rdf2nx(example_ns, SCHEMA, simple_rdf_graph):
    """A simple test for the rdf2nx converter.

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


def test_rdf2nx_custom(example_ns, SCHEMA, simple_rdf_graph):
    """A simple test for the rdf2nx converter w/ custom behavior."""
    namespaces = {"schema": SCHEMA, "ex": example_ns, "base": example_ns}

    # Note: we are replacing the default behavior
    RDF2NX.node_iris = [CustomNodeIRIs1, CustomNodeIRIs2]
    RDF2NX.node_properties = CustomNodeProperties

    # Note: the expected results are only the Protagonist, and for them to have
    #  a data attribute `ex:hasItem_label`

    nx_graph = RDF2NX.convert(rdf_graph=simple_rdf_graph, namespaces=namespaces)

    expected_len = len(list(simple_rdf_graph.triples((None, RDF.type, SCHEMA.Person))))
    assert (
        len(nx_graph) == expected_len
    ), f"Expected len = {expected_len}. Got {len(nx_graph)} nodes."

    expected_keys = {"iri", "ex:hasItem_label"}

    protagonist_iri, protagonist_data = list(nx_graph.nodes(data=True))[0]

    assert len(protagonist_data.keys()) == len(expected_keys)
    assert all([key in expected_keys for key in protagonist_data.keys()])
    assert isinstance(protagonist_data["ex:hasItem_label"], (tuple, list))
    assert len(protagonist_data["ex:hasItem_label"]) > 1
