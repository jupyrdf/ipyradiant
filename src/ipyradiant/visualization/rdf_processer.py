import os
import textwrap
from pathlib import Path
from rdflib import URIRef, Literal, Graph
import traitlets as trt
from rdflib.namespace import RDF
from pandas import DataFrame
import ipycytoscape


class CytoscapeGraph:
    """
    Generate a cytoscape graph visualization based on some subgraph (set of triples).

    :param df: a triples DataFrame with the first 3 columns being [subject, predicate,
               object]. All other columns are ignored.
    """

    data_object = trt.Union([trt.Instance(DataFrame),trt.Instance(Graph)])

    def __init__(self, data_object, include_unlabeled=True):
        # reduce Dataframe to first three columns/convert to dataframe if its a graph object
        if isinstance(data_object, Graph):
            self.df = self.rdf_to_dataframe(data_object)
        elif isinstance(data_object, DataFrame):
            self.df = data_object[list(data_object.columns)[:3]]

        self.nodes = {}
        self.edges = []

        self.include_unlabeled = include_unlabeled

        self._build()

    def rdf_to_dataframe(self, rdf_graph):
        return DataFrame(list(rdf_graph))

    def _build(self):
        self._get_base_graph_data()
        self.build_cytoscape_object()

    def _get_base_graph_data(self):
        """Collect cytoscape graph data from the DataFrame."""
        df = self.df
        df.columns = ["s", "p", "o"] + list(df.columns[3:])

        # collect uris & edges
        element_set = set()
        edges = []
        for i, (s, p, o) in df.iterrows():
            if p != RDF.type:
                if isinstance(s, URIRef):
                    element_set.add(s)
                if isinstance(o, URIRef):
                    element_set.add(o)
                if not isinstance(o, Literal):
                    edges.append(
                        {"source": s, "target": o, "label": f"{Path(p).name}",}
                    )

        # create nodes
        nodes = {}
        for uri in element_set:
            pathed_node = Path(uri)
            nodes[uri] = {
                "id": uri,
                "name": f"{pathed_node.parent.name} {pathed_node.name}",
            }


        self.nodes = nodes
        self.edges = edges


    @property
    def cytoscape_json_data(self):
        """Create the data structures cytoscape uses."""

        return{
            "nodes": [{"data":v} for v in self.nodes.values()],
            "edges": [{"data":v} for v in self.edges]
        }

    def build_cytoscape_object(self):
        """Creates the actual cytoscape object."""
        self.cytoscapeobj = ipycytoscape.CytoscapeWidget()
        self.cytoscapeobj.graph.add_graph_from_json(self.cytoscape_json_data,directed=True)

    # def isolate_node(self,node):
    #     df_with_node_as_subj = self.df["s" == node]
