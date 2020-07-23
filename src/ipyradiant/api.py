import traitlets as T

import ipywidgets as W
from rdflib import BNode, Graph

from .loader import LoadWidget
from .query import QueryWidget


class RadiantObject(W.Tab):
    graph = T.Instance(Graph, allow_none=True)
    graph_id = T.Instance(BNode)
    load_widget = T.Instance(LoadWidget)
    query_widget = T.Instance(QueryWidget)
    log = W.Output()

    def __init__(self, graph: Graph = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        T.link((self.load_widget, "graph"), (self, "graph"))
        T.link((self, "graph"), (self.query_widget, "graph"))

        if graph:
            self.graph = graph
            self.graph_id = graph.identifier

        self.children = [self.load_widget, self.query_widget]
        self.set_title(0, "RDF Loader")
        self.set_title(1, "Query Panel")

    @T.default("graph")
    def make_default_graph(self):
        return Graph()

    @T.default("graph_id")
    def make_default_graph_id(self):
        return self.graph.identifier

    @T.default("load_widget")
    def make_default_load_widget(self):
        load_widget = LoadWidget()
        return load_widget

    @T.default("query_widget")
    def make_default_query_widget(self):
        query_widget = QueryWidget(self.graph)
        return query_widget
