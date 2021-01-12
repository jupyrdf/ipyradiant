# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from ..query.api import SPARQLQueryFramer


class RelationTypes(SPARQLQueryFramer):
    """A query class for collecting all relations of interest in an RDF graph.

    TODO is this overlapping with reified query?
      e.g. this one is returning triples from the reification pattern...
    """

    sparql = """
    # Example of mapping from RDF relations, either plain relations or reified ones.
    #
    # - ?iri: the relation; uniquely identifies a triple (relation between two nodes)
    # - ?source, ?target: the resources representing the relation's endpoint nodes
    # - ?predicate: a tag (usually an IRI) representing the relation type.
    #
    #  Note: needs a fictitious IRI for the relation that uses the base namespace

    SELECT DISTINCT ?iri ?predicate ?source ?target
    WHERE {
        {
          # Plain relations, non-reified
            ?source ?predicate ?target.

            FILTER ( isIRI ( ?target ) ).  # prevent bad things

            # Plain relations must get their fictitious IRI from constructs like this.
            # Using the triple components ensures a unique IRI identifying the triple.
            BIND (
                IRI (
                    CONCAT (
                      STR ( base: ),
                      MD5( CONCAT( STR( ?predicate ), STR( ?source ), STR( ?target )))
                    )
                )
              AS ?iri
            )
        }
    }
    """


class ReifiedRelations(SPARQLQueryFramer):
    """A query class for collecting all reified relations (via rdf:Statement) in an RDF
    graph.
    """

    sparql = """
    # Example of mapping from RDF reified relations via rdf:Statement
    #
    # - ?iri: the reified relation IRI
    # - ?source, ?target: the resources representing the relation's endpoint nodes
    # - ?predicate: a tag (usually an IRI) representing the relation type.

    SELECT DISTINCT ?iri ?predicate ?source ?target
    WHERE {
        ?iri a rdf:Statement;
            rdf:subject ?source;
            rdf:predicate ?predicate;
            rdf:object ?target.
    }
    """


class RelationProperties(SPARQLQueryFramer):
    """A query class for collecting all reified relation properties in an RDF graph."""

    sparql = """
    # Example of reified relation properties query.
    #
    # - ?iri: the reified relation IRI
    # - ?predicate: the name (URI) of the property
    # - ?value: the value for the predicate

    SELECT DISTINCT ?iri ?predicate ?value
    {
      ?iri ?predicate ?value.
    }
    """
