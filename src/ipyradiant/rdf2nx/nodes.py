# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import pandas
import rdflib

from ..query.framer import SPARQLQueryFramer


class NodeIRIs(SPARQLQueryFramer):
    """This query must return unique IRIs for subjects in the graph, which are used to
    create LPG nodes.
    """

    sparql = """
    # Example query for the IRIs of RDF resources that you want to become LPG nodes.

    SELECT DISTINCT ?iri
    WHERE {
      # This picks up nodes of interests based on their rdf:type, which should be common
      ?iri a ?type_ .
    }
    """

    @classmethod
    def run_query(
        cls,
        graph: rdflib.graph.Graph,
        initBindings: dict = None,
        **initBindingsKwarg,
    ) -> pandas.DataFrame:
        """Overwrite the super method in order to wrap with validation checks."""
        qres = super().run_query(graph, initBindings=initBindings, **initBindingsKwarg)
        # Validating with known requirements on query results
        assert qres.columns == [
            "iri"
        ], "Query results dataframe must be exactly one 'iri' column."
        assert len(set(qres["iri"].values)) == len(
            qres.values
        ), "Query must return unique IRIs."
        return qres


class NodeTypes(SPARQLQueryFramer):
    """This query is typically the same as the NodeIRIs, but the iri should be bound on
    execution, and the type_ of the node should be returned.
    """

    sparql = """
    # Typically this will be same query as NodeIRIs, but return the ?type_ var

    SELECT DISTINCT ?iri ?type_
    WHERE {
      # Copy of code from NodeIRI unless using custom predicate for type.
      ?iri a ?type_ .
    }
    """


class NodeProperties(SPARQLQueryFramer):
    """An example of how to return properties for a LPG node.
    - ?iri: bound to a specific node IRI, to get the properties for that node.
    - ?predicate: IRI for the property name (e.g. ex:hasThing) and is converted into a
        shorter ID by means of a configured IRI->ID converter.
    - ?value: a literal that may be converted using its lexical value.
    """

    sparql = """
    SELECT DISTINCT ?iri ?predicate ?value
    {
      ?iri ?predicate ?value.
    }
    """


class NodeAnnotationProperties(SPARQLQueryFramer):
    """An example of how to return properties for a LPG node.
    - ?iri: bound to a specific node IRI, to get the properties for that node.
    - ?predicate: IRI for the property name (e.g. ex:hasThing) and is converted into a
        shorter ID by means of a configured IRI->ID converter.
    - ?value: a literal that may be converted using its lexical value.

    TODO experimental, taken from https://www.w3.org/TR/rdf-schema/#ch_properties
    """

    sparql = """
    SELECT DISTINCT ?iri ?predicate ?value
    {
      ?iri ?predicate ?value.

      VALUES (?predicate) {
          (rdfs:range)
          (rdfs:domain)
          (rdf:type)
          (rdfs:subClassOf)
          (rdfs:subPropertyOf)  # TODO remove this one?
          (rdfs:label)
          (rdfs:comment)
      }
    }
    """
