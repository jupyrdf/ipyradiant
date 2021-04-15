# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from uuid import uuid4

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, Namespace


@pytest.fixture
def example_ns() -> Namespace:
    return Namespace("https://www.example.org/test/")


@pytest.fixture
def SCHEMA() -> Namespace:
    return Namespace("https://schema.org/")


@pytest.fixture
def simple_rdf_graph(example_ns, SCHEMA) -> Graph:
    graph = Graph()

    protagonist = example_ns.Protagonist
    antagonist = example_ns.Antagonist

    # Protagonist as subject
    graph.add((protagonist, RDFS.label, Literal("The Protagonist")))
    graph.add((protagonist, RDF.type, SCHEMA.Person))
    graph.add((protagonist, example_ns.height, Literal("170", datatype=XSD.float)))

    # Antagonist as subject
    graph.add((antagonist, RDFS.label, Literal("The Antagonist")))
    graph.add((antagonist, RDF.type, SCHEMA.Person))
    graph.add((antagonist, example_ns.height, Literal("185.5", datatype=XSD.float)))

    # Items for protagonist
    item = example_ns.Item
    item1_iri = URIRef(item + "/" + str(uuid4()))
    item2_iri = URIRef(item + "/" + str(uuid4()))

    graph.add((item1_iri, RDF.type, item))
    graph.add((item1_iri, RDFS.label, Literal("All-powerful weapon")))
    graph.add((item2_iri, RDF.type, item))
    graph.add((item2_iri, RDFS.label, Literal("Immortality armor")))

    # Relationships
    graph.add((protagonist, example_ns.counters, antagonist))
    graph.add((protagonist, example_ns.hasItem, item1_iri))
    graph.add((protagonist, example_ns.hasItem, item2_iri))
    graph.add((antagonist, example_ns.isCounteredBy, protagonist))

    return graph
