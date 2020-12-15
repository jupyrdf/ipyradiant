# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import pytest
from rdflib import Graph, Literal
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

    # Relationships
    graph.add((protagonist, example_ns.counters, antagonist))
    graph.add((antagonist, example_ns.isCounteredBy, protagonist))

    # Antagonist as subject
    graph.add((antagonist, RDFS.label, Literal("The Antagonist")))
    graph.add((antagonist, RDF.type, SCHEMA.Person))
    graph.add((antagonist, example_ns.height, Literal("185.5", datatype=XSD.float)))

    return graph
