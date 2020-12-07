import pandas
import rdflib

from ..sparql.api import SPARQLQueryFramer


class RelationTypes(SPARQLQueryFramer):
    """
    TODO
    TODO is this overlapping with reified query? e.g. this one is returning triples from the reification pattern...
    """

    sparql = """
    # 
    # An example of how to define mapping from RDF relations, either plain relations or reified ones.
    #
    # - ?iri is the resource about the relation, and uniquely identifies a triple or a relation between two nodes.
    # - ?source, ?target are the resources representing the relation's endpoint nodes (must refer to LPG node IRIs)
    # - ?predicate is a tag (usually an IRI, but it can be a string???) representing the relation type.
    #
    #  TODO needs a namespace for fictitous IRI
    # 
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
        # TODO
        return qres


class ReifiedRelations(SPARQLQueryFramer):
    """
    TODO
    """

    sparql = """
    SELECT DISTINCT ?iri ?predicate ?source ?target
    WHERE {
        ?iri a rdf:Statement;
            rdf:subject ?source;
            rdf:predicate ?predicate;
            rdf:object ?target.
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
        # TODO
        return qres


class RelationProperties(SPARQLQueryFramer):
    """
    TODO bind IRI
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
        # TODO
        return qres
