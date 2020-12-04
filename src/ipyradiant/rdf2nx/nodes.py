import pandas
import rdflib

from ..sparql.api import SPARQLQueryFramer


class NodeIRIs(SPARQLQueryFramer):
    """
    This query can return anything you want, as long as it meets one (?) requirement;
    it must return unique IRIs for subjects in the graph (used to create LPG nodes).
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
    """
    TODO
    """

    sparql = """
    # Typically, this will be same query as the node IRIs, but returning the ?type_ variable in the results
    # Here the ?iri variable is bound to a particular node, using the results coming from the node IRI query.
    SELECT DISTINCT ?iri ?type_
    WHERE {
      # Copy of code from NodeIRI unless using custom predicate for type. 
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
        # TODO (uniques check?)
        return qres


class NodeProperties(SPARQLQueryFramer):
    """
    An example of how to return pairs of name/value that represent the properties of a LPG node.
     - ?iri is bound to a specific node IRI, to get the properties for that node.
     - ?predicate is an IRI and is converted into a shorter ID by means of a configured IRI->ID converter.
     - ?value is a literal and, for the moment, is converted into a string, using its lexical value. More options soon (e.g., mapping XSD types to Cortex/python types).
    """

    sparql = """
    SELECT DISTINCT ?iri ?predicate ?value
    {
      ?iri ?predicate ?value.
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
        # TODO (uniques check?)
        return qres
